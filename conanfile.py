from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conans import ConanFile, tools
import os
import shutil

class Conan(ConanFile):
    name = "sdl2"
    version = "2.0.14"
    description = "A cross-platform development library designed to provide low level " \
                  "access to audio, keyboard, mouse, joystick, and graphics hardware " \
                  "via OpenGL and Direct3D."
    homepage = "https://www.libsdl.org"
    license = "Zlib https://www.libsdl.org/license.php"
    url = f"https://github.com/ssrobins/conan-{name}"
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps"
    revision_mode = "scm"
    exports_sources = [
        "CMakeLists.diff",
        "CMakeLists.txt",
        "HIDDeviceManager.diff",
        "SDL_uikitappdelegate.diff"]
    zip_folder_name = f"SDL2-{version}"
    zip_name = f"{zip_folder_name}.tar.gz"
    build_subfolder = "build"
    source_subfolder = "source"

    def system_requirements(self):
        if self.settings.os == "Linux":
            installer = tools.SystemPackageTool()
            installer.install("libasound2-dev")

    def layout(self):
        self.folders.build = f"cmake-build-{str(self.settings.build_type).lower()}"

    def source(self):
        tools.get(f"https://www.libsdl.org/release/{self.zip_name}")
        os.rename(self.zip_folder_name, self.source_subfolder)
        
        # Apply a patch to the SDL2 CMakeLists.txt file with the following changes:
        # https://bugzilla.libsdl.org/show_bug.cgi?id=5415
        # https://bugzilla.libsdl.org/show_bug.cgi?id=5417
        tools.patch(base_path=self.source_subfolder, patch_file="CMakeLists.diff")
        tools.patch(base_path=self.source_subfolder, patch_file="HIDDeviceManager.diff")
        tools.patch(base_path=self.source_subfolder, patch_file="SDL_uikitappdelegate.diff")

    def generate(self):
        tc = CMakeToolchain(self)
        if self.settings.os == "Android":
            tc.generator = "Ninja Multi-Config"
        elif self.settings.os == "iOS":
            tc.generator = "Xcode"
            tc.variables["CMAKE_OSX_DEPLOYMENT_TARGET"] = self.settings.os.version
        elif self.settings.os == "Linux":
            tc.generator = "Ninja Multi-Config"
        elif self.settings.os == "Macos":
            tc.generator = "Xcode"
            tc.variables["CMAKE_OSX_DEPLOYMENT_TARGET"] = self.settings.os.version
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        if self.settings.os == "Android":
            self.copy("*.java", dst="android", src=os.path.join(self.source_subfolder, "android-project", "app", "src", "main", "java", "org", "libsdl", "app"))
        elif self.settings.compiler == "Visual Studio":
            self.copy("*.pdb", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.includedirs = [os.path.join("include", "SDL2")]
        if self.settings.build_type == "Debug":
            self.cpp_info.libs = ["SDL2d", "SDL2maind"]
        else:
            self.cpp_info.libs = ["SDL2", "SDL2main"]
        if self.settings.os == "Windows":
            self.cpp_info.libs.extend(["Imm32", "SetupAPI", "Version", "WinMM"])
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["dl", "m", "pthread"])
        elif self.settings.os == "Macos":
            self.cpp_info.libs.append("iconv")
            frameworks = ["Cocoa", "Carbon", "IOKit", "CoreVideo", "CoreAudio", "AudioToolbox", "ForceFeedback"]
            for framework in frameworks:
                self.cpp_info.exelinkflags.append(f"-framework {framework}")
        elif self.settings.os == "Android":
            if self.settings.build_type == "Debug":
                self.cpp_info.libs.append("hidapid")
            else:
                self.cpp_info.libs.append("hidapi")
            self.cpp_info.libs.extend(["android", "GLESv1_CM", "GLESv2", "log"])
        elif self.settings.os == "iOS":
            self.cpp_info.libs.append("iconv")
            frameworks = ["AVFoundation", "CoreBluetooth", "CoreGraphics", "CoreHaptics", "CoreMotion", "Foundation", "GameController", "Metal", "OpenGLES", "QuartzCore", "UIKit", "CoreVideo", "IOKit", "CoreAudio", "AudioToolbox"]
            for framework in frameworks:
                self.cpp_info.exelinkflags.append(f"-framework {framework}")
        elif self.settings.os == "Android":
            self.cpp_info.libs.extend(["android"])
