MESSAGE(STATUS "PhysX Build Platform: " ${TARGET_BUILD_PLATFORM})
MESSAGE(STATUS "  CXX Compiler: " ${CMAKE_CXX_COMPILER})

set(NV_USE_GAMEWORKS_OUTPUT_DIRS ON)
set(NV_USE_STATIC_WINCRT ON)

set(PX_OUTPUT_LIB_DIR ${PHYSX_ROOT_DIR})
set(PX_OUTPUT_BIN_DIR ${PHYSX_ROOT_DIR})

include(NvidiaBuildOptions)

message(STATUS "PLATFORM_BIN_NAME: ${PLATFORM_BIN_NAME}")


set(physx_build_targets_file "${CMAKE_CURRENT_BINARY_DIR}/PhysXTargets.cmake")
set(install_cmake_dir "${PX_ROOT_LIB_DIR}/cmake/physx")

# Include the platform specific CMakeLists
message(STATUS "PLATFORM_CMAKELISTS: ${PLATFORM_CMAKELISTS}")
include(${PLATFORM_CMAKELISTS})

# generate PxPhysXConfig.h header that will contain PhysX configuration defines like PX_PHYSX_STATIC_LIB
# XXX(phcerdan) the template is actually empty? Maybe populated after? No harm having an empty header meanwhile.
SET(HEADER_GUARD_NAME "CONFIG")
SET(HEADER_CONTENT "")
configure_file(${CMAKEMODULES_PATH}/template/PxIncludeTemplate.h ${PHYSX_ROOT_DIR}/include/PxConfig.h)

### Move libPhysXGPU from source tree to build and install tree:
# libPhysXGPU libraries are in the repository (/bin) but the CUDA code is not open
# XXX(phcerdan) Nvdia does not provides GNU (gcc) GPU libaries, only clang.
# I guess both compilers are ABI compatible, but not explicitly tested in this codebase
# GCC in linux is not an option right now upstream
