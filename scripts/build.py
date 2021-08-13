from __future__ import annotations

import json
import os
from typing import List
import docker
from docker import DockerClient
from docker.models.containers import Container
from loguru import logger

from src.config import (
    root_dir,
    docker_bot_name,
    docker_bot_port,
    docker_action_server_name,
    docker_action_server_port
)


def load_version() -> str:
    logger.info(f'loading version ...')
    with open(os.path.join(root_dir, 'VERSION'), 'r', encoding='utf-8') as f:
        version = f.read().strip()
    return version


def rebuild_and_start_docker(docker_name: str, internal_port: int, port: int, docker_file: str, command: List[str] = []):
    """
    1. stop & remove target docker containers
    2. build the docker image
    3. creating the docker container

    Args:
        docker_name: the name of running container name
        internal_port: the internal port of container
        port: the outsize port of container
        docker_file: the file path of docker file
        command: list of command
    """
    version = load_version()
    client: DockerClient = docker.from_env()

    # 1. stop & remove container
    containers: List[Container] = client.containers.list(
        all=True, ignore_removed=True,
        filters={
            "name": docker_name
        }
    )

    for container in containers:
        logger.info(f'stopping the running docker<{container}>')
        container.stop()
        container.remove()

    # 2. build the docker image
    # with open(os.path.join(root_dir, docker_file), 'rb') as f:
    streams = client.api.build(
        path=root_dir,
        dockerfile=docker_file,
        tag=f'{docker_name}:{version}',
        rm=True,
    )
    for stream in streams:
        stream_log: dict = json.loads(stream.decode(encoding='utf-8'))
        if 'stream' in stream_log:
            log = stream_log['stream']
            logger.info(log.strip())
        else:
            logger.info(stream_log)

    # 2. restart with action server port
    logger.info(f'creating the docker<{docker_name}>')
    client.containers.run(
        command=command,
        image=f'{docker_name}:{version}',
        ports={
            f"{internal_port}/tcp": port
        },
        name=docker_name,
        detach=True
    )


if __name__ == '__main__':
    rebuild_and_start_docker(docker_bot_name, 5005, docker_bot_port, 'Dockerfile')
    rebuild_and_start_docker(docker_action_server_name, 5055, docker_action_server_port, 'ActionServerDockerfile')
