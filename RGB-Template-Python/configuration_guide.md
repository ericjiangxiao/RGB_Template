# Configuration Guide

Open main.py and search for 'custom code section'. This is where to configure your code using RGB template Python.

---

## Drivetrain Configuration *(Required)*

This section is **mandatory** - you must configure your drivetrain for the robot to function properly.

### Step 1: Configure Motor Ports

Locate the motor definitions and update the port numbers and motor directions:

```python
# Left side motors
left_motor1 = Motor(Ports.PORT1, GearSetting.RATIO_6_1, True)
left_motor2 = Motor(Ports.PORT2, GearSetting.RATIO_6_1, True)
left_motor3 = Motor(Ports.PORT3, GearSetting.RATIO_18_1, False)

# Right side motors
right_motor1 = Motor(Ports.PORT4, GearSetting.RATIO_6_1, False)
right_motor2 = Motor(Ports.PORT5, GearSetting.RATIO_6_1, False)
right_motor3 = Motor(Ports.PORT6, GearSetting.RATIO_18_1, True)

# Inertial sensor
inertial_1 = Inertial(Ports.PORT10)
```

**Action:** Replace `Ports.PORT1`, `Ports.PORT2`, etc. with your actual motor port numbers. Make sure the *motor directions* (True/False) are correct. If you have a 4-motor setup, simply assign the `left_motor3`, `right_motor3` to unused ports.

### Step 2: Set Drive Mode
Locate the drive mode setting:

```python
# 0: double arcade drive, 1: single arcade, 2: tank drive, 3: mecanum drive
DRIVE_MODE = 0
```

**Action:** Set the drive mode value:
- `0` for **Double Arcade** (right stick for forward/backward, left stick for turning)
- `1` for **Single Arcade** (left stick for both forward/backward and turning)
- `2` for **Tank Drive** (left stick for left side, right stick for right side)
- `3` for **Mecanum Drive** (four-wheel independent control for strafing)

### Step 3: Configure Wheel Size and Gear Ratio
Find the Drive constructor in `main.py` and update the wheel diameter and gear ratio parameters:

```python
# Initialize drive chassis
chassis = Drive(
    left_drive,      # Left Motors
    right_drive,     # Right Motors
    inertial_1,      # Inertial Sensor
    4.0,             # Wheel diameter
    1.0              # Gear ratio
)
```

**Action:** 
- Set the wheel diameter (currently `4.0`) to your actual wheel diameter in inches
- Set the gear ratio (currently `1.0`) to your motor-to-wheel gear ratio:
  - `1.0` for direct drive (motor directly connected to wheel)
  - `0.75` for 36:48 gear ratio (36-tooth motor gear, 48-tooth wheel gear)
  - `2.0` for 2:1 gearbox (2 motor rotations = 1 wheel rotation)
  - `0.5` for 1:2 gearbox (0.5 motor rotations = 1 wheel rotation)

---


## Set Total Motor Count
Locate the motor count definition:

```python
# Total number of motors, including drivetrain
NUMBER_OF_MOTORS = 6
```

**Action:** Update to match your total number of motors.

**Motor Monitoring System:**
The program automatically check motor health at the start and will alert the driver if:
- **Disconnected motors**: Controller vibrates with "---" pattern and displays "X motor is disconnected"
- **Overheated motors**: Controller vibrates with "---" pattern and displays "motor X is Y°C" (default temperature limit: 50°C)

**When alerts occur:**
- Controller will vibrate to get driver's attention
- Error message appears on controller screen
- Check motor connections and temperatures immediately


## Button Control Configuration 
### Step 1: Create Button Functions
Add button functions for your subsystems:

```python
def button_l1_action():
    """Intake action when L1 button is pressed."""
    # Add your intake logic here
    while controller_1.button_l1.pressing():
        wait(20, TimeUnits.MSEC)
    # Add your stop logic here
```

**Action:** Create button functions for each action you want to control.

### Step 2: Map Buttons to Functions
Find the button mapping section in the `setup_button_mapping()` function:

```python
def setup_button_mapping():
    """Set up button mappings for the controller."""
    controller_1.button_l1.pressed(button_l1_action)
```

**Action:** Map your button functions to controller buttons.

---

## Autonomous Routines Configuration

### Step 1: Create Auton Functions
Add your autonomous routines:

```python
def sample_auton1():
    """The first autonomous routine."""
    chassis.drive_with_voltage(3, 3)
    wait(1000, TimeUnits.MSEC)
    chassis.stop(BrakeType.BRAKE)

def sample_auton2():
    """The second autonomous routine."""
    chassis.set_heading(180)  # Place the robot backwards
    chassis.drive_distance(-12, 6)
    chassis.turn_to_heading(0, 6)
    chassis.drive_distance(12, 6)
```

**Action:** Write your autonomous routines using the drive APIs.
**Important:** The V5 brain operates on a 12V system. When using voltage-based functions:
- **Maximum voltage**: 12V
- **Recommended range**: 2V to 10V for precise control

### Step 2: Map Auton Functions
Find the `run_auton_item()` function:

```python
def run_auton_item():
    """Run the selected autonomous routine."""
    if current_auton_selection == 0:
        sample_auton1()
    elif current_auton_selection == 1:
        sample_auton2()
```

**Action:** Add your auton functions to the if/elif statements.

### Step 3: Add Menu Text
Find the `auton_menu_text` array:

```python
# The names of the autonomous routines to be displayed in the menu
auton_menu_text = ["auton1", "auton2"]
```

**Action:** Add names for your autonomous routines that will be displayed on the brain screen.

---

## Troubleshooting

### Common Issues:
1. **Motors not responding or in conflict**: Check port numbers and motor directions in main.py
2. **Robot drives in wrong direction**: Reverse motor directions (True/False) in main.py
3. **Buttons not working**: Verify button mappings in setup_button_mapping() function
4. **Auton not running**: Check auton function names in run_auton_item()
5. **Turn sensitivity too high/low**: Adjust arcade constants in set_chassis_defaults() function - higher values increase sensitivity, lower values decrease sensitivity
6. **Controller vibrating with "---" pattern**: Check for disconnected or overheated motors - the system automatically check motor health via check_motors() function
7. **Inertial sensor warnings**: If you don't have an inertial sensor, assign it to an unused port or simply ignore the warning

