FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV POETRY_HOME=/opt/poetry
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get update && apt-get install -y \
    python3.9 \
    python3.9-venv \
    python3.9-dev \
    python3-pip \
    python3-tk \
    curl \
    qt6-base-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Update alternatives to make python3.9 the default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
RUN update-alternatives --set python3 /usr/bin/python3.9

# Upgrade pip and install it for Python 3.9
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.9 get-pip.py
RUN update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip3.9 1
RUN update-alternatives --set pip /usr/local/bin/pip3.9

COPY requirements.txt .

RUN pip install -U pip \
    && pip install pyinstaller \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install "python-xlib>=0.33,<1.0"

WORKDIR /app
COPY . .

CMD ["/bin/bash"]