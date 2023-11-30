#!/bin/bash

INSTANCE_NAME=$1
OPT_COMMAND=$2

echo "Docker entry point for codeql"


# install tool
cd /home/ubuntu/
wget https://github.com/github/codeql-action/releases/download/codeql-bundle-20230524/codeql-bundle-linux64.tar.gz
# wget https://github.com/github/codeql-action/releases/latest/download/codeql-bundle-linux64.tar.gz
tar -xvzf ./codeql-bundle-linux64.tar.gz
rm codeql-bundle-linux64.tar.gz

# add codeql directory to PATH
export PATH="$HOME/codeql:$PATH"

# test installation / packs
codeql resolve qlpacks

cd /home/ubuntu/workspace/script

# run pipeline with selected tool
python3 -u pipeline.py codeql $INSTANCE_NAME $OPT_COMMAND