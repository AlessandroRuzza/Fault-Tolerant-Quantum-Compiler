cmake_minimum_required(VERSION 3.15)
if(POLICY CMP0167)
    cmake_policy(SET CMP0167 OLD)
endif()

project(FaultTolerantQuantumCompiler CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include_directories(include)


file(GLOB_RECURSE ALL_SRC_FILES CONFIGURE_DEPENDS src/*.cpp)

# ------Boost (header-only Graph library)-------------
# The cluster module system exposes Boost via $mkBoostPrefix rather than BOOST_ROOT,
# so seed BOOST_ROOT from it before calling find_package.
if(DEFINED ENV{mkBoostPrefix})
    set(Boost_ROOT "$ENV{mkBoostPrefix}" CACHE PATH "Boost root from mkBoostPrefix")
endif()

set(FTOQC_HAS_BOOST_ROUTER OFF)
find_package(Boost QUIET)
if(Boost_FOUND)
    set(FTOQC_HAS_BOOST_ROUTER ON)
    message(STATUS "Found Boost: ${Boost_INCLUDE_DIRS}")
elseif(DEFINED ENV{mkBoostInc} AND EXISTS "$ENV{mkBoostInc}/boost/graph/adjacency_list.hpp")
    # Fallback: use the header path directly when find_package still fails.
    set(FTOQC_HAS_BOOST_ROUTER ON)
    set(Boost_INCLUDE_DIRS "$ENV{mkBoostInc}")
    message(STATUS "Using Boost headers from mkBoostInc: $ENV{mkBoostInc}")
else()
    list(REMOVE_ITEM ALL_SRC_FILES "${CMAKE_SOURCE_DIR}/src/routing/boost_router.cpp")
    message(STATUS "Boost not found: Boost_QubitRouter (RRR router) is disabled. Non-boost routing strategies will still compile.")
endif()

add_executable(FaultTolerantQuantumCompiler ${ALL_SRC_FILES})
add_definitions(-DPROJECT_ROOT="${CMAKE_SOURCE_DIR}")

find_package(OpenMP QUIET)

if(FTOQC_HAS_BOOST_ROUTER)
    target_include_directories(FaultTolerantQuantumCompiler SYSTEM PRIVATE ${Boost_INCLUDE_DIRS})
    # Silence "#pragma message: This header is deprecated" notes from Boost 1.76
    # internals (boost/detail/iterator.hpp etc.). BOOST_ALLOW_DEPRECATED_HEADERS
    # makes BOOST_HEADER_DEPRECATED(...) expand to nothing instead of the pragma.
    target_compile_definitions(FaultTolerantQuantumCompiler PRIVATE
        FTOQC_HAS_BOOST_ROUTER=1
        BOOST_ALLOW_DEPRECATED_HEADERS
    )
else()
    target_compile_definitions(FaultTolerantQuantumCompiler PRIVATE FTOQC_HAS_BOOST_ROUTER=0)
endif()

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

if (OpenMP_CXX_FOUND)
    target_link_libraries(FaultTolerantQuantumCompiler PRIVATE OpenMP::OpenMP_CXX)
    message(STATUS "OpenMP enabled for benchmark parallelism")
else()
    message(WARNING "OpenMP not found: benchmark mode will run sequentially")
endif()

# -------- TARGETS --------------

# Target to run the main executable (not built/executed by default)
add_custom_target(run-main
    DEPENDS FaultTolerantQuantumCompiler
    COMMAND $<TARGET_FILE:FaultTolerantQuantumCompiler>
    COMMENT "Running FaultTolerantQuantumCompiler after build"
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
)

add_custom_target(clearexpanded
    COMMAND sh -c "rm -f ${CMAKE_SOURCE_DIR}/config/executed/*_expanded.json ${CMAKE_SOURCE_DIR}/config/executed/*_expanded.status.jsonl"
    COMMENT "Removing config/executed/*_expanded.json and *.status.jsonl files"
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
)

# Target to run the executable in bench mode:
# make run-bench BENCH_PATH=<path_or_name> [RERUN_TIMEOUTS=1] [BENCH_JOBS=<n>] [BENCH_PROCESS_COUNT=<n>] [PROCESSOR=<n>]
add_custom_target(run-bench
    DEPENDS FaultTolerantQuantumCompiler
    COMMAND sh ${CMAKE_SOURCE_DIR}/scripts/benchmark_execution/run-bench.sh $<TARGET_FILE:FaultTolerantQuantumCompiler>
    COMMENT "Running FaultTolerantQuantumCompiler with --bench_path"
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
)

# make run-wisq QASM=QASM="<file1> [file2 ...]" [OUTPUT=<csv>] [MR_TIMEOUT=<secs>]
add_custom_target(run-wisq
    COMMAND sh ${CMAKE_SOURCE_DIR}/scripts/wisq_compare/run-wisq.sh
    COMMENT "Running wisq (usage: make run-wisq QASM=\"<name> [name2 ...]\")"
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
)

# make run-wisq-all [OUTPUT=<csv>] [MR_TIMEOUT=<secs>]
add_custom_target(run-wisq-all
    COMMAND sh ${CMAKE_SOURCE_DIR}/scripts/wisq_compare/run-wisq-all.sh
    COMMENT "Running wisq on all QASMs in universal_set_qasms/"
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
)


# Suppress deprecated enum-enum conversion warning
target_compile_options(FaultTolerantQuantumCompiler PRIVATE -Wno-deprecated-enum-enum-conversion)

# Optimization: default build carries no flags, which leaves the binary
# unoptimized (~3-5x slower). -O2 without -DNDEBUG keeps asserts enabled.
target_compile_options(FaultTolerantQuantumCompiler PRIVATE -O2)

# Add graph_viewer target and a run/open target to build, run --test, copy the html to Windows (WSL)
# and open it (or fall back to xdg-open on Linux).
add_executable(graph_viewer
    src/igraph.cpp
    src/graph.cpp
    src/defines.cpp
    visualization/graph_viewer.cpp
)

target_include_directories(graph_viewer PRIVATE
    ${PROJECT_SOURCE_DIR}/include
)

# Link nlohmann/json (added earlier via add_subdirectory)
target_link_libraries(graph_viewer PRIVATE
    nlohmann_json::nlohmann_json
)

# Target that runs the binary (--test)
add_custom_target(run-graph-viewer
    DEPENDS graph_viewer
    COMMAND $<TARGET_FILE:graph_viewer> --test
    COMMENT "Running graph_viewer --test (generates /tmp/graph_view.html)"
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
)

# Target to export PROJECT and generate gaussian animation at 2 fps.
add_custom_target(make-video
    COMMAND ${CMAKE_COMMAND} -E env PROJECT=${CMAKE_SOURCE_DIR} sh ${CMAKE_SOURCE_DIR}/scripts/plots/make-video.sh
    COMMENT "Exporting gaussian frames MP4+GIF (2 fps)"
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
)
