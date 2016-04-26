FROM ubuntu:trusty

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get -q update && apt-get -q -y install --no-install-recommends \
    curl \
    httping \
    iputils-tracepath \
    netcat \
    openssh-client \
    openssh-server \
    python-gevent \
    python-pip \
    python-virtualenv \
    screen \
    siege \
    socat \
    supervisor \
    tmux \
    vim-nox \
    wget \
    zsh

RUN locale-gen en_US.UTF-8 de_DE.UTF-8 && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8


RUN mkdir -p /var/run/sshd /var/log/supervisor && \
    touch /var/log/cron.log && \
    rm -f /etc/skel/.bashrc /root/.bashrc

RUN echo "dash dash/sh boolean false" | debconf-set-selections && \
    dpkg-reconfigure dash

COPY configs/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

COPY configs/profile.sh /etc/profile.d/zzz_c-bastion.sh

COPY configs/sshrc.sh /etc/ssh/sshrc
RUN echo '    SendEnv USERHOME_DATA' >> /etc/ssh/ssh_config && \
    echo 'AcceptEnv USERHOME_DATA' >> /etc/ssh/sshd_config

COPY configs/screenrc /etc/screenrc
COPY target/dist/c-bastion-* /tmp/c-bastion/
RUN ls /tmp/c-bastion && \
    cd /tmp/c-bastion && \
    pip install . && \
    rm -rf /tmp/c-bastion

EXPOSE 22 8080

CMD ["/usr/bin/supervisord"]
