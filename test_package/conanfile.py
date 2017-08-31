from conans import ConanFile, CMake
import os
import platform
import subprocess


class AzureuamqpcTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    user = os.getenv("CONAN_USERNAME", "bincrafters")
    channel = os.getenv("CONAN_CHANNEL", "testing")
    requires = "Azure-uAMQP-C/1.0.41@%s/%s" % (user, channel)

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_dir=self.conanfile_directory, build_dir="./")
        cmake.build()

    def imports(self):
        self.copy("*.dll", dst="bin", src="bin")
        self.copy("*.dylib*", dst="bin", src="lib")
        self.copy("*.so*", dst="bin", src="lib")
        self.copy("*.cmake", dst="res", src="res")

    def test(self):
        app_name = "local_client_sample"
        if platform.system() == "Windows":
            app_name += ".exe"
        assert(os.path.isfile(os.path.join("res", "uamqpConfig.cmake")))
        assert(os.path.isfile(os.path.join("bin", app_name)))
        subprocess.check_call(os.path.join("bin", app_name))
