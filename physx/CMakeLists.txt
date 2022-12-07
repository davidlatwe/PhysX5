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

cmake_minimum_required(VERSION 3.13)

file(READ "version.txt" PHYSX_VERSION)
project(PhysX
        LANGUAGES C CXX
        VERSION ${PHYSX_VERSION})
message(STATUS "PhysX VERSION: ${PHYSX_VERSION}")
cmake_policy(SET CMP0057 NEW) # Enable IN_LIST
cmake_policy(SET CMP0077 NEW) # option() does nothing when variable is alredy set

# PhysXSDK options:
option(PX_BUILDSNIPPETS "Generate the snippets" OFF)
option(PX_CMAKE_SUPPRESS_REGENERATION "Disable zero_check projects" OFF)

# PhysX options:
option(PX_SCALAR_MATH "Disable SIMD math" OFF)
option(PX_GENERATE_STATIC_LIBRARIES "Generate static libraries" OFF)
option(PX_EXPORT_LOWLEVEL_PDB "Export low level pdb's" OFF)
option(PX_GENERATE_GPU_PROJECTS_ONLY "Generate GPU projects only. (Untested)" OFF)
mark_as_advanced(PX_GENERATE_GPU_PROJECTS_ONLY)

set(PUBLIC_RELEASE 1)

if(DISABLE_CUDA_PHYSX)
    set(DISABLE_CUDA_PHYSX "DISABLE_CUDA_PHYSX" CACHE STRING "" FORCE)
    message(STATUS "DISABLE_CUDA_PHYSX: Yes")
else()
    set(DISABLE_CUDA_PHYSX "" CACHE STRING "" FORCE)
    message(STATUS "DISABLE_CUDA_PHYSX: No")
endif()

# Enable folder properties
set_property(GLOBAL PROPERTY USE_FOLDERS ON)

if(CMAKE_CONFIGURATION_TYPES)
    set(CMAKE_CONFIGURATION_TYPES debug checked profile release)
    set(CMAKE_CONFIGURATION_TYPES "${CMAKE_CONFIGURATION_TYPES}" CACHE STRING
        "Reset config to what we need"
        FORCE)

    set(CMAKE_SHARED_LINKER_FLAGS_CHECKED "")
    set(CMAKE_SHARED_LINKER_FLAGS_PROFILE "")

    # XXX(phcerdan) PDB are not for consumers, ignore this line
    # Build PDBs for all configurations.
    # set(CMAKE_SHARED_LINKER_FLAGS "/DEBUG")
endif()

# Disable zero_check projects. The default for Switch and XboxOne is ON.
if(PX_CMAKE_SUPPRESS_REGENERATION)
    set(CMAKE_SUPPRESS_REGENERATION TRUE)
endif()

### Set PHYSX_ROOT_DIR to PROJECT_SOURCE_DIR
if(DEFINED PHYSX_ROOT_DIR)
    message(WARNING "PHYSX_ROOT_DIR is externally defined, but it will be overwritten in this CMakeLists. DEPRECATED")
    message("PHYSX_ROOT_DIR (externally set --not used--): ${PHYSX_ROOT_DIR}")
    message("PHYSX_ROOT_DIR (currently set): ${PROJECT_SOURCE_DIR}")
endif()
set(PHYSX_ROOT_DIR ${PROJECT_SOURCE_DIR})

### Set TARGET_BUILD_PLATFORM using CMAKE_SYSTEM_NAME
# for compatibility with current CMake files,
# for cross-complation, CMAKE_SYSTEM_NAME can be set when running cmake
if(DEFINED TARGET_BUILD_PLATFORM)
    if(TARGET_BUILD_PLATFORM STREQUAL "switch" OR
       TARGET_BUILD_PLATFORM STREQUAL "playstation" OR
       TARGET_BUILD_PLATFORM STREQUAL "ios")
       message(FATAL_ERROR "switch, playstation and ios builds are not valid because have not been tested. Use official repository for these.")
    endif()
    message(INFO "TARGET_BUILD_PLATFORM (externally set --not used--): ${TARGET_BUILD_PLATFORM}")
