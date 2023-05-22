#!/usr/bin/env bash

BUILD_TYPE=Release

BUILD_DIR=build/linux/$BUILD_TYPE

echo "-- Checking dependency..."
python3 ./download_external.py --gpu --config $BUILD_TYPE

mkdir -p $BUILD_DIR
pushd $BUILD_DIR
cmake ../../../physx -G Ninja \
    -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
    -DPX_ENABLE_GPU=ON \
	  -DPX_BUILDSNIPPETS=ON \
	  -DPX_BUILDSNIPPETS_RENDER=OFF

cmake --build . --config $BUILD_TYPE
popd

