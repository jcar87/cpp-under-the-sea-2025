# SPDX-FileCopyrightText: Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

cmake_minimum_required(VERSION 3.15 FATAL_ERROR)

project(CCCLDemo CUDA CXX)

set(CMAKE_BUILD_RPATH_USE_ORIGIN ON)

# if (CMAKE_CROSSCOMPILING)
#   include(cmake/cross_test.cmake)
# endif()


find_package(CUDAToolkit REQUIRED)
find_package(fmt REQUIRED)

# Default to building for the GPU on the current system
if(NOT DEFINED CMAKE_CUDA_ARCHITECTURES)
  set(CMAKE_CUDA_ARCHITECTURES native)
endif()


add_executable(example example.cpp)
target_compile_features(example PUBLIC cuda_std_17 cxx_std_17)
set_source_files_properties(example.cpp PROPERTIES LANGUAGE CUDA)
target_link_libraries(example PRIVATE fmt::fmt)

include(CTest)
enable_testing()


# Example app and test
add_test(NAME test_example COMMAND example)
set_tests_properties(test_example PROPERTIES
  PASS_REGULAR_EXPRESSION "Detected device system: ${CCCL_THRUST_DEVICE_SYSTEM}"
)

# Device query app and test
add_executable(device_query device_query.cpp)
target_link_libraries(device_query PRIVATE CUDA::cudart fmt::fmt)
target_include_directories(device_query PRIVATE include)

add_test(NAME test_device_query COMMAND device_query)
set_tests_properties(test_device_query PROPERTIES
 PASS_REGULAR_EXPRESSION "Device 0: \"Xavier\"")