endif()

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


# Download external dependencies
#

function(get_7z 7z_exe)
    set(pkg_name "7za")
    set(pkg_ver "16.02.4")
    set(pkg_dir "${PROJECT_SOURCE_DIR}/../externals/${pkg_name}")
    if(NOT EXISTS ${pkg_dir})
        file(MAKE_DIRECTORY ${pkg_dir})
        set(file_name "${pkg_name}@${pkg_ver}.zip")
        set(file_md5 "df8c71fbba63a6d2c1d98fbdfa805f78")
        set(output "${PROJECT_SOURCE_DIR}/../download/${file_name}")
        file(DOWNLOAD "https://bootstrap.packman.nvidia.com/${file_name}" ${output} EXPECTED_MD5 ${file_md5})
        execute_process(
                COMMAND ${CMAKE_COMMAND} -E tar -xf "${output}"
                WORKING_DIRECTORY ${pkg_dir}
                RESULT_VARIABLE rv
        )
        if(rv)
            message(FATAL_ERROR ${rv})
        endif()
    endif()

    if(CMAKE_CL_64)
        set(7z_arch "64")
    else()
        set(7z_arch "32")
    endif()

    if(WIN32)
        set(7z_exe ${pkg_dir}/win-x86/${7z_arch}/7za.exe PARENT_SCOPE)
    elseif(APPLE)
        set(7z_exe ${pkg_dir}/mac-x86/${7z_arch}/7za PARENT_SCOPE)
    else()
        set(7z_exe ${pkg_dir}/linux-x86/${7z_arch}/7za PARENT_SCOPE)
    endif()
endfunction()


function(external_package pkg_name pkg_version file_ext file_md5)
    if(EXISTS "${PROJECT_SOURCE_DIR}/../externals/${pkg_name}")
        return()
    endif()
    set(7z_exe "")
    get_7z(7z_exe)
    # Get Package
    set(pkg_dir "${PROJECT_SOURCE_DIR}/../externals/${pkg_name}")
    if(NOT EXISTS ${pkg_dir})
        file(MAKE_DIRECTORY ${pkg_dir})

        set(file_name "${pkg_name}@${pkg_version}.${file_ext}")
        set(url "https://d4i3qtqj3r0z5.cloudfront.net/${file_name}")
        set(output "${PROJECT_SOURCE_DIR}/../download/${file_name}")

        file(DOWNLOAD ${url} ${output} EXPECTED_MD5 ${file_md5})
        message(STATUS "Unzipping: ${output}")
        execute_process(
                COMMAND ${7z_exe} x "${output}"
                WORKING_DIRECTORY ${pkg_dir}
                RESULT_VARIABLE rv
        )
        if(rv)
            message(FATAL_ERROR ${rv})
        endif()
    endif()
endfunction()


external_package("CMakeModules" "1.28.trunk.31965103" "7z" "7eb7cd4cf029ae3b2fa8206511d0cb13")
set(ENV{PM_CMakeModules_PATH} "${PROJECT_SOURCE_DIR}/../externals/CMakeModules")
external_package("rapidjson" "1.1.0-67fac85-073453e1" "7z" "cebce7f986c4505568e8e7c47fcaccdc")
set(ENV{PM_rapidjson_PATH} "${PROJECT_SOURCE_DIR}/../externals/rapidjson")
external_package("clang-physxmetadata" "4.0.0.31968624_1.1" "7z" "d8fc156c7c5db89d486da234bade4b3b")

