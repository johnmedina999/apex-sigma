import pip
import platform
import os

win_x86 = ["install/Shapely-1.5.17-cp36-cp36m-win32.whl",]
win_x64 = ["install/Shapely-1.5.17-cp36-cp36m-win_amd64.whl",]


def install(packages):
    for package in packages:
        pip.main(['install', package]) 


if __name__ == '__main__':

    print(platform.architecture())
    if platform.architecture() == '64bit':
        install(win_x64)
    else:
        install(win_x86)

    with open("install/requirements.txt") as f:
        packages = f.read().splitlines()

    install(packages)