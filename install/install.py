import pip
import platform
import os

win_x86 = ["install/Shapely-1.5.17-cp36-cp36m-win32.whl",]
win_x64 = ["install/Shapely-1.5.17-cp36-cp36m-win_amd64.whl",]
elf_x86 = ["",]
elf_x64 = ["https://pypi.python.org/packages/d0/a5/7a6410801991a8a67a6c319d41a5ebaee2d18e473a952f0fca2e5e4ee9ed/Shapely-1.6b4-cp36-cp36m-manylinux1_x86_64.whl#md5=687106f4483565a6ecf755af2b686172",]


def install(packages):
    for package in packages:
        pip.main(['install', package]) 


if __name__ == '__main__':

    if platform.architecture()[1] == "WindowsPE":
        if platform.architecture()[0] == "64bit":
            print("Installing for win_x64...")
            install(win_x64)
        elif platform.architecture()[0] == "32bit":
            print("Installing for win_x86...")
            install(win_x86)
        else:
            print("Unknown architecture \"" + platform.architecture() + "\"")
            exit(1)
    elif platform.architecture()[1] == "ELF":
        if platform.architecture()[0] == "64bit":
            print("Installing for elf_x64...")
            install(elf_x64)
        elif platform.architecture()[0] == "32bit":
            print("elf_x86 is unsupported")
            exit(0)
        else:
            print("Unknown architecture \"" + platform.architecture() + "\"")
            exit(1)
    else:
        print("Unknown platform \"" + platform.architecture() + "\"")
        exit(1)

    with open("install/requirements.txt") as f:
        packages = f.read().splitlines()

    install(packages)