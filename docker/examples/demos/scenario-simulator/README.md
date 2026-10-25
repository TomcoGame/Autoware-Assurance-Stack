# scenario-simulator

Runs a `scenario_simulator_v2` scenario against a live Autoware planning stack. Two services are defined in `docker-compose.yaml`:

- `autoware` — the `ghcr.io/autowarefoundation/autoware:universe-humble` image launching `planning_simulator.launch.xml` with `scenario_simulation:=true` so it pairs with an external scenario runner.
- `scenario-simulator` — the `scenario_test_runner` from `ghcr.io/tier4/scenario_simulator_v2:humble-25.0.17-runtime`, with `launch_autoware:=false` so it only drives the simulator engine.

Both services use `network_mode: host` and share a generated `cyclonedds.xml` (via the `cyclonedds-config` named volume) so ROS 2 discovery works between them. The `scenario-simulator` service waits for the `autoware` service's healthcheck (`/api/operation_mode/state` topic) to pass before launching.

## Prerequisites

- Docker Compose v2
- Sample map extracted to `~/autoware_data/maps/sample-map-planning` (the layout produced by the `demo_artifacts` ansible role)
- Sample scenarios cloned to `~/autoware_data/scenarios`

[Download the sample map](https://autowarefoundation.github.io/autoware-documentation/main/demos/planning-sim/#download-the-sample-map) and unpack it to `~/autoware_data/maps/sample-map-planning`, or run the `demo_artifacts` ansible role which places it there automatically.

Clone the sample scenarios repository:

```bash
mkdir -p ~/autoware_data/scenarios/
cd ~/autoware_data/scenarios/
git clone https://github.com/autowarefoundation/autoware_sample_scenarios.git
```

## Run

```bash
xhost +local:docker
cd docker/examples/demos/scenario-simulator
HOST_UID=$(id -u) HOST_GID=$(id -g) docker compose up
```

`docker compose up` starts both services; the `scenario-simulator` service blocks on the `autoware` healthcheck and then launches the scenario. Logs are interleaved.

To run them in separate terminals (each gets its own stdout/stdin):

```bash
xhost +local:docker

# terminal 1 — Autoware planning stack (rviz needs X11)
cd docker/examples/demos/scenario-simulator
HOST_UID=$(id -u) HOST_GID=$(id -g) docker compose run --rm autoware

# terminal 2 — scenario runner
# --no-deps stops compose from starting a second `autoware` container
# (scenario-simulator declares depends_on: autoware); wait until the
# container in terminal 1 is healthy before running this.
cd docker/examples/demos/scenario-simulator
docker compose run --rm --no-deps scenario-simulator
```

`HOST_UID`/`HOST_GID` default to `1000`; drop the prefix if your host UID/GID are 1000.

## After the launch exits

Each `command:` block ends with `exec bash`, so when `ros2 launch` exits the container drops into an interactive shell instead of disappearing. `Ctrl+D` exits and removes the container (`--rm`).

## Customizing

Edit the `command:` block in `docker-compose.yaml` to change launch arguments — for example, point `scenario:=` at a different YAML under `~/autoware_data/scenarios`, or flip `launch_rviz:=true` on the scenario-simulator side to watch the run.

## Launch command reference

`autoware`:

```bash
ros2 launch autoware_launch planning_simulator.launch.xml \
  map_path:=/home/aw/autoware_data/maps/sample-map-planning \
  vehicle_model:=sample_vehicle \
  sensor_model:=sample_sensor_kit \
  scenario_simulation:=true
```

`scenario-simulator`:

```bash
ros2 launch scenario_test_runner scenario_test_runner.launch.py \
  architecture_type:=awf/universe/20250130 \
  record:=false \
  scenario:=/home/aw/autoware_data/scenarios/autoware_sample_scenarios/sample-scenario.yaml \
  use_custom_centerline:=true \
  launch_rviz:=false \
  launch_autoware:=false
```

The `cyclonedds-config` named volume is populated by the `autoware` service on startup (a copy of `/home/aw/cyclonedds.xml`) and mounted into the scenario-simulator at `/shared-config`, which `CYCLONEDDS_URI` points at.

## Abbreviations, terms and symbols

| Term                            | Meaning                                                                                                                         |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| ansible role                    | A reusable ansible script for one setup task, such as downloading maps and models                                               |
| `/api/operation_mode/state`     | The Autoware interface that reports the current operation mode, used here to tell when Autoware is ready                        |
| `architecture_type`             | Launch argument telling the scenario runner which Autoware version's interfaces to expect; `awf` is the Autoware Foundation     |
| Autoware                        | The open-source self-driving software stack that these images package                                                           |
| `bash`                          | The standard Linux command-line shell                                                                                           |
| centerline                      | The line along the middle of a lane that the vehicle's planned path follows                                                     |
| `command:`                      | The part of the Compose file that sets what the container runs when it starts                                                   |
| container                       | A running, isolated instance of an image; it shares the host's operating system kernel but has its own files and processes      |
| Ctrl+D                          | Keyboard shortcut that ends the current shell, which here also exits the container                                              |
| CycloneDDS                      | Eclipse Cyclone DDS: the DDS implementation Autoware uses to carry ROS 2 messages                                               |
| `CYCLONEDDS_URI`                | Environment variable that tells CycloneDDS where its configuration file is                                                      |
| `cyclonedds.xml`                | The CycloneDDS configuration file, which sets network interfaces and discovery                                                  |
| `demo_artifacts`                | Ansible role in this repository that downloads the demo maps and models                                                         |
| `depends_on`                    | Compose setting that starts one service only after another                                                                      |
| Docker Compose v2               | The current version of Docker Compose, run as `docker compose` (with a space) rather than the older `docker-compose`            |
| GHCR                            | GitHub Container Registry (`ghcr.io`): GitHub's service for storing and downloading images                                      |
| GID                             | Group ID: the number Linux uses to identify a user group, which decides file permissions                                        |
| git clone                       | Command that downloads a copy of a Git repository                                                                               |
| healthcheck                     | A command Compose runs repeatedly to decide whether a container is ready; here it checks that Autoware is up                    |
| host                            | The physical computer that runs Docker and the containers                                                                       |
| humble                          | ROS 2 Humble Hawksbill: the 2022 long-term-support ROS 2 release, for Ubuntu 22.04                                              |
| image                           | A packaged, read-only snapshot of an operating system plus installed software, from which containers are started                |
| interleaved                     | Mixed together line by line in one output                                                                                       |
| launch argument                 | A `name:=value` setting passed to `ros2 launch` to choose the map, vehicle, sensors and so on                                   |
| named volume                    | Storage that Docker manages and that several containers can share                                                               |
| `network_mode: host`            | Compose setting that makes the container use the host's network directly, so ROS 2 traffic flows as if Autoware ran on the host |
| `--no-deps`                     | Start only the named service, not the services it depends on                                                                    |
| `planning_simulator.launch.xml` | Autoware's launch file for the planning simulator                                                                               |
| planning stack                  | The Autoware parts that plan the vehicle's path and speed                                                                       |
| `--rm`                          | Remove the container when it exits                                                                                              |
| ROS 2                           | Robot Operating System 2: the open-source framework Autoware is built on, which passes messages between programs called nodes   |
| ROS 2 discovery                 | How ROS 2 nodes find each other automatically over the network                                                                  |
| `ros2 launch`                   | ROS 2 command that starts many nodes at once from a launch file                                                                 |
| `-runtime` (tag)                | A runtime image: contains only what is needed to run the software                                                               |
| rviz                            | RViz (`rviz2`): the ROS 3D visualisation tool that shows the map, vehicle, sensor data and plans                                |
| sample map                      | Small example map provided by Autoware for the planning simulator demo                                                          |
| scenario                        | A scripted traffic situation, written in a YAML file, with a pass or fail result                                                |
| `scenario_simulator_v2`         | Open-source tool from TIER IV that runs scenarios against Autoware and checks the result                                        |
| `scenario_test_runner`          | The `scenario_simulator_v2` program that loads a scenario and runs it                                                           |
| service                         | One container definition in a Compose file                                                                                      |
| simulator engine                | The part of the scenario simulator that moves the other traffic and the simulated world                                         |
| stdin                           | Standard input: the keyboard input a program reads                                                                              |
| stdout                          | Standard output: where a program prints its text                                                                                |
| tag                             | The name after the colon in an image name (for example `universe-jazzy`) that selects one variant or version                    |
| topic                           | A named channel in ROS 2 that nodes publish messages to and subscribe to                                                        |
| UID                             | User ID: the number Linux uses to identify a user, which decides who owns files                                                 |
| URI                             | Uniform resource identifier: a string that names a file or resource                                                             |
| X11                             | The X Window System: the Linux display system that draws GUI windows; containers send their windows to the host's X server      |
| `xhost +local:docker`           | Command that allows local containers to open windows on the host's display                                                      |
| YAML                            | A plain-text format for configuration files (`.yaml`)                                                                           |
| `:=`                            | Sets a ROS 2 launch argument, as in `name:=value`                                                                               |
| `~`                             | Your home folder on the host, for example `/home/<you>`                                                                         |
| `$(...)`                        | In shell commands: run the command inside and use its output, for example `$(id -u)` gives your user ID                         |
| `#`                             | In shell commands: starts a comment, which is not run                                                                           |
| `\`                             | At the end of a command line: the command continues on the next line                                                            |

Other project terms are defined in the [Glossary](../../../../wiki/Glossary.md).
