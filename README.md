### CUDA and C++ Development with Conan and CMake – Build on Windows, Linux (and Jetson!)  - C++ Under the Sea 2025

Slides [here](https://github.com/jcar87/cpp-under-the-sea-2025/releases/download/breda-2025/CUDA-cpp-Development-Conan-CMake.pdf)

## License

- `01_llama-cpp`:
 The recipe is adapted from [Conan Center Index](https://github.com/conan-io/conan-center-index) - see [MIT License](https://github.com/conan-io/conan-center-index?tab=MIT-1-ov-file#readme)
- `02_vector-add`:
  Adapted from [cuda-samples](https://github.com/NVIDIA/cuda-samples/tree/master/Samples/0_Introduction/vectorAdd). Please see the individual files which retain the Apache-2.0 license.
- `03_cccl_example`:
  Adapted from [cccl](https://github.com/NVIDIA/cccl/tree/main/examples/thrust_flexible_device_system) and [cuda-samples](https://github.com/NVIDIA/cuda-samples/) - Please see individual files which retain the Apache-2.0 license.
- Recipes in `recipes` subfolder:
  See the LICENSE file in this repository. The license covers **only** the recipes, not the contents of the packages.
  
  Note: the recipes download CUDA Toolkit and Jetson GCC toolchain directly from NVIDIA. Usage is governed by NVIDIA terms of service. Please see CUDA Toolkit End User License Agreement before proceeding.
- Where otherwise not stated (in the file itself), the license from this repository applies.
## Demo 1:

(Tested on Linux)

```
conan export recipes/cuda-toolkit/12.8.1
conan create 01_llama-cpp -s compiler.cppstd=17 --build=missing
conan create 01_llama-cpp -s compiler.cppstd=17 -o "*:with_cuda=True" --build=missing
```

Test *without* CUDA:

```
cd 01_llama-cpp/demo
conan install --require=llama-cpp/b6565

source conanrun.sh

llama-cli \
  --hf-repo unsloth/Llama-3.2-1B-Instruct-GGUF \
  --hf-file Llama-3.2-1B-Instruct-Q6_K.gguf \
  -p "How do you install CUDA on Linux for C++ development?\n"
```

Test *with* CUDA:

```
cd 01_llama-cpp/demo
conan install --require=llama-cpp/b6565 -o "*:with_cuda=True"

source conanrun.sh

llama-cli \
  --hf-repo unsloth/Llama-3.2-1B-Instruct-GGUF \
  --hf-file Llama-3.2-1B-Instruct-Q6_K.gguf \
  -p "How do you install CUDA on Linux for C++ development?\n"
```

## Demo 2:

Adapted from: https://github.com/NVIDIA/cuda-samples/tree/master/Samples/0_Introduction/vectorAdd 

On Linux:
```
conan export recipes/cuda-toolkit/12.8.1 --build=missing

cd 02_vector-add
conan install . 
cmake --preset conan-release
cmake --build --preset conan-release
./build/Release/vectorAdd
```

On Windows:

From a Visual C++ command prompt:

```
conan export recipes/cuda-toolkit/12.8.1

cd 02_vector-add
conan install . -c tools.cmake.cmaketoolchain:generator=Ninja --build=missing
cmake --preset conan-release
cmake --build --preset conan-release
cd build/Release
vectorAdd
```

## Demo 3:

Note: Linux only, assumes all commands are run from a Linux x86_64 box.

Note: CUDA Toolkit 12.2.0 was chosen to support Jetson Xavier NX


Create `cuda-toolkit` package for Linux x86_64:
```
conan create recipes/cuda-toolkit/12.2.0
```

Create `cuda-toolkit` package for Linux aarch64:
```
conan create recipes/cuda-toolkit/12.2.0 -s:h arch=armv8
```

Check that we have two packages for CUDA Toolkit 12.2.0
```

$ conan list "cuda-toolkit/12.2.0:*" --format=compact
Local Cache
  cuda-toolkit/12.2.0
    cuda-toolkit/12.2.0#22496c65fdba18dcac5afd2839a59f27%1760976903.390953 (2025-10-20 16:15:03 UTC)
      cuda-toolkit/12.2.0#22496c65fdba18dcac5afd2839a59f27:63fead0844576fc02943e16909f08fcdddd6f44b
        settings: Linux, x86_64
      cuda-toolkit/12.2.0#22496c65fdba18dcac5afd2839a59f27:c93719558cf197f1df5a7f1d071093e26f0e44a0
        settings: Linux, armv8
```


For cross-building from x86_64 to aarch64 (Jetson), also create a package for the gcc compiler:

```
conan create recipes/jetson-toolchain/35.4.1 -s:h arch=armv8 --build-require
```


### Build for Linux x86_64 natively:

```
cd 03_cccl_example
conan install . 
cmake --preset conan-release
cmake --build --preset conan-release
ctest --preset conan-release
```

Expected result:
```
ctest --preset conan-release
Test project /home/luisc/cpp-under-the-sea-2025/03_cccl_example/build/Release
    Start 1: test_example
1/2 Test #1: test_example .....................   Passed    0.57 sec
    Start 2: test_device_query
2/2 Test #2: test_device_query ................***Failed  Required regular expression not found. Regex=[Device 0: "Xavier"
]  0.48 sec
```
### Cross-build for Jetson

Note: still in `03_cccl_example` directory

```
conan install . -pr jetson
cmake --preset conan-release
cmake --build --preset conan-release
```

Note: to "cross-test" on a remote Jetson device, ensure:
- The current machine has SSH access to a Jetson device, setup with passwordless login (private key)
- Modify `03_cccl_example/cmake/cross_test.cmake` to reflect the remote host and the remote working directory

Cross-testing:

The `ctest --preset conan-release` command should transperently sync up the dependencies and build artifacts to the jetson and report the test result as-if invoked from the Jetson

Remote-run script:

You can `cd build/Release` and invoke `./remote_run.sh device_query` - This will run the executable on the remote host. Note that `./sync_runtime_deps.sh` must have been invoked first.