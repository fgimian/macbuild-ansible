#!/usr/bin/env bash

# shellcheck source=/dev/null
source $(dirname "$0")/config.sh
# shellcheck source=/dev/null
source $(dirname "$0")/colours.sh

# Ensure that hidden files are matched with wildcards
shopt -s dotglob

# Enable Ctrl-C to work
interrupt_handler()
{
  echo -e "${RED}Aborting sample library extraction, this could leave a library incomplete${ENDC}"
  exit 1;
}
trap interrupt_handler INT

# Check if both the sample libraries source and destination have been defined
if [[ -z $SAMPLE_LIBRARIES_SOURCE || -z $DESTINATION ]]
then
  echo -e "${RED}The SAMPLE_LIBRARIES_SOURCE or DESTINATION variable was not defined${ENDC}"
  exit 1
fi

# Parse command line arguments
VERBOSE=0
if [[ $1 == '-h' || $1 == '--help' ]]
then
  echo -e "Usage: $0 [-h|--help|-v|--verbose]"
  exit
elif [[ $1 == '-v' || $1 == '--verbose' ]]
then
  VERBOSE=1
fi

echo -e "${BLUE}Sample Library Installer${ENDC}"
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

while read -r library_path
do
  # Build the destination base directory
  vendor=$(basename "$(dirname "$library_path")")
  library=$(basename "$library_path" | sed "s/^$vendor //")
  destination_basedir="${DESTINATION}/${vendor}/${library}"

  echo
  echo -e "${BLUE}Installing ${vendor} ${library}${ENDC}"
  [[ $VERBOSE -eq 1 ]] && echo

  # Initialise all variables that may be overriden by each library
  unset base_dir
  unset installer
  unset extract_subdirs
  declare -A extract_subdirs

  # If present, read the library config to override library variables
  # shellcheck source=/dev/null
  [[ -f "${library_path}/.library" ]] && source "${library_path}/.library"

  if [[ ! -z $base_dir ]] && ls "$destination_basedir"/* > /dev/null 2>&1
  then
    echo -e "Moving contents from base directory of ${base_dir}"

    tempdir=$(mktemp -d "${DESTINATION}/samplelibs.XXXXXXXX")
    mv "${destination_basedir}/"* "$tempdir"

    mkdir -p "${destination_basedir}/${base_dir}/"
    mv "${tempdir}/"* "${destination_basedir}/${base_dir}/"

    rmdir "$tempdir"
  fi

  # Track whether anything was needed to be done
  performed_action=0

  # Go through all ZIP and RAR files present in the downloaded library
  while read -r archive
  do
    # Check for multipart archives and only extract part 1
    if [[ $archive =~ \.part[0-9]+\.rar && ! $archive =~ \.part0*1\.rar ]]
    then
      continue
    fi

    performed_action=1

    # Determine the destination (also taking into account sub-directories)
    archive_relative="${archive/$library_path\//}"
    subdir=$(dirname "${archive_relative}")
    [[ $subdir == "." ]] && subdir=''

    if [[ ! -z ${extract_subdirs[$archive_relative]} ]]
    then
      if [[ $subdir != '' ]]
      then
        subdir="${subdir}/${extract_subdirs[$archive_relative]}"
      else
        subdir="${extract_subdirs[$archive_relative]}"
      fi
    fi

    if [[ $subdir != '' ]]
    then
      destination="${destination_basedir}/${subdir}"
    else
      destination="$destination_basedir"
    fi

    # Extract the archive
    if [[ $subdir != '' ]]
    then
      echo -e "${YELLOW}- ${archive_relative} -> ${subdir}${ENDC}"
    else
      echo -e "${YELLOW}- ${archive_relative}${ENDC}"
    fi

    if [[ $VERBOSE -eq 0 ]]
    then
      7z x -aos -o"$destination" -xr\!__MACOSX -xr\!.DS_Store "$archive" > /dev/null
    else
      7z x -aos -o"$destination" -xr\!__MACOSX -xr\!.DS_Store "$archive"
    fi
    [[ $VERBOSE -eq 1 ]] && echo

  done < <(find "$library_path" -type f \( -name "*.zip" -o -name "*.rar" \))

  if [[ ! -z $base_dir ]]
  then
    echo -e "${BLUE}Stripping base directory of ${base_dir}${ENDC}"
    if [[ $VERBOSE -eq 1 ]]
    then
      ls -la "${destination_basedir}/"
    fi

    move_extras=''
    [[ $VERBOSE -eq 1 ]] && move_extras=' -v'
    mv"$move_extras" "${destination_basedir}/${base_dir}/"* "${destination_basedir}/"

    rmdir "${destination_basedir}/${base_dir}/"
  fi

  if [[ ! -z $installer ]]
  then
    performed_action=1

    echo -e "${BLUE}Running installer ${installer}${ENDC}"

    installer_extras=''
    [[ $VERBOSE -eq 1 ]] && installer_extras=' -verbose'
    sudo installer"$installer_extras" -package "${destination_basedir}/${installer}" -target /
  fi

  if [[ $performed_action -eq 1 ]]
  then
    echo -e "${GREEN}Installation of ${vendor} ${library} complete${ENDC}"
  else
    echo -e "${RED}No action required for ${vendor} ${library}${ENDC}"
  fi

done < <(find "$SAMPLE_LIBRARIES_SOURCE" -maxdepth 2 -mindepth 2 -type d)

# Disable passwordless sudo after the extraction has completed
sudo sed -i -e "s/^%admin.*/%admin  ALL=(ALL) ALL/" /etc/sudoers
