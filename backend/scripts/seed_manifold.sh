#!/usr/bin/env bash

# Resolve paths relative to script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR/../../ai_engine/data/manifold"
DEST_DIR="$SCRIPT_DIR/../data"

echo "Checking for manifold source directory at: $SOURCE_DIR"

if [ -d "$SOURCE_DIR" ]; then
    echo "Source directory found. Copying .json files to $DEST_DIR..."
    mkdir -p "$DEST_DIR"
    
    if compgen -G "$SOURCE_DIR/*.json" > /dev/null; then
        cp "$SOURCE_DIR"/*.json "$DEST_DIR"/
        echo "Successfully copied manifold JSON files to $DEST_DIR."
    else
        echo "Source directory exists, but no .json files were found to copy."
    fi
else
    echo "Source directory '$SOURCE_DIR' missing. Skipping copy."
fi
