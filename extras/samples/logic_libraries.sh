#!/usr/bin/env bash

# shellcheck source=/dev/null
source $(dirname "$0")/config.sh
# shellcheck source=/dev/null
source $(dirname "$0")/colours.sh

# Enable Ctrl-C to work
interrupt_handler()
{
  echo -e "${RED}Aborting Logic Pro X library installation, this could leave a library incomplete${ENDC}";
  exit 1;
}
trap interrupt_handler INT

# Check if both the sample libraries source and destination have been defined
if [[ -z $SAMPLE_LIBRARIES_SOURCE || -z $DESTINATION ]]
then
  echo -e "${RED}The SAMPLE_LIBRARIES_SOURCE or DESTINATION variable was not defined${ENDC}"
  exit 1
fi

echo -e "${BLUE}Apple Logic Pro X Library Installer${ENDC}"
echo
echo -e "${GREEN}Sample Library Source: ${SAMPLE_LIBRARIES_SOURCE}${ENDC}"
echo -e "${GREEN}Destination Path: ${DESTINATION}${ENDC}"

# Prompt the user for their sudo password (if required)
if ! sudo -vn 2> /dev/null
then
  echo
  sudo -v
fi

# Enable passwordless sudo for the run
sudo sed -i -e "s/^%admin.*/%admin  ALL=(ALL) NOPASSWD: ALL/" /etc/sudoers

echo
echo -e "${BLUE}Cleaning up any content on operating system drive${ENDC}"
sudo rm -rf \
  '/Library/Application Support/GarageBand' \
  '/Library/Application Support/Logic' \
  '/Library/Audio/Apple Loops' \
  '/Library/Audio/Impulse Responses'

echo -e "${BLUE}Creating directory structure on sample drive${ENDC}"
mkdir -p \
  "${DESTINATION}/Apple/Apple Logic Pro X Sound Library/Apple Loops" \
  "${DESTINATION}/Apple/Apple Logic Pro X Sound Library/GarageBand" \
  "${DESTINATION}/Apple/Apple Logic Pro X Sound Library/Impulse Responses" \
  "${DESTINATION}/Apple/Apple Logic Pro X Sound Library/Logic"

echo -e "${BLUE}Building symbolic links to new directories${ENDC}"
sudo ln -s \
  "${DESTINATION}/Apple/Apple Logic Pro X Sound Library/GarageBand" \
  '/Library/Application Support/GarageBand'
sudo ln -s \
  "${DESTINATION}/Apple/Apple Logic Pro X Sound Library/Logic" \
  '/Library/Application Support/Logic'
sudo ln -s \
  "${DESTINATION}/Apple/Apple Logic Pro X Sound Library/Apple Loops" \
  '/Library/Audio/Apple Loops'
sudo ln -s \
  "${DESTINATION}/Apple/Apple Logic Pro X Sound Library/Impulse Responses" \
  '/Library/Audio/Impulse Responses'

while read -r package
do
  echo
  echo -e "${BLUE}Running installer $(basename "$package")${ENDC}"
  sudo installer -package "$package" -target "/"
done < <(find "${SAMPLE_LIBRARIES_SOURCE}/Apple/Apple Logic Pro X Sound Library" -type f -name "*.pkg")

# Disable passwordless sudo after the installation has completed
sudo sed -i -e "s/^%admin.*/%admin  ALL=(ALL) ALL/" /etc/sudoers
