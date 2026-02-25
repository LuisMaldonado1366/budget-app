#!/bin/sh
export $(grep -v '^#' .env | xargs -d '\n')
docker stop ${DOCKER_NAME}
docker logs ${DOCKER_NAME} >> ${DOCKER_NAME}.log
docker compose down
docker rmi ${DOCKER_NAME}-${DOCKER_NAME}
docker compose build
docker compose up -d