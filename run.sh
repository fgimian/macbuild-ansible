#!/bin/bash

# Install Homebrew
if ! which brew > /dev/null 2>&1
then
    echo "Installing Homebrew"
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
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

# Prompt the user for their sudo password
sudo -v

# Escalate sudo rights and keep them open
while true
do
    sleep 60
    sudo -v
done &

# Ensure that the background process is killed if the user cancels the run
sudo_bg_pid=$!
trap 'kill $sudo_bg_pid && wait $sudo_bg_pid 2> /dev/null' INT TERM

# Create a temporary inventory to avoid warnings
inventory=$(mktemp -t macbuild-inventory)
echo localhost > "$inventory"

# Perform the build
ansible-playbook -i "$inventory" macbuild.yml
rm -f "$inventory"

# Set Terminal settings
./terminal.js
