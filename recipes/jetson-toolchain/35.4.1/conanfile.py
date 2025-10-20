import os
from conan import ConanFile
from conan.tools.files import copy, download, mkdir


class ArmToolchainPackage(ConanFile):
    name = "jetson-toolchain"
    version = "35.4.1"
    settings = "os", "arch"
    package_type = "application"

    @property
    def _toolchain(self):
        return "aarch64-linux"

    def validate(self):
        pass

    def source(self):
        download(self, "https://developer.nvidia.com/downloads/embedded/l4t/r36_release_v4.4/release/tegra_software_license_agreement-tegra-linux.txt",
                 "LICENSE", verify=False)

    def build(self):
        # TODO: Conan's get() breaks relative symlinks, should not be the case
        download(self, "https://developer.nvidia.com/embedded/jetson-linux/bootlin-toolchain-gcc-93",
            filename="jetson-toolchain.tar.gz",
            sha256="7725b4603193a9d3751d2715ef242bd16ded46b4e0610c83e76d8891cf580975")
        mkdir(self, os.path.join(self.source_folder, "unpacked"))
        self.run(f"tar -xzf jetson-toolchain.tar.gz --strip-components=1 -C {self.source_folder}/unpacked")

    def package_id(self):
        self.info.settings_target = self.settings_target
        # We only want the ``arch`` setting
        self.info.settings_target.rm_safe("os")
        self.info.settings_target.rm_safe("compiler")
        self.info.settings_target.rm_safe("build_type")

    def package(self):
        copy(self, "*", src=os.path.join(self.source_folder, "unpacked"), dst=self.package_folder)
        copy(self, "LICENSE", src=os.path.join(self.source_folder, "unpacked"), dst=os.path.join(self.package_folder, "licenses"))

    def finalize(self):
        copy(self, "*", src=self.immutable_package_folder, dst=self.package_folder)
        self.run(f'"{os.path.join(self.package_folder, "relocate-sdk.sh")}"')

    def package_info(self):
        self.cpp_info.bindirs = ["bin", "aarch64-buildroot-linux-gnu/bin"]

        self.conf_info.define("tools.build:compiler_executables", {
            "c":   f"{self._toolchain}-gcc",
            "cpp": f"{self._toolchain}-g++",
        })
