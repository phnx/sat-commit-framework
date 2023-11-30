#!/bin/bash

INSTANCE_NAME=$1
OPT_COMMAND=$2

echo "Docker entry point for infer"


# install tool
cd /home/ubuntu/

VERSION=1.1.0
wget https://github.com/facebook/infer/releases/download/v$VERSION/infer-linux64-v$VERSION.tar.xz
tar -xvf ./infer-linux64-v$VERSION.tar.xz
rm infer-linux64-v$VERSION.tar.xz
export PATH=/home/ubuntu/infer-linux64-v$VERSION/bin:$PATH

cd /home/ubuntu/workspace/script

# run pipeline with selected tool
python3 -u pipeline.py infer $INSTANCE_NAME $OPT_COMMAND