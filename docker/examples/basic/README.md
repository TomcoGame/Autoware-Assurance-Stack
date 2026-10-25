# basic

Three flavors of "drop me into a shell" container. All three use the `universe-devel-*` images (build tooling plus `/opt/autoware` built from source), mount `~/autoware_data/maps` and `~/autoware_data/ml_models`, forward `$DISPLAY`, and differ only in how the GPU is exposed.

| Host GPU / driver            | Use          | How                                              |
| ---------------------------- | ------------ | ------------------------------------------------ |
| NVIDIA + proprietary driver  | `dev-nvidia` | `runtime: nvidia` injects proprietary GLX / CUDA |
| NVIDIA + Nouveau open driver | `dev-dri`    | `/dev/dri` passthrough with Mesa nouveau         |
| Intel / AMD                  | `dev-dri`    | `/dev/dri` passthrough with Mesa iris / radeonsi |
| No GPU / headless CI         | `dev-cpu`    | forces Mesa `llvmpipe` software rendering        |

`dev-nvidia` uses `universe-devel-cuda-jazzy`; the other two use `universe-devel-jazzy`.

## Prerequisites

- `~/autoware_data/maps` and `~/autoware_data/ml_models` on the host, which the `artifacts` and `demo_artifacts` ansible roles create

Compose does not create these. It stops with `bind source path does not exist` when one is missing, because a path that Compose creates belongs to root, and the unprivileged `aw` user in the container cannot write it.

On NVIDIA hosts running the proprietary driver, `dev-dri` silently falls back to `llvmpipe` (no `nvidia-drm` loader in Mesa) — use `dev-nvidia` instead. Software rendering is fine for text-heavy rviz but laggy on dense point clouds.

Verify you actually got hardware acceleration inside the container:

```bash
glxinfo -B | grep -E "OpenGL (vendor|renderer)"
```

You want to see your GPU (`NVIDIA Corporation` / `AMD Radeon...` / `Mesa Intel...`), not `llvmpipe`.

## Run

```bash
# Allow the container to connect to the host X server
xhost +local:docker

# Pick one
COMPOSE=docker/examples/basic/dev-cpu.compose.yaml
COMPOSE=docker/examples/basic/dev-dri.compose.yaml
COMPOSE=docker/examples/basic/dev-nvidia.compose.yaml

HOST_UID=$(id -u) HOST_GID=$(id -g) \
  docker compose -f "$COMPOSE" run --rm autoware
```

`HOST_UID` / `HOST_GID` are forwarded so the entrypoint can remap the in-container `aw` user to match your host UID/GID; without them, files created in mounted volumes would be owned by the wrong user. The compose files default both to `1000` — you can drop the prefix if your host UID/GID are 1000.

Inside the container, `/opt/autoware` holds the prebuilt install space. The devel images don't source it automatically — you do that yourself before running ROS 2 commands:

```bash
source /opt/autoware/setup.bash
ros2 doctor   # quick smoke test: RMW, topics, node discovery
```

See `demos/` for pre-configured launches (planning-simulator, awsim).

## Attaching a second terminal

`docker compose run` creates a one-off container that disappears when you exit. To open more shells in the same container, start it detached with `up` instead:

```bash
# Terminal 1 — start the container in the background
HOST_UID=$(id -u) HOST_GID=$(id -g) \
  docker compose -f "$COMPOSE" up -d

# Terminal 2, 3, ... — attach a new bash shell
docker compose -f "$COMPOSE" exec autoware /docker-entrypoint.sh bash

# Any terminal — tear it down when you're done
docker compose -f "$COMPOSE" down
```

Running `bash` through `/docker-entrypoint.sh` is what `docker compose up` does for you on the first shell. It drops to the `aw` user and sources `/opt/ros/$ROS_DISTRO/setup.bash` before handing you the prompt. Without it, `docker exec` lands you as `root` with no ROS environment.

## Abbreviations, terms and symbols

