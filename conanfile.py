from conans import ConanFile, CMake, tools
import os
import shutil

class Conan(ConanFile):
    name = "sdl2"
    version = "2.0.22"
    description = "A cross-platform development library designed to provide low level " \
                  "access to audio, keyboard, mouse, joystick, and graphics hardware " \
                  "via OpenGL and Direct3D."
    homepage = "https://www.libsdl.org"
    license = "Zlib https://www.libsdl.org/license.php"
    url = f"https://github.com/ssrobins/conan-{name}"
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    _cmake = None
    revision_mode = "scm"
    exports_sources = ["CMakeLists.txt"]
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

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.generator = "Ninja Multi-Config"

        if self.settings.os == "Android":
            self._cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = os.getenv("ANDROID_NDK_ROOT") + "/build/cmake/android.toolchain.cmake"

        if self.settings.os == "iOS" and self.settings.arch != "x86_64":
            self._cmake.definitions["CMAKE_OSX_ARCHITECTURES"] = "armv7;arm64"

        self._cmake.configure(build_dir=self.build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build(args=["--verbose"])
        cmake.install()

    def package(self):
        if self.settings.os == "Android":
            self.copy("*.java", dst="android", src=os.path.join(self.source_subfolder, "android-project", "app", "src", "main", "java", "org", "libsdl", "app"))
        elif self.settings.compiler == "msvc":
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
            system_libs = ["dl", "m", "pthread"]
            self.cpp_info.debug.libs.extend(system_libs)
            self.cpp_info.release.libs.extend(system_libs)
        elif self.settings.os == "Macos":
            self.cpp_info.libs.append("iconv")
            self.cpp_info.frameworks = [
                "AudioToolbox",
                "Carbon",
                "Cocoa",
                "CoreAudio",
                "CoreHaptics",
                "CoreVideo",
                "ForceFeedback",
                "GameController",
                "IOKit",
                "Metal"]
        elif self.settings.os == "Android":
            system_libs = ["android", "GLESv1_CM", "GLESv2", "log", "OpenSLES"]
            self.cpp_info.debug.libs.extend(system_libs)
            self.cpp_info.release.libs.extend(system_libs)
        elif self.settings.os == "iOS":
            self.cpp_info.libs.append("iconv")
            self.cpp_info.frameworks = [
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
        elif self.settings.os == "Android":
            self.cpp_info.libs.extend(["android"])
