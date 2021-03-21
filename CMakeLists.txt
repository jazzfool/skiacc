cmake_minimum_required(VERSION 3.0)

project(skiacc)

execute_process(
    COMMAND python ${CMAKE_CURRENT_SOURCE_DIR}/clone.py
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

if (SKIACC_SHARED)
    set(SKIACC_SKIA_OUT ${CMAKE_CURRENT_SOURCE_DIR}/skia/out/ReleaseShared)
    set(SKIACC_LIB_TYPE SHARED)
    set(SKIACC_SHARED_ARG "--shared")
else()
    set(SKIACC_SKIA_OUT ${CMAKE_CURRENT_SOURCE_DIR}/skia/out/Release)
    set(SKIACC_LIB_TYPE STATIC)
    set(SKIACC_SHARED_ARG "")
endif()

if (SKIACC_COPY_INCLUDE)
    execute_process(
        COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_CURRENT_SOURCE_DIR}/skia/include ${CMAKE_CURRENT_BINARY_DIR}/include/skia
    )

    file(GLOB SKIACC_MODULE_PARTICLES_HEADERS ${CMAKE_CURRENT_SOURCE_DIR}/skia/modules/particles/include/*.h)
    foreach(HEADER_FILE IN LISTS SKIACC_MODULE_PARTICLES_HEADERS)
        execute_process(
            COMMAND ${CMAKE_COMMAND} -E copy ${HEADER_FILE} ${CMAKE_CURRENT_BINARY_DIR}/include/skia/modules/particles/.
        )
    endforeach()

    file(GLOB SKIACC_MODULE_SKOTTIE_HEADERS ${CMAKE_CURRENT_SOURCE_DIR}/skia/modules/skottie/include/*.h)
    foreach(HEADER_FILE IN LISTS SKIACC_MODULE_SKOTTIE_HEADERS)
        execute_process(
            COMMAND ${CMAKE_COMMAND} -E copy ${HEADER_FILE} ${CMAKE_CURRENT_BINARY_DIR}/include/skia/modules/skottie/.
        )
    endforeach()

    file(GLOB SKIACC_MODULE_SKPARAGRAPH_HEADERS ${CMAKE_CURRENT_SOURCE_DIR}/skia/modules/skparagraph/include/*.h)
    foreach(HEADER_FILE IN LISTS SKIACC_MODULE_SKPARAGRAPH_HEADERS)
        execute_process(
            COMMAND ${CMAKE_COMMAND} -E copy ${HEADER_FILE} ${CMAKE_CURRENT_BINARY_DIR}/include/skia/modules/skparagraph/.
        )
    endforeach()

    file(GLOB SKIACC_MODULE_SKSHAPER_HEADERS ${CMAKE_CURRENT_SOURCE_DIR}/skia/modules/skshaper/include/*.h)
    foreach(HEADER_FILE IN LISTS SKIACC_MODULE_SKSHAPER_HEADERS)
        execute_process(
            COMMAND ${CMAKE_COMMAND} -E copy ${HEADER_FILE} ${CMAKE_CURRENT_BINARY_DIR}/include/skia/modules/skshaper/.
        )
    endforeach()

    file(GLOB SKIACC_MODULE_SVG_HEADERS ${CMAKE_CURRENT_SOURCE_DIR}/skia/modules/svg/include/*.h)
    foreach(HEADER_FILE IN LISTS SKIACC_MODULE_SVG_HEADERS)
        execute_process(
            COMMAND ${CMAKE_COMMAND} -E copy ${HEADER_FILE} ${CMAKE_CURRENT_BINARY_DIR}/include/skia/modules/svg/.
        )
    endforeach()
endif()

if (SKIACC_ALL_MODULES)
    set(SKIACC_MODULES_ARG "-m")
else()
    set(SKIACC_MODULES_ARG "")
endif()

add_custom_target(skiacc_build ALL
    COMMAND python ${CMAKE_CURRENT_SOURCE_DIR}/build.py -q ${SKIACC_SHARED_ARG} -c ${SKIACC_COMMIT} ${SKIACC_MODULES_ARG}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

add_library(skiacc ${SKIACC_LIB_TYPE} IMPORTED GLOBAL)

if (WIN32)
    if (SKIACC_SHARED)
        set_property(TARGET skiacc PROPERTY IMPORTED_LOCATION ${SKIACC_SKIA_OUT}/skia.dll)
        set_property(TARGET skiacc PROPERTY IMPORTED_IMPLIB ${SKIACC_SKIA_OUT}/skia.dll.lib)
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

target_include_directories(skiacc INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/skia ${CMAKE_CURRENT_BINARY_DIR}/include)

if (SKIACC_ALL_MODULES)
    if (WIN32)
        target_link_libraries(skiacc INTERFACE
            ${SKIACC_SKIA_OUT}/particles.lib
            ${SKIACC_SKIA_OUT}/skottie.lib
            ${SKIACC_SKIA_OUT}/skparagraph.lib
            ${SKIACC_SKIA_OUT}/skshaper.lib
            ${SKIACC_SKIA_OUT}/svg.lib
        )
    elseif(UNIX)
        target_link_libraries(skiacc INTERFACE
            ${SKIACC_SKIA_OUT}/particles.a
            ${SKIACC_SKIA_OUT}/skottie.a
            ${SKIACC_SKIA_OUT}/skparagraph.a
            ${SKIACC_SKIA_OUT}/skshaper.a
            ${SKIACC_SKIA_OUT}/svg.a
        )
    endif()
endif()
