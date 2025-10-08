conan install --require=llama-cpp/b6565

source conanrun.sh

llama-cli \
  --hf-repo unsloth/Llama-3.2-1B-Instruct-GGUF \
  --hf-file Llama-3.2-1B-Instruct-Q6_K.gguf \
  -p "How do you install CUDA on Linux for C++ development?\n"

  