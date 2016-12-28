#!/usr/bin/env python3
import os
import re
import shlex
import subprocess
import tempfile

import yaml


# Colours
BOLD = '\033[1m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
ENDC = '\033[0m'

# Open /dev/null
DEVNULL = open(os.devnull, 'w')


def run(command, **kwargs):
    return subprocess.run(shlex.split(command), encoding='utf-8', **kwargs)


def sudo(command, **kwargs):
    return run(f'sudo {command}', **kwargs)


def logic_pro_x_content(sample_libraries_source, destination_basedir):
    print()
    print(f'{BOLD}Logic Pro X Content{ENDC}')

    source = f'{sample_libraries_source}/Apple/Apple Logic Pro X Sound Library'
    destination = f'{destination_basedir}/Apple/Apple Logic Pro X Sound Library'

    print()
    print(f'{BLUE}Cleaning up any content on operating system drive{ENDC}')
    for dir in [
        '/Library/Application Support/GarageBand',
        '/Library/Application Support/Logic',
        '/Library/Audio/Apple Loops',
        '/Library/Audio/Impulse Responses'
    ]:
        print(f'- {dir}')
        sudo(f'rm -rf "{dir}"')

    print()
    print(f'{BLUE}Creating directory structure on sample drive{ENDC}')
    for dir in [
        f'{destination}/GarageBand',
        f'{destination}/Logic',
        f'{destination}/Apple Loops',
        f'{destination}/Impulse Responses'
    ]:
        print(f'- {dir}')
        run(f'mkdir -p "{dir}"')

    print()
    print(f'{BLUE}Building symbolic links to new directories{ENDC}')
    for src, dest in [
        (f'{destination}/GarageBand', '/Library/Application Support/GarageBand'),
        (f'{destination}/Logic', '/Library/Application Support/Logic'),
        (f'{destination}/Apple Loops', '/Library/Audio/Apple Loops'),
        (f'{destination}/Impulse Responses', '/Library/Audio/Impulse Responses')
    ]:
        print(f'- {src} -> {dest}')
        sudo(f'ln -s "{src}" "{dest}"')

    packages_proc = run(f'find "{source}" -type f -name "*.pkg"', stdout=subprocess.PIPE)

    for package in packages_proc.stdout.strip().split('\n'):
        print()
        print(f'{BLUE}Running installer {os.path.basename(package)}{ENDC}')
        sudo(f'installer -package "{package}" -target /')

    print()
    print(f'{GREEN}Installation of the Logic Pro X content complete{ENDC}')


def omnisphere_steam_library(music_software_source, destination_basedir):
    print()
    print(f'{BOLD}Spectrasonics STEAM Library{ENDC}')

    home = os.path.expanduser('~')
    source = f'{music_software_source}/Spectrasonics/Spectrasonics Omnisphere v2/STEAM/'
    destination = f'{destination_basedir}/Spectrasonics'
    steam_symlink = f'{home}/Library/Application Support/Spectrasonics/STEAM'

    print()
    print(f'{BLUE}Installing STEAM library into {destination}{ENDC}')
    print()

    run(f'mkdir -p "{destination}"')
    run(
        'rsync --archive --info=progress2 --human-readable --exclude=.DS_Store '
        f'"{source}" "{destination}"'
    )

    print()
    print(f'{BLUE}Correcting permissions for files and folders in {destination}{ENDC}')
    run(f'find "{destination}" -type d -exec chmod 755 "{{}}" ;')
    run(f'find "{destination}" -type f -exec chmod 644 "{{}}" ;')

    print()
    print(f'{BLUE}Cleaning up any existing STEAM symbolic link{ENDC}')
    print(f'- {steam_symlink}')
    run(f'mkdir -p "{os.path.dirname(steam_symlink)}"')
    run(f'rm -f "{steam_symlink}"')

    print()
    print(f'{BLUE}Creating a STEAM symbolic link to the library path{ENDC}')
    print(f'- {destination} -> {steam_symlink}')
    run(f'ln -s "{destination}" "{steam_symlink}"')

    print()
    print(f'{GREEN}Installation of the Omnisphere STEAM library complete{ENDC}')


