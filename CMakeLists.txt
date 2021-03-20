cmake_minimum_required(VERSION 3.0)

project(skiacc)

set(SKIACC_SHARED OFF)
set(SKIACC_MODULES "")

if (SKIACC_SHARED)
    set(SKIACC_SKIA_OUT ${CMAKE_CURRENT_SOURCE_DIR}/skia/out/ReleaseShared)
    set(SKIACC_LIB_TYPE SHARED)
    set(SKIACC_SHARED_ARG "--shared")
else()
    set(SKIACC_SKIA_OUT ${CMAKE_CURRENT_SOURCE_DIR}/skia/out/Release)
    set(SKIACC_LIB_TYPE STATIC)
    set(SKIACC_SHARED_ARG "")
endif()

add_custom_target(skiacc_build ALL
    COMMAND python ${CMAKE_CURRENT_SOURCE_DIR}/build.py -q ${SKIACC_SHARED_ARG} -m ${SKIACC_MODULES}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

add_library(skiacc ${SKIACC_LIB_TYPE} IMPORTED)

if (WIN32)
    if (SKIACC_SHARED)
        set_property(TARGET skiacc PROPERTY IMPORTED_LOCATION ${SKIACC_SKIA_OUT}/skia.dll)
        set_property(TARGET skiacc PROPERTY IMPORTED_IMPLIB ${SKIACC_SKIA_OUT}/skia.lib)
    else()
        set_property(TARGET skiacc PROPERTY IMPORTED_LOCATION ${SKIACC_SKIA_OUT}/skia.lib)
    endif()
elseif(APPLE)
    if (SKIACC_SHARED)
        set_property(TARGET skiacc PROPERTY IMPORTED_LOCATION ${SKIACC_SKIA_OUT}/skia.dylib)
    else()
        set_property(TARGET skiacc PROPERTY IMPORTED_LOCATION ${SKIACC_SKIA_OUT}/skia.a)
    endif()
elseif(UNIX AND NOT APPLE)
    if (SKIACC_SHARED)
        set_property(TARGET skiacc PROPERTY IMPORTED_LOCATION ${SKIACC_SKIA_OUT}/skia.so)
    else()
        set_property(TARGET skiacc PROPERTY IMPORTED_LOCATION ${SKIACC_SKIA_OUT}/skia.a)
    endif()
else()
    message(FATAL_ERROR "Unsupported skiacc platform")
endif()

target_include_directories(skiacc INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/skia/include)
