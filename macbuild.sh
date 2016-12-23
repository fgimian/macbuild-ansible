#!/bin/bash

# Prompt the user for their sudo password
sudo -v

# Enable passwordless sudo for the macbuild run
sudo sed -i -e "s/^%admin.*/%admin  ALL=(ALL) NOPASSWD: ALL/" /etc/sudoers

# Install Homebrew
if ! which brew > /dev/null 2>&1
then
    echo "Installing Homebrew"
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" < /dev/null
fi

# Install Python
if ! brew list python > /dev/null 2>&1
then
    echo "Installing Python 2.x"
    brew install python
fi

# Install Ansible (using pip is the officially supported way)
if ! pip2 show ansible > /dev/null 2>&1
then
    echo "Installing Ansible"
    pip2 install ansible
fi

# Install biplist to allow manipulation of plist files
if ! pip2 show biplist > /dev/null 2>&1
then
    echo "Installing biplist"
    pip2 install biplist
fi

# Setup the source of music production software from the backup drive attached
if [ -d "/Volumes/Backup Mac 1" ]
then
  export HOMEBREW_CASK_MUSIC_SOFTWARE_BASEDIR='/Volumes/Backup Mac 1/Software/Music Production'
elif [ -d "/Volumes/Backup Mac 2" ]
then
  export HOMEBREW_CASK_MUSIC_SOFTWARE_BASEDIR='/Volumes/Backup Mac 2/Software/Music Production'
fi

if [ ! -z "$HOMEBREW_CASK_MUSIC_SOFTWARE_BASEDIR" ]
then
  echo "Using cask music software basedir of ${HOMEBREW_CASK_MUSIC_SOFTWARE_BASEDIR}"
else
  echo "Unable to find the music software basedir"
fi

# Perform the build
ansible-playbook -i localhost, -e ansible_python_interpreter=/usr/local/bin/python local.yml && \

# Set Terminal settings
./extras/terminal.js

# Disable passwordless sudo after the macbuild is complete
sudo sed -i -e "s/^%admin.*/%admin  ALL=(ALL) ALL/" /etc/sudoers
