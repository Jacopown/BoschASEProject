"""
Manual driving script for the Bosch model car using the keyboard.

Controls:
  W -> increase speed
  S -> decrease speed
  A -> steer left
  D -> steer right
  Q -> brake
  SPACE -> reset speed and steer to 0
  CTRL+C -> stop the program
"""
import sys
import readchar

from src.utils.serial_controller import SerialController

PORT = "/dev/ttyACM0"

# State
speed = 0      # range: -500 to +500 (mm/s)
steer = 0      # range: -230 to +230 (deg * 10)

controller = SerialController(port=PORT)

try:
    controller.connect()
    controller.set_power_state_on()
    print("W/S: Speed | A/D: Steering | Q: Brake | SPACE: reset | ^C : stop the program")

    while True:
        key = readchar.readkey().lower()

        # Update state based on keypress
        if key == 'w':
            speed = min(speed + 50, 500)
        elif key == 's':
            speed = max(speed - 50, -500)
        elif key == 'a':
            steer = max(steer - 20, -230)
        elif key == 'd':
            steer = min(steer + 20, 230)
        elif key == 'q':
            speed = 0
            # set_brake expects degrees (range -23..+23), steer is in deg*10
            controller.set_brake(steer // 10)
            print("\nBRAKE!")
            continue
        elif key == ' ':
            speed, steer = 0, 0

        # Send commands via the controller
        controller.set_steer(steer)
        controller.set_speed(speed)

        # Terminal feedback
        sys.stdout.write(f"\rSpeed: {speed:4} | Steer: {steer/10:5}°    ")
        sys.stdout.flush()

except KeyboardInterrupt:
    pass
finally:
    print("\n\nThe engine has been stopped")
    try:
        if controller.is_connected():
            controller.set_speed(0)
            controller.set_steer(0)
            controller.set_power_state_off()
            controller.disconnect()
    except Exception:
        pass