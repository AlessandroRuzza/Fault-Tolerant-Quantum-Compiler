cmake_minimum_required(VERSION 3.15)
project(FaultTolerantQuantumCompiler CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include_directories(include)


file(GLOB ALL_SRC_FILES src/*.cpp)

add_executable(FaultTolerantQuantumCompiler ${ALL_SRC_FILES})

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


# ------Eigen-------------

# Suppress deprecated enum-enum conversion warning
target_compile_options(FaultTolerantQuantumCompiler PRIVATE -Wno-deprecated-enum-enum-conversion)

if(DEFINED ENV{mkEigenInc} OR DEFINED mkEigenInc)
    # Usa la variabile mkEigenInc (da env o CMake option)
    if(DEFINED ENV{mkEigenInc})
        set(EIGEN_INCLUDE_DIR $ENV{mkEigenInc})
    else()
        set(EIGEN_INCLUDE_DIR ${mkEigenInc})
    endif()
    
    message(STATUS "Using Eigen from mkEigenInc: ${EIGEN_INCLUDE_DIR}")
    target_include_directories(FaultTolerantQuantumCompiler PRIVATE ${EIGEN_INCLUDE_DIR})
    
else()
    # Fallback a find_package
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
        else()
            message(FATAL_ERROR "Eigen3 not found. Please install Eigen3, set mkEigenInc environment variable, or set CMAKE_PREFIX_PATH.")
        endif()
    endif()
endif()

# Add graph_viewer target and a run/open target to build, run --test, copy the html to Windows (WSL)
# and open it (or fall back to xdg-open on Linux).
add_executable(graph_viewer
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

