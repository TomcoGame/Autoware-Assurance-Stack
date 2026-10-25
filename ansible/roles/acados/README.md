# Setup acados

Installs [acados](https://github.com/acados/acados), a fast and embedded solver for nonlinear optimal control, from source.

## What it does

1. Clones the acados repository (shallow) to `/opt/acados`
2. Initializes submodules (shallow)
3. Builds and installs acados in-tree with `QPOASES` and position-independent code enabled
4. Downloads the [tera renderer](https://github.com/acados/tera_renderer) binary to `/opt/acados/bin/t_renderer` (supports `x86_64` and `aarch64`)
5. Creates a Python virtual environment at `/opt/acados/.venv`
6. Installs `casadi`, `sympy`, and `acados_template` (editable) in the venv
7. Adds `CMAKE_PREFIX_PATH`, `ACADOS_SOURCE_DIR`, and `LD_LIBRARY_PATH` to the user's `.bashrc`

## Installation ⭐

Install ansible following the instructions in the [ansible installation guide](../../README.md#ansible-installation).

```bash
cd ~/autoware # The root directory of the cloned repository
ansible-galaxy collection install -f -r "ansible-galaxy-requirements.yaml"
```

This step should be repeated when the ansible directory is updated.

```bash
ansible-playbook autoware.dev_env.install_dev_env --tags acados --ask-become-pass
```

## Directory layout

After running, `/opt/acados` contains both the source tree and installed artifacts:

```text
/opt/acados/
├── .venv/            # Python virtual environment
├── bin/t_renderer    # tera renderer binary
├── build/            # cmake build directory
├── cmake/            # acadosConfig.cmake (used by find_package)
├── lib/              # built shared libraries
├── include/          # headers
├── interfaces/       # acados_template Python package (installed to .venv)
├── external/         # submodules (qpoases, etc.)
└── ...               # remaining source tree
```

## Usage in CMake

After provisioning, any CMake project can use acados with:

```cmake
find_package(acados REQUIRED)
target_link_libraries(your_target PRIVATE acados)
```

No additional path configuration is needed, `CMAKE_PREFIX_PATH` is set via `.bashrc`.

## Using the Python interface during `colcon build`

If your ROS 2 package generates acados C code at build time (e.g. via a Python script that uses `acados_template` and `casadi`), you need to source the venv so the code-generation script can find the installed packages.

The Ansible role already exports `ACADOS_SOURCE_DIR` and `LD_LIBRARY_PATH` in `.bashrc`, so those are available to `colcon build` as long as you've sourced your shell. The only extra step is pointing CMake at the venv Python so `casadi`, `sympy`, and `acados_template` are importable:

```cmake
find_program(ACADOS_PYTHON NAMES python3 PATHS $ENV{ACADOS_SOURCE_DIR}/.venv/bin NO_DEFAULT_PATH)

add_custom_command(
  OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/generated/acados_solver.c
  COMMAND ${ACADOS_PYTHON} ${CMAKE_CURRENT_SOURCE_DIR}/scripts/generate_solver.py
    --output-dir ${CMAKE_CURRENT_BINARY_DIR}/generated
  DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/scripts/generate_solver.py
  COMMENT "Generating acados solver C code"
)
```

The generated C code is then compiled as part of your normal CMake target, no Python dependency at runtime.

## Requirements

- CMake
- A C compiler (gcc/clang)
- `make`
- `git`
- `python3` with `venv` module (`python3-venv` on Ubuntu)

## Idempotency

The role is safe to run multiple times. The git clone resets any local modifications, and the build steps re-run on each invocation to ensure correctness when the version is changed. The `.bashrc` entries use `lineinfile` with regex matching to avoid duplication. The venv creation is skipped if it already exists (`creates` guard).

## Abbreviations, terms and symbols

| Term                      | Meaning                                                                                                              |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| aarch64                   | The 64-bit ARM processor architecture, used by ARM servers and NVIDIA Jetson boards                                  |
| acados                    | Open-source software that solves nonlinear optimal control problems fast enough to run on embedded computers         |
| `ACADOS_SOURCE_DIR`       | Environment variable telling tools where the acados source tree is (`/opt/acados`)                                   |
| `acados_template`         | acados' Python package that turns a control problem described in Python into C solver code                           |
| Ansible                   | An automation tool that sets up a machine by running steps written in YAML files                                     |
| ansible-galaxy            | Ansible's command for installing collections and roles that a project depends on                                     |
| ansible-playbook          | Ansible's command that runs a playbook on the machine                                                                |
| artifacts                 | Files produced by a build, such as libraries and headers                                                             |
| `.bashrc`                 | A script in your home directory that the bash shell runs each time it starts; used here to set environment variables |
| binary                    | A compiled program, ready to run                                                                                     |
| C                         | The C programming language; acados generates C code for its solvers                                                  |
| `casadi`                  | CasADi: a library for numerical optimisation with automatic differentiation, used to write the control problem       |
| clang                     | A C and C++ compiler from the LLVM project, an alternative to gcc                                                    |
| CMake                     | A cross-platform tool that generates build instructions for C and C++ projects                                       |
| `CMAKE_PREFIX_PATH`       | Environment variable listing the folders where CMake looks for installed packages                                    |
| code-generation           | Writing source code automatically with a program, here a Python script that writes the C solver                      |
| `colcon build`            | colcon is the build tool for ROS 2 workspaces; `colcon build` compiles every package in the workspace                |
| `creates` guard           | An Ansible option that skips a command when the file it would create already exists                                  |
| editable                  | Installed as a Python package that points at the source folder, so edits take effect without reinstalling            |
| `find_package`            | The CMake command that finds an installed library and its settings                                                   |
| gcc                       | GNU Compiler Collection: the standard C and C++ compiler on Linux                                                    |
| Git                       | The version control system used to track changes to source code                                                      |
| headers                   | C or C++ files that declare a library's functions so other code can call them                                        |
| idempotency               | Running something again gives the same result as running it once, with no extra changes                              |
| in-tree                   | Built and installed inside the source folder rather than in a separate location                                      |
| `LD_LIBRARY_PATH`         | Environment variable listing extra folders where Linux looks for shared libraries when a program starts              |
| `lineinfile`              | An Ansible module that makes sure one line is present in a file, without adding duplicates                           |
| `make`                    | A classic build tool that runs the compile commands described in a Makefile                                          |
| nonlinear optimal control | Choosing a system's inputs over time to minimise a cost, when the system's equations are nonlinear                   |
| position-independent code | Machine code that works at any memory address, which shared libraries need                                           |
| `PRIVATE`                 | In CMake, a dependency used only to build this target and not passed on to targets that use it                       |
| `python3-venv`            | The Ubuntu package that provides Python's `venv` module                                                              |
| `QPOASES`                 | qpOASES: an open-source solver for quadratic programming problems that acados can use internally                     |
| regex                     | Regular expression: a pattern for matching text                                                                      |
| role                      | A reusable unit of Ansible tasks that installs or configures one thing; each folder under `ansible/roles/` is a role |
| ROS 2                     | Robot Operating System 2: the second generation of ROS, which Autoware is built on                                   |
| runtime                   | When the built program runs, as opposed to when it is built                                                          |
| shallow                   | A Git clone that fetches only the latest history, to save time and space                                             |
| shared libraries          | Compiled code (`.so` files) that programs load when they start                                                       |
| solver                    | A program that computes the answer to a mathematical problem, here the best control inputs                           |
| source                    | To run a script in the current shell so the settings it makes stay in effect                                         |
| submodules                | Git repositories included inside another Git repository                                                              |
| `sympy`                   | SymPy: a Python library for symbolic mathematics                                                                     |
| target                    | In CMake, a library or program that the project builds                                                               |
| tera renderer             | A small program acados uses to fill in code templates written in the Tera template language                          |
| Ubuntu                    | The Linux distribution Autoware targets; versions are named year.month, such as 22.04 (April 2022)                   |
| venv                      | Python virtual environment: a folder with its own Python packages, kept apart from the system's                      |
| x86_64                    | The 64-bit Intel/AMD processor architecture used by most desktop and laptop PCs                                      |
| `/opt`                    | The Linux folder for add-on software that is not part of the operating system                                        |
| ⭐                        | Star: highlights the main section to follow                                                                          |
| `~`                       | Shorthand for your home directory, for example `/home/<you>`                                                         |
| `#`                       | In a shell or config block, starts a comment that is not run                                                         |
| `-f`                      | For `ansible-galaxy`: reinstall even if already installed (force)                                                    |
| `-r`                      | For `ansible-galaxy`: read the list of things to install from the named requirements file                            |
| `--tags`                  | For `ansible-playbook`: run only the roles and tasks carrying the given tag                                          |
| `--ask-become-pass`       | For `ansible-playbook`: asks for your sudo password once, so steps that need administrator rights can run            |
| `├──`, `└──`              | Tree drawing: shows the files and folders inside the folder above                                                    |
| `...`                     | More entries not listed                                                                                              |
| `$ENV{...}`, `${...}`     | CMake syntax: `$ENV{X}` reads environment variable X, `${X}` reads CMake variable X                                  |

Other project terms are defined in the [Glossary](../../../wiki/Glossary.md).
