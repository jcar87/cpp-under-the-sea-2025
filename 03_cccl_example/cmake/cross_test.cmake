
set(REMOTE_HOST jetson)
set(REMOTE_WORKING_DIR "/home/julius/dev/remote-dev/tmp")

# Render `sync_runtime_deps.sh`
# Note: assuming that CONAN_RUNTIME_LIB_DIRS contains paths to libraries in the conan cache
#       and was set in conan_toolchain.cmake

set(RUNTIME_LIB_DIRS "")
set(REMOTE_LD_LIBRARY_PATH "")
foreach(LIBDIR ${CONAN_RUNTIME_LIB_DIRS})
  string(REPLACE "/p/" "/./p/" LIBDIR "${LIBDIR}")
  string(APPEND RUNTIME_LIB_DIRS "    ${LIBDIR} \\\n")
  # message("LIBDIR: ${LIBDIR}")
  string(REPLACE "/home/luisc/cpp-under-the-sea-2025/conan_home/" "${REMOTE_WORKING_DIR}/conan-deps/" LIBPATH_ENTRY "${LIBDIR}")
  list(APPEND REMOTE_LD_LIBRARY_PATH ${LIBPATH_ENTRY})
endforeach()

string(REPLACE ";" ":" REMOTE_LD_LIBRARY_PATH "${REMOTE_LD_LIBRARY_PATH}")
string(STRIP "${RUNTIME_LIB_DIRS}" RUNTIME_LIB_DIRS)

set(SYNC_RUNTIME_DEPS_SCRIPT "${CMAKE_BINARY_DIR}/sync_runtime_deps.sh")

configure_file(${CMAKE_CURRENT_LIST_DIR}/sync_runtime_deps.sh.in ${SYNC_RUNTIME_DEPS_SCRIPT}
                USE_SOURCE_PERMISSIONS @ONLY)

# Render `CTestCustom.cmake`
configure_file(${CMAKE_CURRENT_LIST_DIR}/CTestCustom.cmake.in ${CMAKE_BINARY_DIR}/CTestCustom.cmake @ONLY)


# Render "remote_run.sh"
set(REMOTE_RUN_SCRIPT "${CMAKE_BINARY_DIR}/remote_run.sh")
configure_file(${CMAKE_CURRENT_LIST_DIR}/remote_run.sh.in ${REMOTE_RUN_SCRIPT} USE_SOURCE_PERMISSIONS @ONLY)
set(CMAKE_CROSSCOMPILING_EMULATOR ${REMOTE_RUN_SCRIPT})
