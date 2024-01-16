FROM postfixadmin:3.3.13-apache

RUN apt-get update && apt-get install -y dovecot-core
RUN rm /etc/dovecot/conf.d/10-ssl.conf
RUN ln -sf /proc/self/fd/1 /var/log/apache2/access.log && \
    ln -sf /proc/self/fd/1 /var/log/apache2/error.log
