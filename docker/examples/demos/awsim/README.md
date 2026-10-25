# awsim

Bridges autoware to the [AWSIM](https://github.com/tier4/AWSIM) Unity simulator over `network_mode: host` and launches `e2e_simulator.launch.xml`. AWSIM itself runs on the host (or elsewhere on the LAN); this container is the autoware side of the bridge.

## Prerequisites

- NVIDIA GPU with the NVIDIA Container Toolkit installed
- Shinjuku map extracted to `~/autoware_data/maps/Shinjuku-Map/map`
- Perception model data under `~/autoware_data/ml_models`
- AWSIM running on the host and reachable on the ROS 2 graph
- Docker Compose v2

## Run

```bash
xhost +local:docker

cd docker/examples/demos/awsim
HOST_UID=$(id -u) HOST_GID=$(id -g) docker compose run --rm awsim
```

When the launch exits the container drops into `bash` (from `exec bash` at the end of `command`) so you can inspect state. `Ctrl+D` exits and removes the container (`--rm`).

The compose file defaults `HOST_UID`/`HOST_GID` to `1000`; drop the prefix if your host UID/GID are 1000.

## Customizing

Edit the `command:` block in `docker-compose.yaml` to change launch arguments (vehicle model, sensor kit, map path). The service uses `universe-cuda-jazzy`; swap the `image:` tag to target a different ROS distro (e.g. `universe-cuda-humble`) or point at a locally built image.

`network_mode: host` is required so AWSIM's DDS traffic reaches the container; removing it will break the connection.

## Launch command reference

The image's entrypoint sources `/opt/autoware/setup.bash` (via `AUTOWARE_RUNTIME=1`), then the service launches:

```bash
ros2 launch autoware_launch e2e_simulator.launch.xml \
  vehicle_model:=sample_vehicle \
  sensor_model:=awsim_sensor_kit \
  map_path:=/home/aw/autoware_data/maps/Shinjuku-Map/map
```

`map_path` points inside the container; it maps to `~/autoware_data/maps/Shinjuku-Map/map` on the host via the `volumes:` mount.

## Abbreviations, terms and symbols

| Term                       | Meaning                                                                                                                         |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Autoware                   | The open-source self-driving software stack that these images package                                                           |
| `AUTOWARE_RUNTIME`         | Environment variable that tells the entrypoint to load the Autoware setup before running the command                            |
| AWSIM                      | An open-source Autoware simulator built on the Unity game engine, with realistic sensors and city maps                          |
| `bash`                     | The standard Linux command-line shell                                                                                           |
| bridge                     | The connection that carries ROS 2 messages between AWSIM and Autoware                                                           |
| `command:`                 | The part of the Compose file that sets what the container runs when it starts                                                   |
| container                  | A running, isolated instance of an image; it shares the host's operating system kernel but has its own files and processes      |
| Ctrl+D                     | Keyboard shortcut that ends the current shell, which here also exits the container                                              |
| DDS                        | Data Distribution Service: the publish-subscribe networking standard ROS 2 uses to pass messages between nodes                  |
| distro                     | ROS distribution: a named ROS 2 release, such as humble or jazzy                                                                |
| Docker Compose v2          | The current version of Docker Compose, run as `docker compose` (with a space) rather than the older `docker-compose`            |
| `e2e_simulator.launch.xml` | Autoware's end-to-end launch file: runs the full stack, from sensors to vehicle control, against a simulator                    |
| entrypoint                 | The script that runs first every time the container starts; here it sets up the `aw` user and the ROS environment               |
| GID                        | Group ID: the number Linux uses to identify a user group, which decides file permissions                                        |
| GPU                        | Graphics processing unit: the graphics card, which Autoware also uses for neural-network perception                             |
| host                       | The physical computer that runs Docker and the containers                                                                       |
| humble                     | ROS 2 Humble Hawksbill: the 2022 long-term-support ROS 2 release, for Ubuntu 22.04                                              |
| image                      | A packaged, read-only snapshot of an operating system plus installed software, from which containers are started                |
| jazzy                      | ROS 2 Jazzy Jalisco: the 2024 long-term-support ROS 2 release, for Ubuntu 24.04                                                 |
| LAN                        | Local area network: the computers on your own network                                                                           |
| launch argument            | A `name:=value` setting passed to `ros2 launch` to choose the map, vehicle, sensors and so on                                   |
| mount                      | Making a host folder or file visible inside the container, so data is shared and kept after the container is removed            |
| `network_mode: host`       | Compose setting that makes the container use the host's network directly, so ROS 2 traffic flows as if Autoware ran on the host |
| NVIDIA                     | Company that makes GPUs and the CUDA software, and the Jetson and DRIVE computers                                               |
| NVIDIA Container Toolkit   | NVIDIA software (`nvidia-container-toolkit`) that lets Docker containers use the host's NVIDIA GPU                              |
| perception                 | The part of Autoware that detects objects around the vehicle from sensor data, mostly with neural networks                      |
| `--rm`                     | Remove the container when it exits                                                                                              |
| ROS 2                      | Robot Operating System 2: the open-source framework Autoware is built on, which passes messages between programs called nodes   |
| ROS 2 graph                | All ROS 2 nodes that can see each other on the network                                                                          |
| `ros2 launch`              | ROS 2 command that starts many nodes at once from a launch file                                                                 |
| sensor kit                 | The set and placement of sensors (lidars, cameras and so on) that Autoware is configured for                                    |
| Shinjuku map               | The map of the Shinjuku area of Tokyo that AWSIM's demo uses                                                                    |
| tag                        | The name after the colon in an image name (for example `universe-jazzy`) that selects one variant or version                    |
| UID                        | User ID: the number Linux uses to identify a user, which decides who owns files                                                 |
| Unity                      | A game engine that AWSIM is built on                                                                                            |
| vehicle model              | The vehicle description (size, steering limits and so on) that Autoware is configured for                                       |
| `volumes:`                 | The part of the Compose file that lists host folders mounted into the container                                                 |
| `xhost +local:docker`      | Command that allows local containers to open windows on the host's display                                                      |
| `~`                        | Your home folder on the host, for example `/home/<you>`                                                                         |
| `$(...)`                   | In shell commands: run the command inside and use its output, for example `$(id -u)` gives your user ID                         |
| `\`                        | At the end of a command line: the command continues on the next line                                                            |
| `:=`                       | Sets a ROS 2 launch argument, as in `name:=value`                                                                               |

Other project terms are defined in the [Glossary](../../../../wiki/Glossary.md).
