// vex.h includes all of the headers for the VEX V5 library
#include "vex.h"

// All vex classes and functions are in the vex namespace
using namespace vex;

// A global instance of competition
competition Competition;


// ------------------------------------------------------------------------
//               Code below are not specific to any game
// ------------------------------------------------------------------------
  
void pollCommandMessages()
{
  static FILE* serialPort = nullptr;
  
  // Open port once
  if (serialPort == nullptr) {
    serialPort = fopen("/dev/serial1", "r");
    if (serialPort == nullptr) return;
  }

  char buffer[256];
  if (fgets(buffer, sizeof(buffer), serialPort) == nullptr) return;

  // Simple trim and check
  std::string command(buffer);
  command.erase(0, command.find_first_not_of(" \t\r\n"));
  command.erase(command.find_last_not_of(" \t\r\n") + 1);
  
  if (command.empty()) return;

  controller(primary).rumble(".");
  printControllerScreen(command.c_str());

  // Parse command
  size_t spacePos = command.find(' ');
  std::string cmd = command.substr(0, spacePos);
  std::string params = spacePos != std::string::npos ? command.substr(spacePos + 1) : "";

  // Execute command
  if (cmd == "drive") {
    chassis.driveDistance(atof(params.c_str()), 6);
  } else if (cmd == "turn") {
    chassis.turnToHeading(atof(params.c_str()), 6);
  } else if (cmd == "set_heading") {
    chassis.setHeading(atof(params.c_str()));
  }
  
  chassis.stop(coast);
}

int main() {
  // Register the autonomous and driver control functions.
  Competition.autonomous(autonomous);
  Competition.drivercontrol(usercontrol);
  
  // Run the pre-autonomous function.
  pre_auton();

  // Set up button mapping
  setupButtonMapping();

  // Prevent main from exiting with an infinite loop.
  while (true) {
    // comment out the following line to disable remote command processing
    pollCommandMessages();
    wait(200, msec);
  }
}
