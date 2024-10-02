# Flow Log Parser
This Python program parses a flow log file and maps each row to a tag based on a lookup table. It generates an output file containing:

- Count of matches for each tag.
- Count of matches for each port/protocol combination.

The lookup table is structured as a nested dictionary, where the protocol is the outer key and the port is the inner key.

## Requirements

- **Python Version**: The program requires Python 3.

## Files

- **`flow_log_parser.py`**: The main Python script.
- **flow_logs.txt**: A text file containing the flow log data (e.g., `flow_logs.txt`).
- **Lookup Table File**: A CSV file containing the tag mappings (e.g., `lookup_table.csv`).
- **Protocol Numbers File**: A CSV file containing the protocol numbers (e.g., `protocol_numbers.csv`).
- **Output File**: The file where the results will be written (e.g., `output.txt`).

## Assumptions

1. **Flow Log Format**:
   - The program assumes the flow log is in **default format**, version 2, as specified by AWS VPC Flow Logs.
   - Fields are space-separated, with **`dstport`** in **field 7** and **`protocol`** in **field 8**.
   - Invalid entries (e.g., missing fields, non-numeric `dstport` or `protocol`) are skipped.

2. **File Validity**:
   - Flow log entries with fewer than 14 fields are skipped without halting execution.
   - The log file can be up to **10 MB** in size and will be processed line by line to minimize memory usage.

3. **Protocol Mapping**:
   - The protocol numbers used in the flow log (column 8) are expected to match IANA protocol numbers. The program uses the pre-downloaded `protocol_numbers.csv` file to map these numbers to protocol names (e.g., TCP, UDP). If a protocol number is not found in the `protocol_numbers.csv` file, the program will use the numeric protocol value as the protocol name.

4. **Lookup Table**:
   - The lookup table uses a **nested dictionary** structure where the outer key is the protocol and the inner key is the destination port.
   - The lookup table file (`lookup_table.csv`) must have three columns: `dstport`, `protocol`, and `tag`, and can contain up to **10,000 mappings**.

5. **Case Insensitivity**:
   - All comparisons for protocol names and tags are **case-insensitive**.

6. **Unmatched Entries**:
   - If a `protocol`/`dstport` pair is not found in the lookup table, the tag **"Untagged"** is applied.

7. **Output**:
   - The output file contains **Tag Counts** and **Port/Protocol Combination Counts**, and overwrites any existing file of the same name.

8. **No External Libraries**:
   - The program uses only Python’s **standard libraries**, ensuring compatibility without requiring additional dependencies.

9. **Manual Protocol Updates**:
   - The `protocol_numbers.csv` file should be manually updated periodically by downloading the latest version from [IANA protocol numbers](https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml).

## Setup and Preparation

### 1. Download the Protocol Numbers CSV File

- Visit the IANA Assigned Internet Protocol Numbers page: [IANA Protocol Numbers](https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml).
- Download the protocol numbers in CSV format:
  - Look for a link labeled "CSV" under the "Available Formats" section.
  - Or, you can directly download it from: [protocol-numbers-1.csv](https://www.iana.org/assignments/protocol-numbers/protocol-numbers-1.csv)
- Save the file as `protocol_numbers.csv` in the same directory as the script.

### 2. Prepare the Lookup Table File

The lookup table should be a CSV file with the following columns:

```csv
dstport,protocol,tag
```

Example content:

```csv
dstport,protocol,tag
25,tcp,sv_P1
68,udp,sv_P2
23,tcp,sv_P1
31,udp,SV_P3
443,tcp,sv_P2
22,tcp,sv_P4
3389,tcp,sv_P5
0,icmp,sv_P5
110,tcp,email
993,tcp,email
143,tcp,email
```

### 3. Prepare the Flow Log File

The flow log file should be in the default AWS VPC flow log format, version 2. Ensure the file is saved as plain text (ASCII).

## Run the Program

   Follow the below command format:

   ```bash
   python3 flow_log_parser.py <flow_log_file> <lookup_table_file> <protocol_numbers_file> <output_file>
   ```

   **Example:**

   ```bash
   python3 flow_log_parser.py flow_logs.txt lookup_table.csv protocol_numbers.csv output.txt
   ```

## Program Structure

The program is structured into the following functions:

1. **`load_lookup_table(filename)`**: Loads the lookup table from the specified CSV file into a nested dictionary. Returns a dictionary where the outer key is the protocol and the inner key is the port.

2. **`load_protocol_map(protocol_numbers_file)`**: Loads the protocol numbers from the specified CSV file. Returns a dictionary mapping protocol numbers to protocol names.

3. **`parse_flow_log_line(line, protocol_map)`**: Parses a single line from the flow log. Returns a tuple `(dstport, protocol_name)` or `None` if the line is invalid.

4. **`process_flow_log(flow_log_file, protocol_map, lookup_table)`**: Processes the flow log file and updates tag counts and port/protocol counts. Returns two dictionaries: `tag_counts` and `port_protocol_counts`.

5. **`write_output(output_file, tag_counts, port_protocol_counts)`**: Writes the tag counts and port/protocol counts to the output file.

6. **`main()`**: Entry point of the program. Parses command-line arguments and orchestrates the program flow.

## Features

- **Extensibility**: The program is designed in a modular fashion, making it easier to extend or modify in the future.
- **Efficient Lookup**: Uses a nested dictionary for lookups, grouping ports under their corresponding protocols, making the lookup faster and more structured.
- **Case-Insensitive Matching**: Matching for protocol names and tags is case-insensitive.
- **Efficient Processing**: The program processes files line by line to handle flow log files up to 10 MB and lookup tables with up to 10,000 entries without consuming excessive memory.
- **No External Dependencies**: Uses only Python's standard library modules; no need to install additional packages.
- **Error Handling**: Includes error handling for file I/O operations and data parsing to prevent crashes.

## Additional Notes

- The `protocol_numbers.csv` file should be updated periodically to ensure it contains the latest protocol assignments.
- Visit the IANA protocol numbers page: [IANA Protocol Numbers](https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml). Download the latest CSV file and replace the existing `protocol_numbers.csv` file.
- Ensure all input files are properly formatted and located in the correct directories.