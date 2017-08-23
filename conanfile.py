from conans import ConanFile, CMake, os, tools


class AzureUAMQPCConan(ConanFile):
    name = "Azure-uAMQP-C"
    version = "1.0.41"
    generators = "cmake" 
    settings = "os", "arch", "compiler", "build_type"
    url = "https://github.com/bincrafters/conan-azure-uamqp-c"
    source_url = "https://github.com/Azure/azure-uamqp-c"
    description = "AMQP library for C"
    license = "https://github.com/Azure/azure-uamqp-c/blob/master/LICENSE"
    requires = "Azure-C-Shared-Utility/1.0.41@bincrafters/stable"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    release_date = "2017-08-11"
    release_name = "%s-%s" % (name.lower(), release_date)
    lib_short_name = "uamqp"
    
    def source(self):
        tools.get("%s/archive/%s.tar.gz" % (self.source_url, self.release_date))

    def configure(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            self.options.shared = False

    def build(self):
        conan_magic_lines='''project(%s)
        include(../conanbuildinfo.cmake)
        conan_basic_setup()
        ''' % self.lib_short_name
        
        tools.replace_in_file("%s/CMakeLists.txt" % self.release_name, "project(%s)" % self.lib_short_name, conan_magic_lines)
        cmake = CMake(self)
        cmake.definitions["skip_samples"] = True
        cmake.definitions["use_installed_dependencies"] = True
        cmake.definitions["azure_c_shared_utility_DIR"] = self.deps_cpp_info["Azure-C-Shared-Utility"].res_paths[0]
        cmake.configure(source_dir=self.release_name)
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst=".", src=".")
        self.copy(pattern="*", dst="include", src=path.join(self.release_name, "inc"))
        self.copy(pattern="*.lib", dst="lib", src="lib")
        self.copy(pattern="*.dll", dst="bin", src=".")
        self.copy(pattern="*.a", dst="lib", src="lib")
        self.copy(pattern="*.so*", dst="lib", src=".")
        self.copy(pattern="*.dylib", dst="bin", src=".")

    def package_info(self):
        self.cpp_info.libs = self.collect_libs()
