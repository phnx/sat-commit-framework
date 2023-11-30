!/bin/bash

INSTANCE_NAME=$1
OPT_COMMAND=$2

echo "Docker entry point for flawfinder"


# install tool
VERSION=2.0.19
pip install flawfinder==$VERSION
export PATH="$HOME/.local/bin:$PATH"

cd /home/ubuntu/workspace/script
# run pipeline with selected tool
python3 -u pipeline.py flawfinder $INSTANCE_NAME $OPT_COMMAND