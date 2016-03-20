# Shortcut Aliases
alias ll='ls -l'

# GNU Aliases
alias find='gfind'
alias locate='glocate'
alias oldfind='goldfind'
alias updatedb='gupdatedb'
alias xargs='gxargs'

# Set the default editor to Sublime Text
export EDITOR='subl -w'

# Avoid duplicates in history
export HISTCONTROL=ignoredups

# Set a more reasonable bash history limit
export HISTSIZE=50000

# Enable bash completion
if [ -f $(brew --prefix)/etc/bash_completion ]; then
	source $(brew --prefix)/etc/bash_completion
fi

# Ensure that redirecting to an existing file doesn't clobber it
shopt -s -o noclobber

# Enable the powerline shell
powerline_path=$(python -c "import os, powerline; print(os.path.dirname(powerline.__file__))")
source "${powerline_path}/bindings/bash/powerline.sh"

# Initialise rbenv
eval "$(rbenv init -)"

# Setup go
export GOPATH=/usr/local/lib/go
export PATH=$PATH:$GOPATH/bin
