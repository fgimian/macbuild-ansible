#!/usr/bin/env bash

# Remove all items from the dock
echo "Removing all items from the dock"
dockutil --remove all --no-restart

# Add applications to the dock
# TODO: Please add 'Siri' back in before Launchpad when upgrading to Sierra
for app in \
  'ForkLift' \
  'Launchpad' \
  'Google Chrome' \
  'Utilities/Terminal' \
  'Sublime Text' \
  'Dash' \
  'iBooks' \
  'Cubase 8.5' \
  'Logic Pro X' \
  'Focusrite Control' \
  'XLD' \
  'Spotify' \
  'Audio Hijack' \
  'OpenEmu' \
  'Clear' \
  'Textual' \
  'Skype' \
  'Slack' \
  'VMware Fusion' \
  'Twitter' \
  'App Store' \
  'System Preferences'
do
  echo "Adding ${app} to the dock"
  dockutil --add "/Applications/${app}.app" --no-restart
done

# Add the Downloads folder near the trash can
echo "Adding Downloads to the dock"
dockutil --add '~/Downloads' --view fan --display stack --no-restart

# Restart the dock
echo "Restarting the dock"
killall Dock
