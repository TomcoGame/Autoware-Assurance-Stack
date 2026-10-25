# qt5ct_setup Ansible role

## Overview

The `qt5ct_setup` Ansible role automates the configuration of the `qt5ct` environment for Autoware.
It won't affect the system-wide configuration.

## Installation

Follow the instructions below to **install** or **update** the custom theme for `RViz2` in Autoware.

> **Important:** Both commands must be run when you want to update the theme.

```bash
cd ~/autoware # The root directory of the cloned repository
ansible-galaxy collection install -f -r "ansible-galaxy-requirements.yaml"
ansible-playbook autoware.dev_env.install_dev_env --tags qt5ct_setup --ask-become-pass
```

## How to use the custom theme in RViz2

To apply a custom theme to RViz2, you can use the `qt5ct` platform theme. Follow these steps to ensure that the `QT_QPA_PLATFORMTHEME` environment variable is set correctly for your RViz2 instance when used with Autoware.

### Manual setup for running RViz2

Before running RViz2 manually, set the `QT_QPA_PLATFORMTHEME` environment variable to `qt5ct`.
This ensures that the custom theme settings are applied.

```bash
export QT_QPA_PLATFORMTHEME=qt5ct
```

Then, start RViz2 as usual.

```bash
rviz2
```

### Automatic setup in Autoware

In Autoware, the `QT_QPA_PLATFORMTHEME` environment variable is automatically set within the main [autoware.launch.xml](https://github.com/autowarefoundation/autoware_launch/blob/main/autoware_launch/launch/autoware.launch.xml) file.
Therefore, you do not need to manually set this environment variable when launching Autoware.

In the `autoware.launch.xml` file, RViz2 is configured with the following `<node>` element:

```xml
<node
  pkg="rviz2"
  exec="rviz2"
  name="rviz2"
  output="screen"
  args="-d $(var rviz_config) -s $(find-pkg-share autoware_launch)/rviz/image/autoware.png"
  if="$(var rviz)"
  respawn="$(var rviz_respawn)">
  <env name="QT_QPA_PLATFORMTHEME" value="qt5ct"/>
</node>
```

This configuration automatically sets the `QT_QPA_PLATFORMTHEME` to `qt5ct` when RViz2 is launched as part of Autoware.
It also includes additional options such as respawn behavior and custom RViz2 configurations.

## Abbreviations, terms and symbols

| Term                   | Meaning                                                                                                              |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Ansible                | An automation tool that sets up a machine by running steps written in YAML files                                     |
| ansible-galaxy         | Ansible's command for installing collections and roles that a project depends on                                     |
| ansible-playbook       | Ansible's command that runs a playbook on the machine                                                                |
| `args`                 | In a launch file, the command-line arguments passed to the program                                                   |
| Autoware               | An open-source software stack for self-driving vehicles; this repository sets up its development environment         |
| environment variable   | A named setting that the shell passes to every program it starts, such as `PATH`                                     |
| `find-pkg-share`       | A ROS 2 launch substitution that gives the path of a package's shared files                                          |
| launch file            | A ROS 2 file (here `autoware.launch.xml`) that starts and configures a set of programs                               |
| node                   | One program in a ROS system; the `<node>` element starts one                                                         |
| platform theme         | A Qt plug-in that sets the look of an application, such as colours and fonts                                         |
| Qt                     | A cross-platform toolkit for graphical user interfaces; RViz2 is built with it                                       |
| qt5ct                  | Qt5 Configuration Tool: sets the theme of Qt 5 applications                                                          |
| `QT_QPA_PLATFORMTHEME` | Environment variable telling Qt which platform theme to load (QPA means Qt Platform Abstraction)                     |
| respawn                | Restart the program automatically if it exits                                                                        |
| role                   | A reusable unit of Ansible tasks that installs or configures one thing; each folder under `ansible/roles/` is a role |
| RViz2                  | The ROS 2 tool that shows sensor data, maps and the vehicle in 3D                                                    |
| system-wide            | For every user on the machine, not just you                                                                          |
| theme                  | A set of colours, fonts and styles for an application's windows                                                      |
| XML                    | Extensible Markup Language: a text format of nested tags, used by ROS 2 launch files                                 |
| `~`                    | Shorthand for your home directory, for example `/home/<you>`                                                         |
| `#`                    | In a shell or config block, starts a comment that is not run                                                         |
| `--tags`               | For `ansible-playbook`: run only the roles and tasks carrying the given tag                                          |
| `--ask-become-pass`    | For `ansible-playbook`: asks for your sudo password once, so steps that need administrator rights can run            |
| `-d`                   | For `rviz2`: the display configuration file to open                                                                  |
| `$(var ...)`           | Launch-file syntax that inserts the value of a launch argument                                                       |
| `-s`                   | For `rviz2`: the image to show as the splash screen while it starts                                                  |

Other project terms are defined in the [Glossary](../../../wiki/Glossary.md).
