from vex import *
import math

"""
This is template code section.
It includes helper functions and class definition of PID and Drive.
"""

# Global variables
brain = Brain()
controller_1 = Controller(ControllerType.PRIMARY)

class PID:
    """
    A class to represent a PID controller.
    
    This class implements a Proportional-Integral-Derivative controller
    for precise robot movement control.
    """
    
    def __init__(self, error, kp, ki, kd, starti, 
                 settle_error, settle_time, timeout):
        """
        Initialize the PID controller.
        
        Args:
            error: Initial error value
            kp: Proportional gain
            kd: Derivative gain (for simple PID)
            ki: Integral gain (for full PID)
            starti: Error threshold to start integrating
            settle_error: Error threshold for settling
            settle_time: Time to be settled before completion
            timeout: Maximum time to run
        """
        self.error = error
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.starti = starti
        self.settle_error = settle_error
        self.settle_time = settle_time
        self.timeout = timeout
        
        # Internal state variables
        self.accumulated_error = 0.0
        self.previous_error = 0.0
        self.output = 0.0
        self.time_spent_settled = 0
        self.time_spent_running = 0
    
    def compute(self, error):
        """
        Compute the PID output for the given error.
        
        Args:
            error: Current error value
            
        Returns:
            float: PID output value
        """
        # Start integrating only when error is below starti threshold
        if abs(error) < self.starti:
            self.accumulated_error += error
        
        # Reset integral term if error crosses zero
        if (error > 0 and self.previous_error < 0) or (error < 0 and self.previous_error > 0):
            self.accumulated_error = 0
        
        # Calculate PID output
        self.output = (self.kp * error + 
                      self.ki * self.accumulated_error + 
                      self.kd * (error - self.previous_error))
        
        self.previous_error = error
        
        # Update settling time tracking
        if abs(error) < self.settle_error:
            self.time_spent_settled += 10  # 10ms increments
        else:
            self.time_spent_settled = 0
        
        self.time_spent_running += 10
        
        return self.output
    
    def is_done(self):
        """
        Check if the PID controller has completed its task.
        
        Returns:
            bool: True if settled or timed out, False otherwise
        """
        # Check for timeout
        if self.time_spent_running > self.timeout and self.timeout != 0:
            return True
        
        # Check if settled for required time
        if self.time_spent_settled > self.settle_time:
            return True
        
        return False


# drive.py

def normalize_360(angle):
    """Normalize angle to 0-360 degrees."""
    return math.fmod(angle + 360, 360)


def normalize_180(angle):
    """Normalize angle to -180 to 180 degrees."""
    return math.fmod(angle + 540, 360) - 180


def threshold(input_val, min_val, max_val):
    """Clamp input value between min and max."""
    if input_val > max_val:
        return max_val
    if input_val < min_val:
        return min_val
    return input_val


def to_volt(percent):
    """Convert percentage to voltage (0-100% to 0-12V)."""
    return percent * 12.0 / 100.0


def deadband(input_val, width):
    """Apply deadband to input value."""
    if abs(input_val) < width:
        return 0
    return input_val


def curve_function(x, curve_scale):
    """Apply curve function to input for smoother control."""
    return (math.pow(2.718, -(curve_scale / 10)) + 
            math.pow(2.718, (abs(x) - 100) / 10) * 
            (1 - math.pow(2.718, -(curve_scale / 10)))) * x


