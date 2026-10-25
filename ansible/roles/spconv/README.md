# spconv

This role install the `cumm` and `spconv` libraries needed to perform sparse convolutions.
The [original implementation](https://github.com/traveller59/spconv) did not provide a shared library, which is pre-generated c++ code and pre-compiled libraries were prepared [separately](https://github.com/autowarefoundation/spconv_cpp).

## Architecture Support

This role supports different architectures with platform-specific package variants:

- **amd64**: No suffix (e.g., `cumm_0.5.3_amd64.deb`)
- **arm64**:
  - Default: `-sbsa` suffix for server platforms (e.g., `cumm_0.5.3_arm64-sbsa.deb`)
  - Jetson: `-jetson` suffix when `spconv_is_jetson=true` (e.g., `cumm_0.5.3_arm64-jetson.deb`)

## Manual Installation

For manual installation, please follow the instructions in [this](https://github.com/autowarefoundation/spconv_cpp) repository.

## Run the playbook

The following command will install a particular version of the packages using ansible.

### Standard installation (amd64 or arm64 server)

```bash
export SPCONV_CUMM_VERSION=0.5.3
export SPCONV_VERSION=2.3.8
ansible-playbook autoware.dev_env.install_dev_env --tags spconv -e spconv_cumm_version=${SPCONV_CUMM_VERSION} -e spconv_version=${SPCONV_VERSION} --ask-become-pass
```

### Installation for NVIDIA Jetson platforms

```bash
export SPCONV_CUMM_VERSION=0.5.3
export SPCONV_VERSION=2.3.8
ansible-playbook autoware.dev_env.install_dev_env --tags spconv -e spconv_cumm_version=${SPCONV_CUMM_VERSION} -e spconv_version=${SPCONV_VERSION} -e spconv_is_jetson=true --ask-become-pass
```

## Abbreviations, terms and symbols

| Term                | Meaning                                                                                                              |
| ------------------- | -------------------------------------------------------------------------------------------------------------------- |
| amd64               | Debian and Ubuntu's name for the 64-bit Intel/AMD processor architecture (the same as `x86_64`)                      |
| ansible             | An automation tool that sets up a machine by running steps written in YAML files                                     |
| architecture        | The processor family a package is built for, such as amd64 or arm64                                                  |
| arm64               | Debian and Ubuntu's name for the 64-bit ARM processor architecture (the same as `aarch64`)                           |
| c++                 | The C++ programming language                                                                                         |
| convolution         | A neural-network operation that slides a small filter over data to find patterns                                     |
| cumm                | A CUDA matrix-multiplication library by the spconv author, which spconv needs                                        |
| deb                 | The package file format used by Debian and Ubuntu; also the keyword that marks a package source line in apt          |
| Jetson              | NVIDIA's family of small embedded computers for robotics, built on 64-bit ARM processors                             |
| library             | Reusable compiled code that programs call                                                                            |
| NVIDIA              | The company that makes the GPUs and GPU software (CUDA, TensorRT, drivers) used by Autoware                          |
| playbook            | An Ansible file that lists which roles and tasks to run; this repository's main one is `install_dev_env`             |
| pre-compiled        | Built in advance, so you do not have to compile it yourself                                                          |
| role                | A reusable unit of Ansible tasks that installs or configures one thing; each folder under `ansible/roles/` is a role |
| SBSA                | Server Base System Architecture: ARM's standard for server-class 64-bit ARM machines                                 |
| shared library      | Compiled code (`.so` file) that programs load when they start                                                        |
| sparse convolution  | A convolution that only processes the non-empty parts of the data, such as a 3D lidar point cloud, to save time      |
| spconv              | A library of sparse convolution operations for GPUs, used by Autoware's 3D object detection                          |
| suffix              | Text added to the end of a file name                                                                                 |
| `0.5.3`             | A version number: major.minor.patch                                                                                  |
| `export`            | Sets a shell variable and passes it to the programs the shell starts                                                 |
| `--tags`            | For `ansible-playbook`: run only the roles and tasks carrying the given tag                                          |
| `-e`                | For `ansible-playbook`: sets a variable for this run, overriding its default (short for `--extra-vars`)              |
| `${...}`            | Inserts the value of a shell variable, for example `${rosdistro}` becomes `humble`                                   |
| `--ask-become-pass` | For `ansible-playbook`: asks for your sudo password once, so steps that need administrator rights can run            |

Other project terms are defined in the [Glossary](../../../wiki/Glossary.md).
