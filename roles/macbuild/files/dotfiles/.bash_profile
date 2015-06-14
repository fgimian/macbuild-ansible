# Aliases
alias ll="ls -l"

# Avoid duplicates in history
export HISTCONTROL=ignoredups

# Enable bash completion
if [ -f $(brew --prefix)/etc/bash_completion ]; then
  . $(brew --prefix)/etc/bash_completion
fi

# Ensure that redirecting to an existing file doesn't clobber it
shopt -s -o noclobber

# ANSI colours for styling our prompt
RESET="\[\017\]"
NORMAL="\[\033[0m\]"
RED="\[\033[31;1m\]"
CYAN="\[\033[36;1m\]"
BLUE="\[\033[34;1m\]"
YELLOW="\[\033[33;1m\]"
WHITE="\[\033[37;1m\]"

# Prepare the status of the last command for the prompt
GOOD="${WHITE}✓${NORMAL}"
BAD="${RED}✗${NORMAL}"
SELECT="if [ \$? = 0 ]; then echo \"${GOOD}\"; else echo \"${BAD}\"; fi"

# Build the final prompt
export PS1="${RESET}${YELLOW}\u${BLUE} ⚛ ${NORMAL}\h${NORMAL} ${CYAN}\w${NORMAL} \`${SELECT}\` ${YELLOW}➔${NORMAL} "