class Drive:
    """
    A class to control the robot's drivetrain.
    
    This class provides methods for controlling robot movement including
    voltage control, PID-based driving, turning, and various drive modes.
    """
    
    def __init__(self, left_drive, right_drive, gyro, wheel_diameter, gear_ratio):
        """
        Initialize the Drive class.
        
        Args:
            left_drive: Left side motor group
            right_drive: Right side motor group
            gyro: Inertial sensor
            wheel_diameter: Diameter of wheels in inches
            gear_ratio: Gear ratio from motor to wheel
        """
        self.wheel_diameter = wheel_diameter
        self.gear_ratio = gear_ratio
        self.drive_in_to_deg_ratio = gear_ratio / 360.0 * math.pi * wheel_diameter
        self.left_drive = left_drive
        self.right_drive = right_drive
        self.gyro = gyro
        
        # PID constants for turning
        self.turn_max_voltage = 0.0
        self.turn_kp = 0.0
        self.turn_ki = 0.0
        self.turn_kd = 0.0
        self.turn_starti = 0.0
        
        # Turn exit conditions
        self.turn_settle_error = 1.5
        self.turn_settle_time = 200
        self.turn_timeout = 1500
        
        # PID constants for driving
        self.drive_max_voltage = 0
        self.drive_kp = 0
        self.drive_ki = 0
        self.drive_kd = 0
        self.drive_starti = 0
        
        # Drive exit conditions
        self.drive_settle_error = 1.0
        self.drive_settle_time = 200
        self.drive_timeout = 2000
        
        # PID constants for maintaining heading while driving
        self.heading_max_voltage = 0.0
        self.heading_kp = 0.0
        self.heading_kd = 0.0
        
        # Constants for arcade drive
        self.k_brake = 0.5
        self.k_turn_bias = 0.5
        self.k_turn_damping_factor = 0.85
        
        # Non-proportional steering response
        self.k_throttle = 5.0
        self.k_turn = 10.0
        
        # Default brake type
        self.stop_mode = BrakeType.COAST
        
        # Control flags
        self.drivetrain_needs_stopped = False
        self.joystick_touched = False
        self.desired_heading = 0
    
    def set_turn_pid(self, turn_max_voltage, turn_kp, turn_ki, turn_kd, turn_starti):
        """Set PID constants for turning."""
        self.turn_max_voltage = turn_max_voltage
        self.turn_kp = turn_kp
        self.turn_ki = turn_ki
        self.turn_kd = turn_kd
        self.turn_starti = turn_starti
    
    def set_drive_pid(self, drive_max_voltage, drive_kp, drive_ki, drive_kd, drive_starti):
        """Set PID constants for driving."""
        self.drive_max_voltage = drive_max_voltage
        self.drive_kp = drive_kp
        self.drive_ki = drive_ki
        self.drive_kd = drive_kd
        self.drive_starti = drive_starti
    
    def set_heading_pid(self, heading_max_voltage, heading_kp, heading_kd):
        """Set PID constants for maintaining heading."""
        self.heading_max_voltage = heading_max_voltage
        self.heading_kp = heading_kp
        self.heading_kd = heading_kd
    
    def set_turn_exit_conditions(self, turn_settle_error, turn_settle_time, turn_timeout):
        """Set exit conditions for turning."""
        self.turn_settle_error = turn_settle_error
        self.turn_settle_time = turn_settle_time
        self.turn_timeout = turn_timeout
    
    def set_drive_exit_conditions(self, drive_settle_error, drive_settle_time, drive_timeout):
        """Set exit conditions for driving."""
        self.drive_settle_error = drive_settle_error
        self.drive_settle_time = drive_settle_time
        self.drive_timeout = drive_timeout
    
    def set_heading(self, orientation_deg):
        """Set the current heading of the robot."""
        self.gyro.set_heading(orientation_deg)
        self.desired_heading = orientation_deg
    
    def get_heading(self):
        """Get the current heading of the robot."""
        return self.gyro.heading()
    
    def get_left_position_in(self):
        """Get the position of the left side of the drivetrain in inches."""
        return self.left_drive.position(RotationUnits.DEG) * self.drive_in_to_deg_ratio
    
    def get_right_position_in(self):
        """Get the position of the right side of the drivetrain in inches."""
        return self.right_drive.position(RotationUnits.DEG) * self.drive_in_to_deg_ratio
    
    def drive_with_voltage(self, left_voltage, right_voltage):
        """Drive the robot with specific voltage for each side."""
        self.left_drive.spin(FORWARD, left_voltage, VoltageUnits.VOLT)
        self.right_drive.spin(FORWARD, right_voltage, VoltageUnits.VOLT)
    
    def turn_to_heading(self, heading, turn_max_voltage=None):
        """Turn the robot to a specific heading."""
        if turn_max_voltage is None:
            turn_max_voltage = self.turn_max_voltage
        
        self.desired_heading = normalize_360(heading)
        turn_pid = PID(normalize_180(heading - self.get_heading()), 
                      self.turn_kp, self.turn_ki, self.turn_kd, self.turn_starti,
                      self.turn_settle_error, self.turn_settle_time, self.turn_timeout)
        
        while not turn_pid.is_done() and not self.drivetrain_needs_stopped:
            error = normalize_180(heading - self.get_heading())
            output = turn_pid.compute(error)
            output = threshold(output, -turn_max_voltage, turn_max_voltage)
            self.drive_with_voltage(output, -output)
            wait(10, TimeUnits.MSEC)
        
        self.left_drive.stop(BrakeType.HOLD)
        self.right_drive.stop(BrakeType.HOLD)
    
    def drive_distance(self, distance, drive_max_voltage=None, heading=None, heading_max_voltage=None):
        """Drive the robot a specific distance."""
        if drive_max_voltage is None:
            drive_max_voltage = self.drive_max_voltage
        if heading is None:
            heading = self.desired_heading
        if heading_max_voltage is None:
            heading_max_voltage = self.heading_max_voltage
        
        self.desired_heading = normalize_360(heading)
        drive_pid = PID(distance, self.drive_kp, self.drive_ki, self.drive_kd, self.drive_starti, self.drive_settle_error, self.drive_settle_time, self.drive_timeout)
        
        heading_pid = PID(normalize_180(self.desired_heading - self.get_heading()),
                         self.heading_kp, 0.0, self.heading_kd, 0.0, 0.0, 0.0, 0.0)
        
        start_average_position = (self.get_left_position_in() + self.get_right_position_in()) / 2.0
        average_position = start_average_position
        
        while not drive_pid.is_done() and not self.drivetrain_needs_stopped:
            average_position = (self.get_left_position_in() + self.get_right_position_in()) / 2.0
            drive_error = distance + start_average_position - average_position
            heading_error = normalize_180(self.desired_heading - self.get_heading())
            drive_output = drive_pid.compute(drive_error)
            heading_output = heading_pid.compute(heading_error)
            
            drive_output = threshold(drive_output, -drive_max_voltage, drive_max_voltage)
            heading_output = threshold(heading_output, -heading_max_voltage, heading_max_voltage)
            
            self.drive_with_voltage(drive_output + heading_output, drive_output - heading_output)
            wait(10, TimeUnits.MSEC)
        
        self.left_drive.stop(BrakeType.HOLD)
        self.right_drive.stop(BrakeType.HOLD)
    
    def set_arcade_constants(self, k_brake, k_turn_bias, k_turn_damping_factor):
        """Set constants for arcade drive."""
        self.k_brake = k_brake
        self.k_turn_bias = k_turn_bias
        self.k_turn_damping_factor = k_turn_damping_factor
    
    def control_arcade(self, y, x):
        """Control the robot in arcade mode."""
        throttle = deadband(y, 5)
        turn = deadband(x, 5) * self.k_turn_damping_factor
        
        turn = curve_function(turn, self.k_turn)
        throttle = curve_function(throttle, self.k_throttle)
        
        left_power = to_volt(throttle + turn)
        right_power = to_volt(throttle - turn)
        
        if self.k_turn_bias > 0:
            if abs(throttle) + abs(turn) > 100:
                old_throttle = throttle
                old_turn = turn
                throttle *= (1 - self.k_turn_bias * abs(old_turn / 100.0))
                turn *= (1 - (1 - self.k_turn_bias) * abs(old_throttle / 100.0))
            left_power = to_volt(throttle + turn)
            right_power = to_volt(throttle - turn)
        
        if abs(throttle) > 0 or abs(turn) > 0:
            self.left_drive.spin(FORWARD, left_power, VoltageUnits.VOLT)
            self.right_drive.spin(FORWARD, right_power, VoltageUnits.VOLT)
            self.drivetrain_needs_stopped = True
        else:
            if self.drivetrain_needs_stopped:
                if self.stop_mode != BrakeType.HOLD:
                    self.left_drive.reset_position()
                    self.right_drive.reset_position()
                    wait(20, TimeUnits.MSEC)
                    self.left_drive.spin(FORWARD, 
                                       -self.left_drive.position(RotationUnits.REV) * self.k_brake, 
                                       VoltageUnits.VOLT)
                    self.right_drive.spin(FORWARD, 
                                        -self.right_drive.position(RotationUnits.REV) * self.k_brake, 
                                        VoltageUnits.VOLT)
                else:
                    self.left_drive.stop(BrakeType.HOLD)
                    self.right_drive.stop(BrakeType.HOLD)
                self.drivetrain_needs_stopped = False
    
    def control_tank(self, left, right):
        """Control the robot in tank mode."""
        left_throttle = curve_function(left, self.k_throttle)
        right_throttle = curve_function(right, self.k_throttle)
        
        if abs(left_throttle) > 0 or abs(right_throttle) > 0:
            self.left_drive.spin(FORWARD, to_volt(left_throttle), VoltageUnits.VOLT)
            self.right_drive.spin(FORWARD, to_volt(right_throttle), VoltageUnits.VOLT)
            self.drivetrain_needs_stopped = True
        else:
            if self.drivetrain_needs_stopped:
                self.left_drive.stop(self.stop_mode)
                self.right_drive.stop(self.stop_mode)
                self.drivetrain_needs_stopped = False
    
    def control_mecanum(self, x, y, acc, steer, drive_lf, drive_rf, drive_lb, drive_rb):
        """Control the robot in mecanum mode."""
        throttle = deadband(y, 5)
        strafe = deadband(x, 5)
        straight = deadband(acc, 5)
        turn = deadband(steer, 5)
        straight = curve_function(straight, self.k_throttle)
        turn = curve_function(turn, self.k_turn)
        
        if turn == 0 and strafe == 0 and throttle == 0 and straight == 0:
            if self.drivetrain_needs_stopped:
                self.left_drive.stop(self.stop_mode)
                self.right_drive.stop(self.stop_mode)
                self.drivetrain_needs_stopped = False
                return
        
        if turn == 0 and straight == 0:
            drive_lf.spin(FORWARD, to_volt(throttle + turn + strafe), VoltageUnits.VOLT)
            drive_rf.spin(FORWARD, to_volt(throttle - turn - strafe), VoltageUnits.VOLT)
            drive_lb.spin(FORWARD, to_volt(throttle + turn - strafe), VoltageUnits.VOLT)
            drive_rb.spin(FORWARD, to_volt(throttle - turn + strafe), VoltageUnits.VOLT)
        else:
            # Arcade drive
            left_power = to_volt(throttle + turn)
            right_power = to_volt(throttle - turn)
            self.left_drive.spin(FORWARD, left_power, VoltageUnits.VOLT)
            self.right_drive.spin(FORWARD, right_power, VoltageUnits.VOLT)
            self.drivetrain_needs_stopped = True
    
    def stop(self, mode):
        """Stop the drivetrain with specified brake mode."""
        self.drivetrain_needs_stopped = True
        self.left_drive.stop(mode)
        self.right_drive.stop(mode)
        self.stop_mode = mode
        self.left_drive.reset_position()
        self.right_drive.reset_position()
        self.drivetrain_needs_stopped = False
    
    def check_status(self):
        """Display heading and distance traveled on controller screen."""
        distance_traveled = (self.get_left_position_in() + self.get_right_position_in()) / 2.0
        heading = self.get_heading()
        Controller(ControllerType.PRIMARY).screen.print("heading: %d, dist: %d", heading, distance_traveled)


