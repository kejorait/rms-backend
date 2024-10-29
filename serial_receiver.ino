// Pin definitions for the relays (you can modify these if needed)
const int relayPins[] = {2, 3, 4, 5};
const int numRelays = sizeof(relayPins) / sizeof(relayPins[0]);

// Variables to store the state of each relay (0 = off, 1 = on)
int relayStates[numRelays] = {0, 0, 0, 0};

// Setup function to initialize serial communication and set pin modes
void setup() {
  Serial.begin(9600);
  for (int i = 0; i < numRelays; i++) {
    pinMode(relayPins[i], OUTPUT);
    digitalWrite(relayPins[i], HIGH);  // Start with all relays off
  }
  Serial.println("Ready. Use commands to control relays.");
}

// Function to update the relays based on the current states
void updateRelays() {
  for (int i = 0; i < numRelays; i++) {
    digitalWrite(relayPins[i], relayStates[i] ? LOW : HIGH); // LOW = ON, HIGH = OFF
  }
}

// Function to print the status of each relay
void printStatus() {
  Serial.print("Relay Status: ");
  for (int i = 0; i < numRelays; i++) {
    Serial.print("Relay ");
    Serial.print(i + 1);
    Serial.print(": ");
    Serial.print(relayStates[i] ? "On" : "Off");
    if (i < numRelays - 1) Serial.print(", ");
  }
  Serial.println();
}

// Loop function to check for serial input and execute commands
void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();  // Remove any trailing newline or spaces

    // Parse the command
    if (command == "SYNC ON") {
      for (int i = 0; i < numRelays; i++) relayStates[i] = 0;
      updateRelays();
      Serial.println("All relays turned off (SYNC ON).");

    } else if (command == "SYNC OFF") {
      for (int i = 0; i < numRelays; i++) relayStates[i] = 1;
      updateRelays();
      Serial.println("All relays turned on (SYNC OFF).");

    } else if (command.startsWith("RELAY ")) {
      int relayNum = command.substring(6).toInt();
      if (relayNum >= 1 && relayNum <= numRelays) {
        if (command.endsWith(" ON")) {
          relayStates[relayNum - 1] = 1;
          updateRelays();
          Serial.print("Relay ");
          Serial.print(relayNum);
          Serial.println(" turned on.");
        } else if (command.endsWith(" OFF")) {
          relayStates[relayNum - 1] = 0;
          updateRelays();
          Serial.print("Relay ");
          Serial.print(relayNum);
          Serial.println(" turned off.");
        } else {
          Serial.println("Invalid RELAY command. Use 'RELAY <number> ON/OFF'.");
        }
      } else {
        Serial.println("Invalid relay number. Use 1 to 4.");
      }

    } else if (command == "STATUS") {
      printStatus();

    } else if (command == "RESET") {
      for (int i = 0; i < numRelays; i++) relayStates[i] = 0;
      updateRelays();
      Serial.println("All relays reset to off.");

    } else {
      Serial.println("Invalid command. Available commands:");
      Serial.println("  RELAY <number> ON - Turn on specific relay (1-4)");
      Serial.println("  RELAY <number> OFF - Turn off specific relay (1-4)");
      Serial.println("  SYNC ON - Turn all relays off");
      Serial.println("  SYNC OFF - Turn all relays on");
      Serial.println("  STATUS - Print current relay status");
      Serial.println("  RESET - Reset all relays to off");
    }
  }
}
