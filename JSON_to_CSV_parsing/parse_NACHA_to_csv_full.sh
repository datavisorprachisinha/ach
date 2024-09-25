#!/bin/bash

# Directory containing .ach files (cannot contain any other files!)
DIRECTORY="/Users/prachisinha/Desktop/code/cuoc_nacha/Returns"

JSONDIR="/Users/prachisinha/Desktop/code/cuoc_nacha/ReturnsJSONParsed"
CSVDIR="/Users/prachisinha/Desktop/code/cuoc_nacha/ReturnsCSVParsed"

# Create JSON and CSV directories if they do not exist
if [ ! -d "$JSONDIR" ]; then
    # Create the directory if it does not exist
    mkdir "$JSONDIR"
    echo "Directory '$JSONDIR' created."
else
    echo "Directory '$JSONDIR' already exists."
fi

if [ ! -d "$CSVDIR" ]; then
    # Create the directory if it does not exist
    mkdir "$CSVDIR"
    echo "Directory '$CSVDIR' created."
else
    echo "Directory '$CSVDIR' already exists."
fi

# Iterate over each file in the directory 
# (some files have .ach extension, some do not, so not checking)
for file in "$DIRECTORY"/*; do
    if [ -e "$file" ]; then
        # Extract the base filename without extension if exists
        base_filename=$(basename "$file" .ach)

        json_file="$JSONDIR/$base_filename.JSON"

        csv_file="$CSVDIR/$base_filename.csv"

        # create the file and save the JSON conversion
        curl -X POST --data-binary "@$file" http://localhost:8080/files/create  > "$json_file"

        # Clean up the JSON conversion outut
        python3 /Users/prachisinha/Desktop/code/moov_output_cleaned.py -f "$json_file"
        python3 /Users/prachisinha/Desktop/code/parse_nacha_json.py -i "$json_file" -o "$csv_file"
    else
        echo "No files found in the directory."
    fi
done