| Term                          | Meaning                                                                                                                          |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| AMD                           | Advanced Micro Devices: a maker of processors and Radeon graphics cards                                                          |
| ansible role                  | A reusable ansible script for one setup task, such as downloading maps and models                                                |
| `artifacts`, `demo_artifacts` | Ansible roles in this repository that download the maps and ML models Autoware needs                                             |
| `aw`                          | The ordinary (non-administrator) user account that runs Autoware inside the container                                            |
| `bash`                        | The standard Linux command-line shell                                                                                            |
| bind source path              | The host folder a container mount points at; Compose stops if it does not exist                                                  |
| CI                            | Continuous integration: automatic builds and tests that run on every change                                                      |
| Compose                       | Docker Compose: a tool that starts one or more containers from a YAML file that lists their settings                             |
| container                     | A running, isolated instance of an image; it shares the host's operating system kernel but has its own files and processes       |
| CUDA                          | Compute Unified Device Architecture: NVIDIA's platform for running general computations, such as neural networks, on the GPU     |
| detached                      | Running in the background, without holding your terminal (`up -d`)                                                               |
| `/dev/dri`                    | Direct Rendering Infrastructure: the Linux device files that give programs access to the GPU for drawing                         |
| devel                         | Development image: includes compilers, headers and build tools so you can build code, which makes it larger than a runtime image |
| `DISPLAY`                     | Environment variable that tells GUI programs which X11 screen to draw on                                                         |
| entrypoint                    | The script that runs first every time the container starts; here it sets up the `aw` user and the ROS environment                |
| GID                           | Group ID: the number Linux uses to identify a user group, which decides file permissions                                         |
| GLX                           | The link between OpenGL and the X11 display system                                                                               |
| `glxinfo`                     | Command that reports which OpenGL driver and GPU are in use                                                                      |
| GPU                           | Graphics processing unit: the graphics card, which Autoware also uses for neural-network perception                              |
| hardware acceleration         | Drawing graphics on the GPU rather than the CPU, which is much faster                                                            |
| headless                      | Without a monitor or display                                                                                                     |
| host                          | The physical computer that runs Docker and the containers                                                                        |
| install space                 | The folder (`/opt/autoware`) that holds the built Autoware programs, ready to run                                                |
| Intel                         | A maker of processors and the graphics built into them                                                                           |
| iris                          | Mesa's open-source driver for Intel graphics                                                                                     |
| jazzy                         | ROS 2 Jazzy Jalisco: the 2024 long-term-support ROS 2 release, for Ubuntu 24.04                                                  |
| llvmpipe                      | Mesa's software renderer: draws graphics on the CPU when no GPU acceleration is available, so it works everywhere but is slow    |
| Mesa                          | The open-source graphics library on Linux that provides OpenGL for Intel, AMD and Nouveau drivers, plus software rendering       |
| mount                         | Making a host folder or file visible inside the container, so data is shared and kept after the container is removed             |
| node discovery                | How ROS 2 programs (nodes) find each other automatically                                                                         |
| Nouveau                       | The open-source driver for NVIDIA graphics cards, part of Mesa                                                                   |
| NVIDIA                        | Company that makes GPUs and the CUDA software, and the Jetson and DRIVE computers                                                |
| `nvidia-drm`                  | Part of NVIDIA's proprietary driver; Mesa has no loader for it, so `dev-dri` cannot use it                                       |
| OpenGL                        | A standard programming interface for drawing 3D graphics                                                                         |
| passthrough                   | Giving the container direct access to a host device                                                                              |
| point cloud                   | A set of 3D points, usually from a lidar sensor; dense ones are heavy to draw                                                    |
| proprietary driver            | NVIDIA's own closed-source graphics driver, as opposed to the open-source Nouveau driver                                         |
| radeonsi                      | Mesa's open-source driver for AMD Radeon graphics                                                                                |
| RMW                           | ROS middleware: the layer in ROS 2 that selects which DDS implementation carries the messages                                    |
| root                          | The Linux administrator account, which can change any file                                                                       |
| ROS 2                         | Robot Operating System 2: the open-source framework Autoware is built on, which passes messages between programs called nodes    |
| `ros2 doctor`                 | ROS 2 command that checks the setup and reports problems                                                                         |
| `runtime: nvidia`             | Compose setting that starts the container with NVIDIA's container runtime so it can use the GPU                                  |
| rviz                          | RViz (`rviz2`): the ROS 3D visualisation tool that shows the map, vehicle, sensor data and plans                                 |
| shell                         | A command-line prompt where you type commands                                                                                    |
| smoke test                    | A quick check that the basics work before going further                                                                          |
| software rendering            | Drawing graphics on the CPU instead of the GPU                                                                                   |
| source                        | Shell command that loads a setup script into the current shell, here to make ROS 2 and Autoware commands available               |
| topic                         | A named channel in ROS 2 that nodes publish messages to and subscribe to                                                         |
| UID                           | User ID: the number Linux uses to identify a user, which decides who owns files                                                  |
| unprivileged                  | Without administrator rights                                                                                                     |
| volume                        | Storage attached to a container, either a mounted host folder or a Docker-managed named volume                                   |
| `xhost +local:docker`         | Command that allows local containers to open windows on the host's display                                                       |
| X server                      | The program on the host that draws GUI windows (X11)                                                                             |
| `~`                           | Your home folder on the host, for example `/home/<you>`                                                                          |
| `$`                           | In shell commands: reads an environment variable, for example `$DISPLAY`                                                         |
| `+`                           | With: for example NVIDIA hardware with the proprietary driver                                                                    |
| `\|`                          | In shell commands: send one command's output to the next command                                                                 |
| `...`                         | More text follows that varies by machine, for example the exact GPU name                                                         |
| `#`                           | In shell commands: starts a comment, which is not run                                                                            |
| `\`                           | At the end of a command line: the command continues on the next line                                                             |
| `$(...)`                      | In shell commands: run the command inside and use its output, for example `$(id -u)` gives your user ID                          |

Other project terms are defined in the [Glossary](../../../wiki/Glossary.md).
