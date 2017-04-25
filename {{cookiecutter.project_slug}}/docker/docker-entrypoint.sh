#!/bin/bash

db_host=$1
db_port=$2
shift 2
cmd="$@"

function db_ready() {
  nc -z $db_host $db_port>/dev/null 2>&1
}

if [[ -z $db_host ]]; then
  echo "Waiting for datapase skipped"
else
  echo "Waiting for datapase"
  while ! db_ready; do
    >&2 printf "."
    sleep 1
  done
  >&2 echo "Database is up - executing command"
fi


function check_config() {
  python manage.py check
}

if ! check_config; then
  exit 0
fi

# run the command
exec $cmd
