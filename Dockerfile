FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV POETRY_HOME=/opt/poetry
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get update && apt-get install -y \
    python3.9 \
    python3.9-venv \
    python3.9-dev \
    python3-pip \
    libfontconfig1-dev \
    libfreetype6-dev \
    libx11-dev \
    libx11-xcb-dev \
    libxext-dev \
    libxfixes-dev \
    libxi-dev \
    libxrender-dev \
    libxkbcommon-dev \
    libxkbcommon0 \
    libxkbcommon-x11-dev \
    libatspi2.0-dev \
    '^libxcb.*-dev' \
    libxcb-cursor-dev \
    libxcb-xinerama0 \
    libglib2.0-0 \
    python3-tk \
    libkrb5-3 \
    libdbus-1-3 \
    curl \
    libcairo2-dev \
    libgl1-mesa-glx \
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
    && pip install "python-xlib>=0.33,<1.0" \
    && pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY . .

CMD ["/bin/bash"]