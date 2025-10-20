

# Note: replace these with the values relevant to your setup
# REMOTE_HOST: an SSH hostname (or IP address) to ssh into. Note that the 
#             user must have passwordless SSH access (e.g., via SSH keys).
# REMOTE_WORKING_DIR: a working directory on the remote host where build
#                     and test files will be synced to.

set(REMOTE_HOST jetson)
set(REMOTE_WORKING_DIR "/home/julius/dev/remote-dev/tmp")

# Render `sync_runtime_deps.sh`
# Note: assuming that CONAN_RUNTIME_LIB_DIRS contains paths to libraries in the conan cache
#       and was set in conan_toolchain.cmake

execute_process(
  COMMAND conan config home
  OUTPUT_VARIABLE CONAN_HOME
  OUTPUT_STRIP_TRAILING_WHITESPACE
)

set(RUNTIME_LIB_DIRS "")
set(REMOTE_LD_LIBRARY_PATH "")
foreach(LIBDIR ${CONAN_RUNTIME_LIB_DIRS})
  string(REPLACE "/p/" "/./p/" LIBDIR "${LIBDIR}")
  string(APPEND RUNTIME_LIB_DIRS "    ${LIBDIR} \\\n")
  string(REPLACE "${CONAN_HOME}/" "${REMOTE_WORKING_DIR}/conan-deps/" LIBPATH_ENTRY "${LIBDIR}")
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
