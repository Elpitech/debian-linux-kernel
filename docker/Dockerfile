FROM debian:bullseye-slim

RUN echo 'deb-src http://deb.debian.org/debian bullseye main' >> /etc/apt/sources.list && \
    apt-get update -y && apt-get upgrade -y && \
    apt-get install -y build-essential fakeroot devscripts unifdef cpio nano git
RUN apt-get build-dep -y linux

ARG uid
RUN useradd -ms /bin/bash -u $uid builder && mkdir /home/builder/workspace
USER builder

WORKDIR /home/builder/workspace
