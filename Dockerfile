FROM ubuntu:trusty

ENV DEBIAN_FRONTEND noninteractive

RUN echo 'deb mirror://mirrors.ubuntu.com/mirrors.txt trusty main restricted universe multiverse' > /etc/apt/sources.list; \
echo 'deb mirror://mirrors.ubuntu.com/mirrors.txt trusty-updates main restricted universe multiverse' >> /etc/apt/sources.list; \
echo 'deb mirror://mirrors.ubuntu.com/mirrors.txt trusty-security main restricted universe multiverse' >> /etc/apt/sources.list; \
echo 'deb-src mirror://mirrors.ubuntu.com/mirrors.txt trusty main restricted universe multiverse' >> /etc/apt/sources.list; \
echo 'deb-src mirror://mirrors.ubuntu.com/mirrors.txt trusty-updates main restricted universe multiverse' >> /etc/apt/sources.list; \
echo 'deb-src mirror://mirrors.ubuntu.com/mirrors.txt trusty-security main restricted universe multiverse' >> /etc/apt/sources.list;

RUN apt-get update && apt-get install -y openssh-server supervisor python-pip git

RUN mkdir -p /var/run/sshd /var/log/supervisor
RUN touch /var/log/cron.log
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN pip install pybuilder
ADD . /tmp/auth/
RUN cd /tmp/auth && pyb -X install_dependencies && pyb -X install
RUN apt-get remove git
RUN rm -rfv /tmp/auth
EXPOSE 22 8080

CMD ["/usr/bin/supervisord"]
