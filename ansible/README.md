# Ansible Collection - autoware.dev_env

This collection contains the playbooks to set up the development environment for Autoware.

## Set up a development environment

### Ansible installation

```bash
# Remove apt installed ansible (In Ubuntu 22.04, ansible the version is old)
sudo apt-get purge ansible

# Install pipx
sudo apt-get -y update
sudo apt-get -y install pipx

# Add pipx to the system PATH
python3 -m pipx ensurepath

# Install ansible
pipx install --include-deps --force "ansible==10.*"
```

### Install ansible collections

This step should be repeated when a new playbook is added.

```bash
cd ~/autoware # The root directory of the cloned repository
ansible-galaxy collection install -f -r "ansible-galaxy-requirements.yaml"
```

## Abbreviations, terms and symbols

| Term                    | Meaning                                                                                                          |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Ansible                 | An automation tool that sets up a machine by running steps written in YAML files                                 |
| ansible-galaxy          | Ansible's command for installing collections and roles that a project depends on                                 |
| apt                     | Advanced Package Tool: Ubuntu's package manager, used to install, update and remove system software              |
| Autoware                | An open-source software stack for self-driving vehicles; this repository sets up its development environment     |
| collection              | A bundle of Ansible playbooks and roles distributed together; this repository's collection is `autoware.dev_env` |
| development environment | The tools and libraries a developer needs installed to build and run Autoware                                    |
| `ensurepath`            | A pipx command that adds the folder pipx installs programs into to your `PATH`                                   |
| `PATH`                  | The environment variable listing the folders the shell searches for programs                                     |
| pipx                    | A tool that installs Python command-line applications, each in its own isolated environment                      |
| playbook                | An Ansible file that lists which roles and tasks to run; this repository's main one is `install_dev_env`         |
| purge                   | An apt operation that removes a package together with its configuration files                                    |
| `python3`               | The command that runs Python 3, the programming language pipx and Ansible are written in                         |
| repository              | A collection of files with their version history, kept with Git; you clone (copy) it to your machine             |
| sudo                    | A command that runs another command with administrator (root) rights, after asking for your password             |
| Ubuntu 22.04            | The Ubuntu Linux release from April 2022; Ubuntu versions are named year.month                                   |
| YAML                    | YAML Ain't Markup Language: a human-readable text format for configuration files                                 |
| `#`                     | In a shell or config block, starts a comment that is not run                                                     |
| `-y`                    | Answers yes to every question so the command runs without stopping to ask                                        |
| `--include-deps`        | For `pipx install`: also make the command-line programs of the package's dependencies available                  |
| `--force`               | Reinstall even if the package is already installed                                                               |
| `"ansible==10.*"`       | Version notation: `==` means exactly this version and `10.*` means any 10.x release                              |
| `~`                     | Shorthand for your home directory, for example `/home/<you>`                                                     |
| `-f`                    | For `ansible-galaxy`: reinstall even if already installed (force)                                                |
| `-r`                    | For `ansible-galaxy`: read the list of things to install from the named requirements file                        |

Other project terms are defined in the [Glossary](../wiki/Glossary.md).
