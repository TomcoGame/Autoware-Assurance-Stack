# ros2_dev_tools

This role installs ROS 2 development tools following [this page](https://docs.ros.org/en/humble/Installation/Alternatives/Ubuntu-Development-Setup.html).

## Inputs

None.

## Manual Installation

```bash
# Taken from https://docs.ros.org/en/humble/Installation/Alternatives/Ubuntu-Development-Setup.html
sudo apt update && sudo apt install -y \
  python3-colcon-mixin \
  python3-flake8-docstrings \
  python3-pip \
  python3-pytest-cov \
  python3-flake8-blind-except \
  python3-flake8-builtins \
  python3-flake8-class-newline \
  python3-flake8-comprehensions \
  python3-flake8-deprecated \
  python3-flake8-import-order \
  python3-flake8-quotes \
  python3-pytest-repeat \
  python3-pytest-rerunfailures \
  build-essential \
  cmake \
  git \
  python3-setuptools \
  python3-bloom \
  python3-colcon-common-extensions \
  python3-colcon-mixin \
  python3-rosdep \
  python3-vcs2l \
  wget

# Initialize rosdep
sudo rosdep init
rosdep update
```

## Abbreviations, terms and symbols

| Term              | Meaning                                                                                                                  |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------ |
| apt               | Advanced Package Tool: Ubuntu's package manager, used to install, update and remove system software                      |
| bloom             | A tool for releasing ROS packages as Debian packages                                                                     |
| `build-essential` | An Ubuntu package with the C and C++ compilers, `make` and other basic build tools                                       |
| CMake             | A cross-platform tool that generates build instructions for C and C++ projects                                           |
| colcon            | The build tool for ROS 2 workspaces; `colcon-common-extensions` and `colcon-mixin` add common features and build presets |
| docstrings        | Documentation text written at the start of a Python function or class                                                    |
| flake8            | A Python code style checker; each `flake8-*` package adds extra checks                                                   |
| Git               | The version control system used to track changes to source code                                                          |
| Inputs            | The role variables you can set to change what the role does                                                              |
| pip               | Python's package installer                                                                                               |
| pytest            | A Python testing framework; `-cov` measures test coverage, `-repeat` and `-rerunfailures` re-run tests                   |
| role              | A reusable unit of Ansible tasks that installs or configures one thing; each folder under `ansible/roles/` is a role     |
| ROS 2             | Robot Operating System 2: the second generation of ROS, which Autoware is built on                                       |
| rosdep            | A tool that installs the system packages ROS packages depend on                                                          |
| setuptools        | The Python library used to build and install Python packages                                                             |
| sudo              | A command that runs another command with administrator (root) rights, after asking for your password                     |
| vcs2l             | A tool that downloads many source repositories at once from a `.repos` list                                              |
| wget              | A command-line tool that downloads files from a web address                                                              |
| `#`               | In a shell or config block, starts a comment that is not run                                                             |
| `&&`              | Runs the next command only if the previous one succeeded                                                                 |
| `-y`              | Answers yes to every question so the command runs without stopping to ask                                                |
| `\`               | At the end of a line, continues the command on the next line                                                             |

Other project terms are defined in the [Glossary](../../../wiki/Glossary.md).
