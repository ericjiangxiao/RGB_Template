# RGB BOTS Python Template 
From Haverford Robotics Team 169X (The Cavalry) and RGB Bots Team 99009A (the little red pony).

This project provides a simple Python template for VEX V5 robotics. It offers APIs for PID based automonous driving control and auton screen selections,  supports tank, arcade and mecanum drive mode, and automatically checks motor health. The library is designed specifically as a learning tool for middle school teams who are beginning their journey with VEX Python programming.

## Installation
*   **Prerequisites:** Before you begin, make sure:
    - You have [VSCode with VEX extension](https://kb.vex.com/hc/en-us/categories/360002333191-V5?sc=vs-code-extension) installed.
*   **Dowload Source Code:** 
    - Download [main.py](src/main.py) from the github repository 
    - [Create a new v5 Python project](https://kb.vex.com/hc/en-us/articles/20146074601748-Creating-VS-Code-Projects-for-V5#:~:text=Select%20the%20'New%20Project'%20button,and%20select%20the%20corresponding%20icon)
    - Copy downloaded main.py to the src folder of the created project and overwrite the existing file

## Configuration
Open main.py, search for "competition code section". In this section, edit your own code.

For detailed step-by-step configuration instructions, see [Configuration Guide](configuration_guide.md).

For general VEX API reference, check out [Python commands in VEXcode V5](https://api.vex.com/v5/home/python/index.html).

## How to Tune PID Parameters
Read the introduction and tutorial for PID controllers by [George Gillard](https://smithcsrobot.weebly.com/uploads/6/0/9/5/60954939/pid_control_document.pdf). 
- Set kp, kd and ki all to zero
- Increase the kp until the drive overshoots its target a bit
- Increase the kd until the overshoot is corrected
- Increase the ki to speed up the settle

## Programming Interfaces of the library

### Voltage Limits
- **Important:** The VEX V5 brain operates on a 12V system. All voltage-based functions have a maximum voltage of 12V.
- **Recommended range**: 3V to 10V for precise control.

### Drive APIs
The `Drive` class provides a set of APIs to control the robot's movement.

### `drive_with_voltage(left_voltage, right_voltage)`

This is the most basic drive function. It sets the voltage for the left and right sides of the drivetrain directly. 

**Example:**

```python
# Drive forward at half speed for 1 second
chassis.drive_with_voltage(6, 6)
wait(1000, TimeUnits.MSEC)
# rotate slowly for 1 second
chassis.drive_with_voltage(-4, 4)
wait(1000, TimeUnits.MSEC)
chassis.stop(BrakeType.COAST)
```

### `turn_to_heading(heading, turn_max_voltage=None)`

This API turns the robot to a specific heading using a PID controller.

**Parameters:**
- `heading`: Target heading in degrees
- `turn_max_voltage`: Optional maximum voltage for the turn (uses default if not specified)

**Examples:**

```python
# Simple turn to 90 degrees
chassis.turn_to_heading(90)

# Slower, more accurate turn
chassis.turn_to_heading(-90, 6)
```

### `drive_distance(distance, drive_max_voltage=None, heading=None, heading_max_voltage=None)`

This API drives the robot a specific distance using a PID controller, with options for maintaining a heading.

**Parameters:**
- `distance`: Distance to drive in inches (positive = forward, negative = backward)
- `drive_max_voltage`: Optional maximum voltage for driving (uses default if not specified)
- `heading`: Optional target heading to maintain while driving
- `heading_max_voltage`: Optional maximum voltage for heading correction (recommended < 6V for consistent results)

**Examples:**

```python
# Drive forward 24 inches
chassis.drive_distance(24)

# Drive backward 24 inches with a maximum voltage of 8
chassis.drive_distance(-24, 8)

# Drive forward 24 inches while turning to a heading of 45 degrees
chassis.drive_distance(24, 10, 45, 4)
```

### `set_heading(orientation_deg)`

This API sets the robot to a specific heading, e.g. when the autonomous routine starts.

**Parameters:**
- `orientation_deg`: Target heading in degrees

**Examples:**

```python
# Set robot initial heading to 90 degrees
chassis.set_heading(90)
```
