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


# Download external dependencies
#

function(run_process)
    cmake_parse_arguments(PARSE_ARGV 0 PARSED "" "DIR" "CMD")
    execute_process(
            COMMAND ${PARSED_CMD}
            WORKING_DIRECTORY ${PARSED_DIR}
    )
    if(rv)
        message(FATAL_ERROR ${rv})
    endif()
endfunction()


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
        run_process(
            CMD ${CMAKE_COMMAND} -E tar -xf "${output}"
            DIR ${pkg_dir}
        )
    endif()

    set(bitness 32)
    if(CMAKE_SIZEOF_VOID_P EQUAL 8)
        set(bitness 64)
    endif()

    if(WIN32)
        set(7z_exe ${pkg_dir}/win-x86/${bitness}/7za.exe PARENT_SCOPE)
    elseif(APPLE)
        set(7z_exe ${pkg_dir}/mac-x86/${bitness}/7za PARENT_SCOPE)
    else()
        set(7z_exe ${pkg_dir}/linux-x86/${bitness}/7za PARENT_SCOPE)
    endif()
endfunction()


function(un7z archive work_dir)
    set(7z_exe "")
    get_7z(7z_exe)
    message(STATUS "Unzipping: ${archive}")
    run_process(
        CMD ${7z_exe} x -bso0 -- ${archive}
        DIR ${work_dir}
    )
endfunction()


function(download_package url file_name file_md5 dst_dir)
    if(NOT EXISTS ${dst_dir})
        file(MAKE_DIRECTORY ${dst_dir})

        set(output "${PROJECT_SOURCE_DIR}/../download/${file_name}")
        file(DOWNLOAD ${url} ${output} EXPECTED_MD5 ${file_md5})
        un7z(${output} ${dst_dir})

    endif()
endfunction()


function(external_package pkg_name pkg_version file_ext file_md5)
    set(pkg_dir "${PROJECT_SOURCE_DIR}/../externals/${pkg_name}")
    download_package(
            "https://d4i3qtqj3r0z5.cloudfront.net/${pkg_name}@${pkg_version}.${file_ext}"
            "${pkg_name}@${pkg_version}.${file_ext}"
            ${file_md5}
            ${pkg_dir}
    )
endfunction()


external_package("CMakeModules" "1.28.trunk.31965103" "7z" "7eb7cd4cf029ae3b2fa8206511d0cb13")
external_package("rapidjson" "1.1.0-67fac85-073453e1" "7z" "cebce7f986c4505568e8e7c47fcaccdc")
external_package("clang-physxmetadata" "4.0.0.31968624_1.1" "7z" "d8fc156c7c5db89d486da234bade4b3b")

set(ENV{PM_CMakeModules_PATH} "${PROJECT_SOURCE_DIR}/../externals/CMakeModules")
set(ENV{PM_rapidjson_PATH} "${PROJECT_SOURCE_DIR}/../externals/rapidjson")

if(NOT DISABLE_CUDA_PHYSX AND NOT APPLE)
    if(WIN32)
        external_package("freeglut-windows" "3.4_1.1" "7z" "53c4bee83f386beb837f68d0d468f419")
        external_package("PhysXDevice" "18.12.7.3" "7z" "7bb668cfab0dd298f00e746c94ce7003")

        set(ENV{PM_freeglut_PATH} "${PROJECT_SOURCE_DIR}/../externals/freeglut-windows")
        set(ENV{PM_PhysXDevice_PATH} "${PROJECT_SOURCE_DIR}/../externals/PhysXDevice")
    endif()

    if(UNIX)
        external_package("opengl-linux" "2017.5.19.1" "7z" "356e2046346080cfc739e05e69e6736f")
    endif()

    if(WIN32 OR UNIX)
        external_package("PhysXGpu" "104.1-5.1.1151.32112585-public" "zip" "c78c177a825e2771739a55f2d9402c72")

        set(ENV{PM_PhysXGpu_PATH} "${PROJECT_SOURCE_DIR}/../externals/PhysXGpu")
    endif()

    # UPX, to compress GPU lib
    set(upx_version "4.0.1")
    set(upx_dir "${PROJECT_SOURCE_DIR}/../externals/upx")
    if (WIN32)
        set(upx_exe "${upx_dir}/upx-${upx_version}-win64/upx.exe")
        download_package(
                "https://github.com/upx/upx/releases/download/v${upx_version}/upx-${upx_version}-win64.zip"
                "upx-${upx_version}-win64.zip"
                "acf37b08b0788a640edb25e4de6edca9"
                ${upx_dir}
        )

    else()
        set(upx_exe "${upx_dir}/upx-${upx_version}-i386_linux/upx")
        download_package(
                "https://github.com/upx/upx/releases/download/v${upx_version}/upx-${upx_version}-i386_linux.tar.xz"
                "upx-${upx_version}-i386_linux.tar.xz"
                "a36817c86da90a323eb35430f9707074"
                ${upx_dir}
        )
    endif()

    string(TOLOWER ${CMAKE_BUILD_TYPE} config)
    if (${config} STREQUAL "debug")
        set(config "checked")
    endif()

    set(compress_target "")
    if (WIN32)
        set(compress_target "$ENV{PM_PhysXGpu_PATH}/bin/win.x86_64.vc141.mt/${config}/PhysXGpu_64.dll")
    elseif(CMAKE_SYSTEM_PROCESSOR STREQUAL "aarch64")
        set(compress_target "$ENV{PM_PhysXGpu_PATH}/bin/linux.aarch64/${config}/PhysXGpu_64.so")
    elseif("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
        set(compress_target "$ENV{PM_PhysXGpu_PATH}/bin/linux.clang/${config}/PhysXGpu_64.so")
    endif()

    message(STATUS "About to compress GPU lib: ${compress_target}")
    execute_process(
            COMMAND ${upx_exe} -t -qq ${compress_target}
            WORKING_DIRECTORY ${upx_dir}
            RESULT_VARIABLE not_compressed
    )
    if(not_compressed)
        message(STATUS "Compressing GPU lib, this may take a few minutes...")
        run_process(
            CMD ${upx_exe} ${compress_target}
            DIR ${upx_dir}
        )
    else()
        message(STATUS "GPU lib already been compressed.")
    endif()

endif()


add_subdirectory(compiler/public)
