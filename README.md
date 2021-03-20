# skiacc: Build scripts for Skia

- `build.py`: Clone Skia and depot-tools, then build with specified modules.
- `CMakeLists.txt`: Invoke `build.py` and generate target.

Always builds with Clang as that is what Skia primarily targets. According to Skia, other compilers result in slower performance.

Currently supports Windows, MacOS, and Linux, but only tested on Windows.

A config cache is kept so that consecutive builds of the same configuration do not waste time (especially helpful for the `CMakeLists.txt`).

# Usage

Either:
1. Invoke `build.py` on its own to build standalone binaries.
2. Add `CMakeLists.txt` as a subdirectory to build binaries and link into your own CMake project.

For example, to build with `svg` and `skshaper` modules at commit `7cee3ef`:

### `build.py`

Available options:
- `--modules`, `-m`: Skia modules to build.
    - `audioplayer`
    - `canvaskit`
    - `particles`
    - `pathkit`
    - `skottie`
    - `skparagraph`
    - `skplaintexteditor`
    - `skresources`
    - `sksg`
    - `skshaper`
    - `svg`
- `--commit`, `-c`: Specific commit/branch of Skia to checkout and build.
- `--shared`: Build Skia as a shared libary (i.e. `dll/dylib/so`) instead of a static library.
- `--quiet`, `-q`: Do not show output of commands being executes.
- `--llvm-win`: *Windows only*. LLVM directory (defaults to `C:\Program Files\LLVM`).

```shell
$ build.py --modules svg skshaper --commit 7cee3ef
```

### CMake

```cmake
project(MyProject CXX)

add_executable(MyProject main.cpp) # Alternatively, add_library

set(SKIACC_MODULES svg skshaper)
set(SKIACC_COMMIT "7cee3ef")

add_subdirectory(skiacc) # Invokes build.py
target_link_libraries(MyProject PRIVATE skiacc)
```
