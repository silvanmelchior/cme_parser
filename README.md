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

## Quickstart

To use CME Parser in your own project, create an **environment.yml.meta** file in your project folder, e.g. like this:

```
name: demo_env2
channels:
  - conda-forge
  - defaults
dependencies:
  - numpy=1.16.4
  - matplotlib=3.1.0 [allow_plot and plot_tool == matplotlib]
  - ggplot=0.11.5    [allow_plot and plot_tool == ggplot]
  - pip=19.1.1
  - some-linux-package=1.2.3 [platform startswith linux]
  - pip:
    - selenium=3.141.0
```

If **create_env.py** gets called without an `--input` argument, it will try to find **environment.yml.meta** either in the same directory or its parent.
Thus, either directly add **create_env.py** to your project folder next to the meta-env file or add this repo as git submodule:

```
$ cd your_project_folder
$ git rm environment.yml  # if exists
$ echo "environment.yml" >> .gitignore
$ git add environment.yml.meta
$ git submodule add https://github.com/silvanmelchior/cme_parser
$ git commit -m "cme parser added"
$ git push
```

If you now execute (in the case of using a submodule)

`python cme_parser/create_env.py --flag allow_plot --variable plot_tool matplotlib`

in your project folder, CME Parser will find the meta-env file and create **environment.yml**.
In general, if not specified differently with a `--output` argument, the parser will write the output into the same location as the input, removing *.meta* from the filename.
If *.meta* is not present, it will append *_out* to the filename instead.
In all cases, the parser will in the end invoke conda to create the environment specified by the output file. 

## Syntax

If a line contains `[condition]`, the parser only outputs it if the condition is met (removing the condition itself).
If a line contains `[[condition` and a later line `]]`, the parser outputs everything in between only if the condition is met (removing the two lines marking the block borders).
Nested blocks are allowed.

A condition can either be an arbitrary name, which is then interpreted as a flag, or a tripplet of an arbitrary name, some operator and a string.
In the latter, the name is interpreted as variable and the operator can be one of `==`, `!=`, `startswith`, `endswith`, `contains`.
The string does not need any special terminators (e.g. no `""`).

Conditions can be combined by adding `and` and `or` in between them.
Furthermore, `not` can be added in front of a condition. The precedence order is `or` (highest), `and`, `not` (lowest), so e.g. `a and not b` is evaluated as `a and (not b)`.
Brackets to enforce another evaluation order are currently not supported.

Flags are evaluated as *false* per default, except given to the parser with `-f flag_name`.
Variables have to be given to the parser with `-v var_name var_value`, otherwise an error is risen.
An exception are variables of the form  `var_name%value`, which are interpreted as variable `var_name` with default value `value`.
Furthermore, the special variable `platform` is reserved and populated with the result of `sys.platform`.

