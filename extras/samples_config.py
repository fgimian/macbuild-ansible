import os

# Setup the source of sample libraries from the backup drive attached
if os.path.isdir('/Volumes/Backup Mac 1'):
    SOFTWARE_SOURCE = '/Volumes/Backup Mac 1/Software'
elif os.path.isdir('/Volumes/Backup Mac 2'):
    SOFTWARE_SOURCE = '/Volumes/Backup Mac 2/Software'

SAMPLE_LIBRARIES_SOURCE = f'{SOFTWARE_SOURCE}/Sample Libraries'
MUSIC_SOFTWARE_SOURCE = f'{SOFTWARE_SOURCE}/Music Production'

# Set the destination base directory for installing all libraries
DESTINATION_BASEDIR = '/Volumes/Sound Libraries'
