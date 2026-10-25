# agnocast

This role installs [Agnocast](https://github.com/tier4/agnocast), true zero-copy communication middleware for all ROS 2 message types.

## Inputs

None.

## Manual Installation

```bash
agnocast_version="2.1.2"
agnocast_heaphook_package="agnocast-heaphook-v${agnocast_version}"
agnocast_kmod_package="agnocast-kmod-v${agnocast_version}"

sudo add-apt-repository -y ppa:t4-system-software/agnocast
sudo apt update
sudo apt install -y "${agnocast_heaphook_package}"

if dkms status | grep agnocast | grep -q "{agnocast_version}"; then
    echo "agnocast-kmod-v${agnocast_version} is already registered in dkms. Skipping purge and install."
else
    sudo apt purge -y "${agnocast_kmod_package}"
    sudo apt install -y "${agnocast_kmod_package}"
fi

```

## Abbreviations, terms and symbols

| Term                 | Meaning                                                                                                              |
| -------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `add-apt-repository` | A command that adds an extra package source to apt                                                                   |
| Agnocast             | Middleware from TIER IV that lets ROS 2 programs share messages without copying them                                 |
| apt                  | Advanced Package Tool: Ubuntu's package manager, used to install, update and remove system software                  |
| dkms                 | Dynamic Kernel Module Support: rebuilds kernel modules automatically when the Linux kernel is updated                |
| grep                 | A command that searches text for lines matching a pattern                                                            |
| heaphook             | The Agnocast package that intercepts a program's dynamic memory (heap) allocation so message memory can be shared    |
| Inputs               | The role variables you can set to change what the role does                                                          |
| kmod                 | Kernel module: code loaded into the Linux kernel; the `agnocast-kmod` package is Agnocast's kernel part              |
| message types        | The data structures ROS 2 programs send to each other, such as an image or a point cloud                             |
| middleware           | A software layer that carries data between programs                                                                  |
| PPA                  | Personal Package Archive: a third-party apt repository hosted on Launchpad, Ubuntu's code hosting site               |
| purge                | An apt operation that removes a package together with its configuration files                                        |
| role                 | A reusable unit of Ansible tasks that installs or configures one thing; each folder under `ansible/roles/` is a role |
| ROS 2                | Robot Operating System 2: the second generation of ROS, which Autoware is built on                                   |
| sudo                 | A command that runs another command with administrator (root) rights, after asking for your password                 |
| zero-copy            | Passing data between programs without duplicating it in memory, which saves time                                     |
| `${...}`             | Inserts the value of a shell variable, for example `${rosdistro}` becomes `humble`                                   |
| `-y`                 | Answers yes to every question so the command runs without stopping to ask                                            |
| `\|`                 | Pipe: sends the output of one command into the next one                                                              |
| `-q`                 | For `grep`: print nothing and only report whether a match was found                                                  |

Other project terms are defined in the [Glossary](../../../wiki/Glossary.md).
