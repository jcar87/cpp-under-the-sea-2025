import os
import xml.etree.ElementTree as ET

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, download
from conan.tools.scm import Version


required_conan_version = ">=2.1.0"


class CudaToolkitConan(ConanFile):
    name = "cuda-toolkit"
    version = "12.8.1"
    package_type = "shared-library"
    license = "CUDA Toolkit End-User License Agreement"
    homepage = "https://developer.nvidia.com/cuda-toolkit"
    description = "A development environment for creating high performance GPU-accelerated applications"
    settings = "os", "arch", "compiler", "build_type"

    def validate(self):
        if self.settings.os not in ["Windows", "Linux"]:
            raise ConanInvalidConfiguration("Operating system not supported")
        
    def requirements(self):
        if self.settings_build.os == "Windows":
            self.tool_requires("7zip/22.01")

    def build(self):
        os = str(self.settings.os)
        arch = str(self.settings.arch)

        installer_url = self.conan_data['sources'][self.version][os][arch]['url']
        installer_md5 = self.conan_data['sources'][self.version][os][arch]['md5']
        installer_sha256 = self.conan_data['sources'][self.version][os][arch]['sha256']

        self.output.info(f'Cuda installer URL: {installer_url}')
        installer_filename = "installer"
        download(self, installer_url, installer_filename, md5=installer_md5, sha256=installer_sha256)

        if os == "Windows":
            self.run(f"7z x {installer_filename} -o{self.build_folder}")
        else: 
            # linux: `--override` is needed to prevent the installer from checking
            #        the gcc version currently installed on the system
            self.run(f"sh {installer_filename} --extract={self.build_folder} --override")
    
    def package(self):
        toolkit_version = Version(self.version)
        if self.settings.os == "Windows":
            components = [
                "cuda_cccl/thrust/thrust.nvi", # on 11+
                "cuda_cudart/cudart/cudart.nvi",
                "cuda_cuobjdump/cuobjdump/cuobjdump.nvi",
                # "cuda_cupti/cupti/cupti.nvi",
                "cuda_cuxxfilt/cuxxfilt/cuxxfilt.nvi",
                "cuda_nvcc/nvcc/nvcc.nvi",
                "cuda_nvdisasm/nvdisasm/nvdisasm.nvi",
                "cuda_nvml_dev/nvml_dev/nvml_dev.nvi",
                "cuda_nvprof/nvprof/nvprof.nvi",
                "cuda_nvprune/nvprune/nvprune.nvi",
                "cuda_nvrtc/nvrtc_dev/nvrtc_dev.nvi",
                "cuda_nvrtc/nvrtc/nvrtc.nvi",
                "cuda_nvtx/nvtx/nvtx.nvi",
                "cuda_profiler_api/cuda_profiler_api/cuda_profiler_api.nvi",
                # "cuda_nvvp/CUDAVisualProfiler/CUDAVisualProfiler.nvi",
                "cuda_sanitizer_api/sanitizer/sanitizer.nvi",
                "CUDAToolkit/CUDAToolkit.nvi",
                "libcublas/cublas_dev/cublas_dev.nvi",
                "libcublas/cublas/cublas.nvi",
                "libcufft/cufft_dev/cufft_dev.nvi",
                "libcufft/cufft/cufft.nvi",
                "libcurand/curand_dev/curand_dev.nvi",
                "libcurand/curand/curand.nvi",
                "libcusolver/cusolver_dev/cusolver_dev.nvi",
                "libcusolver/cusolver/cusolver.nvi",
                "libcusparse/cusparse_dev/cusparse_dev.nvi",
                "libcusparse/cusparse/cusparse.nvi",
                "libnpp/npp_dev/npp_dev.nvi",
                "libnpp/npp/npp.nvi",
                "libnvjitlink/nvjitlink/nvjitlink.nvi",
                "libnvjpeg/nvjpeg_dev/nvjpeg_dev.nvi",
                "libnvjpeg/nvjpeg/nvjpeg.nvi",
                "visual_studio_integration/CUDAVisualStudioIntegration/CUDAVisualStudioIntegration.nvi"
            ]

            if toolkit_version >= "12.4.0":
                components.append("libnvfatbin/nvfatbin/nvfatbin.nvi")

            if toolkit_version < "12.0" and toolkit_version >= "11.0":
                components.append("cuda_memcheck/memcheck/memcheck.nvi")

            if toolkit_version < "11.0":
                components = [
                    # "cuda_cccl/thrust/thrust.nvi", # on 11+
                    "cudart/cudart.nvi",
                    "cuobjdump/cuobjdump.nvi",
                    # "cuda_cupti/cupti/cupti.nvi",
                    #"cuda_cuxxfilt/cuxxfilt/cuxxfilt.nvi",
                    "memcheck/memcheck.nvi",
                    "nvcc/nvcc.nvi",
                    "nvdisasm/nvdisasm.nvi",
                    "nvml_dev/nvml_dev.nvi",
                    "nvprof/nvprof.nvi",
                    "nvprune/nvprune.nvi",
                    "nvrtc_dev/nvrtc_dev.nvi",
                    "nvrtc/nvrtc.nvi",
                    "nvtx/nvtx.nvi",
                    # "cuda_nvvp/CUDAVisualProfiler/CUDAVisualProfiler.nvi",
                    "sanitizer/sanitizer.nvi",
                    "CUDAToolkit/CUDAToolkit.nvi",
                    "cublas_dev/cublas_dev.nvi",
                    "cublas/cublas.nvi",
                    "cufft_dev/cufft_dev.nvi",
                    "cufft/cufft.nvi",
                    "curand_dev/curand_dev.nvi",
                    "curand/curand.nvi",
                    "cusolver_dev/cusolver_dev.nvi",
                    "cusolver/cusolver.nvi",
                    "cusparse_dev/cusparse_dev.nvi",
                    "cusparse/cusparse.nvi",
                    "npp_dev/npp_dev.nvi",
                    "npp/npp.nvi",
                    "nvjpeg_dev/nvjpeg_dev.nvi",
                    "nvjpeg/nvjpeg.nvi",
                    "CUDAVisualStudioIntegration/CUDAVisualStudioIntegration.nvi"
                ]


            for nvi_file in components:
                source_folder = os.path.dirname(nvi_file)
                self.output.info(f"Component folder: {source_folder}")
                nvi_file = f"{self.build_folder}/{nvi_file}"
                              
                tree = ET.parse(nvi_file).getroot()

                # This is going to be slow because there's a 'copy' for each file
                # but it will retain the correct folder structure as if it was installed
                # by the installer
                for x in tree.findall("phases/standard[@phase='copyFiles']/copyFile"):
                    if 'source' in x.attrib:
                        continue

                    pattern = x.attrib['target']
                    dest = os.path.join(self.package_folder, os.path.dirname(x.attrib['target']))
                    copy(self, pattern, source_folder, dest, keep_path=False)

        elif self.settings.os == "Linux":
            dev_components = [
                "cuda_cccl",
                "cuda_cudart",
                "cuda_nvml_dev", 
                "cuda_nvrtc",
                "cuda_nvtx",
                "cuda_profiler_api",
                "libcublas",
                "libcufft",
                "libcurand",
                "libcusolver",
                "libcusparse",
                "libnpp",
                "libnvjitlink",
                "libnvjpeg"
                ]
            if toolkit_version >= "12.4.0":
                dev_components.append("libnvfatbin")

            cuda_compiler = [
                "cuda_cuobjdump",
                "cuda_cxxfilt",
                "cuda_nvcc",
                "cuda_nvprune",
            ]

            for component in [*dev_components, *cuda_compiler]:
                self.output.info(f"Component: {component}")
                copy(self, "*", src=os.path.join(self.build_folder, component), dst=self.package_folder)

    def package_id(self):
        # TODO:  we need to determine what the best logic is here.
        #        for example: all binaries are `Release`, and clang may be supported on Linux, etc.
        pass

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CUDAToolkit") # what consumers will expect
        self.cpp_info.set_property("cmake_find_mode", "none") # but don't generate it
        self.cpp_info.set_property("cmake_target_name", "CUDA::toolkit")

        #TODO: Use tools.build:compiler_executables ?
        nvcc = "nvcc.exe" if self.settings.os == "Windows" else "nvcc"
        self.buildenv_info.define_path("CUDACXX", os.path.join(self.package_folder, "bin", nvcc))
        self.buildenv_info.define_path("CUDAToolkit_ROOT", self.package_folder)

        self.cpp_info.libdirs = ["lib64" if self.settings.os == "Linux" else "lib"]

        # Only has effect when Windows and the CMake generator is Visual Studio
        if self.settings_build.os == "Windows":
            package_folder = f"{self.package_folder}".replace('\\', '/')
            self.conf_info.define("tools.cmake.cmaketoolchain:toolset_cuda", package_folder)
