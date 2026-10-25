# Role: huggingface_cli

This role installs the Hugging Face CLI (`hf`) to download model artifacts from the Hugging Face Hub.

## Inputs

None.

## Manual Installation

```bash
pipx install --force "huggingface_hub==1.*"
```

## Abbreviations, terms and symbols

| Term                     | Meaning                                                                                                              |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------- |
| artifacts                | Here, files such as trained models that Autoware downloads                                                           |
| CLI                      | Command-Line Interface: a program you control by typing commands                                                     |
| `hf`                     | The command name of the Hugging Face CLI                                                                             |
| Hugging Face             | A website that hosts machine learning models and datasets for download                                               |
| `huggingface_hub`        | The Python package that provides the `hf` command                                                                    |
| Hugging Face Hub         | The Hugging Face service that stores models and datasets                                                             |
| Inputs                   | The role variables you can set to change what the role does                                                          |
| model                    | A trained neural network saved as files                                                                              |
| pipx                     | A tool that installs Python command-line applications, each in its own isolated environment                          |
| role                     | A reusable unit of Ansible tasks that installs or configures one thing; each folder under `ansible/roles/` is a role |
| `--force`                | Reinstall even if the package is already installed                                                                   |
| `"huggingface_hub==1.*"` | Version notation: `==` means exactly this version and `1.*` means any 1.x release                                    |

Other project terms are defined in the [Glossary](../../../wiki/Glossary.md).