'''
Start of competition code section
This section is used to configure the motors, controller buttons, and auton functions .
'''

# Drivetrain definition
# If you only have 4 motors (or mecanum drive), assign left_motor3, right_motor3 to unused ports.
left_motor1 = Motor(Ports.PORT1, GearSetting.RATIO_6_1, True)
left_motor2 = Motor(Ports.PORT2, GearSetting.RATIO_6_1, True)
left_motor3 = Motor(Ports.PORT3, GearSetting.RATIO_6_1, False)

right_motor1 = Motor(Ports.PORT4, GearSetting.RATIO_6_1, False)
right_motor2 = Motor(Ports.PORT5, GearSetting.RATIO_6_1, False)
right_motor3 = Motor(Ports.PORT6, GearSetting.RATIO_6_1, True)

# Inertial sensor for auton turning
# If you do not have an inertial sensor, assign it to an unused port. Ignore the warning at the start of the program.
inertial_1 = Inertial(Ports.PORT10)

# 0: double arcade drive, 1: single arcade, 2: tank drive, 3: mecanum drive
DRIVE_MODE = 0
NUMBER_OF_MOTORS = 6   # Total number of motors, including drivetrain
WHEEL_DIAMETER = 2.75  # in inches
GEAR_RATIO = 0.75      # output (wheel) speed / input (motor) speed

