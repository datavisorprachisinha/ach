#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <DIRECTORY>"
    exit 1
fi

# Directory containing NACHA files (cannot contain any other files!)
DIRECTORY="$1"

# Check if the directory exists
if [ ! -d "$DIRECTORY" ]; then
    echo "Error: Directory '$DIRECTORY' does not exist."
    exit 1
fi

JSONDIR="${DIRECTORY}_JSONParsed"
CSVDIR="${DIRECTORY}_CSVParsed"

# Create JSON and CSV directories if they do not exist
if [ ! -d "$JSONDIR" ]; then
    mkdir "$JSONDIR"
    echo "Directory '$JSONDIR' created."
else
    echo "Directory '$JSONDIR' already exists."
fi

if [ ! -d "$CSVDIR" ]; then
    mkdir "$CSVDIR"
    echo "Directory '$CSVDIR' created."
else
    echo "Directory '$CSVDIR' already exists."
fi

for file in "$DIRECTORY"/*; do
    if [ -e "$file" ]; then
        # Extract the base filename without extension (if exists)
        base_filename=$(basename "$file" .ach)

        json_file="$JSONDIR/$base_filename.JSON"

        csv_file="$CSVDIR/$base_filename.csv"

        # create the file and save the JSON conversion (need docker container to be running for this!!)
        curl -X POST --data-binary "@$file" http://localhost:8080/files/create  > "$json_file"

        # Clean up moov's JSON conversion output and convert to CSV
        python3 moov_output_cleaned.py -f "$json_file"
        python3 parse_nacha_json.py -i "$json_file" -o "$csv_file"
    else
        echo "No files found in the directory."
    fi
done
