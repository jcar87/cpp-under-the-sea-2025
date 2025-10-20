### CUDA and C++ Development with Conan and CMake – Build on Windows, Linux (and Jetson!)  - C++ Under the Sea 2025

[code and slides will be published here]

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