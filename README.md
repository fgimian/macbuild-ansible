# Mac Build (using Ansible)
*Automating OS X setup from the ground up*

![](images/osx-yosemite-logo.png)

The goal of this project is fully automate my OS X Yosemite workstation using
Ansible.  I have currently implemented the following:

* **OS X Defaults**: Updating of plist properties for various aspects of OS X 
  such as enabling zoom, configuring Finder and so on.  This uses a custom
  plist module which allows for complex updates of plist files far beyond
  the defaults command.
* **Configuration Files**: Any files that are to be copied to the Mac, 
  including app settings, licenses and dotfiles.
* **Symlinks to Cloud Storage**: This allows you to store certain app 
  configuration in the cloud (e.g. Dropbox, Google Drive .etc) and then
  symlink to it so that your settings are stored and updated in the cloud.
* **Unix Package Installation**: This is being accomplish with the use of
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
  Textual and other applications which are of interest to me.  This is performed using plist properties, files and custom code.

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

* **1Password**: Locate your 1Password database (this setting is stored in an 
  SQLite database)
* **CanOpener**: Install this manually
* **Chrome**: Sign in with your Google account to sync settings
* **Clear**: Enable iCloud (this triggers various actions which I can't 
  automate)
* **Dropbox**: Disable camera uploads (settings are stored a binary)
* **Firefox**: Go through wizard and sign into your Firefox account
* **Microsoft Office**: License this manually
* **Spotify**: Update sources to only include iTunes (settings are stored
  in binary format)
* **ValhallaVintageVerb**: Install this manualy

## TODO

### Bugs

* Docker role can't modify Kitematic SQL database when it hasn't been created
* The new version of Ansible (2.1) doesn't pass variables correctly to my 
  plist module which leads to it failing
* The new version of DMG Audio plugins don't show up correctly in Audio Hijack
* Sudo keeps dropping out during installs due to Homebrew invalidating it
* Google Drive won't be available for symlinking during install

### Features

* **Handlers**: Implementation of handlers to avoid the reboot requirement
* **Audio Hijack**: Implement code to modify plist and add license
* **Finder**: Sidebar containing favourites and so forth
* **Dock**: Setup the Dock with the appropriate icons (via dockutil)
* **LaunchPad**: Setup Launchpad with the appropriate icons and structure
* **Notification Centre**: Set the order of items and allow permission
* **Git**: Further aliases and touch-ups to gitconfig (possibly 
  integrating cdiff)
* **Microsoft Office**: License installation
* **VMware Fusion**: Software settings and licenses

## References

### Projects

* [mac-dev-playbook](https://github.com/geerlingguy/mac-dev-playbook)
* [ansible-modules-plist](https://github.com/mtneug/ansible-modules-plist)
* [legacy-common](https://github.com/osxc/legacy-common)
* [custom-ansible-osx](https://github.com/mtneug/custom-ansible-osx)

### Frameworks

* [superlumic](https://github.com/superlumic/superlumic)
* [battleschool](https://github.com/spencergibb/battleschool)
* [osxc](http://osxc.github.io/)

### Blog Posts

* [Automating your development environment with Ansible](http://www.nickhammond.com/automating-development-environment-ansible/)
* [How to automate your Mac OS X setup with Ansible](https://blog.vandenbrand.org/2016/01/04/how-to-automate-your-mac-os-x-setup-with-ansible/)
* [Using Ansible to automate OSX installs via Superlumic](http://vanderveer.be/2015/09/27/using-ansible-to-automate-osx-installs-via-superlumic.html)
* [How to Bootstrap a new OS X Environment with Ansible](http://flounderedge.com/bootstrap-new-os-x-environment-ansible/)
* [Automation of Installation on Mac w/ Ansible](https://medium.com/@hackyGQ/automation-of-installation-on-mac-w-ansible-21354cce0d7b#.j7rujxwgc)

## License

Mac Build is released under the **MIT** license. Please see the
[LICENSE](https://github.com/fgimian/macbuild/blob/master/LICENSE) file for
more details.  Feel free take what you like and use it in your own Ansible
scripts.
