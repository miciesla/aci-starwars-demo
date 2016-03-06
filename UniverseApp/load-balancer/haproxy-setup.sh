#!/bin/bash

if [ ! -f /etc/haproxy/haproxy.cfg ]; then

  # Install haproxy
  /usr/bin/apt-get -y install haproxy

  # Configure haproxy
  cat > /etc/default/haproxy <<EOD
# Set ENABLED to 1 if you want the init script to start haproxy.
ENABLED=1
# Add extra flags here.
#EXTRAOPTS="-de -m 16"
EOD
  cat > /etc/haproxy/haproxy.cfg <<EOD
  global
  	log /dev/log	local0
  	log /dev/log	local1 notice
  	chroot /var/lib/haproxy
  	user haproxy
  	group haproxy
  	daemon

  defaults
  	log	global
  	mode	http
  	option	httplog
  	option	dontlognull
          contimeout 5000
          clitimeout 50000
          srvtimeout 50000
  	errorfile 400 /etc/haproxy/errors/400.http
  	errorfile 403 /etc/haproxy/errors/403.http
  	errorfile 408 /etc/haproxy/errors/408.http
  	errorfile 500 /etc/haproxy/errors/500.http
  	errorfile 502 /etc/haproxy/errors/502.http
  	errorfile 503 /etc/haproxy/errors/503.http
  	errorfile 504 /etc/haproxy/errors/504.http

  frontend http-in
      bind *:80
      default_backend webservers


  backend webservers
     balance roundrobin
     option httpchk
     option forwardfor
     option http-server-close
     server web1 10.67.17.202:80 maxconn 32 check
     server web2 10.67.17.203:80 maxconn 32 check

  listen admin
      bind *:8080
      stats enable
EOD

  cp /etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg.orig
  /usr/sbin/service haproxy restart
fi
