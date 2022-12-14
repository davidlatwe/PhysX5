# NVIDIA PhysX

Copyright (c) 2008-2022 NVIDIA Corporation. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
 * Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
 * Neither the name of NVIDIA CORPORATION nor the names of its
   contributors may be used to endorse or promote products derived
   from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS "AS IS" AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

## About this fork

### Changes
* Adopted [`NVIDIAGameWorks/PhysX#222`](https://github.com/NVIDIAGameWorks/PhysX/pull/222) (partially) for CMake style build
* Adopted [`NVIDIA-Omniverse/PhysX#51`](https://github.com/NVIDIA-Omniverse/PhysX/pull/51) for macOS support
* Additional build scripts, also able to build snippets in headless mode (no render)
* The `PhysXGpu` lib will be compressed by [UPX](https://upx.github.io/) (from 140MB to 25MB)

### Build
The additional `physx/CMakeLists.txt` is an entry point that leads to `physx/compiler/public`, where Nvidia build script starts with.

Just run `./build_for_win32.ps1` or `./build_for_linux.sh` if on Linux.

#### Build script flags
* `-gpu` To build PhysX with GPU features or not.
* `-snippets` Build snippets.
* `-render` Build snippets with render (interactive 3d view window) enabled or not.
* `-buildtype` Just, build type.
* `-clean` Clean up build dir, and external dependencies before build.

## Introduction

Welcome to the NVIDIA PhysX source code repository.

This repository contains source releases of the PhysX and Flow SDKs used in NVIDIA Omniverse.

## Documentation

The user guide and API documentation are available on [GitHub Pages](https://nvidia-omniverse.github.io/PhysX). Please create an [Issue](https://github.com/NVIDIA-Omniverse/PhysX/issues/) if you find a documentation issue.

## Instructions

Please see instructions specific to each of the libraries in the respective subfolder.

## Support

* Please use GitHub [Discussions](https://github.com/NVIDIA-Omniverse/PhysX/discussions/) for questions and comments.
* GitHub [Issues](https://github.com/NVIDIA-Omniverse/PhysX/issues) should only be used for bug reports or documentation issues.
* You can also ask questions in the NVIDIA Omniverse #physics [Discord Channel](https://discord.com/invite/XWQNJDNuaC).

