# Where is the source code?

Autoware uses **multiple Git repositories** managed through a meta-repository approach.
The `autoware` repository itself **does not contain the full source code**. Instead, it references many separately maintained repositories.

To manage these repositories, Autoware uses **[vcs2l](https://github.com/ros-infrastructure/vcs2l)** (`vcs`), which allows you to clone and keep multiple repositories in sync using manifest files under [repositories](../repositories) folder.

## Repository structure

- [`repositories/autoware.repos`](../repositories/autoware.repos) ➡️ The manifest file that lists essential Autoware repositories and their versions
- `src/` (here) ➡️ The directory where all Autoware source repositories will be cloned

⭐ Check the [**🔗 Repository structure and versioning documentation**](https://autowarefoundation.github.io/autoware-documentation/main/design/repository-structure/) for more details.

## Cloning the essential Autoware source code

⭐ Check the [**🔗‍ Installation guide**](https://autowarefoundation.github.io/autoware-documentation/main/installation/) for detailed setup instructions.

Here is a brief summary of the steps:

```bash
# Navigate to the repository root
cd autoware

# Clone the Autoware source code into src/
vcs import src < repositories/autoware.repos
```

This command will clone and check out the correct versions as defined in [`autoware.repos`](../repositories/autoware.repos)

> **Note**
> Make sure `vcs2l` is installed before running this command:
>
> ```bash
> sudo apt install python3-vcs2l
> ```

In the future, to update all source repositories to their latest versions as defined in the manifest file, run:

```bash
vcs pull src
```

## Abbreviations, terms and symbols

| Term            | Meaning                                                                                                   |
| --------------- | --------------------------------------------------------------------------------------------------------- |
| apt             | Advanced Package Tool: Ubuntu's command for installing software packages                                  |
| Git             | The version control system each Autoware repository uses                                                  |
| Manifest file   | A `.repos` file listing each source repository, where to get it and which version to check out            |
| Meta-repository | A repository that holds no code itself and instead lists the repositories that make up the project        |
| `src/`          | Short for "source": the folder the source repositories are cloned into                                    |
| sudo            | Runs a command with administrator rights                                                                  |
| vcs, vcs2l      | The version control system tool that clones and updates every repository named in a manifest file at once |
| ➡️              | "is": points from a path to what it holds                                                                 |
| ⭐              | Marks a link worth following for more detail                                                              |
| 🔗              | Marks a link to the external Autoware documentation                                                       |

Other project terms are defined in the [Glossary](../wiki/Glossary.md).
