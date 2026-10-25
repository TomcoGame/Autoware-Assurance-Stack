# geographiclib

## Inputs

None.

## Manual Installation

```bash
sudo apt update
sudo apt install -y geographiclib-tools

# Add EGM2008 geoid grid to geographiclib
sudo geographiclib-get-geoids egm2008-1
```

## Abbreviations, terms and symbols

| Term          | Meaning                                                                                                     |
| ------------- | ----------------------------------------------------------------------------------------------------------- |
| apt           | Advanced Package Tool: Ubuntu's package manager, used to install, update and remove system software         |
| EGM2008       | Earth Gravitational Model 2008: a model of Earth's gravity used to compute the geoid                        |
| `egm2008-1`   | The EGM2008 geoid data at a spacing of 1 arc-minute                                                         |
| GeographicLib | A library for converting between geographic coordinate systems; `geographiclib-tools` adds its commands     |
| geoid         | The shape sea level would take over the whole Earth; used to convert GPS heights to heights above sea level |
| geoid grid    | A table of geoid heights over the Earth that programs look up                                               |
| Inputs        | The role variables you can set to change what the role does                                                 |
| sudo          | A command that runs another command with administrator (root) rights, after asking for your password        |
| `-y`          | Answers yes to every question so the command runs without stopping to ask                                   |
| `#`           | In a shell or config block, starts a comment that is not run                                                |

Other project terms are defined in the [Glossary](../../../wiki/Glossary.md).
