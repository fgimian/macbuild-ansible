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
brew install ansible --HEAD
/usr/bin/easy_install biplist

# Clone my macbuild repository
git clone git@github.com:fgimian/macbuild.git

# Perform the build
cd macbuild
ansible-playbook macbuild.yml
```

## TODO ##

This list will be long but is my ultimate wish list for this project:

* Bugs & Issues
    - Ensure that Energy Saver is set correctly before running Ansible
    - One of the cask apps requires root and password prompt comes up
    - Docker machine needs vmware fusion to be registered to start the VM
    - Docker machine needs VMware Fusion in /Applications to work
* OSX
    - **Dock**: Setup the Dock with the appropriate icons
    - **LaunchPad**: Setup Launchpad with the appropriate icons and structure
    - **Notification Centre**: Set the order of items and allow permission
    - **Terminal**
        - Find a way to set the font, background color and screen 
          width and height for Terminal
    - **Spotlight**: Set search order in plist com.apple.Spotlight 
      underorderedItems
* Unix Utilities
    - **Shell**: Explore the use of ZSH with Powerline (or at least Powerline 
      with bash)
    - **Git**: Further aliases and touch-ups to gitconfig (possibly 
      integrating cdiff)
* Applications
    - **1Password**: ?
    - **Clear**: ?
    - **Dash**: ?
    - **Dropbox**: ?
    - **Entropy**: ?
    - **f.lux**: ?
    - **Firefox**: ?
    - **GitHub Pulse**: ?
    - **Google Chrome**: ?
    - **iStat Mini**: ?
    - **MacDown**: ?
    - **MPlayerX**: ?
    - **Pixelmator**: ?
    - **Slack**: ?
    - **SourceTree**: ?
    - **Sublime Text 3**: ?
    - **Textual 5**: ?
    - **Transmission**: ?
    - **Transmit**: ?
    - **Twitter**: ?
    - **Vagrant**: ?
    - **VMware Fusion**: ?
    - **VOX**: ?

## Out of Scope at Present ##

At the moment, I don't intend to cover the following:

* Restoring window positions and sizes for apps
* Installing licenses for software
* Signing into accounts for applications

## License ##

Mac Build is released under the **MIT** license. Please see the
[LICENSE](https://github.com/fgimian/macbuild/blob/master/LICENSE) file for
more details.  Feel froo take what you like and use it in your own Ansible
scripts.
