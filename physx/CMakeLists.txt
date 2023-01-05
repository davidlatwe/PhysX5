## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions
## are met:
##  * Redistributions of source code must retain the above copyright
##    notice, this list of conditions and the following disclaimer.
##  * Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in the
##    documentation and/or other materials provided with the distribution.
##  * Neither the name of NVIDIA CORPORATION nor the names of its
##    contributors may be used to endorse or promote products derived
##    from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ''AS IS'' AND ANY
## EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
## IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
## PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
## PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
## OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
##
## Copyright (c) 2008-2022 NVIDIA Corporation. All rights reserved.

if(APPLE)
    cmake_minimum_required(VERSION 3.19.2)  # Apple ARM
else()
    cmake_minimum_required(VERSION 3.13)  # CMP0077
endif()
cmake_policy(SET CMP0057 NEW) # Enable IN_LIST
cmake_policy(SET CMP0077 NEW) # option() does nothing when variable is alredy set
message(STATUS "CMake version: ${CMAKE_MAJOR_VERSION}.${CMAKE_MINOR_VERSION}.${CMAKE_PATCH_VERSION}")


file(READ "version.txt" PHYSX_VERSION)
project(PhysXSDK
        LANGUAGES C CXX
        VERSION ${PHYSX_VERSION})
message(STATUS "PhysXSDK VERSION: ${PHYSX_VERSION}")


# PhysXSDK options:
option(PX_BUILDSNIPPETS "Generate the snippets" OFF)
option(PX_BUILDSNIPPETS_RENDER "Generate the snippets with rendering enabled" ON)
option(PX_CMAKE_SUPPRESS_REGENERATION "Disable zero_check projects" OFF)

# PhysX options:
option(PX_SCALAR_MATH "Disable SIMD math" OFF)
option(PX_GENERATE_STATIC_LIBRARIES "Generate static libraries" OFF)
option(PX_EXPORT_LOWLEVEL_PDB "Export low level pdb's" OFF)
option(PX_GENERATE_GPU_PROJECTS_ONLY "Generate GPU projects only. (Untested)" OFF)
mark_as_advanced(PX_GENERATE_GPU_PROJECTS_ONLY)

# GPU feature switch:
if(DISABLE_CUDA_PHYSX)
    set(DISABLE_CUDA_PHYSX "DISABLE_CUDA_PHYSX" CACHE STRING "" FORCE)
    message(STATUS "DISABLE_CUDA_PHYSX: Yes")
else()
    set(DISABLE_CUDA_PHYSX "" CACHE STRING "" FORCE)
    message(STATUS "DISABLE_CUDA_PHYSX: No")
endif()

set(RENDER_SNIPPET "")
if(PX_BUILDSNIPPETS_RENDER)
    set(RENDER_SNIPPET "RENDER_SNIPPET")
endif()


# Set PHYSX_ROOT_DIR to PROJECT_SOURCE_DIR
if(DEFINED PHYSX_ROOT_DIR)
    message(WARNING "PHYSX_ROOT_DIR is externally defined, but it will be overwritten in this CMakeLists. DEPRECATED")
    message("PHYSX_ROOT_DIR (externally set --not used--): ${PHYSX_ROOT_DIR}")
    message("PHYSX_ROOT_DIR (currently set): ${PROJECT_SOURCE_DIR}")
endif()
set(PHYSX_ROOT_DIR ${PROJECT_SOURCE_DIR})


# To NvidiaBuildOptions
set(NV_USE_STATIC_WINCRT ON)
set(NV_USE_GAMEWORKS_OUTPUT_DIRS ON)
set(PX_OUTPUT_LIB_DIR ${PHYSX_ROOT_DIR})
set(PX_OUTPUT_BIN_DIR ${PHYSX_ROOT_DIR})


set(TARGET_BUILD_PLATFORM "")
if(CMAKE_SYSTEM_NAME STREQUAL "Windows")
    set(TARGET_BUILD_PLATFORM "windows")
elseif(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    set(TARGET_BUILD_PLATFORM "linux")
elseif(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
    set(TARGET_BUILD_PLATFORM "mac")
elseif(CMAKE_SYSTEM_NAME STREQUAL "Android")
    set(TARGET_BUILD_PLATFORM "android")
endif()

if(APPLE AND CMAKE_HOST_SYSTEM_PROCESSOR STREQUAL "arm64")
    set(PX_OUTPUT_ARCH "arm")
endif()


# Install path
set(CMAKE_INSTALL_PREFIX "${CMAKE_SOURCE_DIR}/../install/${TARGET_BUILD_PLATFORM}/PhysX")
set(PHYSX_INSTALL_PREFIX ${CMAKE_INSTALL_PREFIX} CACHE INTERNAL "Install path to install PhysX")
message(STATUS "PHYSX_INSTALL_PREFIX: " ${PHYSX_INSTALL_PREFIX})


# Package version
include(CMakePackageConfigHelpers)
write_basic_package_version_file(
        ${CMAKE_CURRENT_BINARY_DIR}/PhysXConfigVersion.cmake
        VERSION ${PHYSX_VERSION}
        COMPATIBILITY SameMajorVersion)


# External dependencies
#
if(NOT EXISTS "${PROJECT_SOURCE_DIR}/../external")
    message(FATAL_ERROR "PhysX dependency dir not exists, did you run the download script?" )
endif()

set(ENV{PM_CMakeModules_PATH} "${PROJECT_SOURCE_DIR}/../external/CMakeModules")
set(ENV{PM_rapidjson_PATH} "${PROJECT_SOURCE_DIR}/../external/rapidjson")

if(NOT DISABLE_CUDA_PHYSX AND NOT APPLE)
    if(WIN32)
        set(ENV{PM_freeglut_PATH} "${PROJECT_SOURCE_DIR}/../external/freeglut-windows")
        set(ENV{PM_PhysXDevice_PATH} "${PROJECT_SOURCE_DIR}/../external/PhysXDevice")
    endif()

    if(WIN32 OR UNIX)
        set(ENV{PM_PhysXGpu_PATH} "${PROJECT_SOURCE_DIR}/../external/PhysXGpu")
    endif()
endif()


# Export target?
# set(physx_build_targets_file "${CMAKE_CURRENT_BINARY_DIR}/PhysXTargets.cmake")


add_subdirectory(compiler/public)
