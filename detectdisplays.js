#!/usr/bin/env osascript -l JavaScript

function run(argv) {
  // Open System Preferences and bring the window forward
  var preferences = Application('System Preferences');
  preferences.includeStandardAdditions = true;
  preferences.activate();

  // Reveal the Displays / Display preference pane
  var displays = preferences.panes['Displays'];
  var displayTab = displays.anchors['displaysDisplayTab'];
  displayTab.reveal();

  // Click on the Detect Displays button while holding down option
  var events = Application('System Events');
  displayTabEvents = events.processes['System Preferences'].windows[0];

  // Note that a try / catch block is used to ensure that option is released
  // even if an error occurs
  try {
    events.keyDown('eOpt');
    displayTabEvents.buttons['Detect Displays'].click();
  }
  catch(err) {
    preferences.displayAlert(
      "Unable to detect displays", {message: err.message}
    );
  }
  finally {
    events.keyUp('eOpt');
  }

  // Quit System Preferences
  preferences.quit();
}
