# Setup the source of sample libraries from the backup drive attached
if [ -d "/Volumes/Backup Mac 1" ]
then
  SAMPLE_LIBRARIES_SOURCE='/Volumes/Backup Mac 1/Software/Sample Libraries'
elif [ -d "/Volumes/Backup Mac 2" ]
then
  SAMPLE_LIBRARIES_SOURCE='/Volumes/Backup Mac 2/Software/Sample Libraries'
fi

# Set the destination base directory for installing all libraries
DESTINATION='/Volumes/Sound Libraries'
