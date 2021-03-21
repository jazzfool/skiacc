import argparse
import subprocess
import os
import sys
from collections import Counter

parser = argparse.ArgumentParser(description='Skia build utility')

parser.add_argument('-m', '--all-modules',
                    help='Build additional Skia modules', action='store_true')

parser.add_argument('-c', '--commit', type=str,
                    help='Skia SHA commit to checkout')

parser.add_argument(
    '--shared', help='Build as a shared library instead of a static library', action='store_true')

parser.add_argument(
    '-q', '--quiet', help='Hide output from commands (e.g. git clone, etc)', action='store_true')

parser.add_argument('--llvm-win', type=str, help='LLVM directory for Windows')

parser.add_argument(
    '-f', '--force', help='Force rebuild, regardless of cache', action='store_true')

parser.add_argument('--args', type=str,
                    help='Additional arguments to pass to gn')

parser.add_argument(
    '--debug', help='Build in debug configuration', action='store_true')

args = parser.parse_args()

if args.all_modules and args.shared:
    print('Cannot build all modules as a shared library. This configuration is unsupported by Skia. Either remove --shared or --all-modules/-m')
    exit()

all_modules = False
commit = 'master'
llvm_win = 'C:\\Program Files\\LLVM'
is_shared = False
user_args = ''
debug_arg = 'is_debug=false'
is_debug = False

if args.all_modules:
    all_modules = True

if args.commit:
    commit = args.commit

if args.llvm_win:
    llvm_win = args.llvm_win

if args.shared:
    is_shared = True

if args.args:
    user_args = args.args

if args.debug:
    debug_arg = 'is_debug=true'
    is_debug = True


def call(call_args, cwd='.', shell=False, env=None):
    if args.quiet:
        subprocess.call(call_args, cwd=cwd, stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT, shell=shell, env=env)
    else:
        subprocess.call(call_args, cwd=cwd, shell=shell, env=env)


if not args.force:
    if os.path.exists('skiacc_cache.txt'):
        print('Cache file found')
        cache = open('skiacc_cache.txt', 'r').read().splitlines()

        if len(cache) > 1:
            if int(cache[0]) == int(args.shared) and cache[1] == commit and int(cache[2]) >= int(all_modules) and int(cache[3]) == int(is_debug):
                print('Cached options are equal, no rebuild needed')
                exit()
            else:
                print('Cached options are different')
        else:
            print('Invalid cache file')
    else:
        print('No cache file found')
else:
    print('Forcing rebuild')

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


out_dir = 'out/Release'

if args.shared:
    out_dir = 'out/ReleaseShared'

module_args = []

if args.all_modules:
    module_args = ['skia_enable_particles=true', 'skia_enable_skottie=true',
                   'skia_enable_skparagraph=true', 'skia_enable_skshaper=true', 'skia_enable_svg=true']

module_args = ' '.join(module_args)


def build_ninja():
    call_args = ['ninja', '-C', out_dir, 'skia']
    if all_modules:
        call_args.extend(
            ['particles', 'skottie', 'skparagraph', 'skshaper', 'svg'])

    call(call_args, cwd='skia', shell=True)

# Platform-specific commands from here on


def build_win32():
    call(['call', 'C:/Program Files (x86)/Microsoft Visual Studio/2019/Community/Common7/Tools/VsDevCmd.bat', '-arch=x64'], shell=True)

    call(
        f'call ../depot_tools/gn gen {out_dir} --args="{debug_arg} is_official_build=true {module_args} {shared_opt} {user_args} skia_enable_gpu=true skia_use_gl=true skia_use_system_expat=false skia_use_system_icu=false skia_use_system_libjpeg_turbo=false skia_use_system_libpng=false skia_use_system_libwebp=false skia_use_system_zlib=false skia_use_sfntly=false skia_use_freetype=true skia_use_harfbuzz=true skia_pdf_subset_harfbuzz=true skia_use_system_freetype2=false skia_use_system_harfbuzz=false target_cpu=\\"x64\\" clang_win=\\"{llvm_win}\\" win_vc=\\"C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Community\\VC\\" extra_cflags=[\\"-MD\\"]"', cwd='skia', shell=True)

    build_ninja()


def build_macos():
    call(
        f'../depot_tools/gn gen {out_dir} --args="{debug_arg} is_official_build=true {module_args} {shared_opt} {user_args} skia_enable_gpu=true skia_use_gl=true skia_use_system_expat=false skia_use_system_icu=false skia_use_system_libjpeg_turbo=false skia_use_system_libpng=false skia_use_system_libwebp=false skia_use_system_zlib=false skia_use_sfntly=false skia_use_freetype=true skia_use_harfbuzz=true skia_pdf_subset_harfbuzz=true skia_use_system_freetype2=false skia_use_system_harfbuzz=false target_cpu=\\"x64\\" extra_cflags=[\\"-stdlib=libc++\\", \\"-mmacosx-version-min=10.9\\"] extra_cflags_cc=[\\"-frtti\\"]"', cwd='skia', shell=True)

    build_ninja()


def build_linux():
    call(
        f'../depot_tools/gn gen {out_dir} --args="{debug_arg} is_official_build=true {module_args} {shared_opt} {user_args} skia_enable_gpu=true skia_use_gl=true skia_use_system_expat=false skia_use_system_icu=false skia_use_system_libjpeg_turbo=false skia_use_system_libpng=false skia_use_system_libwebp=false skia_use_system_zlib=false', cwd='skia', shell=True)

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

cached = [str(int(args.shared)), commit, str(
    int(all_modules)), str(int(is_debug))]

cache.write('\n'.join(cached))

cache.close()