# Create motor groups
left_drive = MotorGroup(left_motor1, left_motor2, left_motor3)
right_drive = MotorGroup(right_motor1, right_motor2, right_motor3)

# Initialize drive chassis
chassis = Drive(
    left_drive,      # Left Motors
    right_drive,     # Right Motors
    inertial_1,      # Inertial Sensor
    WHEEL_DIAMETER,             # Wheel diameter
    GEAR_RATIO              # Gear ratio
)


# define button actions during driver control
def button_r2_action():
    """Brake the drivetrain until the button is released."""
    chassis.stop(BrakeType.HOLD)
    controller_1.rumble(".")
    while controller_1.buttonR2.pressing():
        wait(10, TimeUnits.MSEC)
    chassis.check_status()
    chassis.stop(BrakeType.COAST)

def button_r1_action():
    """Macro action to turn to the right and drive a tile distance"""
    chassis.turn_to_heading(chassis.get_heading() + 90)
    chassis.drive_distance(24)

def setup_button_mapping():
    """Set up button mappings for the controller."""
    controller_1.buttonR2.pressed(button_r2_action)
    controller_1.buttonR1.pressed(button_r1_action)


# The names of the autonomous routines to be displayed in the menu
auton_menu_text = ["auton1", "auton2"]
current_auton_selection = 0  # Index of the currently selected autonomous routine

