#!/usr/bin/env osascript -l JavaScript

function run(argv) {
  // Obtain the terminal application
  var terminal = Application('Terminal');

  // Grab the Pro profile
  proSettings = terminal.settingsSets.Pro;

  // Set the font
  proSettings.fontName = 'Source Code Pro for Powerline';
  proSettings.fontSize = 16;
  proSettings.fontAntialiasing = true;

  // Set the background colour (with no opacity)
  proSettings.backgroundColor = [0, 0, 0];

  // Set the window size
  proSettings.numberOfRows = 26;
  proSettings.numberOfColumns = 135;

  // Set the default profile to Pro
  terminal.defaultSettings = proSettings;

  // Set the profile to Pro for all open windows and tabs
  for (var window of terminal.windows()) {
    for (var tab of window.tabs()) {
      tab.currentSettings = proSettings;
    }
  }
}
