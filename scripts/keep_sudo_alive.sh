#!/bin/bash

# Re-validate sudo priveleges every minute to keep sudo open
while true
do
  sudo -v
  sleep 60
done