def sample_auton1():
    """The first autonomous routine."""
    chassis.drive_with_voltage(3, 3)
    wait(1000, TimeUnits.MSEC)
    chassis.stop(BrakeType.BRAKE)

def sample_auton2():
    """The second autonomous routine."""
    chassis.set_heading(180)  # Place the robot backwards
    chassis.turn_to_heading(0, 6)
    chassis.drive_distance(12, 6)

def run_auton_item():
    """Run the selected autonomous routine."""
    if current_auton_selection == 0:
        sample_auton1()
    elif current_auton_selection == 1:
        sample_auton2()



'''
End of the competition code section
'''





'''
This is the main program entry point.
It initializes the robot, sets up the controller and auton selection.
'''

# Global state variables
auton_num = 0
exit_auton_menu = False

def set_chassis_defaults():
    """Reset the chassis constants."""
    # Set the heading of the chassis to the current heading of the inertial sensor
    chassis.set_heading(chassis.gyro.heading())
    
    # Set the drive PID constants for the chassis
    chassis.set_drive_pid(10, 1.5, 0, 10, 0)
    
    # Set the turn PID constants for the chassis
    chassis.set_turn_pid(10, 0.2, .015, 1.5, 7.5)
    
    # Set the heading PID constants for the chassis
    chassis.set_heading_pid(6, 0.4, 1)
    
    # Set the exit conditions for the drive functions
    chassis.set_drive_exit_conditions(1, 300, 3000)
    
    # Set the exit conditions for the turn functions
    chassis.set_turn_exit_conditions(1.5, 300, 3000)
    
    # Set the arcade drive constants for the chassis
    chassis.set_arcade_constants(0.5, 0.5, 0.85)


def check_motors(motor_count, temperature_limit=50):
    """Check motor health and temperature."""
    count = 0
    for i in range(20):
        motor = Motor(i)
        if motor.installed():
            count += 1
            temp = motor.temperature(TemperatureUnits.CELSIUS)
            if temp > temperature_limit:
                controller_1.screen.print("motor %d is %dC", i + 1, temp)
                controller_1.rumble("---")
                return False
    
    if count < motor_count:
        controller_1.screen.print("%d motor is disconnected", motor_count - count)
        controller_1.rumble("---")
        return False
    
    return True


def print_controller_screen(message):
    """Print a message to the controller screen."""
    controller_1.screen.print('{:<24}'.format(message))


