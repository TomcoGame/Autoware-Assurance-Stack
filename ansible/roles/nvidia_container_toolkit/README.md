# nvidia_container_toolkit

This role installs [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-container-toolkit) following the [installation guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).

## Inputs

None.

## Manual Installation (Recommended)

> ℹ️ The steps below may differ from the role implementation.  
> They reflect the **most up-to-date and preferred procedure** for manual installation.  
> The role will be updated to align with these steps.

<!-- cspell:ignore Disp, Uncorr -->

```bash
# Install the prerequisites for the instructions below:
sudo apt-get update && sudo apt-get install -y --no-install-recommends \
   curl \
   gnupg2

# Configure the production repository:
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Update the packages list from the repository:
sudo apt-get update

# Install NVIDIA Container Toolkit
sudo apt-get install -y nvidia-container-toolkit

# Add NVIDIA runtime support to docker engine
sudo nvidia-ctk runtime configure --runtime=docker

# Restart docker daemon
sudo systemctl restart docker

# At this point, a working setup can be tested by running a base CUDA container:
sudo docker run --rm --gpus all nvcr.io/nvidia/cuda:12.8.1-runtime-ubuntu24.04 nvidia-smi

# ==========
# == CUDA ==
# ==========
#
# CUDA Version 12.8.1
#
# Container image Copyright (c) 2016-2023, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
#
# This container image and its contents are governed by the NVIDIA Deep Learning Container License.
# By pulling and using the container, you accept the terms and conditions of this license:
# https://developer.nvidia.com/ngc/nvidia-deep-learning-container-license
#
# A copy of this license is made available in this container at /NGC-DL-CONTAINER-LICENSE for your convenience.
#
# Thu Jan 15 19:48:46 2026
# +-----------------------------------------------------------------------------------------+
# | NVIDIA-SMI 580.126.09             Driver Version: 580.126.09     CUDA Version: 13.0     |
# +-----------------------------------------+------------------------+----------------------+
# | GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
# | Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
# |                                         |                        |               MIG M. |
# |=========================================+========================+======================|
# |   0  NVIDIA GeForce RTX 3090        On  |   00000000:2B:00.0  On |                  N/A |
# |  0%   52C    P8             41W /  350W |     369MiB /  24576MiB |     31%      Default |
# |                                         |                        |                  N/A |
# +-----------------------------------------+------------------------+----------------------+
#
# +-----------------------------------------------------------------------------------------+
# | Processes:                                                                              |
# |  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
# |        ID   ID                                                               Usage      |
# |=========================================================================================|
# |  No running processes found                                                             |
# +-----------------------------------------------------------------------------------------+
```

## Abbreviations, terms and symbols

| Term                          | Meaning                                                                                                               |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| apt-get                       | The older, script-friendly command-line front end of apt; it does the same job as `apt`                               |
| Bus-Id                        | The address of the GPU on the computer's PCI bus                                                                      |
| C                             | Degrees Celsius, in the GPU temperature column                                                                        |
| container                     | An isolated environment, started from an image, with its own files and libraries                                      |
| Container Toolkit             | NVIDIA's software that lets Docker containers use the host's NVIDIA GPUs                                              |
| cspell                        | The spell checker this project runs; the hidden comment tells it to accept the listed words                           |
| CUDA                          | Compute Unified Device Architecture: NVIDIA's toolkit for running general computation on its GPUs                     |
| curl                          | A command-line tool that downloads data from a web address                                                            |
| daemon                        | A program that runs in the background as a service; here the Docker service                                           |
| `--dearmor`                   | For `gpg`: convert a key from text form to the binary form apt expects                                                |
| Disp.A                        | Display Active: whether a display is using the GPU                                                                    |
| Docker                        | A tool that runs software in containers, isolated environments that carry their own files and libraries               |
| ECC                           | Error-Correcting Code memory; the column counts memory errors that could not be corrected                             |
| GeForce RTX 3090              | An NVIDIA graphics card; the output shown is an example from one                                                      |
| GI, CI                        | GPU Instance and Compute Instance: the ID columns used when a GPU is split with MIG                                   |
| gnupg2, gpg                   | GNU Privacy Guard: the tool that handles the keys apt uses to trust a repository                                      |
| GPU                           | Graphics Processing Unit: a processor built for parallel work, used here for graphics and for running neural networks |
| GPU-Util                      | How busy the GPU is, as a percentage                                                                                  |
| image                         | A packaged set of files and settings from which containers are started                                                |
| Inputs                        | The role variables you can set to change what the role does                                                           |
| keyring                       | A file holding the keys apt uses to trust a repository                                                                |
| MiB                           | Mebibyte: 1,048,576 bytes                                                                                             |
| MIG                           | Multi-Instance GPU: splitting one GPU into several isolated parts                                                     |
| N/A                           | Not applicable or not available                                                                                       |
| NGC                           | NVIDIA GPU Cloud: NVIDIA's catalogue of containers and models                                                         |
| `nvcr.io`                     | NVIDIA's container image registry, where its images are downloaded from                                               |
| NVIDIA                        | The company that makes the GPUs and GPU software (CUDA, TensorRT, drivers) used by Autoware                           |
| `nvidia-ctk`                  | The command-line tool of the NVIDIA Container Toolkit                                                                 |
| `nvidia-smi`                  | NVIDIA System Management Interface: a command that shows the GPUs, the driver and what is running                     |
| Perf                          | Performance state, from P0 (fastest) to P12 (lowest power); P8 is a low-power idle state                              |
| Persistence-M                 | Persistence mode: keeps the driver loaded even when no program uses the GPU                                           |
| PID                           | Process ID: the number Linux gives each running program                                                               |
| production repository         | NVIDIA's repository of stable releases, as opposed to test releases                                                   |
| Pwr:Usage/Cap                 | Power the GPU draws now and its power limit, in watts (W)                                                             |
| role                          | A reusable unit of Ansible tasks that installs or configures one thing; each folder under `ansible/roles/` is a role  |
| runtime                       | The component that starts containers; NVIDIA's adds GPU access                                                        |
| sed                           | Stream editor: a command that finds and replaces text in files or command output                                      |
| sudo                          | A command that runs another command with administrator (root) rights, after asking for your password                  |
| `systemctl`                   | The command that starts, stops and restarts system services                                                           |
| Volatile                      | Counted since the last reboot                                                                                         |
| ℹ️                            | Information: a note to read before continuing                                                                         |
| `#`                           | In a shell or config block, starts a comment that is not run                                                          |
| `&&`                          | Runs the next command only if the previous one succeeded                                                              |
| `-y`                          | Answers yes to every question so the command runs without stopping to ask                                             |
| `--no-install-recommends`     | For `apt-get`: install only the required packages, not the suggested extras                                           |
| `\`                           | At the end of a line, continues the command on the next line                                                          |
| `-fsSL`, `-s -L`              | For `curl`: fail on errors, stay quiet except for errors, and follow redirects                                        |
| `\|`                          | Pipe: sends the output of one command into the next one                                                               |
| `-o`                          | Save the output to the given file                                                                                     |
| `s#...#...#g`                 | A `sed` replace command; `#` separates the text to find from its replacement, and `g` replaces every match            |
| `--rm`                        | For `docker run`: delete the container when it exits                                                                  |
| `--gpus all`                  | For `docker run`: give the container access to every GPU                                                              |
| `:12.8.1-runtime-ubuntu24.04` | Image tag: CUDA 12.8.1, runtime-only variant, based on Ubuntu 24.04                                                   |

Other project terms are defined in the [Glossary](../../../wiki/Glossary.md).
