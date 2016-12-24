# Setup the source of sample libraries from the backup drive attached
if [ -d "/Volumes/Backup Mac 1" ]
then
  SOFTWARE_SOURCE='/Volumes/Backup Mac 1/Software'
elif [ -d "/Volumes/Backup Mac 2" ]
then
  SOFTWARE_SOURCE='/Volumes/Backup Mac 2/Software'
fi
SAMPLE_LIBRARIES_SOURCE="${SOFTWARE_SOURCE}/Sample Libraries"
MUSIC_SOFTWARE_SOURCE="${SOFTWARE_SOURCE}/Music Production"

# Set the destination base directory for installing all libraries
DESTINATION='/Volumes/Sound Libraries'
