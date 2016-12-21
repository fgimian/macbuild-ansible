#/bin/bash

# Setup the source of sample libraries from the backup drive attached
if [ -d "/Volumes/Backup Mac 1" ]
then
  SAMPLE_LIBRARIES_BASEDIR='/Volumes/Backup Mac 1/Software/Sample Libraries'
elif [ -d "/Volumes/Backup Mac 2" ]
then
  SAMPLE_LIBRARIES_BASEDIR='/Volumes/Backup Mac 2/Software/Sample Libraries'
fi

if [ ! -z "$SAMPLE_LIBRARIES_BASEDIR" ]
then
  echo "Using sample library basedir of ${SAMPLE_LIBRARIES_BASEDIR}"
else
  echo "Unable to find the music software basedir"
  exit 1
fi

DESTINATION='/Volumes/Sound Libraries'

find "$SAMPLE_LIBRARIES_BASEDIR" \
  -maxdepth 1 -mindepth 1 -type d -exec basename {} \; | while read vendor
do
  mkdir -p "${DESTINATION}/${vendor}"
done

find "$SAMPLE_LIBRARIES_BASEDIR" \
  -maxdepth 2 -mindepth 2 -type d | while read library_path
do
  # Build the destination base directory
  vendor=$(basename "$(dirname "$library_path")")
  library=$(basename "$library_path" | sed "s/^$vendor //")
  destination_basedir="${DESTINATION}/${vendor}/${library}"

  # Go through all ZIP and RAR files present in the downloaded library
  find "$library_path" \
    -type f \( -name "*.zip" -o -name "*.rar" \) | while read archive
  do
    extension="${archive##*.}"

    # Determine the sub-directory (and remove . if there's no sub-directory)
    subdir=$(dirname "${archive/$library_path\//}")
    [[ $subdir == "." ]] && subdir=''

    # Create the appropriate destination directory and extract the archive
    mkdir -p "$destination_basedir/$subdir"
    if [[ $extension == "zip" ]]
    then
      true
      unzip -n "$archive" -d "$destination_basedir/$subdir"
    elif [[ $extension == "rar" ]]
    then
      # Check for multipart archives and only extract part 1
      if [[ $archive =~ \.part[0-9]+\. && ! $archive =~ \.part0*1\. ]]
      then
        continue
      fi
      unrar x -o- "$archive" "$destination_basedir/$subdir"
    fi
  done
done
