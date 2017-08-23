// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

#include <stdlib.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdint.h>
#include "amqp_client_sample.h"
#include "azure_uamqp_c/amqp_client.h"
#include "azure_c_shared_utility/socketio.h"
#include "azure_c_shared_utility/platform.h"

static const char* TOPIC_NAME_A = "msgA";
static const char* TOPIC_NAME_B = "msgB";
static const char* APP_NAME_A = "This is the app msg A.";

static uint16_t PACKET_ID_VALUE = 11;
static bool g_continue = true;

#define PORT_NUM_UNENCRYPTED        1883
#define PORT_NUM_ENCRYPTED          8883
#define PORT_NUM_ENCRYPTED_CERT     8884

#define DEFAULT_MSG_TO_SEND         1

static const char* QosToString(QOS_VALUE qosValue)
{
    switch (qosValue)
    {
        case DELIVER_AT_LEAST_ONCE: return "Deliver_At_Least_Once";
        case DELIVER_EXACTLY_ONCE: return "Deliver_Exactly_Once";
        case DELIVER_AT_MOST_ONCE: return "Deliver_At_Most_Once";
        case DELIVER_FAILURE: return "Deliver_Failure";
    }
    return "";
}

static void OnRecvCallback(AMQP_MESSAGE_HANDLE msgHandle, void* context)
{
    (void)context;
    const APP_PAYLOAD* appMsg = amqpmessage_getApplicationMsg(msgHandle);

    (void)printf("Incoming Msg: Packet Id: %d\r\nQOS: %s\r\nTopic Name: %s\r\nIs Retained: %s\r\nIs Duplicate: %s\r\nApp Msg: ", amqpmessage_getPacketId(msgHandle),
        QosToString(amqpmessage_getQosType(msgHandle) ),
        amqpmessage_getTopicName(msgHandle),
        amqpmessage_getIsRetained(msgHandle) ? "true" : "fale",
        amqpmessage_getIsDuplicateMsg(msgHandle) ? "true" : "fale"
        );
    for (size_t index = 0; index < appMsg->length; index++)
    {
        (void)printf("0x%x", appMsg->message[index]);
    }

    (void)printf("\r\n");
}

static void OnCloseComplete(void* context)
{
    (void)context;

    (void)printf("%d: On Close Connection failed\r\n", __LINE__);
}

static void OnOperationComplete(AMQP_CLIENT_HANDLE handle, AMQP_CLIENT_EVENT_RESULT actionResult, const void* msgInfo, void* callbackCtx)
{
    (void)msgInfo;
    (void)callbackCtx;
    switch (actionResult)
    {
        case AMQP_CLIENT_ON_CONNACK:
        {
            (void)printf("ConnAck function called\r\n");

            SUBSCRIBE_PAYLOAD subscribe[2];
            subscribe[0].subscribeTopic = TOPIC_NAME_A;
            subscribe[0].qosReturn = DELIVER_AT_MOST_ONCE;
            subscribe[1].subscribeTopic = TOPIC_NAME_B;
            subscribe[1].qosReturn = DELIVER_EXACTLY_ONCE;

            if (amqp_client_subscribe(handle, PACKET_ID_VALUE++, subscribe, sizeof(subscribe) / sizeof(subscribe[0])) != 0)
            {
                (void)printf("%d: amqp_client_subscribe failed\r\n", __LINE__);
                g_continue = false;
            }
            break;
        }
        case AMQP_CLIENT_ON_SUBSCRIBE_ACK:
        {
            AMQP_MESSAGE_HANDLE msg = amqpmessage_create(PACKET_ID_VALUE++, TOPIC_NAME_A, DELIVER_EXACTLY_ONCE, (const uint8_t*)APP_NAME_A, strlen(APP_NAME_A));
            if (msg == NULL)
            {
                (void)printf("%d: amqpmessage_create failed\r\n", __LINE__);
                g_continue = false;
            }
            else
            {
                if (amqp_client_publish(handle, msg))
                {
                    (void)printf("%d: amqp_client_publish failed\r\n", __LINE__);
                    g_continue = false;
                }
                amqpmessage_destroy(msg);
            }
            // Now send a message that will get 
            break;
        }
        case AMQP_CLIENT_ON_PUBLISH_ACK:
        {
            break;
        }
        case AMQP_CLIENT_ON_PUBLISH_RECV:
        {
            break;
        }
        case AMQP_CLIENT_ON_PUBLISH_REL:
        {
            break;
        }
        case AMQP_CLIENT_ON_PUBLISH_COMP:
        {
            // Done so send disconnect
            amqp_client_disconnect(handle);
            break;
        }
        case AMQP_CLIENT_ON_DISCONNECT:
            g_continue = false;
            break;
        case AMQP_CLIENT_ON_UNSUBSCRIBE_ACK:
        {
            break;
        }
        default:
        {
            (void)printf("unexpected value received for enumeration (%d)\n", (int)actionResult);
        }
    }
}

static void OnErrorComplete(AMQP_CLIENT_HANDLE handle, AMQP_CLIENT_EVENT_ERROR error, void* callbackCtx)
{
    (void)callbackCtx;
    (void)handle;
    switch (error)
    {
    case AMQP_CLIENT_CONNECTION_ERROR:
    case AMQP_CLIENT_PARSE_ERROR:
    case AMQP_CLIENT_MEMORY_ERROR:
    case AMQP_CLIENT_COMMUNICATION_ERROR:
    case AMQP_CLIENT_NO_PING_RESPONSE:
    case AMQP_CLIENT_UNKNOWN_ERROR:
        g_continue = false;
        break;
    }
}

void amqp_client_sample_run()
{
    if (platform_init() != 0)
    {
        (void)printf("platform_init failed\r\n");
    }
    else
    {
        AMQP_CLIENT_HANDLE amqpHandle = amqp_client_init(OnRecvCallback, OnOperationComplete, NULL, OnErrorComplete, NULL);
        if (amqpHandle == NULL)
        {
            (void)printf("amqp_client_init failed\r\n");
        }
        else
        {
            AMQP_CLIENT_OPTIONS options = { 0 };
            options.clientId = "azureiotclient";
            options.willMessage = NULL;
            options.username = NULL;
            options.password = NULL;
            options.keepAliveInterval = 10;
            options.useCleanSession = true;
            options.qualityOfServiceValue = DELIVER_AT_MOST_ONCE;

            SOCKETIO_CONFIG config = {"test.mosquitto.org", PORT_NUM_UNENCRYPTED, NULL};

            XIO_HANDLE xio = xio_create(socketio_get_interface_description(), &config);
            if (xio == NULL)
            {
                (void)printf("xio_create failed\r\n");
            }
            else
            {
                if (amqp_client_connect(amqpHandle, xio, &options) != 0)
                {
                    (void)printf("amqp_client_connect failed\r\n");
                }
                else
                {
                    do
                    {
                        amqp_client_dowork(amqpHandle);
                    } while (g_continue);
                }
                xio_close(xio, OnCloseComplete, NULL);
            }
            amqp_client_deinit(amqpHandle);
        }
        platform_deinit();
    }

#ifdef _CRT_DBG_MAP_ALLOC
    _CrtDumpMemoryLeaks();
#endif
}
