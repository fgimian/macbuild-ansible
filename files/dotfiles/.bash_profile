# Aliases
alias ll="ls -l"

# Avoid duplicates in history
export HISTCONTROL=ignoredups

# Set a more reasonable bash history limit
export HISTSIZE=50000

# Enable bash completion
if [ -f $(brew --prefix)/etc/bash_completion ]; then
	. $(brew --prefix)/etc/bash_completion
fi

# Ensure that redirecting to an existing file doesn't clobber it
shopt -s -o noclobber

# ANSI colours for styling our prompt
RESET="\[\017\]"
NORMAL="\[\033[m\]"
RED="\[\033[1;31m\]"
GREEN="\[\033[1;32m\]"
YELLOW="\[\033[1;33m\]"
BLUE="\[\033[1;34m\]"
PURPLE="\[\033[1;35m\]"
CYAN="\[\033[1;36m\]"
WHITE="\[\033[1;37m\]"

# Prepare the status of the last command for the prompt
RC_GOOD="${GREEN}✓${NORMAL}"
RC_BAD="${RED}✗${NORMAL}"
SELECT="[[ \$? = 0 ]] && echo '${RC_GOOD}' || echo '${RC_BAD}'"

# Build the final prompt
export PS1="\n${RESET}${YELLOW}\u${BLUE} ⚛ ${NORMAL}\h${NORMAL} ${CYAN}\w${NORMAL} \`${SELECT}\` ${PURPLE}\@${NORMAL}\n${YELLOW}➔${NORMAL} "

# Initialise rbenv
eval "$(rbenv init -)"
