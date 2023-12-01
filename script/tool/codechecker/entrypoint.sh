#!/bin/bash

INSTANCE_NAME=$1
INPUT_FILE=$2
USE_DATABASE=$3

echo "Docker entry point for codechecker"


# normal scenairo
# install tool (updated as of July 2023)
VERSION=6.22.2
pip install codechecker==$VERSION
export PATH="$HOME/.local/bin:$PATH"


# test installation
CodeChecker version

# base analyzers i.e., clang, clang-tidy were installed in Docker base container
# not installing cppcheck - avoid redundancy between tools

cd /home/ubuntu/workspace/script

# run pipeline with selected tool
python3 -u pipeline.py codechecker $INSTANCE_NAME $INPUT_FILE $USE_DATABASE

# alternative scenario (the target version cannot be installed from PIP)
# manual installation (and manual pipeline stating)

# 1) start container
# mkdir ./output/codechecker-trial6
# mkdir ./output_analysis/codechecker-trial6

# sudo docker run -it --network=host \
#     --cpus=4 \
#     --name codechecker-trial6 \
#     --log-driver json-file --log-opt max-size=5m --log-opt max-file=10 \
#     -v "$PWD/output/codechecker-trial6":/home/ubuntu/workspace/output:rw \
#     -v "$PWD/output_analysis/codechecker-trial6":/home/ubuntu/workspace/output_analysis:rw \
#     -v "$PWD/script":/home/ubuntu/workspace/script:ro \
#     -v "$PWD/data":/home/ubuntu/workspace/data:ro \
#     -v "$PWD/data-ref":/home/ubuntu/workspace/data-ref:ro \
#     jammy-base \
#     bash 

# 2) compile target version of CodeChecker, add path
# sudo apt-get install clang clang-tidy build-essential curl gcc-multilib \
#       git python3-dev python3-venv

# curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash -
# sudo apt-get install -y nodejs

# git clone --depth 1 -b release-v6.22.2 https://github.com/Ericsson/codechecker/ ~/codechecker
# cd ~/codechecker

# make venv
# source $PWD/venv/bin/activate

# make standalone_package
# deactivate
# export PATH="$PWD/build/CodeChecker/bin:$PATH"

# 3) get more dependencies into vevn and start pipeline
# cd ~/workspace/script
# pip install -r requirements.txt
# python3 -u pipeline.py codechecker codechecker-trial6 selected-vcc-compact-information.csv

# 4) leave container and let it run in background
# CTRL + P & CTRL + Q

# 5) reattach container
# docker attach codechecker-trial3