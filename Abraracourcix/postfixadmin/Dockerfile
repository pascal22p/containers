FROM postfixadmin:3.3.10-apache

RUN apt-get update && apt-get install -y dovecot-core
RUN rm /etc/dovecot/conf.d/10-ssl.conf

