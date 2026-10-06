# SPDX-License-Identifier: MIT
ARG BASE_IMAGE
FROM ${BASE_IMAGE}
USER root
# Target compilers are built by the pinned OE recipes, not installed here.
RUN groupmod --gid 1000 builder && usermod --uid 1000 --gid 1000 builder
ENV LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 TZ=UTC USER=builder LOGNAME=builder
USER 1000:1000
WORKDIR /work
ENTRYPOINT []
