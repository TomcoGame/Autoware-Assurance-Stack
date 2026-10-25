# planning-simulator

Launches the planning simulator with the sample map, vehicle, and sensor kit using the `universe-jazzy` image. The `docker-compose.yaml` here runs the full launch command automatically on container start, then drops to `bash` so you can inspect state after the sim exits.

Planning sim itself doesn't need a GPU — perception is dummy. The only reason to use GPU passthrough here is to get hardware-accelerated rviz rendering. See the NVIDIA section below.

## Prerequisites

- Sample map extracted to `~/autoware_data/maps/sample-map-planning` (the layout produced by the `demo_artifacts` ansible role)
- Perception model data under `~/autoware_data/ml_models` (mounted but not used by this demo)
- Docker Compose v2

[Download the sample map](https://autowarefoundation.github.io/autoware-documentation/main/demos/planning-sim/#download-the-sample-map) and unpack it to `~/autoware_data/maps/sample-map-planning` before running, or run the `demo_artifacts` ansible role which places it there automatically.

## Run (no GPU, software rendering)

Works on any host. rviz will use Mesa's `llvmpipe` software rasterizer — fine for light views, laggy on dense point clouds.

```bash
xhost +local:docker

cd docker/examples/demos/planning-simulator
HOST_UID=$(id -u) HOST_GID=$(id -g) docker compose run --rm planning-simulator
```

## Run (Intel / AMD hosts, hardware accel)

Merge the `docker-compose.dri.yaml` overlay to pass `/dev/dri` into the container. Works with Mesa's open drivers (iris, radeonsi, nouveau). Silently falls back to `llvmpipe` on NVIDIA + proprietary driver, so use the NVIDIA overlay there instead.

```bash
xhost +local:docker

cd docker/examples/demos/planning-simulator
HOST_UID=$(id -u) HOST_GID=$(id -g) \
  docker compose -f docker-compose.yaml -f docker-compose.dri.yaml \
  run --rm planning-simulator
```

## Run (NVIDIA hosts, hardware accel)

Merge the `docker-compose.nvidia.yaml` overlay to add `runtime: nvidia`, NVIDIA env, and the `deploy.devices` block. Requires the NVIDIA proprietary driver and `nvidia-container-toolkit`.

```bash
xhost +local:docker

cd docker/examples/demos/planning-simulator
HOST_UID=$(id -u) HOST_GID=$(id -g) \
  docker compose -f docker-compose.yaml -f docker-compose.nvidia.yaml \
  run --rm planning-simulator
```

## After the launch exits

The `command:` block ends with `exec bash`, so when `ros2 launch` exits the container drops into an interactive shell instead of disappearing. `Ctrl+D` exits and removes the container (`--rm`).

The compose file defaults `HOST_UID`/`HOST_GID` to `1000`; drop the prefix if your host UID/GID are 1000.

## Customizing

Edit the `command:` block in `docker-compose.yaml` to change launch arguments (different map, vehicle, sensor kit). Swap the `image:` tag to target a different ROS distro (e.g. `universe-humble`).

To enable ROS 2 discovery with other hosts on the network, add `network_mode: host` to the service.

## Launch command reference

```bash
ros2 launch autoware_launch planning_simulator.launch.xml \
  map_path:=/home/aw/autoware_data/maps/sample-map-planning \
  vehicle_model:=sample_vehicle \
  sensor_model:=sample_sensor_kit
```

`map_path` points inside the container; it maps to `~/autoware_data/maps/sample-map-planning` on the host via the `volumes:` mount.

## Abbreviations, terms and symbols

| Term                     | Meaning                                                                                                                         |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| AMD                      | Advanced Micro Devices: a maker of processors and Radeon graphics cards                                                         |
| ansible role             | A reusable ansible script for one setup task, such as downloading maps and models                                               |
| `bash`                   | The standard Linux command-line shell                                                                                           |
| `command:`               | The part of the Compose file that sets what the container runs when it starts                                                   |
| container                | A running, isolated instance of an image; it shares the host's operating system kernel but has its own files and processes      |
| Ctrl+D                   | Keyboard shortcut that ends the current shell, which here also exits the container                                              |
| `demo_artifacts`         | Ansible role in this repository that downloads the demo maps and models                                                         |
| `deploy.devices`         | Compose setting that reserves GPU devices for the container                                                                     |
| `/dev/dri`               | Direct Rendering Infrastructure: the Linux device files that give programs access to the GPU for drawing                        |
| distro                   | ROS distribution: a named ROS 2 release, such as humble or jazzy                                                                |
| Docker Compose v2        | The current version of Docker Compose, run as `docker compose` (with a space) rather than the older `docker-compose`            |
| dummy perception         | Simulated object detection, so no sensors or neural networks run                                                                |
| env                      | Environment variables: named settings passed to the programs in the container                                                   |
| GID                      | Group ID: the number Linux uses to identify a user group, which decides file permissions                                        |
| GPU                      | Graphics processing unit: the graphics card, which Autoware also uses for neural-network perception                             |
| GPU passthrough          | Giving the container direct access to the host GPU                                                                              |
| hardware accel           | Hardware acceleration: drawing graphics on the GPU rather than the CPU, which is much faster                                    |
| host                     | The physical computer that runs Docker and the containers                                                                       |
| humble                   | ROS 2 Humble Hawksbill: the 2022 long-term-support ROS 2 release, for Ubuntu 22.04                                              |
| image                    | A packaged, read-only snapshot of an operating system plus installed software, from which containers are started                |
| Intel                    | A maker of processors and the graphics built into them                                                                          |
| iris                     | Mesa's open-source driver for Intel graphics                                                                                    |
| jazzy                    | ROS 2 Jazzy Jalisco: the 2024 long-term-support ROS 2 release, for Ubuntu 24.04                                                 |
| launch argument          | A `name:=value` setting passed to `ros2 launch` to choose the map, vehicle, sensors and so on                                   |
| llvmpipe                 | Mesa's software renderer: draws graphics on the CPU when no GPU acceleration is available, so it works everywhere but is slow   |
| Mesa                     | The open-source graphics library on Linux that provides OpenGL for Intel, AMD and Nouveau drivers, plus software rendering      |
| mount                    | Making a host folder or file visible inside the container, so data is shared and kept after the container is removed            |
| `network_mode: host`     | Compose setting that makes the container use the host's network directly, so ROS 2 traffic flows as if Autoware ran on the host |
| nouveau                  | The open-source driver for NVIDIA graphics cards, part of Mesa                                                                  |
| NVIDIA                   | Company that makes GPUs and the CUDA software, and the Jetson and DRIVE computers                                               |
| NVIDIA Container Toolkit | NVIDIA software (`nvidia-container-toolkit`) that lets Docker containers use the host's NVIDIA GPU                              |
| overlay                  | A second Compose file merged on top of the first (with another `-f`) to add or change settings                                  |
| perception               | The part of Autoware that detects objects around the vehicle from sensor data, mostly with neural networks                      |
| planning simulator       | Autoware's lightweight simulator that tests planning and control on a map with simulated vehicle motion and no real sensors     |
| point cloud              | A set of 3D points, usually from a lidar sensor; dense ones are heavy to draw                                                   |
| proprietary driver       | NVIDIA's own closed-source graphics driver, as opposed to the open-source Nouveau driver                                        |
| radeonsi                 | Mesa's open-source driver for AMD Radeon graphics                                                                               |
| rasterizer               | The part of a graphics system that turns shapes into screen pixels                                                              |
| `--rm`                   | Remove the container when it exits                                                                                              |
| ROS 2                    | Robot Operating System 2: the open-source framework Autoware is built on, which passes messages between programs called nodes   |
| ROS 2 discovery          | How ROS 2 nodes find each other automatically over the network                                                                  |
| `ros2 launch`            | ROS 2 command that starts many nodes at once from a launch file                                                                 |
| `runtime: nvidia`        | Compose setting that starts the container with NVIDIA's container runtime so it can use the GPU                                 |
| rviz                     | RViz (`rviz2`): the ROS 3D visualisation tool that shows the map, vehicle, sensor data and plans                                |
| sample map               | Small example map provided by Autoware for the planning simulator demo                                                          |
| sensor kit               | The set and placement of sensors (lidars, cameras and so on) that Autoware is configured for                                    |
| sim                      | Simulator                                                                                                                       |
| software rendering       | Drawing graphics on the CPU instead of the GPU                                                                                  |
| tag                      | The name after the colon in an image name (for example `universe-jazzy`) that selects one variant or version                    |
| UID                      | User ID: the number Linux uses to identify a user, which decides who owns files                                                 |
| vehicle model            | The vehicle description (size, steering limits and so on) that Autoware is configured for                                       |
| `volumes:`               | The part of the Compose file that lists host folders mounted into the container                                                 |
| `xhost +local:docker`    | Command that allows local containers to open windows on the host's display                                                      |
| `~`                      | Your home folder on the host, for example `/home/<you>`                                                                         |
| `$(...)`                 | In shell commands: run the command inside and use its output, for example `$(id -u)` gives your user ID                         |
| `\`                      | At the end of a command line: the command continues on the next line                                                            |
| `:=`                     | Sets a ROS 2 launch argument, as in `name:=value`                                                                               |

Other project terms are defined in the [Glossary](../../../../wiki/Glossary.md).
