#!/usr/bin/env python3

import sys
import csv
from collections import defaultdict

def load_lookup_table(filename):
    """
    Load the lookup table from a CSV file into a nested dictionary,
    outer key is protocol, inner key is portal.

    Return a dictionary where protocol is the key, and each value is a dictionary
    mapping ports to their corresponding tags
    """
    lookup = defaultdict(dict)
    try:
        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            #Skip header if present
            headers = next(reader)
            if headers[0].lower() != 'dstport':
                #First row is not header, back to very begining and process it
                csvfile.seek(0) 
                reader = csv.reader(csvfile)
            else:
                pass #headers already read
            for row in reader:
                if len(row) < 3:
                    continue #Skip invalid rows
                port_str, protocol, tag = row
                try:
                    port = int(port_str.strip())
                except ValueError:
                    continue #Skip invalid port numbers
                protocol = protocol.strip().lower()
                tag = tag.strip()
                #Use protocolas outer key, port as inner key
                lookup[protocol][port] = tag
        return lookup
    except Exception as e:
        print(f"Error: reading lookup table: {e}")
        sys.exit(1)

def load_protocal_map(protocol_numbers_file):
    """
    Load the protocol numbers from a CSV file

    Return a dictionary mapping protocol number to protocol name
    """
    protocol_map = {}
    try:
        with open(protocol_numbers_file, 'r') as csvfile:
            reader = csv.reader(csvfile)
            #Skip header
            headers = next(reader)
            for row in reader:
                if len(row) < 2:
                    continue #Skip invalid rows
                decimal_str, keyword = row[0], row[1]
                try:
                    decimal = int(decimal_str.strip())
                except ValueError:
                    continue #Skip invalid protocol numbers
                protocol_map[decimal] = keyword.strip().lower()
        return protocol_map
    except Exception as e:
        print(f"Error: reading protocol numbers file: {e}")
        sys.exit(1)

def parse_flow_log_line(line, protocol_map):
    """
    Parse a single line from the flow log.

    Return a tuple(dstport, protocol_name) or None if the line is invalid
    """
    line = line.strip()
    if not line or line.startswith("#"):
        return None #Skip empty lines or comments
    fields = line.split()
    if len(fields) < 14:
        return None #Skip invalid lines
    #Extract dstport(column 7), protocol(column 8)
    try:
        dstport = int(fields[6])
        protocol_number = int(fields[7])
    except ValueError:
        return None #Skip lines with invalid port or protocol numbers
    
    protocol_name = protocol_map.get(protocol_number, str(protocol_number)).lower()
    return (dstport, protocol_name)

def process_flow_log(flow_log_file, protocol_map, lookup_table):
    """
    Process the flow log file and update tag counts and port/protocol counts.

    Return two dictionaries: tag_counts and port_protocol_counts.
    """
    tag_counts = defaultdict(int)
    port_protocol_counts = defaultdict(int)

    try:
        with open(flow_log_file, 'r') as f:
            for line in f:
                result = parse_flow_log_line(line, protocol_map)
                if result is None:
                    continue
                dstport, protocol_name = result
                key = (dstport, protocol_name)
                port_protocol_counts[key] += 1

                #Lookup tag using nested dictionary
                tag = lookup_table.get(protocol_name, {}).get(dstport, 'Untagged')
                tag_counts[tag] += 1
        return tag_counts, port_protocol_counts
    except Exception as e:
        print(f"Error: reading flow log file: {e}")
        sys.exit(1)

def write_output(output_file, tag_counts, port_protocol_counts):
    """
    write the tag counts and port/protocol counts to the output file.
    """
    try:
        with open(output_file, 'w') as out_file:
            #Write tag counts
            out_file.write("Tag Counts:\n")
            out_file.write("Tag, Count\n")
            for tag, count in sorted(tag_counts.items(), key =lambda x:x[0].lower()):
                out_file.write(f"{tag},{count}\n")

            #Write port/protocol counts
            out_file.write("\nPort/Protocol Combination Counts:\n")
            out_file.write("Port,Protocol,Count\n")
            for(port, protocol), count in sorted(port_protocol_counts.items(), key=lambda x: (x[0][0], x[0][1])):
                out_file.write(f"{port},{protocol},{count}\n")
        print(f"Output written to {output_file}")
    except Exception as e:
        print(f"Error: writing output file: {e}")
        sys.exit(1)
    
def main():
    if len(sys.argv) != 5:
        print("*Usage*: python3 flow_log_parser.py <flow_log_file> <lookup_table_file> <protocol_numbers_file> <output_file>")
        sys.exit(1)
        
    flow_log_file = sys.argv[1]
    lookup_table_file = sys.argv[2]
    protocol_numbers_file = sys.argv[3]
    output_file = sys.argv[4]

    #load the lookup table
    lookup_table = load_lookup_table(lookup_table_file)

    #load protocol map from protocol_numbers.csv
    protocol_map = load_protocal_map(protocol_numbers_file)

    #process the flow log and get counts
    tag_counts, port_protocol_counts = process_flow_log(flow_log_file, protocol_map, lookup_table)

    #write the results to the output file
    write_output(output_file, tag_counts, port_protocol_counts)

if __name__ == '__main__':
    main()
    