FROM ubuntu:trusty

ENV DEBIAN_FRONTEND noninteractive

RUN echo 'deb mirror://mirrors.ubuntu.com/mirrors.txt trusty main restricted universe multiverse' > /etc/apt/sources.list; \
echo 'deb mirror://mirrors.ubuntu.com/mirrors.txt trusty-updates main restricted universe multiverse' >> /etc/apt/sources.list; \
echo 'deb mirror://mirrors.ubuntu.com/mirrors.txt trusty-security main restricted universe multiverse' >> /etc/apt/sources.list; \
echo 'deb-src mirror://mirrors.ubuntu.com/mirrors.txt trusty main restricted universe multiverse' >> /etc/apt/sources.list; \
echo 'deb-src mirror://mirrors.ubuntu.com/mirrors.txt trusty-updates main restricted universe multiverse' >> /etc/apt/sources.list; \
echo 'deb-src mirror://mirrors.ubuntu.com/mirrors.txt trusty-security main restricted universe multiverse' >> /etc/apt/sources.list;

RUN apt-get update && apt-get install -y openssh-server supervisor python-pip

RUN locale-gen "en_US.UTF-8" && dpkg-reconfigure locales


RUN mkdir -p /var/run/sshd /var/log/supervisor
RUN touch /var/log/cron.log
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
ADD target/dist/c-bastion-* /tmp/c-bastion/
RUN ls /tmp/c-bastion
RUN cd /tmp/c-bastion && pip install .
RUN echo 'export PS1="${debian_chroot:+($debian_chroot)}\u@\H:\w\$"' >> /etc/.profile
EXPOSE 22 8080

CMD ["/usr/bin/supervisord"]
