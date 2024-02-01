#!/bin/bash

set -e

VER="0.1" # версия пакета
LOG_TAG="DEBUG" # метка журнала
STAGE=0 # индикатор прогресса
LOG_PATH="build.log"
DATE="$(date -R)"

# использовать версию пакета и метку журнала
while getopts "t:v:" opt; do
    case "$opt" in
        t) if [ "$OPTARG" != "$LOG_TAG" ]; then
              LOG_TAG="$OPTARG"
              echo "$DATE $LOG_TAG: log tag changed to $LOG_TAG"
           fi ;;
        v) VER="$OPTARG"
           echo "$DATE $LOG_TAG: $VER is used for version" ;;
        *) echo "$DATE ERROR: invalid option specified, it will be skipped" ;;
    esac
done

# минимизировать вывод в зависимости от метки журнала
if [ "$LOG_TAG" != "DEBUG" ]; then
    echo "$DATE $LOG_TAG: terminal output is minimized and $LOG_PATH is used for logging"
    exec 3>&1 > "$LOG_PATH" 2>&1
else
    exec 3>&1
fi

# cобрать в отдельном контейнере
STAGE=$((STAGE + 1))
echo "$DATE $LOG_TAG: [STAGE $STAGE] start building separate container for packaging" >&3
if ! docker build -t rnf-backend:build -f Dockerfile.build .; then
    echo "$DATE ERROR: [STAGE $STAGE] failed to build container" >&3
    exit $?
else
    echo "$DATE $LOG_TAG: [STAGE $STAGE] container built" >&3
fi
STAGE=$((STAGE + 1))
echo "$DATE $LOG_TAG: [STAGE $STAGE] start building package" >&3
if ! docker run --name backend-build -e VER="$VER" rnf-backend:build; then
    echo "$DATE ERROR: [STAGE $STAGE] failed to build package" >&3
    docker rm backend-build
    exit $?
else
    echo "$DATE $LOG_TAG: [STAGE $STAGE] package built" >&3
fi

# копировать пакет на хост
STAGE=$((STAGE + 1))
echo "$DATE $LOG_TAG: [STAGE $STAGE] trying to copy package to host" >&3
if ! docker cp backend-build:/app/packaging/rnf-backend_"$VER"_all.deb app/packaging/; then
    echo "$DATE ERROR: [STAGE $STAGE] failed to copy package to host" >&3
    exit $?
else
    echo "$DATE $LOG_TAG: [STAGE $STAGE] package copied" >&3
fi

# запустить
STAGE=$((STAGE + 1))
echo "$DATE $LOG_TAG: [STAGE $STAGE] start building serving container" >&3
if ! docker build -t rnf-backend --build-arg version="$VER" -f Dockerfile .; then
    echo "$DATE ERROR: [STAGE $STAGE] failed to build container" >&3
    exit $?
else
    echo "$DATE $LOG_TAG: [STAGE $STAGE] container built" >&3
fi

STAGE=$((STAGE + 1))
echo "$DATE $LOG_TAG: [STAGE $STAGE] start server at http://localhost:8000/" >&3
if ! ( docker run -d --privileged --name backend -p 8000:8000 rnf-backend systemd && \
    docker exec -d backend dpkg -i /package/rnf-backend_"$VER"_all.deb ); then
    echo "$DATE ERROR: [STAGE $STAGE] failed to start server" >&3
    docker rm backend
    exit $?
else
    echo "$DATE $LOG_TAG: [STAGE $STAGE] server started" >&3
fi