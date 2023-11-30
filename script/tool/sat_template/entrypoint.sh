#!/bin/bash

INSTANCE_NAME=$1
OPT_COMMAND=$2

echo "Docker entry point for [a new tool]"


# install tool
cd /home/ubuntu/

# TODO download and install tool in the container
VERSION=1.0
wget https://dummy-tool-url.com/release/tool-$VERSION.tar.xz
tar -xvf ./tool-v$VERSION.tar.xz
rm tool-$VERSION.tar.xz

# TODO export tool path, if necessary
export PATH=/home/ubuntu/tool-$VERSION/bin:$PATH

cd /home/ubuntu/workspace/script

# run pipeline with selected tool
python3 -u pipeline.py [a new tool] $INSTANCE_NAME $OPT_COMMAND