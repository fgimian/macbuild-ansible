#!/usr/bin/env bash

# shellcheck source=/dev/null
source $(dirname "$0")/config.sh
# shellcheck source=/dev/null
source $(dirname "$0")/colours.sh

# Enable Ctrl-C to work
interrupt_handler()
{
  echo -e "${RED}Aborting Omnisphere STEAM installation extraction, this could leave the library incomplete${ENDC}"
  exit 1;
}
trap interrupt_handler INT

# Check if both the sample libraries source and destination have been defined
if [[ -z $MUSIC_SOFTWARE_SOURCE || -z $DESTINATION ]]
then
  echo -e "${RED}The MUSIC_SOFTWARE_SOURCE or DESTINATION variable was not defined${ENDC}"
  exit 1
fi

echo -e "${BLUE}Spectrasonics STEAM Installer${ENDC}"
echo
echo -e "${GREEN}Music Software Source: ${MUSIC_SOFTWARE_SOURCE}${ENDC}"
echo -e "${GREEN}Destination Path: ${DESTINATION}${ENDC}"

# Build the destination base directory
destination_basedir="${DESTINATION}/Spectrasonics"

echo
echo -e "${BLUE}Installing STEAM library into ${destination_basedir}${ENDC}"
echo

mkdir -p "${destination_basedir}"
rsync --archive --info=progress2 --human-readable --exclude .DS_Store \
  "${MUSIC_SOFTWARE_SOURCE}/Spectrasonics/Spectrasonics Omnisphere v2/STEAM/" \
  "${destination_basedir}"

echo
echo -e "${BLUE}Correcting permissions for files and folders${ENDC}"
find "${destination_basedir}" -type d -exec chmod 755 "{}" \;
find "${destination_basedir}" -type f -exec chmod 644 "{}" \;

echo -e "${BLUE}Creating a STEAM symbolic link to the library path${ENDC}"

rm -f "${HOME}/Library/Application Support/Spectrasonics/STEAM"
ln -s "${destination_basedir}" "${HOME}/Library/Application Support/Spectrasonics/STEAM"

echo -e "${GREEN}Installation of the Omnisphere STEAM library complete${ENDC}"
