import os
import sys

def read_from_file(file_path, start, end):
    """Read data from file between byte offsets start and end."""
    with open(file_path, 'r') as file:
        file.seek(start)  # Move to the start byte position
        return file.read(end - start)
def extract_logs_from_specific_chunk(file_path, mid, file_size):
    """Extract logs from a specific chunk: 10MB before and after mid."""
    extend_size = 10 * 1024 * 1024  # 10MB
    start = max(0, mid - extend_size)  # Ensure the start doesn't go below 0
    end = min(file_size, mid + extend_size)  # Ensure the end doesn't go beyond file size

    # Read the chunk data
    chunk = read_from_file(file_path, start, end)

    # Process the chunk to extract logs
    lines = chunk.splitlines()

    logs_for_date = []
    for line in lines:
        logs_for_date.append(line)

    return logs_for_date
def find_log_for_date(file_path, target_date):
    """Find logs for a specific date by binary search approach on file chunks."""
    file_size = os.path.getsize(file_path)
    lower_bound = 0
    upper_bound = file_size
    chunk_size = 1024  # Start with 1KB chunks
    
    logs_for_date = []

    while lower_bound < upper_bound:
        # Find middle byte and adjust the chunk size for line boundaries
        mid = (lower_bound + upper_bound) // 2  
        
        # Read chunk from mid to the end of the next line boundary
        chunk = read_from_file(file_path, mid, min(mid + chunk_size, file_size))

        # Find the first line in this chunk (split by newline)
        lines = chunk.splitlines()

        if lines:
            first_log = lines[1]
            
            if first_log.startswith(target_date):
                # If the first log matches the date, process this chunk for the logs
                logs_for_date = extract_logs_from_specific_chunk(file_path, mid, file_size)
                break
            elif first_log < target_date:
                # If the first log is earlier than the target date, move the lower bound
                lower_bound = mid + len(chunk)
            else:
                # If the first log is later than the target date, move the upper bound
                upper_bound = mid
        
        # Dynamically reduce chunk size when bounds converge
        if upper_bound - lower_bound < chunk_size:
            chunk_size = upper_bound - lower_bound

    return logs_for_date

def extract_logs(date):
    log_file_path = "./generated_logs.txt"
    output_file_path = f"output/output_{date}.txt"
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    try:
        # Find the logs for the specified date
        logs_for_date = find_log_for_date(log_file_path, date)

        if logs_for_date:
            # Write the logs to the output file
            with open(output_file_path, 'w') as output_file:
                output_file.write("\n".join(logs_for_date))
            print(f"Logs for {date} have been saved to {output_file_path}")
        else:
            print(f"No logs found for {date}.")
    
    except FileNotFoundError:
        print(f"Error: The log file {log_file_path} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_logs.py YYYY-MM-DD")
    else:
        # Get the date from the command line argument
        date = sys.argv[1]
        extract_logs(date)
