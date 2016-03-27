#!/bin/bash

# Prompt the user for their sudo password
sudo -v

# Install Homebrew
if ! which brew > /dev/null 2>&1
then
    echo "Installing Homebrew"
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" < /dev/null
    echo "Copy any installers you have to /Library/Caches/Homebrew and press any key to continue..."
    read -r
fi

# Install Python
if ! brew list python > /dev/null 2>&1
then
    echo "Installing Python 2.x"
    brew install python
fi

# Install Ansible (using pip is the officially supported way)
if ! pip show ansible > /dev/null 2>&1
then
    echo "Installing Ansible"
    pip install ansible
fi

# Install biplist to allow manipulation of plist files
if ! pip show biplist > /dev/null 2>&1
then
    echo "Installing biplist"
    pip install biplist
fi

# Perform the build
ansible-playbook -i localhost, local.yml

# Set Terminal settings
./terminal.js
