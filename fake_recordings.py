import os
from random import randbytes

recordings_dir = "recordings"
byte_count = 100

for dir in 'abcde':
    for index in range(0, 4):
        session_dir = f"{recordings_dir}/{dir}"
        os.makedirs(session_dir, exist_ok=True)
        binary_name = f"{session_dir}/rec_{index}.bin"
        with open(binary_name, "wb") as file:
            random_bytes = randbytes(byte_count)
            file.write(random_bytes)
