# Conda Meta Environment Parser

This tiny parser takes as input a meta-environment file, transforms it into an environment file and invokes conda on it.
The input, usually called **environment.yml.meta**, is a standard conda environment file which can be enriched with conditions for certain lines/blocks, e.g. to only include them on specific platforms or if certains flags are given.

## Example

The following meta-file

```
name: demo_env
dependencies:
  - numpy=1.16.4
  - tensorflow=1.14.0
  - tensorflow-gpu=1.14.0 [use_gpu]
  - winreg-helpers [platform == win32]
```

can be used to set up a conda environment with

`python create_env.py` (A)

or

`python create_env.py --flag use_gpu` (B).

In (A), the conda package *tensorflow-gpu* is not installed. In both cases, *winreg-helpers* is only installed on windows platforms.
