# Examples

Docker Compose examples for running Autoware with the `docker` images.

## Basic

Minimal dev shells — `dev-cpu`, `dev-dri`, `dev-nvidia`. Pick the one matching your GPU. See [basic/README.md](basic/README.md).

## Demos

Pre-configured scenarios that launch autoware on container start.

- [planning-simulator/README.md](demos/planning-simulator/README.md)
- [awsim/README.md](demos/awsim/README.md)
- [scenario-simulator/README.md](demos/scenario-simulator/README.md)

## Abbreviations, terms and symbols

| Term               | Meaning                                                                                                                     |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| Autoware           | The open-source self-driving software stack that these images package                                                       |
| AWSIM              | An open-source Autoware simulator built on the Unity game engine, with realistic sensors and city maps                      |
| Compose            | Docker Compose: a tool that starts one or more containers from a YAML file that lists their settings                        |
| container          | A running, isolated instance of an image; it shares the host's operating system kernel but has its own files and processes  |
| demo               | A ready-made example that launches Autoware with a fixed setup                                                              |
| `dev-cpu`          | Dev shell that draws graphics in software, for hosts with no usable GPU                                                     |
| `dev-dri`          | Dev shell that uses the host GPU through `/dev/dri`, for Intel, AMD and open-source NVIDIA drivers                          |
| `dev-nvidia`       | Dev shell that uses an NVIDIA GPU with NVIDIA's own driver                                                                  |
| dev shell          | A container that gives you a command-line prompt with the Autoware development tools                                        |
| Docker             | Software that builds images and runs them as isolated containers                                                            |
| GPU                | Graphics processing unit: the graphics card, which Autoware also uses for neural-network perception                         |
| image              | A packaged, read-only snapshot of an operating system plus installed software, from which containers are started            |
| planning simulator | Autoware's lightweight simulator that tests planning and control on a map with simulated vehicle motion and no real sensors |
| scenario simulator | `scenario_simulator_v2`: a tool that runs scripted traffic scenarios against Autoware and checks the result                 |

Other project terms are defined in the [Glossary](../../wiki/Glossary.md).
