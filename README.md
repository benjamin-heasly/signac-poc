# signac-poc
Proof of concept for working with Python, signac, and Matlab.

This repo contains code and commentary about using signac to do a proof of concept for neural data analysis pipelines that use Matlab and Python.  [Signac](https://signac.io/) is a Python-based tool for managing data and running analysis workflows / pipelines.

This README covers:
 - Setup for Python, signac, and Matlab
 - Overview of sample data and analysis pipeline
 - Musings on pipelines and signac

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

## Sample data and analysis -- overview.

Here's an overview of the sample data and analysis from this proof of concept pipeline.

![Sample data and pipeline](signac-poc.drawio.png)

Summary:

 - We generate some binary data files with random byte values.
 - We use Python and signac to locate all these files and process them in several steps.
 - For some of these steps, we call out to Matlab via the shell and let Matlab do the work.
 - For the final step, we combine raw data with the results of Matlab analysis to create plots, using Python and matplotlib.


## Sample data and analysis -- running it.

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

This iterates over the letter-named sessions and binary recording files created above.  For each one it creates a signac "job" which is signac's way of accounting for unique things to process.  In this case, the jobs are unique by session name and recording index.

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

 - `aggregate_recordings()` -- Group together recordings from the same session, and having the same parity (odd vs even recording index).  This is a placeholder for other groupings we might want to do.  For each group, concatenate the recording files, in index order, into a sigle aggregate file.  To do this, we call Matlab and use the script `concatenateFiles.m`.
 - `compute_stats()` -- For each aggregate, scan over the binary byte data and compute some statistics like min and max.  This is a placeholder for other data preprocessing we might want to do.  This also happens in Matlab, with the script `computeStats.m`.
 - `find_rising_edges()` -- For each aggregate, use the stats we just computed to look for rising edges in the data, using the precomputed min and max, and an arbitrary threshold between them.  This is a placeholder for things like event detection and spike sorting.  This also happens in Matlab with the script `findRisingEdges.m`.
 - `plot_summary()` -- For each aggregate, load the raw byte data and the detected edges and produce a summary figure.  This happens in Python using `matplotlib`, using analysis results computed in Matlab.  This is an example of integrating Python and Matlab via the file system and the pipeline runner (signac), and avoids extra "bridge" code between the two environments.

## Musings on pipelines and signac

WIP...

This section is about qualities of analysis pipelines that we might want to obtain, or set as goals.  I'll organize these in terms of what signac seems to solve, or what we'd be left implement ourselves.  This is a bit unfair to signac -- which seems like a great project -- but I hope it will make things concrete and focused.

### Things signac solves for us

modular operations -- reusable, swappable, sharable
integrate steps via file system – durability enables restarts from last completed
pass data between Matlab and Python steps w/o magic bridge
iterate a bunch of data files
query for a result of interest
aggregate files in groups, by some key function, then process group aggregates

re-run a workflow after minor changes, without recomputing everything
re-run a workflow after "the power goes out", without recomputing everyting

visualize a workflow before it's run
visualize workflow progress during and after a run

useful without cloud provider or sys admin

### Things we could implement along with signac

version control and/or reporting of libs used
capture host system info
capture logging from each step, and overall
capture timing around each step, and overall

iterate over things like recording, tower, probe, channel

take advantage of cluster or cloud resources

### Where signac felt in the way or confusing
share a project with someone else
clean up generated and/or temp files

process singel files and aggregate results in the same pipeline
re-run the same signac project on a different dataset of the same type
