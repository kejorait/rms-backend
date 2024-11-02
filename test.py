import time

import serial

# Configuration for the serial port
serial_port = 'COM5'  # Replace with your port (e.g., 'COM3' on Windows)
baud_rate = 9600

# Establish the serial connection
try:
    ser = serial.Serial(serial_port, baud_rate, timeout=1)
    time.sleep(2)  # Wait for the connection to initialize
    print("Connected to the serial port.")
except serial.SerialException as e:
    print(f"Failed to connect: {e}")
    exit()

# Function to send commands and read response
def send_command(command):
    print(f"Sending command: {command}")
    ser.write((command + '\n').encode())  # Send the command
    time.sleep(0.1)  # Wait a bit for Arduino to process
    response = ser.readline().decode().strip()  # Read response
    if response:
        print(f"Response: {response}")
    else:
        print("No response received.")

# Test commands
commands = [
    "SYNC ON",
    "STATUS",
    "RELAY 1 ON",
    "RELAY 2 OFF",
    "RELAY 3 ON",
    "STATUS",
    "RELAY 1 OFF",
    "RELAY 4 ON",
    "SYNC OFF",
    "RESET"
]

# Send each command with a brief delay between them
for cmd in commands:
    send_command(cmd)
    time.sleep(0.5)

# Close the serial connection
ser.close()
print("Serial connection closed.")
