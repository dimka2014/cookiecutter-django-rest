#!/bin/bash

env | while read -r line; do  # read STDIN by line
    # split LINE by "="
    IFS="=" read var val <<< ${line}
    # remove existing definition of environment variable, ignoring exit code
    sed --in-place "/^${var}[[:blank:]=]/d" /etc/security/pam_env.conf || true
    # append new default value of environment variable
    echo "${var} DEFAULT=\"${val}\"" >> /etc/security/pam_env.conf
done

echo "*/5 * * * *  root  /usr/local/bin/python /srv/application/manage.py runcrons >> /srv/logs/cron.log 2>&1" >> /etc/crontab

# start cron
service cron start

# trap SIGINT and SIGTERM signals and gracefully exit
trap "service cron stop; kill \$!; exit" SIGINT SIGTERM

# start "daemon"
while true
do
    # watch /srv/logs/cron.log restarting if necessary
    cat /srv/logs/cron.log & wait $!
done
