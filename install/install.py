import subprocess
import platform
import sys

win_x86 = ["install/Shapely-1.6.4.post2-cp37-cp37m-win32.whl",]
win_x64 = ["install/Shapely-1.6.4.post2-cp37-cp37m-win_amd64.whl",]
elf_x86 = ["",]
elf_x64 = ["Shapely",]


def install(packages):
    for package in packages:
        subprocess.check_call(['python', '-m', 'pip', 'install', package])


if __name__ == '__main__':

    if sys.version_info < (3, 7):
        print("Need python 3.7 or greater")
        exit(0)

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