import os
import sys

def read_from_file(filepath, start_offset, end_offset):
    with open(filepath, 'r') as file:
        file.seek(start_offset)  
        return file.read(end_offset - start_offset)

def extract_logs_from_specific_chunk(filepath, midpoint, file_size):
    extend_bytes = 10 * 1024 * 1024  
    start_position = max(0, midpoint - extend_bytes)  
    end_position = min(file_size, midpoint + extend_bytes) 

    chunk_data = read_from_file(filepath, start_position, end_position)

    lines = chunk_data.splitlines()

    date_logs = []
    for line in lines:
        date_logs.append(line)

    return date_logs

def find_log_for_date(filepath, target_date):
    file_size = os.path.getsize(filepath)
    lower_limit = 0
    upper_limit = file_size
    chunk_bytes = 1024  

    date_logs = []

    while lower_limit < upper_limit:
        midpoint = (lower_limit + upper_limit) // 2  

        chunk_data = read_from_file(filepath, midpoint, min(midpoint + chunk_bytes, file_size))

        lines = chunk_data.splitlines()

        if lines:
            first_entry = lines[1]

            if first_entry.startswith(target_date):
                date_logs = extract_logs_from_specific_chunk(filepath, midpoint, file_size)
                break
            elif first_entry < target_date:
                lower_limit = midpoint + len(chunk_data)
            else:
                upper_limit = midpoint

        if upper_limit - lower_limit < chunk_bytes:
            chunk_bytes = upper_limit - lower_limit

    return date_logs

def extract_logs(date):
    log_filepath = "./generated_logs.txt"
    output_filepath = f"output/output_{date}.txt"

    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)

    try:
        date_logs = find_log_for_date(log_filepath, date)

        if date_logs:
            with open(output_filepath, 'w') as output_file:
                output_file.write("\n".join(date_logs))
            print(f"Logs for {date} have been saved to {output_filepath}")
        else:
            print(f"No logs found for {date}.")

    except FileNotFoundError:
        print(f"Error: The log file {log_filepath} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_logs.py YYYY-MM-DD")
    else:
        date_argument = sys.argv[1]
        extract_logs(date_argument)
