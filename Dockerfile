FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    unzip \
    libgmp-dev \
    libicu-dev \
    && rm -rf /var/lib/apt/lists/*

# Lean toolchain (pinned)
ENV ELAN_HOME=/usr/local/elan
ENV PATH="${ELAN_HOME}/bin:${PATH}"
RUN curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf \
    | sh -s -- -y --default-toolchain leanprover/lean4:v4.16.0

# Dafny (pinned)
ARG DAFNY_VERSION=4.9.1
RUN curl -L -o /tmp/dafny.zip \
    "https://github.com/dafny-lang/dafny/releases/download/v${DAFNY_VERSION}/dafny-${DAFNY_VERSION}-x64-ubuntu-20.04.zip" \
    && mkdir -p /opt/dafny \
    && unzip -q /tmp/dafny.zip -d /tmp/dafny \
    && cp -r /tmp/dafny/*/* /opt/dafny/ 2>/dev/null || cp -r /tmp/dafny/* /opt/dafny/ \
    && chmod +x /opt/dafny/dafny 2>/dev/null || true \
    && rm -rf /tmp/dafny /tmp/dafny.zip
ENV PATH="/opt/dafny:${PATH}"

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY lean_project ./lean_project
COPY .argusignore.example ./

ENV PYTHONPATH=/app
CMD ["python", "-m", "src.adapters.cli", "--mode", "ci", "--repo-path", "."]

