from conans import ConanFile, CMake, os


class AzureUAMQPCConan(ConanFile):
    name = "Azure-uAMQP-C"
    version = "1.0.41"
    generators = "cmake" 
    settings = "os", "arch", "compiler", "build_type"
    url = "https://github.com/bincrafters/conan-azure-uamqp-c"
    source_url = "https://github.com/Azure/azure-uamqp-c"
    git_tag = "2017-08-11"
    description = "AMQP library for C"
    license = "https://github.com/Azure/azure-uamqp-c/blob/master/LICENSE"
    lib_short_name = "azure-uamqp-c"
    
    def source(self):
        self.run("git clone --depth=1 --branch={0} {1}.git"
                .format(self.git_tag, self.source_url)) 

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_dir=self.lib_short_name, build_dir="./")
        cmake.build()
        
    def package(self):
        self.copy(pattern="*", dst="include", src="include")		
        self.copy(pattern="*", dst="lib", src="lib")

    def package_info(self):
        self.cpp_info.libs = self.collect_libs()

