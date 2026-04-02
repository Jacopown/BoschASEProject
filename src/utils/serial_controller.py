import serial
import time
import threading

class SerialController:
    def __init__(self, port, baudrate=115200, timeout=2.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None
        self.running = False
        self.read_thread = None

    def read_loop(self):
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

    def connect(self):
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


    def disconnect(self):
        self.running = False
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=1.0)

        if self.connection and self.connection.is_open:
            self.set_speed(0)
            self.set_steer(0)

            self.connection.close()
            print("Serial connection closed and device stopped.")

    def send_command(self, command):
        if self.connection is None:
            return
        try:
            self.connection.write(command.encode("utf-8"))
            self.connection.flush()
            print(f"Sent: {command.strip()}")
        except Exception as e:
            print(f"Error sending command: {e}")
            
    def set_power_state_on(self):
        if not self.is_connected():
            return

        command = f"#kl:30;;\r\n"
        self.send_command(command)

    def set_speed(self, speed):
        if not self.is_connected():
            return

        command = f"#speed:{speed};;\r\n"
        self.send_command(command)

    def set_steer(self, steer):
        if not self.is_connected():
            return

        command = f"#steer:{steer};;\r\n"
        self.send_command(command)

    def is_connected(self):
        if not self.connection or not self.connection.is_open:
            print(
                "Warning: Attempted to send command, but serial connection is not open."
            )
            return False
        return True


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
