FROM 123456789012.dkr.ecr.us-east-1.amazonaws.com/jump-auth-base:latest

RUN mkdir -p /var/run/sshd /var/log/supervisor
RUN touch /var/log/cron.log
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN pip install pybuilder
ADD . /tmp/auth
RUN cd /tmp/auth && pyb install_dependencies
EXPOSE 22 8080
ENV http_proxy ""
ENV https_proxy ""
CMD ["/usr/bin/supervisord"]
