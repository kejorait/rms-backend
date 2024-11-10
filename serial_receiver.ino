#include <SoftwareSerial.h>
#include <EEPROM.h>

// Define RX and TX pins for SoftwareSerial
const int rxPin = 2;
const int txPin = 3;

// Create a SoftwareSerial instance
SoftwareSerial mySerial(rxPin, txPin);

// Pin definitions for the relays (you can modify these if needed)
const int relayPins[] = {4, 5, 6, 7};
const int numRelays = sizeof(relayPins) / sizeof(relayPins[0]);

// Pin definitions for the switches
const int switchPins[] = {8, 9, 10, 11};  // Switch pins
const int numSwitches = sizeof(switchPins) / sizeof(switchPins[0]);

// Define pin for manual override
const int overridePin = 12;

// Variables to store the state of each relay (0 = off, 1 = on)
int relayStates[numRelays] = {0, 0, 0, 0}; // Start with all relays off

// Function to save the state of each relay to EEPROM
void saveRelayStates() {
  for (int i = 0; i < numRelays; i++) {
    EEPROM.write(i, relayStates[i]);
  }
}

// Function to load the state of each relay from EEPROM
void loadRelayStates() {
  for (int i = 0; i < numRelays; i++) {
    relayStates[i] = EEPROM.read(i);
    digitalWrite(relayPins[i], relayStates[i] ? HIGH : LOW);
  }
}

// Setup function to initialize serial communication and set pin modes
void setup() {
  Serial.begin(9600);   // Serial for debugging
  mySerial.begin(9600); // SoftwareSerial for commands
  
  for (int i = 0; i < numRelays; i++) {
    pinMode(relayPins[i], OUTPUT);
  }
  for (int i = 0; i < numSwitches; i++) {
    pinMode(switchPins[i], INPUT); // Set switch pins as inputs
  }
  pinMode(overridePin, INPUT); // Set the override pin as input
  
  // Load relay states from EEPROM
  loadRelayStates();

  Serial.println("Ready. Use commands to control relays.");
}

// Function to update the relays based on the current states
void updateRelays() {
  for (int i = 0; i < numRelays; i++) {
    digitalWrite(relayPins[i], relayStates[i] ? HIGH : LOW); // LOW = ON, HIGH = OFF
  }
}

// Function to print the status of each relay
void printStatus() {
  mySerial.print("Relay Status: ");
  for (int i = 0; i < numRelays; i++) {
    mySerial.print("Relay ");
    mySerial.print(i + 1);
    mySerial.print(": ");
    mySerial.print(relayStates[i] ? "On" : "Off");
    if (i < numRelays - 1) mySerial.print(", ");
  }
  mySerial.println();
}

// Loop function to check for serial input and execute commands
void loop() {
  // Check the state of the override pin
  if (digitalRead(overridePin) == HIGH) {
    for (int i = 0; i < numSwitches; i++) {
      relayStates[i] = digitalRead(switchPins[i]) == HIGH ? 1 : 0;
    }
    updateRelays();
    saveRelayStates();
    Serial.println("Manual override activated. Relay states controlled by switches.");
  } else {
    // Normal mode: process mySerial if available
    if (mySerial.available() > 0) {
      String command = mySerial.readStringUntil('\n');
      command.trim();

      if (command == "SYNC ON") {
        for (int i = 0; i < numRelays; i++) relayStates[i] = 1;
        updateRelays();
        saveRelayStates();
        mySerial.println("All relays turned on (SYNC ON).");

      } else if (command == "SYNC OFF") {
        for (int i = 0; i < numRelays; i++) relayStates[i] = 0;
        updateRelays();
        saveRelayStates();
        mySerial.println("All relays turned off (SYNC OFF).");

      } else if (command.startsWith("RELAY ")) {
        int relayNum = command.substring(6).toInt();
        if (relayNum >= 1 && relayNum <= numRelays) {
          if (command.endsWith(" ON")) {
            relayStates[relayNum - 1] = 1;
            updateRelays();
            saveRelayStates();
            mySerial.print("Relay ");
            mySerial.print(relayNum);
            mySerial.println(" turned on.");
          } else if (command.endsWith(" OFF")) {
            relayStates[relayNum - 1] = 0;
            updateRelays();
            saveRelayStates();
            mySerial.print("Relay ");
            mySerial.print(relayNum);
            mySerial.println(" turned off.");
          } else {
            mySerial.println("Invalid RELAY command. Use 'RELAY <number> ON/OFF'.");
          }
        } else {
          mySerial.println("Invalid relay number. Use 1 to 4.");
        }

      } else if (command == "STATUS") {
        printStatus();

      } else if (command == "RESET") {
        for (int i = 0; i < numRelays; i++) relayStates[i] = 0;
        updateRelays();
        saveRelayStates();
        mySerial.println("All relays reset to off.");

      } else {
        mySerial.println("Invalid command. Available commands:");
        mySerial.println("  RELAY <number> ON - Turn on specific relay (1-4)");
        mySerial.println("  RELAY <number> OFF - Turn off specific relay (1-4)");
        mySerial.println("  SYNC ON - Turn all relays on");
        mySerial.println("  SYNC OFF - Turn all relays off");
        mySerial.println("  STATUS - Print current relay status");
        mySerial.println("  RESET - Reset all relays to off");
      }
    }
  }
  updateRelays();
}
