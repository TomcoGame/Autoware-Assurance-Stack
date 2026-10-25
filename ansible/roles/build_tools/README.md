# Build Tools

This role installs build tools for building Autoware.

## Tools

- ccache

## Inputs

## Manual Installation

```bash
sudo apt-get update
sudo apt-get install -y ccache
```

## Configuration (🆕 Recommended)

> ℹ️ These steps differ slightly from the existing Ansible setup and represent the preferred configuration.  
> The Ansible version will be updated to match the steps below.

```bash
# Make sure the ccache directory exists
mkdir -p "$HOME/.cache/ccache"

# Add the following lines to ~/.bashrc file
export CMAKE_C_COMPILER_LAUNCHER=ccache
export CMAKE_CXX_COMPILER_LAUNCHER=ccache
export CCACHE_DIR="$HOME/.cache/ccache/"
export CCACHE_LOGFILE=/tmp/ccache.log
```

Configure ccache maximum size:
`gedit $HOME/.cache/ccache/ccache.conf`

Add the following lines and save the file:

```bash
# Set maximum cache size
max_size = 15G
```

**Also see:** [🔗 Autoware Documentation / Using ccache to speed up compilation](https://autowarefoundation.github.io/autoware-documentation/main/tutorials/others/advanced-usage-of-colcon/#using-ccache-to-speed-up-recompilation).

## Abbreviations, terms and symbols

| Term                                                       | Meaning                                                                                                              |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Ansible                                                    | An automation tool that sets up a machine by running steps written in YAML files                                     |
| apt-get                                                    | The older, script-friendly command-line front end of apt; it does the same job as `apt`                              |
| Autoware                                                   | An open-source software stack for self-driving vehicles; this repository sets up its development environment         |
| `.bashrc`                                                  | A script in your home directory that the bash shell runs each time it starts; used here to set environment variables |
| cache                                                      | A store of earlier results kept so they can be reused instead of recomputed                                          |
| ccache                                                     | Compiler cache: speeds up rebuilds by reusing the results of earlier compilations                                    |
| `CCACHE_DIR`                                               | Environment variable setting the folder where ccache stores its cache                                                |
| `CCACHE_LOGFILE`                                           | Environment variable setting the file where ccache writes its log                                                    |
| `CMAKE_C_COMPILER_LAUNCHER`, `CMAKE_CXX_COMPILER_LAUNCHER` | CMake variables naming a program (here ccache) to run in front of the C and C++ (CXX) compilers                      |
| colcon                                                     | The build tool for ROS 2 workspaces                                                                                  |
| compilation                                                | Turning source code into a program the computer can run                                                              |
| gedit                                                      | The graphical text editor of the GNOME desktop                                                                       |
| `max_size`                                                 | The ccache setting for the largest size the cache may grow to                                                        |
| role                                                       | A reusable unit of Ansible tasks that installs or configures one thing; each folder under `ansible/roles/` is a role |
| sudo                                                       | A command that runs another command with administrator (root) rights, after asking for your password                 |
| `/tmp`                                                     | The Linux folder for temporary files, emptied at reboot                                                              |
| `-y`                                                       | Answers yes to every question so the command runs without stopping to ask                                            |
| 🆕                                                         | New: this procedure is newer than the one in the role                                                                |
| ℹ️                                                         | Information: a note to read before continuing                                                                        |
| `#`                                                        | In a shell or config block, starts a comment that is not run                                                         |
| `-p`                                                       | For `mkdir`: create the folder and any missing parent folders, with no error if it exists                            |
| `$HOME`                                                    | The environment variable holding the path of your home directory                                                     |
| `~`                                                        | Shorthand for your home directory, for example `/home/<you>`                                                         |
| `15G`                                                      | 15 gigabytes                                                                                                         |
| 🔗                                                         | Link: points to further reading                                                                                      |

Other project terms are defined in the [Glossary](../../../wiki/Glossary.md).
