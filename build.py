import argparse
import subprocess
import os
import sys
from collections import Counter

parser = argparse.ArgumentParser(description='Skia build utility')

parser.add_argument('-m', '--modules', nargs='*',
                    help='Additional Skia modules to build', required=False)

parser.add_argument('-c', '--commit', type=str,
                    help='Skia SHA commit to checkout')

parser.add_argument(
    '--shared', help='Build as a shared library instead of a static library', action='store_true')

parser.add_argument(
    '-q', '--quiet', help='Hide output from commands (e.g. git clone, etc)', action='store_true')

parser.add_argument('--llvm-win', type=str, help="LLVM directory for Windows")


args = parser.parse_args()

modules = []
commit = 'master'
llvm_win = 'C:\\Program Files\\LLVM'
is_shared = False

if args.modules:
    modules = args.modules

if args.commit:
    commit = args.commit

if args.llvm_win:
    llvm_win = args.llvm_win

if args.shared:
    is_shared = True


def call(call_args, cwd='.', shell=False, env=None):
    if args.quiet:
        subprocess.call(call_args, cwd=cwd, stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT, shell=shell, env=env)
    else:
        subprocess.call(call_args, cwd=cwd, shell=shell, env=env)


valid_modules = [
    'audioplayer',
    'canvaskit',
    'particles',
    'pathkit',
    'skottie',
    'skparagraph',
    'skplaintexteditor',
    'skresources',
    'sksg',
    'skshaper',
    'svg'
]

for module in modules:
    if module not in valid_modules:
        print(f'Error: \'{module}\' is not a valid Skia module')
        exit()

if os.path.exists('skiacc_cache.txt'):
    print('Cache file found')
    cache = open('skiacc_cache.txt', 'r').read().splitlines()

    if len(cache) > 1:
        same_modules = False

        if len(cache) < 3 and len(modules) == 0:
            same_modules = True
        elif len(cache) >= 3 and len(modules) == len(cache) - 2:
            same_modules = Counter(cache[2:]) == Counter(modules)

        if int(cache[0]) == int(args.shared) and cache[1] == commit and same_modules:
            print('Cached options are equal, no rebuild needed')
            exit()
        else:
            print('Cached options are different')
    else:
        print('Invalid cache file')
else:
    print('No cache file found')

if not os.path.exists('skia'):
    print('Cloning Skia')
    call(['git', 'clone', 'https://skia.googlesource.com/skia.git'])
else:
    print('Skia directory found, skipping clone')

print(f'Skia checkout to {commit}')

call(['git', 'checkout', commit], cwd='skia')
call(['git', 'pull'], cwd='skia')

if not os.path.exists('depot_tools'):
    print('Cloning depot-tools')
    call(
        ['git', 'clone', 'https://chromium.googlesource.com/chromium/tools/depot_tools.git'])
else:
    print('depot-tools directory found, skipping clone')

print('Syncing dependencies')

call(['py', '-2', 'tools/git-sync-deps'], cwd='skia')

call(['gclient', 'sync'], cwd='depot_tools', shell=True)

depot_tools_path = os.path.abspath(os.path.join(os.getcwd(), 'depot_tools'))
shared_opt = ''

if args.shared:
    shared_opt = 'is_component_build=true'

for module in modules:
    module = f'module/{module}'

out_dir = 'out/Release'

if args.shared:
    out_dir = 'out/ReleaseShared'


def build_ninja():
    call_args = ['ninja', '-C', out_dir, 'skia']
    call_args.extend(modules)

    call(call_args, cwd='skia', shell=True)

# Platform-specific commands from here on

# Adapted from Aseprite build commands


def build_win32():
    call(['call', 'C:/Program Files (x86)/Microsoft Visual Studio/2019/Community/Common7/Tools/VsDevCmd.bat', '-arch=x64'], shell=True)

    call(f'call ../depot_tools/gn gen {out_dir} --args="is_debug=false is_official_build=true {shared_opt} skia_use_system_expat=false skia_use_system_icu=false skia_use_system_libjpeg_turbo=false skia_use_system_libpng=false skia_use_system_libwebp=false skia_use_system_zlib=false skia_use_sfntly=false skia_use_freetype=true skia_use_harfbuzz=true skia_pdf_subset_harfbuzz=true skia_use_system_freetype2=false skia_use_system_harfbuzz=false target_cpu=\\"x64\\" clang_win=\\"{llvm_win}\\" win_vc=\\"C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Community\\VC\\""', cwd='skia', shell=True)

    build_ninja()


def build_macos():
    call(
        f'../depot_tools/gn gen {out_dir} --args="is_debug=false is_official_build=true {shared_opt} skia_use_system_expat=false skia_use_system_icu=false skia_use_system_libjpeg_turbo=false skia_use_system_libpng=false skia_use_system_libwebp=false skia_use_system_zlib=false skia_use_sfntly=false skia_use_freetype=true skia_use_harfbuzz=true skia_pdf_subset_harfbuzz=true skia_use_system_freetype2=false skia_use_system_harfbuzz=false target_cpu=\\"x64\\" extra_cflags=[\\"-stdlib=libc++\\", \\"-mmacosx-version-min=10.9\\"] extra_cflags_cc=[\\"-frtti\\"]"', cwd='skia', shell=True)

    build_ninja()


def build_linux():
    call(
        f'../depot_tools/gn gen {out_dir} --args="is_debug=false is_official_build=true {shared_opt} skia_use_system_expat=false skia_use_system_icu=false skia_use_system_libjpeg_turbo=false skia_use_system_libpng=false skia_use_system_libwebp=false skia_use_system_zlib=false', cwd='skia', shell=True)

    build_ninja()


if sys.platform == 'win32':
    print('Building for Win32')
    build_win32()
elif sys.platform == 'darwin':
    print('Building for MacOS')
    build_macos()
elif sys.platform == 'linux':
    print('Building for Linux')
    build_linux()
else:
    print(f'Unsupported platform \'{sys.platform}\'')
    exit()

cache = open('skiacc_cache.txt', 'w+')

cached = [str(int(args.shared)), commit]
cached.extend(modules)

cache.write('\n'.join(cached))

cache.close()
