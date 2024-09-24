#!/bin/bash

# Directory containing .ach files
DIRECTORY="/Users/prachisinha/Desktop/code/cuoc_nacha/Returns"
PARSEDDIR="/Users/prachisinha/Desktop/code/cuoc_nacha/ReturnsParsed"

# Iterate over each .ach file in the directory
for file in "$DIRECTORY"/*; do
    # Check if the file exists
    if [ -e "$file" ]; then
        # Extract the base filename without extension
        base_filename=$(basename "$file" .ach)

        json_file="$PARSEDDIR/$base_filename.JSON"

        # create the file and save the JSON conversion
        curl -X POST --data-binary "@$file" http://localhost:8080/files/create  > "$json_file"

        # Clean up the JSOn conversion
        python3 /Users/prachisinha/Desktop/code/moov_output_cleaned.py -f "$json_file"
    else
        echo "No .ach files found in the directory."
    fi
done
