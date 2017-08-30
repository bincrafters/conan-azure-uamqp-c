#Copyright (c) Microsoft. All rights reserved.
#Licensed under the MIT license. See LICENSE file in the project root for full license information.
cmake_minimum_required(VERSION 2.8.11)
project(test-uamqp)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

macro(compileAsC99)
  if (CMAKE_VERSION VERSION_LESS "3.1")
    if (CMAKE_C_COMPILER_ID STREQUAL "GNU")
      set (CMAKE_C_FLAGS "--std=c99 ${CMAKE_C_FLAGS}")
      set (CMAKE_CXX_FLAGS "--std=c++11 ${CMAKE_CXX_FLAGS}")
    endif()
  else()
    set (CMAKE_C_STANDARD 99)
    set (CMAKE_CXX_STANDARD 11)
  endif()
endmacro(compileAsC99)

compileAsC99()

file(GLOB SOURCE_FILES *.c)

add_executable(local_client_sample ${SOURCE_FILES})

include_directories(.)
if(WIN32)
	#windows needs this define
	add_definitions(-D_CRT_SECURE_NO_WARNINGS)
	add_definitions(-DGB_MEASURE_MEMORY_FOR_THIS -DGB_DEBUG_ALLOC)

if(WINCE)
	target_link_libraries(local_client_sample
		uamqp aziotsharedutil secur32)
else()
	target_link_libraries(local_client_sample
		uamqp aziotsharedutil ws2_32 secur32)
endif()

	if(${use_openssl})
		target_link_libraries(local_client_sample
			$ENV{OpenSSLDir}/lib/ssleay32.lib $ENV{OpenSSLDir}/lib/libeay32.lib)

		file(COPY $ENV{OpenSSLDir}/bin/libeay32.dll DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/Debug)
		file(COPY $ENV{OpenSSLDir}/bin/ssleay32.dll DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/Debug)
	endif()
	if(${use_wolfssl})
		target_link_libraries(local_client_sample $ENV{WolfSSLDir}/Debug/wolfssl.lib)
	endif()
else()
	target_link_libraries(local_client_sample uamqp aziotsharedutil)
endif()
