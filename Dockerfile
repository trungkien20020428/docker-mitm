FROM ubuntu

ENV TZ=Europe/Rome
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get install -y \
    iptables \
    tcpdump \
    dsniff \
    iproute2 \
    python3 \
    python3-pip \
    python3-venv \
    tmux \
    dnsutils

# Create and activate virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python packages in the virtual environment
RUN pip3 install --no-cache-dir scapy mitmproxy

CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"
