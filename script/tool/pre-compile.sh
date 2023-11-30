# !/bin/bash


# [autoreconf -fi, autogen.sh] && ./configure && make

# sub-1
AUTOGEN_FILE=autogen.sh
BOOTSTRAP_FILE=bootstrap.sh
BUILD_FILE=build.sh
CONFIGURE_FILE=configure

# bash script for autobuild - prepare subject for compilation
if  test -f "$AUTOGEN_FILE"; 
then
    echo "use project autogen.sh"
    bash "$AUTOGEN_FILE"
elif test -f "$BOOTSTRAP_FILE";
then
    echo "use project bootstrap file"
    bash "$BOOTSTRAP_FILE"
elif test -f "$BUILD_FILE";
then
    echo "use project build file"
    bash "$BUILD_FILE"
else
    echo "no autofile found - use autoreconf to create configuration file"
    bash autoreconf -fi
fi

# sub 2
echo "start configure"
bash configure
