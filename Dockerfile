FROM ubuntu:trusty

ENV DEBIAN_FRONTEND noninteractive

RUN echo 'deb mirror://mirrors.ubuntu.com/mirrors.txt trusty main restricted universe multiverse' > /etc/apt/sources.list; \
echo 'deb mirror://mirrors.ubuntu.com/mirrors.txt trusty-updates main restricted universe multiverse' >> /etc/apt/sources.list; \
echo 'deb mirror://mirrors.ubuntu.com/mirrors.txt trusty-security main restricted universe multiverse' >> /etc/apt/sources.list; \
echo 'deb-src mirror://mirrors.ubuntu.com/mirrors.txt trusty main restricted universe multiverse' >> /etc/apt/sources.list; \
echo 'deb-src mirror://mirrors.ubuntu.com/mirrors.txt trusty-updates main restricted universe multiverse' >> /etc/apt/sources.list; \
echo 'deb-src mirror://mirrors.ubuntu.com/mirrors.txt trusty-security main restricted universe multiverse' >> /etc/apt/sources.list;

RUN apt-get update && apt-get install -y openssh-server supervisor python-pip

RUN mkdir -p /var/run/sshd /var/log/supervisor
RUN touch /var/log/cron.log
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
ADD target/dist/c-bastion-* /tmp/auth/
RUN ls /tmp/auth
RUN cd /tmp/auth/ && python setup.py install
EXPOSE 22 8080

CMD ["/usr/bin/supervisord"]
