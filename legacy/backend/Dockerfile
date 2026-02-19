FROM python:3.11-slim

# 1. Install system dependencies (including libicu for .NET)
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    libgmp-dev \
    unzip \
    libicu-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Set ELAN_HOME to a global directory
ENV ELAN_HOME="/usr/local/elan"
ENV PATH="${ELAN_HOME}/bin:${PATH}"

# 3. Install elan and Lean 4
RUN curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh -s -- -y --default-toolchain leanprover/lean4:v4.14.0

# 4. Install Dafny 4.9.0 (self-contained, includes .NET runtime)
ARG DAFNY_VERSION=4.9.0
RUN echo "Installing Dafny ${DAFNY_VERSION}..." && \
    curl -L -o /tmp/dafny.zip \
    "https://github.com/dafny-lang/dafny/releases/download/v${DAFNY_VERSION}/dafny-${DAFNY_VERSION}-x64-ubuntu-20.04.zip" && \
    mkdir -p /opt/dafny && \
    unzip -q /tmp/dafny.zip -d /tmp/dafny_extract && \
    echo "=== Contents after unzip ===" && \
    ls -la /tmp/dafny_extract && \
    # Move everything from the extracted folder to /opt/dafny
    cp -r /tmp/dafny_extract/*/* /opt/dafny/ 2>/dev/null || cp -r /tmp/dafny_extract/* /opt/dafny/ && \
    echo "=== Contents of /opt/dafny ===" && \
    ls -la /opt/dafny && \
    chmod +x /opt/dafny/dafny 2>/dev/null || chmod +x /opt/dafny/Dafny 2>/dev/null || true && \
    rm -rf /tmp/dafny.zip /tmp/dafny_extract

ENV PATH="/opt/dafny:${PATH}"

# 5. Test Dafny (allow failure for now to see full logs)
RUN echo "Testing Dafny..." && \
    /opt/dafny/dafny --version || echo "Dafny test returned non-zero, checking files..." && \
    ls -la /opt/dafny/ && \
    file /opt/dafny/dafny 2>/dev/null || true

# 6. Set working directory
WORKDIR /app

# 7. CACHE-BUST for Lean project
ARG LEAN_PROJECT_VERSION=2026-02-06-v14-dafny-debug
RUN echo "Lean project version: ${LEAN_PROJECT_VERSION}"

# 8. Copy the lean_project
COPY lean_project ./lean_project

# 9. Download Mathlib cache
WORKDIR /app/lean_project
RUN lake update && lake exe cache get

# 10. Test Lean
RUN lean --version && lake --version

# 11. Return to app directory
WORKDIR /app

# 12. Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 13. Cache-bust for backend code
ARG BUILD_VERSION=2026-02-06-v29-pr-fix
RUN echo "Build version: ${BUILD_VERSION}"

# 14. Copy backend code
COPY . ./backend

# 15. Setup environment
EXPOSE 8000
ENV PYTHONPATH=/app

# 16. Entrypoint
RUN chmod +x /app/backend/entrypoint.sh

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]