from conans import ConanFile, CMake, tools
import os
import time

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        
    def imports(self):
        self.copy("*", dst="bin", src="lib")
        
    def imports(self):
        self.copy("*.dll", dst="bin", src="bin")
        self.copy("*.dylib*", dst="bin", src="lib")
        self.copy("*.so*", dst="bin", src="lib")        
        self.copy("*.cmake", dst="res", src="res")
        
    def test(self):
        os.chdir("bin")
        try:
            self.run("LD_PRELOAD=/usr/lib/debug/lib/x86_64-linux-gnu/libSegFault.so && ./test_package")
        except:
            time.sleep(3)
            self.run("ls -lah")
            self.run('gdb --batch --quiet -ex "thread apply all bt full" -ex "quit" test_package  core')
