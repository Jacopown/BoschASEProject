"""
This module provides the `SerialController` class to manage communication with
a serial device, such as a microcontroller for a robotic vehicle.

It handles connecting, disconnecting, sending commands, and reading responses in a
non-blocking way by using a separate thread for reading. The class is designed
to be a robust wrapper around the `pyserial` library for controlling hardware.
"""
import serial
import time
import threading

class SerialController:
    """
    Manages a serial connection to a device for sending commands and reading output.

    This class encapsulates the logic for establishing and closing a serial connection,
    sending formatted commands, and continuously reading incoming data on a background
    thread to avoid blocking the main application.

    Attributes:
        port (str): The serial port to connect to (e.g., '/dev/ttyACM0' or 'COM3').
        baudrate (int): The communication speed.
        timeout (float): The read timeout in seconds.
        connection (serial.Serial): The underlying `pyserial` connection object.
        running (bool): A flag to control the background reading thread.
        read_thread (threading.Thread): The background thread for reading serial data.
    """
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 2.0) -> None:
        """
        Initializes the SerialController.

        Args:
            port (str): The serial port name (e.g., '/dev/ttyACM0').
            baudrate (int): The baud rate for the serial communication.
            timeout (float): Read timeout value in seconds.
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None
        self.running = False
        self.read_thread = None

    def read_loop(self) -> None:
        """
        Continuously reads from the serial port in a background thread.

        This method reads incoming data, splits it by newline characters, decodes it,
        and prints it to the console. It runs until the `running` flag is set to False.
        """
        buffer = b""
        while self.running and self.connection and self.connection.is_open:
            try:
                if self.connection.in_waiting > 0:
                    buffer += self.connection.read(self.connection.in_waiting)

                    while b'\n' in buffer:
                        line, buffer = buffer.split(b'\n', 1)
                        try:
                            decoded_line = line.decode("utf-8").strip()
                            if decoded_line:
                                print(f"Received: {decoded_line}")
                        except UnicodeDecodeError:
                            print(f"Received (raw bytes): {line}")
                else:
                    time.sleep(0.01)
            except OSError:
                break
            except Exception as e:
                print(f"Unexpected read error: {e}")
                break

    def connect(self) -> None:
        """
        Establishes the serial connection and starts the reading thread.

        Raises:
            serial.SerialException: If the connection to the specified port fails.
        """
        try:
            self.connection = serial.Serial(
                self.port, self.baudrate, timeout=self.timeout
            )
            time.sleep(2)
            print(f"Successfully connected to {self.port} at {self.baudrate} baud.")
            
            self.running = True
            self.read_thread = threading.Thread(target=self.read_loop, daemon=True)
            self.read_thread.start()
            
        except serial.SerialException as e:
            print(f"Error: Failed to connect to {self.port}. Exception: {e}")
            raise


    def disconnect(self) -> None:
        """
        Stops the device, closes the serial connection, and stops the reading thread.
        
        Ensures the device is safely stopped by setting speed and steer to 0 before
        closing the connection.
        """
        self.running = False
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=1.0)

        if self.connection and self.connection.is_open:
            self.set_speed(0)
            self.set_steer(0)

            self.connection.close()
            print("Serial connection closed and device stopped.")

    def send_command(self, command: str) -> None:
        """
        Sends a command string to the serial device.

        The command is encoded to UTF-8 before sending.

        Args:
            command (str): The command string to send.
        """
        if self.connection is None:
            return
        try:
            self.connection.write(command.encode("utf-8"))
            self.connection.flush()
            print(f"Sent: {command.strip()}")
        except Exception as e:
            print(f"Error sending command: {e}")
            
    def set_power_state_on(self) -> None:
        """Sends the command to turn the device's power on."""
        if not self.is_connected():
            return

        command = f"#kl:30;;\r\n"
        self.send_command(command)

    def set_speed(self, speed: float) -> None:
        """
        Sends a command to set the device's speed.

        Args:
            speed (int or float): The desired speed value.
        """
        if not self.is_connected():
            return

        command = f"#speed:{speed};;\r\n"
        self.send_command(command)

    def set_steer(self, steer: float) -> None:
        """
        Sends a command to set the device's steering angle.

        Args:
            steer (int or float): The desired steering value.
        """
        if not self.is_connected():
            return

        command = f"#steer:{steer};;\r\n"
        self.send_command(command)

    def is_connected(self) -> bool:
        """
        Checks if the serial connection is currently open and active.

        Returns:
            bool: True if connected, False otherwise.
        """
        if not self.connection or not self.connection.is_open:
            print(
                "Warning: Attempted to send command, but serial connection is not open."
            )
            return False
        return True

    def set_brake(self, steer: int = 0) -> None:
        """
        Sets the vehicle in brake state while allowing to set the steering.

        Args:
            steer (int): The steering angle in degrees to maintain during braking.
                        Range: (-23, +23). Default is 0 (straight).
        """
        if not self.is_connected():
            return 
        
        command = f"#brake:{steer};;\r\n"
        self.send_command(command)

if __name__ == "__main__":
    PORT = "/dev/ttyACM0"  # Update this to your actual serial port, e.g.,

    controller = SerialController(port=PORT)
    try:
        controller.connect()

        controller.set_power_state_on()

        controller.set_speed(70)
        time.sleep(0.5)
        controller.set_speed(-70)
        time.sleep(0.5)
        controller.set_speed(0)
        time.sleep(0.5)
        controller.set_steer(-15.0)
        time.sleep(0.5)

    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        controller.disconnect()
