#!/bin/bash

# Create an array files that contains list of filenames
files=($(< data_files.txt))

# execute wget command for every filename URL in file.txt
for file in "${files[@]}"; do 
if [[ ! $file =~ "#" ]]
then
    echo "--------------------"
    echo "Downloading: ${file}"
    wget -N "${file}" -P ./data
    echo "--------------------"
fi
done
