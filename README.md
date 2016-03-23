# Mac Build (using Ansible) #
*Automating OS X setup from the ground up*

![](images/osx-yosemite-logo.png)

The goal of this project is fully automate my OS X Yosemite workstation using
Ansible.  I Have currently implemented the following:

* **OS X Defaults**: Updating of defaults for various aspects of OS X such as
  enabling zoom, configuring Finder and so on.
* **Dot Files**: Configuration of .bash_profile, .gitconfig and other dot 
  files.
* **Terminal Package Installation**: This is being accomplish with the use of
  [homebrew](https://github.com/Homebrew/homebrew).
* **Desktop Application Installation**: This is being performed with the use
  of [homebrew-cask](https://github.com/caskroom/homebrew-cask).
* **Appstore Application Check**: Since there is currently no way to automate
  installation of App Store applications, I perform a check to see if the app
  is installed, and notify the user that they must install it from the App 
  Store if it isn't.
* **Python Base Setup**: Installation of essentials such as virtualenv are
  being performed using [pip](https://github.com/pypa/pip).
* **Application Settings**: Automating configuration of Sublime Text, MacDown,
  Textual and other applications which are of interest to me.

The plist module is a modified version of
[Matthias Neugebauer's plist module](https://github.com/mtneug/ansible-modules-plist).

## Building your System ##

Run the following in your Terminal to use my configuration:

```bash
# Setup your SSH keys and add them to GitHub
ssh-keygen

# Install Homebrew
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# Install Ansible
brew install ansible
/usr/bin/easy_install biplist

# Clone my macbuild repository
git clone git@github.com:fgimian/macbuild.git

# Copy any installers you have already downloaded to the Homebrew cache
# (e.g. larger installers like VMware Fusion and Microsoft Office)
cp <filename> /Library/Caches/Homebrew

cd macbuild

# Escalate sudo rights and keep them open
sudo -v
./keep_sudo_alive.sh &

# Perform the build
ansible-playbook macbuild.yml

# Set Terminal settings
./terminal.js

# Terminate the sudo keepalive script
pkill -f keep_sudo_alive.sh
```

## Manual Configuration ##

Some settings (outside those in the "Out of Scope") section must be set 
manually due to excessive automation complexity.

**1Password**: Locate your 1Password database (this is stored in an SQLite 
  database)
**Chrome**: Sign in with your Google account to sync settings
**Clear**: Enable iCloud (this triggers various actions which I can't automate)
**Dropbox**: Disable camera uploads (settings are stored a binary)
**Firefox**: Go through wizard and sign into your Firefox account
**Spotify**: Update sources to only include iTunes (settings are stored
  in binary format)

## TODO ##

This list will be long but is my ultimate wish list for this project:

* Bugs & Issues
    - Fonts can't be installed by homebrew cask when home directory is on
      a different volume
* OS X
    - **Finder**: Sidebar containing favourites and so forth
    - **Dock**: Setup the Dock with the appropriate icons
      (see `~/Library/Preferences/com.apple.dock.plist` for settings)
    - **LaunchPad**: Setup Launchpad with the appropriate icons and structure
    - **Notification Centre**: Set the order of items and allow permission
* Unix Utilities
    - **Git**: Further aliases and touch-ups to gitconfig (possibly 
      integrating cdiff)
* Applications (local settings)
    - **VMware Fusion**: Difficult due to the fact I want a custom keyboard
      profile for Windows machines

## Out of Scope ##

At the moment, I don't intend to cover the following:

* Restoring window positions and sizes for apps
* Installing licenses for software
* Signing into accounts for applications

## License ##

Mac Build is released under the **MIT** license. Please see the
[LICENSE](https://github.com/fgimian/macbuild/blob/master/LICENSE) file for
more details.  Feel froo take what you like and use it in your own Ansible
scripts.
