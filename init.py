import os
import signac

# Create a signac "Data Space" by running this here script: 
# python init.py
project = signac.init_project()

# Search the nearby "recordings" directory for session folders and ".bin" files.
cwd = os.getcwd()
data_dir = f"recordings"
sessions = [f.name for f in os.scandir(data_dir) if f.is_dir()]

print(f"Searching data dir {data_dir}")
print(f"Found {len(sessions)} sessions: {sessions}")

for session in sessions:
    session_dir = f"{data_dir}/{session}"
    recordings = [f.name for f in os.scandir(session_dir) if f.is_file and f.name.startswith("rec_")]

    print(f"Session {session} has {len(recordings)} recordings: {recordings}")

    for recording in recordings:
        # Create a signac "job" for the unique recording corrdinates: session, recording_index.
        recording_index = int(recording.replace(".", "_").split("_")[1])
        state_point = {
            "session": session,
            "recording_index": recording_index
        }
        job = project.open_job(state_point)
        job.init()

        # Add metadata to help wrangle files per job.
        job.doc["binary_file"] = f"{session_dir}/{recording}"        
        products_dir = f"{session_dir}/products"
        job.doc["products_dir"] = products_dir
        job.doc["logs_dir"] = f"{products_dir}/logs"

        # Add metadata to help group recordings by key, so we can process them as aggregates.
        parity = "even" if recording_index % 2 == 0 else "odd"
        job.doc["parity"] = parity
        job.doc["group_key"] = f"{session}-{parity}"
