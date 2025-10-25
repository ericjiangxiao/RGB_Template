# Test Auton Button System

## Overview

The test auton system allows you to test autonomous routines during driver control with step-by-step execution capability. It uses multiple buttons for navigation and execution control.

## Complete Flow of Actions

### 1. Entering Test Mode
**Button: A** (hold within first 5 seconds of program startup)

```cpp
    controller1.rumble("-");
    printControllerScreen("Test mode: ON");
    waitUntil(!controller1.ButtonA.pressing());
    showAutonMenu();
    autonTestMode = true;
```

**What happens:**
- ✅ Controller rumbles with "-" pattern
- ✅ Displays "Test Mode: ON" on controller screen
- ✅ Shows auton menu
- ✅ Sets `autonTestMode = true`

---

### 2. Navigating the Auton Menu
**Button: Right** (when already in test mode)

```cpp
if (autonTestMode) {
  controller1.rumble(".");
  // if in test mode, scroll through the auton menu
  currentAutonSelection = (currentAutonSelection + 1) % autonNum;
  showAutonMenu();
}
```

**What happens:**
- ✅ Increments `currentAutonSelection` (cycles through available autons)
- ✅ Calls `showAutonMenu()` which displays menu on brain and controller screens
- ✅ Shows current selection (e.g., "auton1", "auton2", "auton_skill")

**Navigation Options:**
- **Right Button**: Move forward in menu (auton1 → auton2 → auton_skill → auton1...)

---

### 3. Step-by-Step Navigation
**Button: Down** (when in test mode)

```cpp
// Down Button - Next Step  
if (autonTestMode) {
  controller1.rumble(".");
  autonTestStep++;
  controller1.Screen.print("Step: %d           ", autonTestStep);
}
```

**What happens:**
- ✅ **Down Button**: Increases step number
- ✅ Controller rumbles to confirm action
- ✅ Displays current step on controller screen

---

### 4. Running the Selected Auton/Step
**Button: A** (when in test mode)

```cpp
void buttonAAction()
{
  if (autonTestMode) 
  {
    // If in test mode, run the selected autonomous routine for testing and displays the run time.
    controller(primary).rumble(".");
    double t1 = Brain.Timer.time(sec);
    runAutonItem(); 
    double t2 = Brain.Timer.time(sec);
    char timeMsg[30];
    sprintf(timeMsg, "run time: %.0f", t2-t1);
    printControllerScreen(timeMsg);
    chassis.stop(coast);
  }
}
```

**What happens:**
- ✅ Checks if in test mode
- ✅ Records start time
- ✅ Calls `runAutonItem()` which executes the selected auton
- ✅ Calculates and displays run time
- ✅ Stops chassis with coast
- ✅ Controller rumbles to confirm execution

---

### 5. Step-by-Step Execution System

**Auton Functions with Step Control:**
```cpp
void sampleSkill() {
  if (autonTestStep == 1) {
    chassis.turnToHeading(180);
    if (!continueAutonStep()) return; // Stop here if in test mode
  }
  if (autonTestStep == 2) {
    chassis.driveDistance(5);
    chassis.turnToHeading(chassis.getHeading() + 90);
    if (!continueAutonStep()) return; // Stop here if in test mode
  } 
  if(autonTestStep == 3) {
    chassis.turnToHeading(chassis.getHeading() - 90);
    chassis.driveDistance(-5);
  }
}
```

**Step Control Function:**
```cpp
bool continueAutonStep() {
  autonTestStep++;
  if (autonTestMode) {
    return false; // Stop execution in test mode
  }
  return true; // Continue execution in normal mode
}
```

**What happens:**
- ✅ Each step checks `autonTestStep` to determine what to execute
- ✅ `continueAutonStep()` increments step and returns false in test mode
- ✅ This causes the function to return early, stopping execution
- ✅ In normal mode, execution continues through all steps


---

### 6. Abort auto driving
- ✅ At any time, move joystick to abort the auto driving.

---

### 7. Show status
**Button: R2**
- ✅ If hold this button while driving, upon releasing it, the controller displays current heading and distance driven.

## Button Summary

| Button | Action | When |
|--------|--------|------|
| **A** | Enter test mode | Within 5 seconds of startup |
| **Right** | Next auton in menu | When in test mode |
| **Left** | Change drive mode | When in test mode |
| **Down** | Next step | When in test mode |
| **A** | Run selected auton/step | When in test mode |
| **Movement of Joystick** | Abort auto driving | Always |
| **R2** | Show status | Always |

---

## Example Flow for two autons

1. **Start program** → Robot boots up
2. **Hold A** (within 5 seconds) → Enter test mode, see "auton1" on screen
3. **Press Right** → See "auton2" on screen  
4. **Press Down** → Step increases to 1
5. **Press A** → Run step 1 of auton2, see "run time: X" on screen
6. **Press Right** → See "auton1" on the screen and step resets to 0
7. **Press A** → Run step 0 of auton1

---

## 🔧 Technical Details

### Global Variables
```cpp
bool autonTestMode = false;         // Indicates if in test mode
int currentAutonSelection = 0;      // Current auton selection
int autonTestStep = 0;              // Current step in auton
int autonNum;                       // Total number of autons (automatically calculated)
```

### Key Functions
- `autonTestButtonCheck()`: all test button checks
- `registerAutonTestButtons()`: run checks of auton testing button press in the background thread 
- `continueAutonStep()`: Controls step progression

### Button Registration
The auton testing buttons are automatically registered in the main function:

```cpp
int main() {
  // Register the autonomous and driver control functions.
  Competition.autonomous(autonomous);
  Competition.drivercontrol(usercontrol);

  // Register auton testing button callbacks
  registerAutonTestButtons();


```

### Menu System
The menu system automatically calculates the number of available autons based on the `autonMenuText` array in `autons.cpp`:

```cpp
char const * autonMenuText[] = {
    "auton1",
    "auton2", 
    "auton_skill"
};
```


---

## Tips for Using

1. **Quick Testing**: Use this system to rapidly test auton changes
2. **Step-by-Step**: Use Down buttons to navigate through steps
3. **Menu Navigation**: Use Right to quickly switch between different autons
4. **Auton Execution**: Use A button to run the selected auton and see execution time
5. **Timing**: Remember to press A within 5 seconds of program startup
6. **Safety**: Driver control can abort the auton execution at any time

---

## Benefits

- **Rapid Iteration**: Quickly test different auton routines in one code base
- **Step Debugging**: Navigate through individual steps for precise testing
- **Menu System**: Easy navigation between multiple autons
- **Timing Feedback**: See execution time for performance optimization

This system allows you to quickly test and iterate on autonomous routines with precise step-by-step control.
