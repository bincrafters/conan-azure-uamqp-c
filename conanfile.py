from conans import ConanFile, CMake, os, tools


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
    build_requires = "Azure-CTest/1.1.0@bincrafters/testing", \
                        "Azure-C-Testrunnerswitcher/1.1.0@bincrafters/testing", \
                        "uMock-C/1.1.0@bincrafters/testing"
    requires = "Azure-C-Shared-Utility/1.0.41@bincrafters/testing"
    
    def source(self):
        self.run("git clone --depth=1 --branch={0} {1}.git"
                .format(self.git_tag, self.source_url)) 

    def build(self):
        tools.replace_in_file("add_subdirectory(add_subdirectory(deps/azure-c-testrunnerswitcher))","")
        tools.replace_in_file("add_subdirectory(deps/azure-ctest)","")
        tools.replace_in_file("add_subdirectory(deps/umock-c)","")    
        tools.replace_in_file("add_subdirectory(deps/azure-c-shared-utility)","")    
        tools.replace_in_file("include(\"dependencies.cmake\")","")    
                
        tools.replace_in_file(
            "target_link_libraries(uamqp aziotsharedutil)",
            "target_link_libraries(uamqp $CONAN_LIBS)") 
           
        cmake = CMake(self)
        cmake.args = ["use_installed_dependencies"]
        cmake.configure(source_dir=self.lib_short_name, build_dir="./")
        cmake.build()
        
    def package(self):
        self.copy(pattern="*", dst="include", src="include")		
        self.copy(pattern="*", dst="lib", src="lib")

    def package_info(self):
        self.cpp_info.libs = self.collect_libs()

