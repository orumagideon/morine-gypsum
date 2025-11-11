FROM python:3.12-slim

# Install system deps (add any needed libs for pdf generation here)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment and use it for installs to avoid system-level conflicts
ENV VENV_PATH=/opt/venv
RUN python -m venv ${VENV_PATH}
ENV PATH="${VENV_PATH}/bin:$PATH"

WORKDIR /app

# Copy and install Python deps into the venv.
# Use --root-user-action=ignore to suppress pip's root-user warning in container builds.
COPY requirements.txt ./
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

# Copy project files
COPY . .

# Create a non-root user and give ownership of the app directory
RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app

ENV PYTHONUNBUFFERED=1
ENV PORT=8080

EXPOSE ${PORT}

# Run as non-root
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]
