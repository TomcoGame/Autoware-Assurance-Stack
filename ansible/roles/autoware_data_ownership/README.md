# Role: autoware_data_ownership

This role makes the user that runs the playbook the owner of `~/autoware_data` and of every path under it.

`~/autoware_data` holds the maps, the ML models, the recordings and the scenarios. It sits in the home directory of the user because every consumer reads it as that user:

- The ansible roles that download into it
- The ROS nodes that write TensorRT engine files next to the models
- The containers under `docker/`, which mount it for the unprivileged `aw` user

Older installs downloaded into this directory as root. A root-owned directory stops all three consumers. This role corrects such an install one time.

When `~/autoware_data` does not exist, the role does nothing. When the user already owns every path in it, the role does nothing. Only the repair needs sudo, so a clean install needs no password.

Remove this role when the installs in use have all migrated. Nothing in this repository creates a root-owned path under `~/autoware_data` any more, so a corrected install cannot return to that state:

- The roles that write into it no longer use `become`
- The compose files under `docker/` set `create_host_path: false`, so Compose stops on a missing mount source instead of creating it as root

## Inputs

| Name                           | Default                                      | Description                                                   |
| ------------------------------ | -------------------------------------------- | ------------------------------------------------------------- |
| `autoware_data_ownership__dir` | `{{ ansible_facts.env.HOME }}/autoware_data` | The directory to take ownership of, with everything under it. |

## Manual correction

```bash
sudo chown -Rh "$USER:$USER" "$(readlink -f ~/autoware_data)"
```

`readlink -f` resolves `~/autoware_data` when it is a symbolic link, so a tree that sits on another disk is corrected too. `-h` acts on a symbolic link inside the tree instead of the file it points to, so a link that points out of `~/autoware_data` leaves the owner of its target alone. The role runs this same command.

## Abbreviations, terms and symbols

| Term               | Meaning                                                                                                                   |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------- |
| Ansible            | An automation tool that sets up a machine by running steps written in YAML files                                          |
| `ansible_facts`    | Information Ansible gathers about the machine, such as the `HOME` environment variable                                    |
| `aw`               | The ordinary (unprivileged) user account inside the project's containers                                                  |
| `become`           | The Ansible keyword that runs a task with administrator rights, as with sudo                                              |
| `chown`            | A command that changes the owner of files                                                                                 |
| Compose            | Docker Compose: a tool that starts a set of containers described in a YAML file                                           |
| consumer           | A program or user that reads the data                                                                                     |
| container          | An isolated environment with its own files and libraries, run with Docker                                                 |
| `create_host_path` | A Compose setting; when false, Compose stops instead of creating a missing host folder for a mount                        |
| Docker             | A tool that runs software in containers, isolated environments that carry their own files and libraries                   |
| engine file        | A model that TensorRT has converted and optimised for one specific GPU                                                    |
| home directory     | Your personal folder, such as `/home/<you>`                                                                               |
| Inputs             | The role variables you can set to change what the role does                                                               |
| ML                 | Machine Learning: software that learns its behaviour from data; here, the trained models Autoware runs                    |
| mount              | Making a folder on the host visible inside a container                                                                    |
| node               | One program in a ROS system                                                                                               |
| playbook           | An Ansible file that lists which roles and tasks to run; this repository's main one is `install_dev_env`                  |
| `readlink`         | A command that shows where a symbolic link points                                                                         |
| role               | A reusable unit of Ansible tasks that installs or configures one thing; each folder under `ansible/roles/` is a role      |
| root               | The Linux administrator account, which can change any file on the system                                                  |
| ROS                | Robot Operating System: the open-source framework of tools and libraries that robot software such as Autoware is built on |
| sudo               | A command that runs another command with administrator (root) rights, after asking for your password                      |
| symbolic link      | A file that points to another path                                                                                        |
| TensorRT           | NVIDIA's library that optimises trained neural networks and runs them fast on NVIDIA GPUs                                 |
| unprivileged       | Without administrator rights                                                                                              |
| `~`                | Shorthand for your home directory, for example `/home/<you>`                                                              |
| `__`               | In a variable name, separates the role name from the variable's own name                                                  |
| `{{ }}`            | Jinja2 template expression: Ansible replaces it with the value of the variable inside                                     |
| `-R`               | For `chown`: apply to the folder and everything inside it                                                                 |
| `$USER:$USER`      | The owner and group to set, both your user name                                                                           |
| `$(...)`           | Command substitution: runs the command inside and puts its output in its place                                            |
| `-f`               | For `readlink`: follow every link to the real final path                                                                  |
| `-h`               | For `chown`: change the link itself, not the file it points to                                                            |

Other project terms are defined in the [Glossary](../../../wiki/Glossary.md).
