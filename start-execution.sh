#!/bin/bash

# execution: bash ./start-execution.sh [custom/clean] infer test1 input_file

DOCKER_BASE=$1
TOOL=$2
INSTANCE_NAME=$3
OPT_COMMAND=$4

if [ $DOCKER_BASE == "custom" ]; then
    IMAGE_NAME="jammy-base"
elif [ $DOCKER_BASE == "clean" ]; then
    IMAGE_NAME="clean-base"
else
    echo "try: bash ./start-execution.sh [custom|clean] [tool_name] [instance_name] [custom_opt]"
    exit -1
fi

echo "setting up a docker instance for $TOOL as $INSTANCE_NAME"
echo "choosing base: $DOCKER_BASE"
echo "custom command for tool: $OPT_COMMAND"

echo "instance name: $INSTANCE_NAME"

# start database container, if needed : auto-tool-investigation-db
# docker-compose -f docker/database.yml up -d

# build custom docker if not exists
EXISTING_IMAGE=$( docker images -q $IMAGE_NAME )
if [[ -n "$EXISTING_IMAGE" ]]; then
    echo "$IMAGE_NAME image exists, launching a new instance"
else
    echo "build base image"
    if [ $IMAGE_NAME == "jammy-base" ]; then
        docker build -t "$IMAGE_NAME" -f script/tool/Dockerfile-Base .
    elif [ $IMAGE_NAME == "clean-base" ]; then
        docker build -t "$IMAGE_NAME" -f script/tool/Dockerfile-Clean-Base .
    fi
fi


# create output directory on host
mkdir -m 777 ./output/$INSTANCE_NAME

# run common docker with the instance name
# attach volume in host output path, 
# also attach data, tool, script folder for hot-reload from host
docker run -d --network=host \
    --cpus=4 \
    --name $INSTANCE_NAME \
    --log-driver json-file --log-opt max-size=5m --log-opt max-file=10 \
    -v "$PWD/output/$INSTANCE_NAME":/home/ubuntu/workspace/output:rw \
    -v "$PWD/script":/home/ubuntu/workspace/script:ro \
    -v "$PWD/data-ref":/home/ubuntu/workspace/data-ref:ro \
    $IMAGE_NAME \
    bash /home/ubuntu/workspace/script/tool/$TOOL/entrypoint.sh $INSTANCE_NAME $OPT_COMMAND
