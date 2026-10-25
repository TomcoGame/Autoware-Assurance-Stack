# ros2

This role installs [ROS 2](http://www.ros2.org/) following [this page](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html).

Additional steps may be needed depending on the `rosdistro` you choose.

To prevent the update of the ROS 2 packages, if ros-`distro`-desktop is held, the installation process for the packages will be skipped and output warning.

<!-- TODO: Add these steps to the role if Humble requires. -->

```bash
$ sudo apt install software-properties-common
$ sudo add-apt-repository universe
$ apt-cache policy | grep universe
 500 http://us.archive.ubuntu.com/ubuntu focal/universe amd64 Packages
     release v=20.04,o=Ubuntu,a=focal,n=focal,l=Ubuntu,c=universe,b=amd64
```

## Inputs

| Name                   | Required | Description                                      |
| ---------------------- | -------- | ------------------------------------------------ |
| rosdistro              | true     | The ROS distro.                                  |
| ros2_installation_type | false    | The installation type (`desktop` or `ros-base`). |

## Manual Installation

The `ros2_installation_type` variable can also be found in:
[./defaults/main.yaml](./defaults/main.yaml)

For Universe, the `rosdistro` variable can also be found in:
[../../playbooks/install_dev_env.yaml](../../playbooks/install_dev_env.yaml)

```bash
# Choose your ROS distribution
rosdistro=humble  # or jazzy

# Taken from: https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html

# You will need to add the ROS 2 apt repository to your system. First, make sure that the Ubuntu Universe repository is enabled by checking the output of this command.
apt-cache policy | grep universe

# The output of the above command should contain following:

# 500 http://us.archive.ubuntu.com/ubuntu focal/universe amd64 Packages
#     release v=20.04,o=Ubuntu,a=focal,n=focal,l=Ubuntu,c=universe,b=amd64

# If you don’t see an output line like the one above, then enable the Universe repository with these instructions.
sudo apt install software-properties-common
sudo add-apt-repository universe

# Now add the ROS 2 apt repository to your system. First authorize our GPG key with apt.
sudo apt update && sudo apt install curl gnupg lsb-release
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

# Then add the repository to your sources list.
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Update your apt repository caches after setting up the repositories.
sudo apt update

# Desktop Install
ros2_installation_type=desktop
sudo apt install ros-${rosdistro}-${ros2_installation_type}

# Environment setup
# (Optional) You can source ros2 in the ~/.bashrc file.
echo '' >> ~/.bashrc && echo "source /opt/ros/${rosdistro}/setup.bash" >> ~/.bashrc
```

## Abbreviations, terms and symbols

| Term                                     | Meaning                                                                                                              |
| ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| amd64                                    | Debian and Ubuntu's name for the 64-bit Intel/AMD processor architecture (the same as `x86_64`)                      |
| apt                                      | Advanced Package Tool: Ubuntu's package manager, used to install, update and remove system software                  |
| `apt-cache policy`                       | An apt command that lists the package sources and their priorities                                                   |
| `.bashrc`                                | A script in your home directory that the bash shell runs each time it starts; used here to set environment variables |
| curl                                     | A command-line tool that downloads data from a web address                                                           |
| deb                                      | The package file format used by Debian and Ubuntu; also the keyword that marks a package source line in apt          |
| Debians                                  | Debian packages (`.deb` files), the package format Ubuntu uses                                                       |
| `defaults/main.yaml`                     | The file inside a role that holds the default values of its variables                                                |
| `desktop`, `ros-base`                    | ROS 2 install types: desktop includes graphical tools such as RViz2; ros-base is the minimal core                    |
| distro                                   | Short for distribution: a release of Ubuntu or of ROS 2                                                              |
| focal                                    | The code name of Ubuntu 20.04                                                                                        |
| gnupg                                    | GNU Privacy Guard: tools for handling the keys apt uses to trust a repository                                        |
| GPG key                                  | GNU Privacy Guard key: a cryptographic key used to check that downloaded packages really come from their publisher   |
| held                                     | Frozen with `apt-mark hold`, so apt does not upgrade it                                                              |
| humble                                   | ROS 2 Humble Hawksbill, the ROS 2 release paired with Ubuntu 22.04                                                   |
| Inputs                                   | The role variables you can set to change what the role does                                                          |
| jazzy                                    | ROS 2 Jazzy Jalisco, the ROS 2 release paired with Ubuntu 24.04                                                      |
| `lsb-release`                            | A package with a command that prints which Linux release is installed                                                |
| playbook                                 | An Ansible file that lists which roles and tasks to run; this repository's main one is `install_dev_env`             |
| role                                     | A reusable unit of Ansible tasks that installs or configures one thing; each folder under `ansible/roles/` is a role |
| ROS 2                                    | Robot Operating System 2: the second generation of ROS, which Autoware is built on                                   |
| rosdistro                                | The variable that names the ROS 2 release (distribution) to use, such as `humble` or `jazzy`                         |
| `setup.bash`                             | The script that makes the installed ROS 2 commands available in your shell                                           |
| `software-properties-common`             | An Ubuntu package that provides `add-apt-repository`, for adding package sources                                     |
| source                                   | To run a script in the current shell so the settings it makes stay in effect                                         |
| sudo                                     | A command that runs another command with administrator (root) rights, after asking for your password                 |
| TODO                                     | A note marking work still to do                                                                                      |
| Ubuntu                                   | The Linux distribution Autoware targets; versions are named year.month, such as 22.04 (April 2022)                   |
| `UBUNTU_CODENAME`                        | A value in `/etc/os-release` giving the Ubuntu release's code name                                                   |
| Universe                                 | Ubuntu's community-maintained package repository                                                                     |
| `$`                                      | The shell prompt: type what follows it, not the `$` itself                                                           |
| `\|`                                     | Pipe: sends the output of one command into the next one                                                              |
| `500`                                    | The priority apt gives this package source; 500 is the normal default                                                |
| `v=`, `o=`, `a=`, `n=`, `l=`, `c=`, `b=` | apt source details: version, origin, archive, code name, label, component and architecture                           |
| `./`, `../`                              | A path relative to this file: `./` is this folder, `../` is the folder above it                                      |
| `#`                                      | In a shell or config block, starts a comment that is not run                                                         |
| `&&`                                     | Runs the next command only if the previous one succeeded                                                             |
| `-sSL`                                   | For `curl`: stay quiet except for errors and follow redirects                                                        |
| `-o`                                     | Save the download to the given file                                                                                  |
| `[arch=... signed-by=...]`               | Options in an apt source line: which processor architecture to use and which key checks the repository               |
| `$(...)`                                 | Command substitution: runs the command inside and puts its output in its place                                       |
| `> /dev/null`                            | Throws away a command's output so it is not printed                                                                  |
| `${...}`                                 | Inserts the value of a shell variable, for example `${rosdistro}` becomes `humble`                                   |
| `~`                                      | Shorthand for your home directory, for example `/home/<you>`                                                         |
| `>>`                                     | Appends a command's output to the end of a file                                                                      |

Other project terms are defined in the [Glossary](../../../wiki/Glossary.md).
