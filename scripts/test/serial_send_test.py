import threading
import time

import serial

# Configuration for the serial port
serial_port = 'COM3'  # Replace with your port (e.g., 'COM3' on Windows)
baud_rate = 9600

# Establish the serial connection
try:
    ser = serial.Serial(serial_port, baud_rate, timeout=1)
    ser.dtr = False  # Prevents the Arduino from resetting
    time.sleep(2)  # Wait for the connection to initialize
    print("Connected to the serial port.")
except serial.SerialException as e:
    print(f"Failed to connect: {e}")
    exit()

# Function to send commands and read response
def send_command(command):
    print(f"Sending command: {command}")
    ser.write((command + '\n').encode())  # Send the command

# Function to continuously receive responses
def receive_responses():
    while True:
        response = ser.readline().decode().strip()  # Read response
        if response:
            print(f"Response: {response}")
        else:
            print("No response received.")

# Start the response thread
response_thread = threading.Thread(target=receive_responses, daemon=True)
response_thread.start()

# Read commands from standard input until 'EXIT' is entered
print("Enter commands (type 'EXIT' to quit):")
while True:
    cmd = input("> ")  # Prompt for user input
    if cmd.strip().upper() == "EXIT":  # Check for exit command
        break
    send_command(cmd)  # Send the command
    time.sleep(0.5)  # Optional delay between commands

# Close the serial connection
ser.close()
print("Serial connection closed.")
