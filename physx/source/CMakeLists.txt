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

# XXX(phcerdan) the template is actually empty? Maybe populated after? No harm having an empty header meanwhile.
set(HEADER_GUARD_NAME "CONFIG")
set(HEADER_CONTENT "")

# generate PxPhysXConfig.h header that will contain PhysX configuration defines like PX_PHYSX_STATIC_LIB
configure_file(${CMAKEMODULES_PATH}/template/PxIncludeTemplate.h ${PHYSX_ROOT_DIR}/include/PxConfig.h)


# Copy GPU lib to build and install tree
if(NOT DISABLE_CUDA_PHYSX AND NOT APPLE)
    # Build tree
    add_custom_command(TARGET PhysX POST_BUILD
            COMMAND "${CMAKE_COMMAND}" -E copy_directory
            ${PROJECT_SOURCE_DIR}/bin/${PLATFORM_BIN_NAME}/$<CONFIG>/
            "${CMAKE_CURRENT_BINARY_DIR}/"
            COMMENT "Copying libPhysXGPU from the appropriate source folder to the build directory.")
    # Install tree
    install(FILES ${PROJECT_SOURCE_DIR}/bin/${PLATFORM_BIN_NAME}/$<CONFIG>
            DESTINATION ${PHYSX_INSTALL_PREFIX}/bin/)
endif()


# Package version
include(CMakePackageConfigHelpers)
write_basic_package_version_file(
        ${CMAKE_CURRENT_BINARY_DIR}/PhysXConfigVersion.cmake
        VERSION ${PHYSX_VERSION}
        COMPATIBILITY SameMajorVersion)
