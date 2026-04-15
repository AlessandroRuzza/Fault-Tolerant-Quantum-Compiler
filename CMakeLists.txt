cmake_minimum_required(VERSION 3.15)
project(FaultTolerantQuantumCompiler CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include_directories(include)


file(GLOB_RECURSE ALL_SRC_FILES CONFIGURE_DEPENDS src/*.cpp)

add_executable(FaultTolerantQuantumCompiler ${ALL_SRC_FILES})
add_definitions(-DPROJECT_ROOT="${CMAKE_SOURCE_DIR}")

# ------JSON and Main-------------

set(JSON_BuildTests OFF CACHE INTERNAL "")
set(JSON_MultipleHeaders OFF CACHE INTERNAL "")

# Aggiungi il submodule nlohmann/json
add_subdirectory(external/nlohmann_json)

# Include directories
target_include_directories(FaultTolerantQuantumCompiler PRIVATE include)

# Crea l'eseguibile con tutti i file sorgente necessari


# Linka nlohmann/json
target_link_libraries(FaultTolerantQuantumCompiler
  PRIVATE nlohmann_json::nlohmann_json
)


# Target to run the main executable (not built/executed by default)
add_custom_target(run-main
    DEPENDS FaultTolerantQuantumCompiler
    COMMAND $<TARGET_FILE:FaultTolerantQuantumCompiler>
    COMMENT "Running FaultTolerantQuantumCompiler after build"
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
)

# Target to run the executable in bench mode:
# make run-bench BENCH_PATH=<path_or_name> [RERUN_TIMEOUTS=1]
add_custom_target(run-bench
    DEPENDS FaultTolerantQuantumCompiler
    COMMAND sh ${CMAKE_SOURCE_DIR}/scripts/run-bench.sh $<TARGET_FILE:FaultTolerantQuantumCompiler> "$$BENCH_PATH" "$$RERUN_TIMEOUTS"
    COMMENT "Running FaultTolerantQuantumCompiler with --bench_path"
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
)

# ------Eigen-------------

# Suppress deprecated enum-enum conversion warning
target_compile_options(FaultTolerantQuantumCompiler PRIVATE -Wno-deprecated-enum-enum-conversion)

find_package(Eigen3 3.3 QUIET)
if(Eigen3_FOUND)
    target_link_libraries(FaultTolerantQuantumCompiler PRIVATE Eigen3::Eigen)
    message(STATUS "Found Eigen3: ${EIGEN3_INCLUDE_DIR}")
else()
    # Prova path specifico del cluster
    if(EXISTS "/u/sw/toolchains/gcc-glibc/11.2.0/pkgs/eigen/3.3.9/share/eigen3/cmake/")
        list(APPEND CMAKE_PREFIX_PATH "/u/sw/toolchains/gcc-glibc/11.2.0/pkgs/eigen/3.3.9/share/eigen3/cmake/")
        find_package(Eigen3 3.3 REQUIRED)
        target_link_libraries(FaultTolerantQuantumCompiler PRIVATE Eigen3::Eigen)
        message(STATUS "Found Eigen3 manually: ${EIGEN3_INCLUDE_DIR}")
    else()
        message(FATAL_ERROR "Eigen3 not found. Please install Eigen3, set mkEigenInc environment variable, or set CMAKE_PREFIX_PATH.")
    endif()
endif()

# Add graph_viewer target and a run/open target to build, run --test, copy the html to Windows (WSL)
# and open it (or fall back to xdg-open on Linux).
add_executable(graph_viewer
    src/igraph.cpp
    src/graph.cpp
    visualization/graph_viewer.cpp
)

target_include_directories(graph_viewer PRIVATE
    ${PROJECT_SOURCE_DIR}/include
)

# Link nlohmann/json (added earlier via add_subdirectory)
target_link_libraries(graph_viewer PRIVATE
    nlohmann_json::nlohmann_json
)

# If Eigen is available, use it; otherwise add system include
if (TARGET Eigen3::Eigen)
    target_link_libraries(graph_viewer PRIVATE Eigen3::Eigen)
else()
    target_include_directories(graph_viewer PRIVATE /usr/include/eigen3)
endif()

# Target that runs the binary (--test)
add_custom_target(run-graph-viewer
    DEPENDS graph_viewer
    COMMAND $<TARGET_FILE:graph_viewer> --test
    COMMENT "Running graph_viewer --test (generates /tmp/graph_view.html)"
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
)

# Target to export PROJECT and generate gaussian animation at 2 fps.
add_custom_target(make-video
    COMMAND ${CMAKE_COMMAND} -E env PROJECT=${CMAKE_SOURCE_DIR} sh ${CMAKE_SOURCE_DIR}/scripts/make-video.sh
    COMMENT "Exporting gaussian frames MP4+GIF (2 fps)"
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
)
