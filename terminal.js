#!/usr/bin/env osascript -l JavaScript

function run(argv) {
  // Obtain the terminal application
  terminal = Application('Terminal');

  // Set the font
  terminal.defaultSettings.fontName = 'Source Code Pro for Powerline';
  terminal.defaultSettings.fontSize = 15;
  terminal.defaultSettings.fontAntialiasing = true;

  // Set the window size
  terminal.defaultSettings.numberOfRows = 26;
  terminal.defaultSettings.numberOfColumns = 130;

  // Set the background color
  terminal.defaultSettings.backgroundColor = {red: 0.05, green: 0.05, blue: 0.05};
}
