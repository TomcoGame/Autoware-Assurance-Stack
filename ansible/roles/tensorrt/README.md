# tensorrt

This role installs TensorRT following [the official NVIDIA TensorRT Installation Guide](https://docs.nvidia.com/deeplearning/tensorrt/install-guide/index.html#installing).

## Inputs

| Name             | Required | Description              |
| ---------------- | -------- | ------------------------ |
| tensorrt_version | true     | The version of TensorRT. |

## Version selection

| Ubuntu         | Architecture                                            | TensorRT version     |
| -------------- | ------------------------------------------------------- | -------------------- |
| 22.04 (humble) | x86_64                                                  | 10.8.0.43-1+cuda12.8 |
| 22.04 (humble) | aarch64 (SBSA)                                          | 10.3.0.26-1+cuda12.5 |
| 24.04 (jazzy)  | x86_64 / aarch64 (SBSA, incl. Jetson Thor + DRIVE Thor) | 10.13.3.9-1+cuda13.0 |

Override `tensorrt_version` explicitly via `-e tensorrt_version=…` to pin a different release.

## Manual Installation

### Set up the environment variables

```bash
# From the Autoware repository root:
# defaults/main.yaml contains an architecture-dependent Jinja2 expression;
# extract the matching version for this machine.
if [ "$(uname -m)" = "aarch64" ]; then
  tensorrt_version=$(grep -oP "'\K[^']+(?=' if)" ansible/roles/tensorrt/defaults/main.yaml)
else
  tensorrt_version=$(grep -oP "else '\K[^']+" ansible/roles/tensorrt/defaults/main.yaml)
fi
```

### Install TensorRT

```bash
sudo apt-get install -y \
libnvinfer10=${tensorrt_version} \
libnvinfer-plugin10=${tensorrt_version} \
libnvonnxparsers10=${tensorrt_version} \
libnvinfer-dev=${tensorrt_version} \
libnvinfer-plugin-dev=${tensorrt_version} \
libnvinfer-headers-dev=${tensorrt_version} \
libnvinfer-headers-plugin-dev=${tensorrt_version} \
libnvonnxparsers-dev=${tensorrt_version}

sudo apt-mark hold \
libnvinfer10 \
libnvinfer-plugin10 \
libnvonnxparsers10 \
libnvinfer-dev \
libnvinfer-plugin-dev \
libnvonnxparsers-dev \
libnvinfer-headers-dev \
libnvinfer-headers-plugin-dev
```

## Abbreviations, terms and symbols

| Term                   | Meaning                                                                                                              |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------- |
| aarch64                | The 64-bit ARM processor architecture, used by ARM servers and NVIDIA Jetson boards                                  |
| apt-get                | The older, script-friendly command-line front end of apt; it does the same job as `apt`                              |
| apt-mark hold          | An apt command that freezes a package at its installed version so upgrades leave it alone                            |
| architecture           | The processor family of the machine, such as x86_64 or aarch64                                                       |
| CUDA                   | Compute Unified Device Architecture: NVIDIA's toolkit for running general computation on its GPUs                    |
| `defaults/main.yaml`   | The file inside a role that holds the default values of its variables                                                |
| `-dev`                 | In a package name, the development package with the headers needed to build against the library                      |
| DRIVE Thor             | NVIDIA's computer platform for vehicles                                                                              |
| environment variables  | Named settings the shell passes to the programs it starts; here shell variables used by the commands below           |
| grep                   | A command that searches text for lines matching a pattern                                                            |
| headers                | C or C++ files that declare a library's functions so other code can call them                                        |
| humble                 | ROS 2 Humble Hawksbill, the ROS 2 release paired with Ubuntu 22.04                                                   |
| incl.                  | Including                                                                                                            |
| Inputs                 | The role variables you can set to change what the role does                                                          |
| jazzy                  | ROS 2 Jazzy Jalisco, the ROS 2 release paired with Ubuntu 24.04                                                      |
| Jetson Thor            | An NVIDIA Jetson embedded computer of the Thor generation                                                            |
| Jinja2                 | The template language Ansible uses for expressions inside variables                                                  |
| `libnvinfer`           | TensorRT's main library for running neural networks (nv infer = NVIDIA inference)                                    |
| `libnvonnxparsers`     | TensorRT's library that reads models in ONNX format                                                                  |
| NVIDIA                 | The company that makes the GPUs and GPU software (CUDA, TensorRT, drivers) used by Autoware                          |
| ONNX                   | Open Neural Network Exchange: an open file format for trained models                                                 |
| plugin                 | An add-on that extends a program; `libnvinfer-plugin` adds extra TensorRT layers                                     |
| role                   | A reusable unit of Ansible tasks that installs or configures one thing; each folder under `ansible/roles/` is a role |
| SBSA                   | Server Base System Architecture: ARM's standard for server-class 64-bit ARM machines                                 |
| TensorRT               | NVIDIA's library that optimises trained neural networks and runs them fast on NVIDIA GPUs                            |
| Ubuntu                 | The Linux distribution Autoware targets; versions are named year.month, such as 22.04 (April 2022)                   |
| `uname -m`             | A command that prints the machine's processor architecture                                                           |
| x86_64                 | The 64-bit Intel/AMD processor architecture used by most desktop and laptop PCs                                      |
| `10.8.0.43-1+cuda12.8` | Version notation: TensorRT version 10.8.0.43, package revision 1, built for CUDA 12.8                                |
| `-e`                   | For `ansible-playbook`: sets a variable for this run, overriding its default (short for `--extra-vars`)              |
| `…`                    | Placeholder: replace with your own value                                                                             |
| `#`                    | In a shell or config block, starts a comment that is not run                                                         |
| `$(...)`               | Command substitution: runs the command inside and puts its output in its place                                       |
| `-oP`                  | For `grep`: print only the matching part, using Perl-style patterns                                                  |
| `'\K[^']+(?=' if)'`    | A Perl-style regular expression that picks out the version text between quotes                                       |
| `-y`                   | Answers yes to every question so the command runs without stopping to ask                                            |
| `\`                    | At the end of a line, continues the command on the next line                                                         |
| `package=version`      | apt syntax to install one exact version of a package                                                                 |

Other project terms are defined in the [Glossary](../../../wiki/Glossary.md).
