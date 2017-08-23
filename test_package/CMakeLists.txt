#Copyright (c) Microsoft. All rights reserved.
#Licensed under the MIT license. See LICENSE file in the project root for full license information.

#this is CMakeLists.txt for amqp_client_sample

cmake_minimum_required(VERSION 2.8.11)
project(azure-uamqp-c-test)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(CMAKE_VERBOSE_MAKEFILE ON)

set(amqp_client_sample_c_files
    amqp_client_sample.c
)

set(amqp_client_sample_c_files ${amqp_client_sample_c_files} main.c)

set(amqp_client_sample_h_files
    amqp_client_sample.h
)

IF(WIN32)
    #windows needs this define
    add_definitions(-D_CRT_SECURE_NO_WARNINGS)
    add_definitions(-DGB_MEASURE_MEMORY_FOR_THIS -DGB_DEBUG_ALLOC)
ENDIF(WIN32)

include_directories(.)

add_executable(amqp_client_sample ${amqp_client_sample_c_files} ${amqp_client_sample_h_files})

if (WIN32)
    target_link_libraries(amqp_client_sample
        aziotsharedutil
        uamqp
        secur32
        ws2_32)
    if(${use_openssl})
        target_link_libraries(amqp_client_sample $ENV{OpenSSLDir}/lib/ssleay32.lib $ENV{OpenSSLDir}/lib/libeay32.lib)
        file(COPY $ENV{OpenSSLDir}/bin/libeay32.dll DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/Debug)
        file(COPY $ENV{OpenSSLDir}/bin/ssleay32.dll DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/Debug)
    endif()
    if(${use_wolfssl})
        target_link_libraries(amqp_client_sample $ENV{WolfSSLDir}/Debug/wolfssl.lib)
    endif()
else()
    target_link_libraries(amqp_client_sample
        aziotsharedutil
        pthread
        uamqp)
    #if(${use_openssl})
        target_link_libraries(amqp_client_sample ${OPENSSL_LIBRARIES})
    #endif()
endif()
