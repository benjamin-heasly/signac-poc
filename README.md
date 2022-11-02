# signac-poc
Proof of concept for working with Python, signac, and Matlab.

## Python Setup

I used conda to manage my Python environment and obtain Python dependencies.  Here's the [conda installation docs](https://conda.io/projects/conda/en/latest/user-guide/install/index.html).

With conda I set up to use signac and matplotlib.
```
$ conda config --add channels conda-forge
$ conda create --name signac signac signac-flow
$ conda activate signac
$ pip install matplotlib
```

## Matlab Setup

I installed and activated Matlab R2022b locally and added `R2022b/bin` to my path.  This allows signac to invoke matlab using just the executable name `matlab`.

## Phony data and analysis.

TODO
