# AGENTS

## Conda Environment

This project uses a conda environment named `africa`.

Activate it in a shell:

```bash
conda activate africa
```

If `conda activate` does not work in a fresh shell, initialize conda first:

```bash
conda init zsh
exec zsh
conda activate africa
```

Run commands in the environment without activating it:

```bash
conda run -n africa python --version
conda run -n africa jupyter notebook
```

The environment is currently located at:

```bash
/opt/homebrew/Caskroom/miniconda/base/envs/africa
```
