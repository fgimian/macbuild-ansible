# Mac Build (using Ansible)
*Automating OS X setup from the ground up*

![](images/osx-yosemite-logo.png)

The goal of this project is fully automate my OS X Yosemite workstation using
Ansible.  I Have currently implemented the following:

* **OS X Defaults**: Updating of plist properties for various aspects of OS X 
  such as enabling zoom, configuring Finder and so on.
* **Configuration Files**: Any files that are to be copied to the Mac, 
  including app settings and dotfiles.
* **Terminal Package Installation**: This is being accomplish with the use of
  [homebrew](https://github.com/Homebrew/homebrew).
* **Terminal Customisation**: Setting up the Terminal using JXA.
* **Desktop Application Installation**: This is being performed with the use
  of [homebrew-cask](https://github.com/caskroom/homebrew-cask).
* **Appstore Application Check**: Since there is currently no way to automate
  installation of App Store applications, I perform a check to see if the app
  is installed, and notify the user that they must install it from the App 
  Store if it isn't.
* **Development Setup**: Installation of development languages like Python,
  Ruby, Node.js and Go, along with development environments like docker and
  Vagrant.  This also includes installation of related packages for each
  technology.
* **Application Settings**: Automating configuration of Sublime Text, MacDown,
  Textual and other applications which are of interest to me.  This is performed
  using plist properties and custom code.
* **Project Setup**: Cloning and setup of certain GitHub projects I work on.

The plist module is a modified version of
[Matthias Neugebauer's plist module](https://github.com/mtneug/ansible-modules-plist).

## Building the System

Run the following in your Terminal to use my configuration:

```bash
git clone https://github.com/fgimian/macbuild.git
cd macbuild
./macbuild.sh
```

It is strongly suggested that you reboot your Mac after the first run
of this.

## Manual Configuration

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

## TODO

I'm really close to covering everything I wish to automate, however the
following items remain:

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

## Out of Scope

At the moment, I don't intend to cover the following:

* Restoring window positions and sizes for apps
* Installing licenses for software
* Signing into accounts for applications

## License

Mac Build is released under the **MIT** license. Please see the
[LICENSE](https://github.com/fgimian/macbuild/blob/master/LICENSE) file for
more details.  Feel free take what you like and use it in your own Ansible
scripts.
