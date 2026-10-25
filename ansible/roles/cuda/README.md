# cuda

This role installs [CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit) following [this page](https://developer.nvidia.com/cuda-12-8-0-download-archive?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=22.04&target_type=deb_network) and [this page](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#post-installation-actions).

This role also registers Vulkan, OpenGL, and OpenCL GPU vendors for future use.

## Inputs

| Name                 | Required | Description                                                      |
| -------------------- | -------- | ---------------------------------------------------------------- |
| cuda_version         | true     | The version of CUDA Toolkit.                                     |
| cuda_repo_distro     | false    | NVIDIA apt repo distro suffix (e.g. `ubuntu2204`, `ubuntu2404`). |
| cuda_install_drivers | false    | Whether to install cuda-drivers.                                 |

## Version selection

The role auto-selects CUDA version and apt repo distro based on the host's Ubuntu version:

| Ubuntu         | CUDA version | Apt repo distro | Driver package                                   |
| -------------- | ------------ | --------------- | ------------------------------------------------ |
| 22.04 (humble) | 12.8         | `ubuntu2204`    | `nvidia-open` (when `cuda_install_drivers=true`) |
| 24.04 (jazzy)  | 13.0         | `ubuntu2404`    | `nvidia-open` (when `cuda_install_drivers=true`) |

Both `cuda_version` and `cuda_repo_distro` are overridable via `-e cuda_version=…` and `-e cuda_repo_distro=…`. Override them together when installing a non-default toolkit release that NVIDIA only publishes under a different `ubuntuXXXX` repo than the host's Ubuntu version (e.g. CUDA 12.x on a 24.04 host).

## Manual Installation

### Version compatibility

- CUDA version `12.8`.
- NVIDIA driver version `570` or **newer**.

#### 🛠️ For Advanced Users

⚠️ **Proceed with caution**: Avoid removing essential system components.

To prevent conflicts during NVIDIA installation, we recommend completely removing old NVIDIA Drivers and CUDA by following this guide: [How can I uninstall a NVIDIA driver completely?](https://askubuntu.com/a/206289/761440).

- **Important**: If you remove the previous NVIDIA drivers, ensure you install the recommended versions listed below **before restarting your system**.

Once the drivers are installed correctly, you may safely restart your system.

### CUDA Toolkit and Driver

Follow these instructions to download and install the CUDA Toolkit.

From: <https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#network-repo-installation-for-ubuntu>

```bash
# From the Autoware repository root:
cuda_version=$(sed -n 's/^cuda_version: *"\(.*\)"/\1/p' ansible/roles/cuda/defaults/main.yaml)

os=ubuntu2204
arch_dir=$(
  case "$(dpkg --print-architecture)" in
    amd64) echo x86_64 ;;
    aarch64) echo arm64 ;;
    *) echo "$(dpkg --print-architecture)";;
  esac
)

wget "https://developer.download.nvidia.com/compute/cuda/repos/${os}/${arch_dir}/cuda-keyring_1.1-1_all.deb"
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
cuda_version_dashed=$(eval sed -e "s/[.]/-/g" <<< "${cuda_version}")
sudo apt-get -y install cuda-toolkit-${cuda_version_dashed}
```

```bash
# ⚠️ this is the minimum version
sudo apt-get install -y cuda-drivers-570

# ✅ latest version is OK
apt search '^nvidia-driver-[0-9]+'
sudo apt install nvidia-driver-580  # or whichever is latest
```

Perform the post installation actions:

```bash
# Taken from: https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#post-installation-actions
echo 'export PATH=/usr/local/cuda/bin${PATH:+:${PATH}}' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}' >> ~/.bashrc
```

### GPU Vendors

Register Vulkan, OpenGL, and OpenCL GPU vendors following the instructions below.

```bash
# Create Vulkan directory
sudo mkdir -p /etc/vulkan/icd.d
sudo chmod 0755 /etc/vulkan/icd.d

# Create OpenGL directory
sudo mkdir -p /etc/glvnd/egl_vendor.d
sudo chmod 0755 /etc/glvnd/egl_vendor.d

# Create OpenCL directory
sudo mkdir -p /etc/OpenCL/vendors
sudo chmod 0755 /etc/OpenCL/vendors

# Download and set permissions for Vulkan GPU vendors JSON
sudo wget https://gitlab.com/nvidia/container-images/vulkan/raw/dc389b0445c788901fda1d85be96fd1cb9410164/nvidia_icd.json -O /etc/vulkan/icd.d/nvidia_icd.json
sudo chmod 0644 /etc/vulkan/icd.d/nvidia_icd.json

# Download and set permissions for OpenGL GPU vendors JSON
sudo wget https://gitlab.com/nvidia/container-images/opengl/raw/5191cf205d3e4bb1150091f9464499b076104354/glvnd/runtime/10_nvidia.json -O /etc/glvnd/egl_vendor.d/10_nvidia.json
sudo chmod 0644 /etc/glvnd/egl_vendor.d/10_nvidia.json

# Register and set permissions for OpenCL GPU vendors
sudo touch /etc/OpenCL/vendors/nvidia.icd
echo "libnvidia-opencl.so.1" | sudo tee /etc/OpenCL/vendors/nvidia.icd > /dev/null
sudo chmod 0644 /etc/OpenCL/vendors/nvidia.icd
```

## Abbreviations, terms and symbols

| Term                                     | Meaning                                                                                                                    |
| ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| aarch64                                  | The 64-bit ARM processor architecture, used by ARM servers and NVIDIA Jetson boards                                        |
| amd64                                    | Debian and Ubuntu's name for the 64-bit Intel/AMD processor architecture (the same as `x86_64`)                            |
| apt                                      | Advanced Package Tool: Ubuntu's package manager, used to install, update and remove system software                        |
| apt-get                                  | The older, script-friendly command-line front end of apt; it does the same job as `apt`                                    |
| arm64                                    | Debian and Ubuntu's name for the 64-bit ARM processor architecture (the same as `aarch64`)                                 |
| `.bashrc`                                | A script in your home directory that the bash shell runs each time it starts; used here to set environment variables       |
| `chmod`                                  | A command that changes who may read, write or run a file                                                                   |
| CUDA                                     | Compute Unified Device Architecture: NVIDIA's toolkit for running general computation on its GPUs                          |
| `cuda-drivers`                           | NVIDIA's package that installs the GPU driver matching the CUDA repository                                                 |
| `cuda-keyring`                           | NVIDIA's package that installs the key apt uses to trust NVIDIA's repository                                               |
| CUDA Toolkit                             | The compiler, libraries and tools for writing and running CUDA programs                                                    |
| deb                                      | The package file format used by Debian and Ubuntu; also the keyword that marks a package source line in apt                |
| `defaults/main.yaml`                     | The file inside a role that holds the default values of its variables                                                      |
| distro                                   | Short for distribution: a particular release of Linux (such as Ubuntu 22.04) or of ROS 2 (such as humble)                  |
| dpkg                                     | The low-level Debian/Ubuntu tool that installs and queries `.deb` package files; apt uses it underneath                    |
| driver                                   | Software that lets the operating system use a piece of hardware, here the GPU                                              |
| EGL                                      | The interface between OpenGL and the system's windowing or display layer                                                   |
| `eval`                                   | A shell command that runs a string as a command                                                                            |
| glvnd                                    | GL Vendor-Neutral Dispatch: lets OpenGL programs find the right vendor's driver                                            |
| GPU                                      | Graphics Processing Unit: a processor built for parallel work, used here for graphics and for running neural networks      |
| humble                                   | ROS 2 Humble Hawksbill, the ROS 2 release paired with Ubuntu 22.04                                                         |
| ICD                                      | Installable Client Driver: a file telling the Vulkan or OpenCL loader which vendor driver to use                           |
| Inputs                                   | The role variables you can set to change what the role does                                                                |
| jazzy                                    | ROS 2 Jazzy Jalisco, the ROS 2 release paired with Ubuntu 24.04                                                            |
| JSON                                     | JavaScript Object Notation: a common text format for structured data                                                       |
| `LD_LIBRARY_PATH`                        | Environment variable listing extra folders where Linux looks for shared libraries when a program starts                    |
| NVIDIA                                   | The company that makes the GPUs and GPU software (CUDA, TensorRT, drivers) used by Autoware                                |
| `nvidia-open`                            | NVIDIA's driver package built on its open-source kernel modules                                                            |
| OpenCL                                   | Open Computing Language: a standard for general computation on GPUs and other processors                                   |
| OpenGL                                   | Open Graphics Library: a long-standing standard interface for 3D graphics                                                  |
| `PATH`                                   | The environment variable listing the folders the shell searches for programs                                               |
| post installation actions                | Steps NVIDIA asks you to do after installing, such as adding CUDA to `PATH`                                                |
| repo                                     | Short for repository: a server that apt downloads packages from                                                            |
| role                                     | A reusable unit of Ansible tasks that installs or configures one thing; each folder under `ansible/roles/` is a role       |
| sed                                      | Stream editor: a command that finds and replaces text in files or command output                                           |
| sudo                                     | A command that runs another command with administrator (root) rights, after asking for your password                       |
| `tee`                                    | A command that writes its input to a file (here with sudo, so it can write system files)                                   |
| Ubuntu                                   | The Linux distribution Autoware targets; versions are named year.month, such as 22.04 (April 2022)                         |
| `ubuntu2204`, `ubuntu2404`, `ubuntuXXXX` | The names NVIDIA uses for its repository for each Ubuntu version (2204 is 22.04)                                           |
| vendor                                   | The company whose driver handles a graphics or compute interface, here NVIDIA                                              |
| Vulkan                                   | A modern cross-platform interface for graphics and GPU computation                                                         |
| wget                                     | A command-line tool that downloads files from a web address                                                                |
| x86_64                                   | The 64-bit Intel/AMD processor architecture used by most desktop and laptop PCs                                            |
| `-e`                                     | For `ansible-playbook`: sets a variable for this run (short for `--extra-vars`). For `sed`: the edit expression to apply   |
| `…`                                      | Placeholder: replace with your own value                                                                                   |
| `12.x`                                   | Any 12-series version, such as 12.4 or 12.8                                                                                |
| 🛠️                                       | Tools: a section for advanced users                                                                                        |
| ⚠️                                       | Warning: be careful, or this is the minimum allowed                                                                        |
| `#`                                      | In a shell or config block, starts a comment that is not run                                                               |
| `$(...)`                                 | Command substitution: runs the command inside and puts its output in its place                                             |
| `-n`                                     | For `sed`: print only the lines the command asks for                                                                       |
| `${...}`                                 | Inserts the value of a shell variable, for example `${rosdistro}` becomes `humble`                                         |
| `-i`                                     | For `dpkg`: install the given package file                                                                                 |
| `<<<`                                    | Here-string: passes the text that follows as the command's input                                                           |
| `-y`                                     | Answers yes to every question so the command runs without stopping to ask                                                  |
| ✅                                       | Check mark: this is fine                                                                                                   |
| `[0-9]+`                                 | Regular-expression pattern for one or more digits                                                                          |
| `${PATH:+:${PATH}}`                      | Adds a colon and the old value only if the variable was already set                                                        |
| `>>`                                     | Appends a command's output to the end of a file                                                                            |
| `~`                                      | Shorthand for your home directory, for example `/home/<you>`                                                               |
| `-p`                                     | For `mkdir`: create the folder and any missing parent folders, with no error if it exists                                  |
| `0755`, `0644`                           | File permissions in number form: 0755 lets everyone read and enter, 0644 lets everyone read, and only the owner may change |
| `-O`                                     | For `wget`: save the download under the given file name                                                                    |
| `> /dev/null`                            | Throws away a command's output so it is not printed                                                                        |

Other project terms are defined in the [Glossary](../../../wiki/Glossary.md).