def kontakt_libraries_and_drum_samples(sample_libraries_source, destination_basedir):
    print()
    print(f'{BOLD}Kontakt Libraries & Drum Samples{ENDC}')

    library_paths_proc = run(
        f'find "{sample_libraries_source}" -maxdepth 2 -mindepth 2 -type d',
        stdout=subprocess.PIPE
    )

    for library_path in library_paths_proc.stdout.strip().split('\n'):
        # Find all ZIP and RAR files present in the downloaded library
        archives_proc = run(
            f'find "{library_path}" -type f ( -name "*.zip" -o -name "*.rar" )',
            stdout=subprocess.PIPE
        )

        if not archives_proc.stdout:
            continue

        # Determine the vendor of the library
        vendor = os.path.basename(os.path.dirname(library_path))

        # Determine the library name and remove the vendor name to remove redundancy
        library = os.path.basename(library_path)
        if library.startswith(f'{vendor} '):
            library = library[len(f'{vendor} '):]

        # Build the destination base directory
        destination = f'{destination_basedir}/{vendor}/{library}'

        print()
        print(f'{BLUE}Processing {vendor} {library}{ENDC}')

        # If present, read the library config to override library variables
        library_config_path = f'{library_path}/.library.yaml'
        library_config = {}

        if os.path.isfile(library_config_path):
            print(f'{BLUE}Loading the library YAML config file{ENDC}')
            with open(library_config_path) as f:
                try:
                    library_config = yaml.load(f)
                except yaml.scanner.ScannerError:
                    print(
                        f'{RED}Unable to load the library config file due to a syntax error{ENDC}'
                    )

        base_dir = library_config.get('base_dir', None)
        installer = library_config.get('installer', None)
        extract_subdirs = library_config.get('extract_subdirs', [])

        if base_dir and os.path.isdir(destination) and os.listdir(destination):
            print(f'Moving contents from base directory of {base_dir}')

            tempdir = tempfile.mkdtemp(prefix='samplelibs.', dir=destination)
            run(f'mv "{destination}/"* "{tempdir}"')

            run(f'mkdir -p "{destination}/{base_dir}/"')
            run(f'mv "{tempdir}/"* "{destination}/{base_dir}/"')

            run(f'rmdir "{tempdir}"')

        # Track whether anything was needed to be done
        performed_action = False

        print(f'{BLUE}Extracting library archives{ENDC}')

        for archive in archives_proc.stdout.strip().split('\n'):
            # Check for multipart archives and only extract part 1
            if (
                re.search('\.part[0-9]+\.rar$', archive) and
                not re.search('\.part0*1\.rar$', archive)
            ):
                continue

            performed_action = True

            # Determine the destination (also taking into account sub-directories)
            archive_relative = archive.replace(f'{library_path}/', '')
            subdir = os.path.dirname(archive_relative)
            if subdir == '.':
                subdir = ''

            if archive_relative in extract_subdirs:
                if subdir and base_dir:
                    subdir = f'{subdir}/{base_dir}/{extract_subdirs[archive_relative]}'
                elif subdir:
                    subdir = f'{subdir}/{extract_subdirs[archive_relative]}'
                else:
                    subdir = f'{extract_subdirs[archive_relative]}'

            if subdir:
                destination_subdir = f'{destination}/{subdir}'
            else:
                destination_subdir = destination

            # Extract the archive
            if subdir:
                print(f'{YELLOW}- {archive_relative} -> {subdir}{ENDC}')
            else:
                print(f'{YELLOW}- {archive_relative}{ENDC}')

            run(
                f'7z x -aoa -o"{destination_subdir}" -xr!__MACOSX -xr!.DS_Store "{archive}"',
                stdout=DEVNULL
            )

        if base_dir:
            if os.path.isdir(f'{destination}/{base_dir}'):
                print(f'{BLUE}Stripping base directory of {base_dir}{ENDC}')
                run(f'mv "{destination}/{base_dir}/"* "{destination}/"')
                run(f'rmdir "{destination}/{base_dir}/"')
            else:
                print(f'{RED}The base directory {base_dir} does not exist{ENDC}')

        if installer:
            if os.path.isfile('{destination}/{installer}'):
                performed_action = True
                print(f'{BLUE}Running installer {installer}{ENDC}')
                sudo(f'installer -package "{destination}/{installer}" -target /')
            else:
                print(f'{RED}The installer {installer} does not exist{ENDC}')

        if performed_action:
            print(f'{GREEN}Installation of {vendor} {library} complete{ENDC}')
        else:
            print(f'{RED}No action required for {vendor} {library}{ENDC}')

    print()
    print(f'{GREEN}Installation of Kontakt libraries and drum samples complete{ENDC}')


def main():
    # Check if both the sample libraries source and destination have been defined
    try:
        from samples_config import (
            SAMPLE_LIBRARIES_SOURCE, MUSIC_SOFTWARE_SOURCE, DESTINATION_BASEDIR
        )
    except ImportError:
        print(
            f'{RED}The SAMPLE_LIBRARIES_SOURCE, MUSIC_SOFTWARE_SOURCE or DESTINATION_BASEDIR '
            f'variable was not defined{ENDC}'
        )
        exit(1)

    print()
    print(f'{BOLD}Sample Library Installer{ENDC}')
    print()
    print(f'{GREEN}Sample Library Source: {SAMPLE_LIBRARIES_SOURCE}{ENDC}')
    print(f'{GREEN}Destination Base Path: {DESTINATION_BASEDIR}{ENDC}')

    sudo_enabled = False
    return_code = 0

    try:
        # Prompt the user for their sudo password (if required)
        sudo_check_proc = sudo('-vn', stderr=DEVNULL)
        if sudo_check_proc.returncode != 0:
            print()
            sudo('-v')

        # Enable passwordless sudo for the run
        sudo('sed -i -e "s/^%admin.*/%admin  ALL=(ALL) NOPASSWD: ALL/" /etc/sudoers')
        sudo_enabled = True

        # Install the various sample libraries
        logic_pro_x_content(
            sample_libraries_source=SAMPLE_LIBRARIES_SOURCE,
            destination_basedir=DESTINATION_BASEDIR
        )
        omnisphere_steam_library(
            music_software_source=MUSIC_SOFTWARE_SOURCE,
            destination_basedir=DESTINATION_BASEDIR
        )
        kontakt_libraries_and_drum_samples(
            sample_libraries_source=SAMPLE_LIBRARIES_SOURCE,
            destination_basedir=DESTINATION_BASEDIR
        )

    except KeyboardInterrupt:
        print(
            f'{RED}Aborting sample library installation, this could leave a '
            f'library incomplete{ENDC}'
        )
        return_code = 1

    finally:
        # Disable passwordless sudo after the installation has completed or has been cancelled
        if sudo_enabled:
            sudo('sed -i -e "s/^%admin.*/%admin  ALL=(ALL) ALL/" /etc/sudoers')

        print()

    exit(return_code)


if __name__ == '__main__':
    main()
