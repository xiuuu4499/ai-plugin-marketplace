#!/bin/bash

# download github-docs folder if it doesn't exist
if [ ! -d "github-docs" ]; then
    echo "Downloading github-docs..."
    wget https://github.com/github/docs/archive/refs/heads/main.zip
    unzip main.zip
    rm main.zip
    mv docs-main github-docs
fi
