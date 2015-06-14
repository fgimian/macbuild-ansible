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
NORMAL="\e[0m"
RED="\e[31;1m"
GREEN="\e[32;1m"
YELLOW="\e[33;1m"
BLUE="\e[34;1m"
PURPLE="\e[35;1m"
CYAN="\e[36;1m"
WHITE="\e[37;1m"

# Prepare the status of the last command for the prompt
RC_GOOD="${GREEN}✓${NORMAL}"
RC_BAD="${RED}✗${NORMAL}"
SELECT="[[ \$? = 0 ]] && echo '${RC_GOOD}' || echo '${RC_BAD}'"

# Build the final prompt
export PS1="\n${RESET}${YELLOW}\u${BLUE} ⚛ ${NORMAL}\h${NORMAL} ${CYAN}\w${NORMAL} \`${SELECT}\` ${PURPLE}\@${NORMAL}\n${YELLOW}➔${NORMAL} "
