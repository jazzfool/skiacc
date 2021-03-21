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

Available `build.py` options:
- `--all-modules`, `-m`: Build the additional Skia modules (listed below).
    - `particles`
    - `skottie`
    - `skparagraph`
    - `skshaper`
    - `svg`
- `--commit`, `-c`: Specific commit/branch of Skia to checkout and build.
- `--shared`: Build Skia as a shared libary (i.e. `dll/dylib/so`) instead of a static library.
- `--quiet`, `-q`: Do not show output of commands being executes.
- `--llvm-win`: *Windows only*. LLVM directory (defaults to `C:\Program Files\LLVM`).
- `--force`, `-f`: Force Skia rebuild, ignoring the cached configuration.

Available CMake options:
- `SKIACC_SHARED`: Maps to `--shared`.
- `SKIACC_MODULES`: Maps to `--modules`.
- `SKIACC_COMMIT`: Maps to `--commit`.
- `SKIACC_COPY_INCLUDE`: Copies Skia include files to a renamed directory in the build tree. This way, Skia can be included by `<skia/core/...>` and modules by `<skia/modules/svg/...>`, instead of `<include/core/...>` and `<modules/svg/include/...>`.

**NOTE:** `shared` + `all-modules` is not a supported combination. Skia's build system does not support building modules as dynamic libraries.

### Example

As an example, to build with additional modules at commit `7cee3ef` as a static library:

**Using `build.py`**

```shell
$ python build.py -m -c 7cee3ef
```

**Using CMake**

```cmake
project(MyProject CXX)

add_executable(MyProject main.cpp) # Alternatively, add_library

set(SKIACC_ALL_MODULES ON)
set(SKIACC_SHARED OFF)
set(SKIACC_COMMIT "7cee3ef")
set(SKIACC_COPY_INCLUDE ON)

add_subdirectory(skiacc) # Invokes build.py
target_link_libraries(MyProject PRIVATE skiacc)
```
