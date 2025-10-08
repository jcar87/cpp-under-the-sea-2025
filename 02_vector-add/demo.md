conan install . 
cmake --preset conan-release
cmake --build --preset conan-release
./build/Release/vectorAdd