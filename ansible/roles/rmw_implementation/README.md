# rmw_implementation

This role sets up ROS 2 RMW implementation following [this page](https://docs.ros.org/en/humble/How-To-Guides/Working-with-multiple-RMW-implementations.html).

## Inputs

| Name               | Required | Description         |
| ------------------ | -------- | ------------------- |
| rosdistro          | true     | The ROS distro.     |
| rmw_implementation | true     | RMW implementation. |

## Manual Installation

## Set up the environment variables

```bash
# Choose your ROS distribution
rosdistro=humble  # or jazzy

# RMW implementation (see ./defaults/main.yaml for the current default)
rmw_implementation=rmw_cyclonedds_cpp
```

## Install the RMW implementation

For details: <https://docs.ros.org/en/humble/How-To-Guides/Working-with-multiple-RMW-implementations.html>

```bash
sudo apt update
sudo apt install ros-${rosdistro}-${rmw_implementation//_/-}

# (Optional) You set the default RMW implementation in the ~/.bashrc file.
echo '' >> ~/.bashrc && echo "export RMW_IMPLEMENTATION=${rmw_implementation}" >> ~/.bashrc
```

## Abbreviations, terms and symbols

| Term                         | Meaning                                                                                                                   |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| apt                          | Advanced Package Tool: Ubuntu's package manager, used to install, update and remove system software                       |
| `.bashrc`                    | A script in your home directory that the bash shell runs each time it starts; used here to set environment variables      |
| `cpp`                        | C++, the language the RMW implementation is written in                                                                    |
| CycloneDDS                   | Eclipse Cyclone DDS: an open-source DDS library; `rmw_cyclonedds_cpp` is the RMW implementation that uses it              |
| DDS                          | Data Distribution Service: the publish-subscribe networking standard ROS 2 uses to send messages                          |
| `defaults/main.yaml`         | The file inside a role that holds the default values of its variables                                                     |
| distro                       | Short for distribution: a ROS 2 release such as humble                                                                    |
| environment variables        | Named settings the shell passes to the programs it starts; here shell variables used by the commands below                |
| humble                       | ROS 2 Humble Hawksbill, the ROS 2 release paired with Ubuntu 22.04                                                        |
| Inputs                       | The role variables you can set to change what the role does                                                               |
| jazzy                        | ROS 2 Jazzy Jalisco, the ROS 2 release paired with Ubuntu 24.04                                                           |
| RMW                          | ROS MiddleWare: the ROS 2 layer that chooses which communication library carries messages between programs                |
| `RMW_IMPLEMENTATION`         | Environment variable that selects the RMW implementation ROS 2 programs use                                               |
| role                         | A reusable unit of Ansible tasks that installs or configures one thing; each folder under `ansible/roles/` is a role      |
| ROS                          | Robot Operating System: the open-source framework of tools and libraries that robot software such as Autoware is built on |
| ROS 2                        | Robot Operating System 2: the second generation of ROS, which Autoware is built on                                        |
| rosdistro                    | The variable that names the ROS 2 release (distribution) to use, such as `humble` or `jazzy`                              |
| sudo                         | A command that runs another command with administrator (root) rights, after asking for your password                      |
| `#`                          | In a shell or config block, starts a comment that is not run                                                              |
| `./`                         | A path starting in this role's folder                                                                                     |
| `${...}`                     | Inserts the value of a shell variable, for example `${rosdistro}` becomes `humble`                                        |
| `${rmw_implementation//_/-}` | Shell syntax that replaces every `_` in the value with `-`, to form the package name                                      |
| `~`                          | Shorthand for your home directory, for example `/home/<you>`                                                              |
| `>>`                         | Appends a command's output to the end of a file                                                                           |
| `&&`                         | Runs the next command only if the previous one succeeded                                                                  |

Other project terms are defined in the [Glossary](../../../wiki/Glossary.md).
