# docker_engine

This role installs [Docker Engine](https://docs.docker.com/engine/) following the [Official Installation Guide](https://docs.docker.com/engine/install/ubuntu/).
Then it sets up execution from non-root users following the [Official Post Installation Steps](https://docs.docker.com/engine/install/linux-postinstall).

## Inputs

None.

## Manual installation (Recommended)

> ℹ️ The steps below may differ from the role implementation.  
> They reflect the **most up-to-date and preferred procedure** for manual installation.  
> The role will be updated to align with these steps.

### Install Docker Engine

```bash
# Taken from: https://docs.docker.com/engine/install/ubuntu/
# And: https://docs.docker.com/engine/install/linux-postinstall

# Uninstall old versions
sudo apt remove $(dpkg --get-selections docker.io docker-compose docker-compose-v2 docker-doc podman-docker containerd runc | cut -f1)

# Add Docker's official GPG key:
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify that Docker Engine is installed correctly by running the hello-world image.
sudo docker run hello-world
# Note: This command downloads a test image and runs it in a container. When the container runs, it prints a message and exits.
```

### Post-Installation setup (non-root usage)

```bash
# Post-installation steps for Linux

# Create the docker group.
sudo groupadd docker

# Add your user to the docker group.
sudo usermod -aG docker $USER

# Log out and log back in so that your group membership is re-evaluated.

# Verify that you can run docker commands without sudo
docker run hello-world
# Note: This command downloads a test image and runs it in a container. When the container runs, it prints a message and exits.
```

## Abbreviations, terms and symbols

| Term                                  | Meaning                                                                                                              |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| apt                                   | Advanced Package Tool: Ubuntu's package manager, used to install, update and remove system software                  |
| `ca-certificates`                     | A package of trusted certificates used to check the identity of HTTPS websites                                       |
| CE                                    | Community Edition: the free edition of Docker (`docker-ce`)                                                          |
| CLI                                   | Command-Line Interface: a program you control by typing commands (`docker-ce-cli` is the `docker` command)           |
| container                             | An isolated environment, started from an image, with its own files and libraries                                     |
| containerd                            | The container runtime that Docker uses underneath to run containers                                                  |
| curl                                  | A command-line tool that downloads data from a web address                                                           |
| Docker                                | A tool that runs software in containers, isolated environments that carry their own files and libraries              |
| `docker-buildx-plugin`                | Buildx: a Docker plug-in with extended image-building features                                                       |
| `docker-compose-plugin`               | Docker Compose: a Docker plug-in that starts a set of containers described in a YAML file                            |
| Docker Engine                         | The Docker background service and command-line tool that build and run containers                                    |
| dpkg                                  | The low-level Debian/Ubuntu tool that installs and queries `.deb` package files; apt uses it underneath              |
| GPG key                               | GNU Privacy Guard key: a cryptographic key used to check that downloaded packages really come from their publisher   |
| group                                 | A Linux user group; members of the `docker` group may use Docker without sudo                                        |
| hello-world                           | A tiny test image that prints a message to confirm Docker works                                                      |
| image                                 | A packaged set of files and settings from which containers are started                                               |
| Inputs                                | The role variables you can set to change what the role does                                                          |
| keyrings                              | The folder where apt keeps the keys it uses to trust repositories                                                    |
| non-root                              | An ordinary user without administrator rights                                                                        |
| podman-docker                         | A package that makes the Podman container tool answer to the `docker` command; removed to avoid a conflict           |
| repository                            | A server that apt downloads packages from                                                                            |
| role                                  | A reusable unit of Ansible tasks that installs or configures one thing; each folder under `ansible/roles/` is a role |
| root                                  | The Linux administrator account, which can change any file on the system                                             |
| runc                                  | The low-level program that actually starts containers                                                                |
| sources                               | The files that tell apt which repositories to download packages from                                                 |
| sudo                                  | A command that runs another command with administrator (root) rights, after asking for your password                 |
| `Suites`, `Components`, `Signed-By`   | Fields of an apt source file: the Ubuntu release name, the section of the repository, and the key used to check it   |
| `UBUNTU_CODENAME`, `VERSION_CODENAME` | Values in `/etc/os-release` giving the Ubuntu release's code name, such as `jammy` for 22.04                         |
| `usermod`                             | A command that changes a user account, here to add it to a group                                                     |
| ℹ️                                    | Information: a note to read before continuing                                                                        |
| `#`                                   | In a shell or config block, starts a comment that is not run                                                         |
| `$(...)`                              | Command substitution: runs the command inside and puts its output in its place                                       |
| `\|`                                  | Pipe: sends the output of one command into the next one                                                              |
| `-f1`                                 | For `cut`: keep only the first column                                                                                |
| `-m 0755 -d`                          | For `install`: create a folder (`-d`) that everyone may read and enter (`0755`)                                      |
| `-fsSL`                               | For `curl`: fail on errors, show no progress but do show errors, and follow redirects                                |
| `-o`                                  | For `curl`: save the download to the given file                                                                      |
| `a+r`                                 | For `chmod`: let all users read the file                                                                             |
| `<<EOF ... EOF`                       | Here-document: the lines up to `EOF` are passed to the command as input                                              |
| `.`                                   | Runs a file in the current shell, here to read the values in `/etc/os-release`                                       |
| `&&`                                  | Runs the next command only if the previous one succeeded                                                             |
| `${A:-B}`                             | The value of A, or B if A is empty                                                                                   |
| `-aG`                                 | For `usermod`: add the user to the group, keeping its other groups                                                   |
| `$USER`                               | The environment variable holding your user name                                                                      |

Other project terms are defined in the [Glossary](../../../wiki/Glossary.md).
