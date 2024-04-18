#!/bin/bash

# Define the base repository path
BASE_REPO_PATH="/home/runner/work/CHATOPSTEST/CHATOPSTEST"

# Define the base workflows directory
BASE_WORKFLOWS_DIR="$BASE_REPO_PATH/.github/workflows"

echo " heelo from scriptcopy.sh"

# Loop through each repository directory
for repo_dir in /home/runner/work/*; do
    echo " heelo from scriptcopy.sh -repo"
    echo $repo_dir
    # Check if the repository directory exists and is a directory
    if [ -d "$repo_dir" ]; then
        # Create the .github/workflows directory if it doesn't exist
        mkdir -p "$repo_dir/.github/workflows"
        echo " heelo from scriptcopy.sh -repodir"

        # Loop through each shared workflow file in the base repository
        for workflow_file in "$BASE_WORKFLOWS_DIR"/*; do
            # Get the filename of the shared workflow file
            workflow_filename=$(basename "$workflow_file")

            # Check if the symbolic link already exists
            if [ ! -L "$repo_dir/.github/workflows/$workflow_filename" ]; then
                # Create a symbolic link to the shared workflow file
                ln -s "$workflow_file" "$repo_dir/.github/workflows/$workflow_filename"
                echo "Created symbolic link to $workflow_filename in $repo_dir"
            else
                echo "Symbolic link already exists for $workflow_filename in $repo_dir"
            fi
        done
    fi
done