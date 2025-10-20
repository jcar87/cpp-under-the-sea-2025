import os
import json
from pathlib import Path

from conan import ConanFile
from conan.tools.build import cross_building
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, download, get, load, rename, replace_in_file

class CudaToolkitConan(ConanFile):
    name = "cuda-toolkit"
    version = "12.2.0"
    license = "CUDA Toolkit End-User License Agreement"
    url = "https://github.com/conan-io/cuda-conan"
    homepage = "https://developer.nvidia.com/cuda-toolkit"
    description = "A development environment for creating high performance GPU-accelerated applications"
    settings = "os", "arch"

    def validate(self):
        if self.settings.os not in ["Windows", "Linux"]:
            raise ConanInvalidConfiguration("Operating system not supported")
        
        # TODO: there are compiler version constraints, maximum supported cppstd, etc
        
    def requirements(self):
        pass

    def build(self):
        base_url = "https://developer.download.nvidia.com/compute/cuda/redist"
        distrib = f"redistrib_{self.version}.json"
        json_distrib = f"{base_url}/{distrib}"
        download(self, url=json_distrib, filename=distrib)
        json_content = load(self, distrib)
        cuda_distrib = json.loads(json_content)

        arch = "aarch64" if self.settings.arch == "armv8" else str(self.settings.arch)

        cuda_platform = f"{str(self.settings.os).lower()}-{arch}"
        self.output.info(f"About to download CUDA toolkit components for {cuda_platform}")

        linux_components = [
            "cuda_cccl",
        #    "cuda_compat", # tegra only
            "cuda_cudart",
            "cuda_nvml_dev", 
            "cuda_nvrtc",
            "libcublas",
          #  "libcudla", # tegra only?
            "libcufft",
            "libcufile",
            "libcurand",
            "libcusolver",
            "libcuspares",
            "libnvjitlink",
            "libnpp",
            "libnvjpeg",
            "cuda_cuobjdump",
            "cuda_profiler_api",
            "cuda_cxxfilt",
            "cuda_nvcc",
            "cuda_nvprune",
        ]

        if self.settings.arch == "armv8":
            linux_components.append("cuda_compat")
            linux_components.append("libcudla")
        
        for component_name, data in cuda_distrib.items():
            #if not isinstance(data, dict) or component_name == "nvidia_driver" or "nsight" in component_name or not data.get(cuda_platform, None):
            if component_name not in linux_components:
                self.output.info(f"Skipping {component_name}")
                continue
            else:
                self.output.info(f"Downloading {component_name}")
            
            url = f"{base_url}/{data[cuda_platform]['relative_path']}"
            checksum = data[cuda_platform]['sha256']
            get(self, url, sha256=checksum, destination="cuda", strip_root=True, keep_permissions=False)
            rename(self, f"{self.build_folder}/cuda/LICENSE", f"LICENSE_{component_name}")
        if self.settings.os == "Linux":
            replace_in_file(self, "cuda/bin/nvcc.profile", '$(TOP)/$(_TARGET_DIR_)/', '$(CONAN_CUDA_TARGET_DIR)/')
            replace_in_file(self, "cuda/bin/nvcc.profile", "lib$(_TARGET_SIZE_)", "lib" )
    
    def package(self):
        for folder in ["bin", "nvml", "nvvm", "compat"]:
            copy(self, "*", src=os.path.join(self.build_folder, "cuda", folder), dst=os.path.join(self.package_folder, folder))

        if self.settings.os == "Linux":
            arch = "aarch64" if self.settings.arch == "armv8" else str(self.settings.arch)
            targets_folder = f"targets/{arch}-linux"
            copy(self, "*", src=os.path.join(self.build_folder, "cuda", "lib"), dst=os.path.join(self.package_folder, targets_folder, "lib"))
            copy(self, "*", src=os.path.join(self.build_folder, "cuda", "include"), dst=os.path.join(self.package_folder, targets_folder, "include"))
            copy(self, "*", src=os.path.join(self.build_folder, "cuda", "res"), dst=os.path.join(self.package_folder, targets_folder, "res"))

            include_symlink = Path(f"targets/{arch}-linux/include")
            lib64_symlink = Path(f"targets/{arch}-linux/lib")
            res_symlink = Path(f"targets/{arch}-linux/res")
            include = Path(os.path.join(self.package_folder, "include"))
            lib = Path(os.path.join(self.package_folder, "lib64"))
            res = Path(os.path.join(self.package_folder, "res"))
            include.symlink_to(include_symlink)
            lib.symlink_to(lib64_symlink)
            res.symlink_to(res_symlink)

    def package_info(self):
        if self.settings_target:
            self.buildenv_info.define_path("CUDACXX", os.path.join(self.package_folder, "bin", "nvcc"))
        elif not cross_building(self):
            self.buildenv_info.define_path("CUDACXX", os.path.join(self.package_folder, "bin", "nvcc"))
            
        if not self.settings_target:
            arch = "aarch64" if self.settings.arch == "armv8" else str(self.settings.arch)
            self.buildenv_info.define_path("CUDAToolkit_ROOT", self.package_folder)
            self.buildenv_info.define_path("CONAN_CUDA_TARGET_DIR", os.path.join(self.package_folder, "targets", f"{arch}-linux"))

        self.cpp_info.libdirs = ['lib64']
        if self.settings.arch == "armv8":
            self.cpp_info.libdirs.append("compat")
            self.cpp_info.libdirs.append("targets/aarch64-linux/lib")
