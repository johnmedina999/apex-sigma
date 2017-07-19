import pip
import platform
import os

win_x86 = ["install/Shapely-1.5.17-cp36-cp36m-win32.whl",]
win_x64 = ["install/Shapely-1.5.17-cp36-cp36m-win_amd64.whl",]


def install(packages):
    for package in packages:
        pip.main(['install', package]) 


if __name__ == '__main__':

    if platform.architecture()[0] == "64bit":
        install(win_x64)
    elif platform.architecture()[0] == "32bit":
        install(win_x86)
    else:
        print("Unknown architecture \"" + platform.architecture() + "\"")
        exit(1)

    with open("install/requirements.txt") as f:
        packages = f.read().splitlines()

    install(packages)