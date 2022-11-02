# signac-poc
Proof of concept for working with Python, signac, and Matlab.

## Python Setup

I used conda to manage my Python environment and obtain Python dependencies.  Here's the [conda installation docs](https://conda.io/projects/conda/en/latest/user-guide/install/index.html).

With conda I set up to use signac and matplotlib.
```
conda config --add channels conda-forge
conda create --name signac signac signac-flow
conda activate signac
pip install matplotlib
```

## Matlab Setup

I installed and activated Matlab R2022b locally and added `R2022b/bin` to my path.  This allows signac to invoke matlab using just the executable name `matlab`.

## Phony data and analysis -- overview.

TODO

## Phony data and analysis -- running it.

We'll run all the commands here `signac` conda environment we created above, from the root folder of this `signac-poc` repository.
```
conda activate signac
cd signac-poc
```

### Fake Recording Data

Generate some random data to work with.

```
python fake_recordings.py
```

This will produce a `recordings` dir, with several subfolders and binary files.  The subfolders have letter names like `a`, `b`, `c`, etc.  Each one represents a "sesssion" of multiple recordings.

Within each session folder are several binary files with names like `rec_0.bin`, `rec_1.bin`, `rec_2.bin`, etc.  Each of these represents an individual "recording" of data.  In reality each one contains 100 pseudorandom byte values, uniform over 0-255.

### Signac Init

Create a signac project that knows about the fake recording data.

```
python init.py
```

This iterates over the lettern-names sessions and binary recording files created aboce.  For each one it creates a signac "job" which is signac's way of accounting for unique things to process.  In this case, the jobs are unique by session name and recording index.

This also adds some metadata to each job to help with things like:

 - wrangling data files and logs that we'll produce during analysis
 - grouping recordings into aggregates, based session and even vs odd recording index

The results of all this end up in a new `workspace` dir.  This is where signac keeps track of the unique jobs to process.

### Signac Analysis

Analyze the data above by running our signac "project".

```
python pipeline.py run -o analyze_aggregates
```

This tells signac to `run` the analysis that's defined in `pipeline.py`, specifically the operation called `analyze_aggregates`.  Here's what it does:

 - Group together recordings from the same session, and having the same parity (odd vs even recording index).  This is a placeholder for other groupings we might want to do.  For each group, concatenate the recording files, in index order, into a sigle aggregate file.  To do this, we call Matlab and use the script `concatenateFiles.m`.
 - For each aggregate, scan over the binary byte data and compute some statistics like min and max.  This is a placeholder for other data preprocessing we might want to do.  This also happens in Matlab, with the script `computeStats.m`.
 - For each aggregate, use the stats we just computed to look for rising edges in the data, using the precomputed min and max, and an arbitrary threshold between them.  This is a placeholder for things like event detection and spike sorting.  This also happens in Matlab with the script `findRisingEdges.m`.
 - For each aggregate, load the raw byte data and the detected edges and produce a summary figure.  This happens in Python using `matplotlib`, using analysis results computed in Matlab.  This is an example of integrating Python and Matlab via the file system and the pipeline runner (signac), and avoids extra "bridge" code between the two environments.

### Signac Reruns

TODO

 - add, detect, and process new data
 - re-run after small script changes
