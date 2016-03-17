#!/usr/bin/env osascript -l JavaScript

function run(argv) {
  // Obtain the terminal application
  var terminal = Application('Terminal');

  // Set the font
  terminal.defaultSettings.fontName = 'Source Code Pro for Powerline';
  terminal.defaultSettings.fontSize = 16;
  terminal.defaultSettings.fontAntialiasing = true;

  // Set the window size
  terminal.defaultSettings.numberOfRows = 26;
  terminal.defaultSettings.numberOfColumns = 130;

  // Set the background color
  terminal.defaultSettings.backgroundColor = [0.05, 0.05, 0.05];
}
