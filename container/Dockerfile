# SPDX-License-Identifier: MIT
ARG BASE_IMAGE
FROM ${BASE_IMAGE}
USER root
# Only identity changes; native build tools are inherited from the digest pin.
RUN groupmod --gid 1000 builder && usermod --uid 1000 --gid 1000 builder
ARG ARM_GNU_URL
ARG ARM_GNU_SHA256
RUN wget -O /tmp/arm-gnu.tar.xz "${ARM_GNU_URL}" && \
    echo "${ARM_GNU_SHA256}  /tmp/arm-gnu.tar.xz" | sha256sum -c - && \
    mkdir -p /opt/arm-gnu/14.3.rel1 && \
    tar -xJf /tmp/arm-gnu.tar.xz --strip-components=1 -C /opt/arm-gnu/14.3.rel1 && \
    rm /tmp/arm-gnu.tar.xz
ENV LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 TZ=UTC USER=builder LOGNAME=builder
USER 1000:1000
WORKDIR /work
ENTRYPOINT []
