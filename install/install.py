import pip
import platform


win_x86 = ["Shapely-1.5.17-cp36-cp36m-win32.whl",]
win_x64 = ["Shapely-1.5.17-cp36-cp36m-win_amd64.whl",]


def install(packages):
    for package in packages:
        pip.main(['install', package]) 


if __name__ == '__main__':

    if platform.architecture() == '64bit':
        install(win_x64)
    else:
        install(win_x86)

    with open('../requirements.txt') as f:
        packages = f.read().splitlines()

    install(packages)