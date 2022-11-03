import os
import shutil
from genericpath import isfile
import json
from flow import FlowProject, aggregator
import matplotlib.pyplot as plt
import numpy as np


# python pipeline.py run -o analyze_aggregates
# Analyze our signac Data Space by running this here project on it:
recording_aggregator = aggregator.groupby(lambda job: job.doc.group_key, sort_by=lambda job: job.sp.recording_index)
analyze_aggregates = FlowProject.make_group("analyze_aggregates", group_aggregator=recording_aggregator)


# Call Matlab in batch mode to run a script and save a log file.
def call_matlab(jobs, mfile_name, *mfile_args):
    logs_dir = jobs[0].doc.logs_dir
    os.makedirs(logs_dir, exist_ok=True)
    group_label = jobs[0].doc.parity
    log_file = f"{logs_dir}/{mfile_name}_{group_label}.log"
    matlab_command = f"{mfile_name} {' '.join(mfile_args)}"
    shell_command = f"matlab -logfile '{log_file}' -batch '{matlab_command}'"
    print(f"Running command: {shell_command}")
    return shell_command


# Choose a file path for the aggregate of several recordings (AKA signac jobs).
def aggregate_file_path(jobs):
    products_dir = jobs[0].doc.products_dir
    os.makedirs(products_dir, exist_ok=True)
    group_label = jobs[0].doc.parity
    file_name = f"aggregate_of_{group_label}.bin"
    return f"{products_dir}/{file_name}"


# Aggregate several recordings (AKA signac jobs) into one binary file.
@analyze_aggregates
@FlowProject.operation(cmd=True)
@FlowProject.post(lambda *jobs: isfile(aggregate_file_path(jobs)))
def aggregate_recordings(*jobs):
    output_path = aggregate_file_path(jobs)
    input_paths = [job.doc.binary_file for job in jobs]
    return call_matlab(jobs, 'concatenateFiles', output_path, *input_paths)


# Choose a file path where we'll write stats about an aggregated recording file.
def stats_file_path(jobs):
    products_dir = jobs[0].doc.products_dir
    os.makedirs(products_dir, exist_ok=True)
    group_label = jobs[0].doc.parity
    file_name = f"stats_of_{group_label}.json"
    return f"{products_dir}/{file_name}"


# Compute stats about an aggregated recording file.
@analyze_aggregates
@FlowProject.operation(cmd=True)
@FlowProject.pre.after(aggregate_recordings)
@FlowProject.post(lambda *jobs: isfile(stats_file_path(jobs)))
def compute_stats(*jobs):
    aggregate_path = aggregate_file_path(jobs)
    stats_path = stats_file_path(jobs)
    return call_matlab(jobs, 'computeStats', aggregate_path, stats_path)


# Choose a file path where we'll write detected edges for an aggregated recording file.
def edges_file_path(jobs):
    products_dir = jobs[0].doc.products_dir
    os.makedirs(products_dir, exist_ok=True)
    group_label = jobs[0].doc.parity
    file_name = f"edges_of_{group_label}.json"
    return f"{products_dir}/{file_name}"


# Detect edges for an aggregated recording file.
@analyze_aggregates
@FlowProject.operation(cmd=True)
@FlowProject.pre.after(compute_stats)
@FlowProject.post(lambda *jobs: isfile(edges_file_path(jobs)))
def find_rising_edges(*jobs):
    aggregate_path = aggregate_file_path(jobs)
    stats_path = stats_file_path(jobs)
    edges_path = edges_file_path(jobs)
    return call_matlab(jobs, 'findRisingEdges', aggregate_path, stats_path, edges_path)


# Choose a file path where we'll write a summary figure for an aggregate recording file.
def figure_file_path(jobs):
    products_dir = jobs[0].doc.products_dir
    os.makedirs(products_dir, exist_ok=True)
    group_label = jobs[0].doc.parity
    file_name = f"figure_of_{group_label}.png"
    return f"{products_dir}/{file_name}"


# Write a summary figure for an aggregate recording file and our analyses here.
@analyze_aggregates
@FlowProject.operation
@FlowProject.pre.after(find_rising_edges)
@FlowProject.post(lambda *jobs: isfile(figure_file_path(jobs)))
def plot_summary(*jobs):
    aggregate_path = aggregate_file_path(jobs)
    with open(aggregate_path, 'rb') as f:
        aggregate_bytes = bytearray(f.read())
    aggregate = np.frombuffer(aggregate_bytes, dtype=np.uint8)
    x_axis = np.arange(aggregate.size)

    fig, ax = plt.subplots()
    ax.set_xlabel('sample number')
    ax.set_ylabel('byte value')
    ax.set_title('Threshold crossings')
    ax.plot(x_axis, aggregate, 'b.')

    edges_path = edges_file_path(jobs)
    with open(edges_path, 'r') as f:
        edge_times = json.load(f)
    edge_x = np.asarray(edge_times)
    edge_y = aggregate.take(edge_x)
    ax.plot(edge_x, edge_y, 'r.')

    fig.savefig(figure_file_path(jobs))


# python pipeline.py run -o clean
# Clean up any analysis results created so we can run fresh:
session_aggregator = aggregator.groupby("session")
clean = FlowProject.make_group("clean", group_aggregator=session_aggregator)


# Delete the "products" directory for a recording session.
@clean
@FlowProject.operation
def clean_products_dir(*jobs):
    products_dir = jobs[0].doc.products_dir
    print(f"Cleaning products dir: {products_dir}")
    shutil.rmtree(products_dir, ignore_errors=True)


# We'll be calling this script from the command line
# and letting signac's FlowProject().main() parse the arguments for us. 
if __name__ == "__main__":
    FlowProject().main()
