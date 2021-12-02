from conans import ConanFile, CMake, tools
import os
import shutil

class Conan(ConanFile):
    name = "sdl2"
    version = "2.0.18"
    description = "A cross-platform development library designed to provide low level " \
                  "access to audio, keyboard, mouse, joystick, and graphics hardware " \
                  "via OpenGL and Direct3D."
    homepage = "https://www.libsdl.org"
    license = "Zlib https://www.libsdl.org/license.php"
    url = f"https://github.com/ssrobins/conan-{name}"
    settings = "os", "compiler", "arch"
    generators = "cmake"
    revision_mode = "scm"
    exports_sources = [
        "CMakeLists.diff",
        "CMakeLists.txt",
        "HIDDeviceManager.diff"]
    zip_folder_name = f"SDL2-{version}"
    zip_name = f"{zip_folder_name}.tar.gz"
    build_subfolder = "build"
    source_subfolder = "source"

    def system_requirements(self):
        if self.settings.os == "Linux":
            installer = tools.SystemPackageTool()
            installer.install("libasound2-dev")

    def build_requirements(self):
        self.build_requires("cmake_utils/3.0.0#4e7b4d9bfca394477325cdfc8eacce8b1c82583e")

    def source(self):
        tools.get(f"https://www.libsdl.org/release/{self.zip_name}")
        os.rename(self.zip_folder_name, self.source_subfolder)

        #tools.patch(base_path=self.source_subfolder, patch_file="CMakeLists.diff")
        #tools.patch(base_path=self.source_subfolder, patch_file="HIDDeviceManager.diff")

    def build(self):
        from cmake_utils import cmake_init, cmake_build_debug_release
        cmake = cmake_init(self.settings, CMake(self), self.build_folder)
        cmake_build_debug_release(cmake, self.build_subfolder, self.run)

    def package(self):
        from cmake_utils import cmake_init, cmake_install_debug_release
        cmake = cmake_init(self.settings, CMake(self), self.build_folder)
        cmake_install_debug_release(cmake, self.build_subfolder)
        if self.settings.os == "Android":
            self.copy("*.java", dst="android", src=os.path.join(self.source_subfolder, "android-project", "app", "src", "main", "java", "org", "libsdl", "app"))
        elif self.settings.compiler == "msvc":
            self.copy("*.pdb", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.includedirs = [os.path.join("include", "SDL2")]
        self.cpp_info.debug.libs = ["SDL2d", "SDL2maind"]
        self.cpp_info.release.libs = ["SDL2", "SDL2main"]
        if self.settings.os == "Windows":
            self.cpp_info.libs.extend(["Imm32", "SetupAPI", "Version", "WinMM"])
        if self.settings.os == "Linux":
            system_libs = ["dl", "m", "pthread"]
            self.cpp_info.debug.libs.extend(system_libs)
            self.cpp_info.release.libs.extend(system_libs)
        elif self.settings.os == "Macos":
            self.cpp_info.libs.append("iconv")
            frameworks = [
                "AudioToolbox",
                "Carbon",
                "Cocoa",
                "CoreAudio",
                "CoreVideo",
                "ForceFeedback",
                "IOKit",
                "Metal"]
            for framework in frameworks:
                self.cpp_info.exelinkflags.append(f"-framework {framework}")
        elif self.settings.os == "Android":
            system_libs = ["android", "GLESv1_CM", "GLESv2", "log", "OpenSLES"]
            self.cpp_info.debug.libs.extend(system_libs)
            self.cpp_info.release.libs.extend(system_libs)
        elif self.settings.os == "iOS":
            self.cpp_info.libs.append("iconv")
            frameworks = [
                "AudioToolbox",
                "AVFoundation",
                "CoreAudio",
                "CoreBluetooth",
                "CoreGraphics",
                "CoreHaptics",
                "CoreMotion",
                "CoreVideo",
                "Foundation",
                "GameController",
                "IOKit",
                "Metal",
                "OpenGLES",
                "QuartzCore",
                "UIKit"]
            for framework in frameworks:
                self.cpp_info.exelinkflags.append(f"-framework {framework}")
        elif self.settings.os == "Android":
            self.cpp_info.libs.extend(["android"])
