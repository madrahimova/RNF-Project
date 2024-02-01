FROM debian:latest

ARG version
ENV VER "$version"

RUN mkdir -p /package
RUN mkdir -p /opt/rnf/data

WORKDIR /package

COPY app/packaging/rnf-backend_"$VER"_all.deb .
COPY app/core/data /opt/rnf/data

# установить systemd для запуска сервиса
# NOTE: в официальных сборках Debian в качестве системы инициализации используется init
#       см. https://server-gu.ru/build-docker-container-with-systemd/
#       в силу ограничений init (см. https://www.opennet.ru/opennews/art.shtml?num=30412) лучше использовать systemd
RUN apt update
RUN apt install -y systemd

# установить зависимости
RUN apt install -y python3 postgresql-client

CMD ["bash"]