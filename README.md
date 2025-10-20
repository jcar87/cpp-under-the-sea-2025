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