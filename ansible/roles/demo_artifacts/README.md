# Autoware demo artifacts

Downloads sample maps and rosbag recordings used by the Autoware demos:

- [Planning simulation](https://autowarefoundation.github.io/autoware-documentation/main/demos/planning-sim/) — uses `sample-map-planning`
- [Rosbag replay simulation](https://autowarefoundation.github.io/autoware-documentation/main/demos/rosbag-replay-simulation/) — uses `sample-map-rosbag` and `sample-rosbag`

The artifacts are hosted on the `autoware-files` S3 bucket.

## Layout

After running the role, the following layout is created under `demo_artifacts__autoware_data_dir` (default `~/autoware_data`):

```console
~/autoware_data
├── maps
│   ├── sample-map-planning/
│   ├── sample-map-planning.zip
│   ├── sample-map-rosbag/
│   └── sample-map-rosbag.zip
└── recordings
    └── bags
        ├── sample-rosbag/
        └── sample-rosbag.zip
```

## Run

```bash
ansible-galaxy collection install -f -r "ansible-galaxy-requirements.yaml"
ansible-playbook autoware.dev_env.install_dev_env --tags demo_artifacts --ask-become-pass
```

To change the install location:

```bash
ansible-playbook autoware.dev_env.install_dev_env --tags demo_artifacts \
  -e "demo_artifacts__autoware_data_dir=$HOME/autoware_data" --ask-become-pass
```

## Abbreviations, terms and symbols

| Term                     | Meaning                                                                                                              |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------- |
| ansible-galaxy           | Ansible's command for installing collections and roles that a project depends on                                     |
| ansible-playbook         | Ansible's command that runs a playbook on the machine                                                                |
| artifacts                | Here, the sample maps and recordings the demos need                                                                  |
| Autoware                 | An open-source software stack for self-driving vehicles; this repository sets up its development environment         |
| bags                     | Recorded data files made with rosbag                                                                                 |
| bucket                   | A named storage container in Amazon S3                                                                               |
| demo                     | A guided example run that shows Autoware working                                                                     |
| map                      | Data describing the roads of a test area, which Autoware needs to drive there                                        |
| Planning simulation      | An Autoware demo that simulates the vehicle driving on a map, without real sensors                                   |
| role                     | A reusable unit of Ansible tasks that installs or configures one thing; each folder under `ansible/roles/` is a role |
| rosbag                   | The ROS tool and file format for recording and replaying the messages programs send                                  |
| Rosbag replay simulation | An Autoware demo that plays recorded sensor data back through Autoware                                               |
| S3                       | Amazon Simple Storage Service: Amazon's cloud file storage                                                           |
| zip                      | A compressed archive file; the role unpacks it next to the archive                                                   |
| `__`                     | In a variable name, separates the role name from the variable's own name                                             |
| `~`                      | Shorthand for your home directory, for example `/home/<you>`                                                         |
| `├──`, `└──`             | Tree drawing: shows the files and folders inside the folder above                                                    |
| `-f`                     | For `ansible-galaxy`: reinstall even if already installed (force)                                                    |
| `-r`                     | For `ansible-galaxy`: read the list of things to install from the named requirements file                            |
| `--tags`                 | For `ansible-playbook`: run only the roles and tasks carrying the given tag                                          |
| `--ask-become-pass`      | For `ansible-playbook`: asks for your sudo password once, so steps that need administrator rights can run            |
| `\`                      | At the end of a line, continues the command on the next line                                                         |
| `-e`                     | For `ansible-playbook`: sets a variable for this run, overriding its default (short for `--extra-vars`)              |
| `$HOME`                  | The environment variable holding the path of your home directory                                                     |

Other project terms are defined in the [Glossary](../../../wiki/Glossary.md).