if(NOT DISABLE_CUDA_PHYSX)
    if(WIN32)
        external_package("freeglut-windows" "3.4_1.1" "7z" "53c4bee83f386beb837f68d0d468f419")
        set(ENV{PM_freeglut_PATH} "${PROJECT_SOURCE_DIR}/../externals/freeglut-windows")
        external_package("PhysXDevice" "18.12.7.3" "7z" "7bb668cfab0dd298f00e746c94ce7003")
        set(ENV{PM_PhysXDevice_PATH} "${PROJECT_SOURCE_DIR}/../externals/PhysXDevice")
    endif()

    if(UNIX AND NOT APPLE)
        external_package("opengl-linux" "2017.5.19.1" "7z" "356e2046346080cfc739e05e69e6736f")
    endif()

    if(WIN32 OR (UNIX AND NOT APPLE))
        external_package("PhysXGpu" "104.1-5.1.1151.32112585-public" "zip" "c78c177a825e2771739a55f2d9402c72")
        set(ENV{PM_PhysXGpu_PATH} "${PROJECT_SOURCE_DIR}/../externals/PhysXGpu")
    endif()

endif()


### Set CMake folders
SET(CMAKEMODULES_PATH $ENV{PM_CMakeModules_PATH} CACHE INTERNAL "Path to CMakeModules")
set(CMAKEMODULES_NAME "CMakeModules" CACHE INTERNAL "CMakeModules name")
set(CMAKEMODULES_VERSION "1.27" CACHE INTERNAL "CMakeModules version from generation batch")
# CMAKE_MODULE_PATH is empty by default
list(APPEND CMAKE_MODULE_PATH ${CMAKEMODULES_PATH})

### Set platform specific files
set(PROJECT_CMAKE_FILES_DIR source/compiler/cmake)
# The following files define all the flags specific to platforms, compilers and build configurations.
# The file is included in the source/ subdirectory
set(PLATFORM_CMAKELISTS "${PHYSX_ROOT_DIR}/${PROJECT_CMAKE_FILES_DIR}/${TARGET_BUILD_PLATFORM}/CMakeLists.txt")

SET(CMAKE_POSITION_INDEPENDENT_CODE ON)

# INSTALL PATHS
if(WIN32)
    SET(CMAKE_INSTALL_PREFIX "${CMAKE_SOURCE_DIR}/../install/windows/PhysX")
elseif(APPLE)
    SET(CMAKE_INSTALL_PREFIX "${CMAKE_SOURCE_DIR}/../install/mac/PhysX")
else()
    SET(CMAKE_INSTALL_PREFIX "${CMAKE_SOURCE_DIR}/../install/linux/PhysX")
endif()
SET(PHYSX_INSTALL_PREFIX ${CMAKE_INSTALL_PREFIX}/PhysX CACHE INTERNAL "Install path to install PhysX")
MESSAGE(STATUS "PHYSX_INSTALL_PREFIX: " ${PHYSX_INSTALL_PREFIX})

# Set PX_ROOT_LIB_DIR (used in cmake files)
string(TOLOWER ${CMAKE_C_COMPILER_ID} compiler_id)
# No need to add TARGET_BUILD_PLATFORM and compiler_id in the folder structure
# set(PX_ROOT_LIB_DIR "${PHYSX_INSTALL_PREFIX}/bin/${TARGET_BUILD_PLATFORM}\.${compiler_id}")
set(PX_ROOT_LIB_DIR "${PHYSX_INSTALL_PREFIX}/bin")

# We add CMakeLists.txt in the source folders, following standard CMake practices
# Add PhysX SDK Source code to solution
set(BUILD_SOURCE_FOLDER ${CMAKE_CURRENT_BINARY_DIR}/sdk_source_bin)
add_subdirectory(source ${BUILD_SOURCE_FOLDER})

if(PX_BUILDSNIPPETS)
    # Add Snippets projects into the solution
    add_subdirectory(${PHYSX_ROOT_DIR}/snippets/compiler/cmake ${CMAKE_CURRENT_BINARY_DIR}/sdk_snippets_bin)

    message("Added Snippets")
endif()
