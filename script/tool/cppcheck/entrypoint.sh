#!/bin/bash

INSTANCE_NAME=$1
OPT_COMMAND=$2

echo "Docker entry point for cppcheck"


# install tool
cd /home/ubuntu/

VERSION=2.10
wget https://sourceforge.net/projects/cppcheck/files/cppcheck/$VERSION/cppcheck-$VERSION.tar.gz
tar -xvzf ./cppcheck-$VERSION.tar.gz
rm cppcheck-$VERSION.tar.gz
cd cppcheck-$VERSION

# cmake build process
mkdir build
cd build
cmake ..
cmake --build .
# sudo make install
export PATH=/home/ubuntu/cppcheck-$VERSION/build/bin:$PATH

cd /home/ubuntu/workspace/script

# run pipeline with selected tool
python3 -u pipeline.py cppcheck $INSTANCE_NAME $OPT_COMMAND