def autonomous():
    """Function called when the autonomous period starts."""
    global exit_auton_menu
    exit_auton_menu = True
    run_auton_item()


def print_menu_item():
    """Print the selected autonomous routine to the brain and controller screens."""
    brain.screen.clear_screen()
    brain.screen.set_cursor(3, 1)
    brain.screen.print(auton_menu_text[current_auton_selection])
    controller_1.screen.print(auton_menu_text[current_auton_selection])


def show_auton_menu():
    """Display the autonomous menu on the brain screen."""
    global auton_num, current_auton_selection
    auton_num = len(auton_menu_text)
    
    brain.screen.set_font(FontType.MONO30)
    print_menu_item()
    
    # Loop until autonomous menu is exited
    while not exit_auton_menu:
        if brain.screen.pressing():
            # Wait until finger is lifted
            while brain.screen.pressing():
                wait(20, TimeUnits.MSEC)
            # Cycle through autonomous routines
            current_auton_selection = (current_auton_selection + 1) % auton_num
            print_menu_item()
            controller_1.rumble(".")
        wait(50, TimeUnits.MSEC)
    
    brain.screen.set_font(FontType.MONO20)

def exit_auton():
    """Exit autonomous mode and start driver control."""
    global exit_auton_menu
    exit_auton_menu = True
    chassis.joystick_touched = False
    
    # Clear the brain timer
    brain.timer.clear()

    
    if not chassis.joystick_touched:
        # TODO: some macro actions
        pass
    
    chassis.stop(BrakeType.COAST)


def setup_gyro():
    """Set up and calibrate the gyro."""
    wait(100, TimeUnits.MSEC)
    
    if not chassis.gyro.installed():
        print_controller_screen("inertial sensor failure")
        controller_1.rumble("---")
        wait(2, TimeUnits.SEC)
        return False
    
    chassis.gyro.calibrate()
    # Wait until the inertial sensor is calibrated
    while chassis.gyro.is_calibrating():
        wait(100, TimeUnits.MSEC)
    
    # Rumble the controller to indicate that the gyro is calibrated
    controller_1.rumble(".")
    return True


def pre_auton():
    """Function called before the autonomous period starts."""
    # Set up the gyro
    gyro_setup_success = setup_gyro()
    
    # Check the motors
    motors_setup_success = check_motors(NUMBER_OF_MOTORS)
    
    # Set the parameters for the chassis
    set_chassis_defaults()
    
    # Show the autonomous menu
    if gyro_setup_success and motors_setup_success:
        show_auton_menu()


def usercontrol():
    """User control function called when driver control period starts."""
    # Exit the autonomous menu
    exit_auton()
    
    # Main control loop
    while True:
        if not chassis.joystick_touched:
            if (controller_1.axis1.position() != 0 or controller_1.axis2.position() != 0 or
                controller_1.axis3.position() != 0 or controller_1.axis4.position() != 0):
                chassis.joystick_touched = True
        
        # Control based on drive mode
        if DRIVE_MODE == 0:  # Double arcade
            chassis.control_arcade(controller_1.axis2.position(), controller_1.axis4.position())
        elif DRIVE_MODE == 1:  # Single arcade
            chassis.control_arcade(controller_1.axis3.position(), controller_1.axis4.position())
        elif DRIVE_MODE == 2:  # Tank drive
            chassis.control_tank(controller_1.axis3.position(), controller_1.axis2.position())
        elif DRIVE_MODE == 3:  # Mecanum drive
            chassis.control_mecanum(controller_1.axis4.position(), controller_1.axis3.position(),
                                  controller_1.axis2.position(), controller_1.axis1.position(),
                                  left_motor1, left_motor2, right_motor1, right_motor2)
        
        wait(20, TimeUnits.MSEC)


def main():
    """Main function - entry point of the program."""
    # Register the autonomous and driver control functions
# create competition instance
    comp = Competition(usercontrol, autonomous)
    # Set up button mapping for the controller
    setup_button_mapping()
    
    # Run the pre-autonomous function
    pre_auton()
    
    # Prevent main from exiting with an infinite loop
    while True:
        wait(200, TimeUnits.MSEC)


# Run the main function
if __name__ == "__main__":
    main()
