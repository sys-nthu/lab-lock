FROM mcr.microsoft.com/devcontainers/python:1-3.11

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get -y install --no-install-recommends build-essential git curl ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install a few global dev tools
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir pre-commit
