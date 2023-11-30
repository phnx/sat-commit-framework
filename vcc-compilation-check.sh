#!/bin/bash

# execution: bash ./vcc-compilation-test.sh"

# TODO test ubuntu version to 20.04
IMAGE_NAME="compilation-base"
# IMAGE_NAME="compilation-base-20"

echo "setting up a docker instance for testing vcc compilation"
echo "choosing base: $IMAGE_NAME"

# build custom docker if not exists
EXISTING_IMAGE=$( docker images -q $IMAGE_NAME )
if [[ -n "$EXISTING_IMAGE" ]]; then
    echo "$IMAGE_NAME image exists, launching a new instance"
else
    echo "build base image"
    if [ $IMAGE_NAME == "compilation-base-20" ]; then
        docker build -t "$IMAGE_NAME" -f script/tool/Dockerfile-Compilation-Test20 .
    elif [ $IMAGE_NAME == "compilation-base" ]; then
        docker build -t "$IMAGE_NAME" -f script/tool/Dockerfile-Compilation-Test .
    fi
   
   
fi


# run common docker with the instance name
# attach volume in host output path, 
# also attach data, tool, script folder for hot-reload from host
docker run -d --network=host \
    --cpus=4 \
    --name vcc-$IMAGE_NAME-check \
    --log-driver json-file --log-opt max-size=5m --log-opt max-file=10 \
    -v "$PWD/data-ref/compilation-check":/home/ubuntu/workspace/data-ref/compilation-check:rw \
    -v "$PWD/script":/home/ubuntu/workspace/script:ro \
    -v "$PWD/data":/home/ubuntu/workspace/data:ro \
    $IMAGE_NAME \
    python3 -u /home/ubuntu/workspace/script/reference/ref_vcc_compilation_check.py $IMAGE_NAME

# for interactive mode
# sudo docker run -it    \
#     --name vcc-compilation-check     \
#     --log-driver json-file --log-opt max-size=5m --log-opt max-file=10     \
#     -v "$PWD/data-ref/compilation-check":/home/ubuntu/workspace/data-ref/compilation-check:rw     \
#     -v "$PWD/script":/home/ubuntu/workspace/script:ro     \
#     -v "$PWD/data":/home/ubuntu/workspace/data:ro    \
#     compilation-base  \
#     bash