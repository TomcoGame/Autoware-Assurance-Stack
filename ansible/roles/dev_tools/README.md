# devel

This role installs optional development tools for Autoware.

## Tools

- pipx
- Go
- PlotJuggler
- Git LFS
- pre-commit
- clang-format

## Inputs

| Name      | Required | Description           |
| --------- | -------- | --------------------- |
| rosdistro | true     | The ROS distribution. |

## Manual Installation

## Set up the environment variables

```bash
# Choose your ROS distribution
rosdistro=humble  # or jazzy
```

## Install the tools

```bash
sudo apt-get update

sudo apt install pipx

sudo apt install -y golang
sudo apt install -y ros-${rosdistro}-plotjuggler-ros
sudo apt install -y git-lfs

# Setup Git LFS
git lfs install

pipx install pre-commit
pipx install clang-format
```

## Abbreviations, terms and symbols

| Term                  | Meaning                                                                                                                   |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| apt                   | Advanced Package Tool: Ubuntu's package manager, used to install, update and remove system software                       |
| apt-get               | The older, script-friendly command-line front end of apt; it does the same job as `apt`                                   |
| Autoware              | An open-source software stack for self-driving vehicles; this repository sets up its development environment              |
| clang-format          | A tool that formats C and C++ code to a consistent style                                                                  |
| devel                 | Short for development                                                                                                     |
| environment variables | Named settings the shell passes to the programs it starts; here shell variables used by the commands below                |
| Git                   | The version control system used to track changes to source code                                                           |
| Git LFS               | Git Large File Storage: a Git extension that keeps large files outside the normal history                                 |
| Go                    | The Go programming language, installed by the `golang` package                                                            |
| humble                | ROS 2 Humble Hawksbill, the ROS 2 release paired with Ubuntu 22.04                                                        |
| Inputs                | The role variables you can set to change what the role does                                                               |
| jazzy                 | ROS 2 Jazzy Jalisco, the ROS 2 release paired with Ubuntu 24.04                                                           |
| pipx                  | A tool that installs Python command-line applications, each in its own isolated environment                               |
| PlotJuggler           | A desktop app for plotting data over time, with a plug-in for reading ROS messages                                        |
| pre-commit            | A tool that runs checks, such as code formatters, automatically before each Git commit                                    |
| role                  | A reusable unit of Ansible tasks that installs or configures one thing; each folder under `ansible/roles/` is a role      |
| ROS                   | Robot Operating System: the open-source framework of tools and libraries that robot software such as Autoware is built on |
| ROS distribution      | A named ROS 2 release, such as humble or jazzy                                                                            |
| rosdistro             | The variable that names the ROS 2 release (distribution) to use, such as `humble` or `jazzy`                              |
| sudo                  | A command that runs another command with administrator (root) rights, after asking for your password                      |
| `#`                   | In a shell or config block, starts a comment that is not run                                                              |
| `-y`                  | Answers yes to every question so the command runs without stopping to ask                                                 |
| `${...}`              | Inserts the value of a shell variable, for example `${rosdistro}` becomes `humble`                                        |

Other project terms are defined in the [Glossary](../../../wiki/Glossary.md).
