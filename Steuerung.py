import RPi.GPIO as GPIO
import time
import sys
import tty
import termios

# GPIO Pin Konfiguration
IN1 = 17  # Input 1
IN2 = 22  # Input 2
IN3 = 23  # Input 3
IN4 = 24  # Input 4

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

# Schrittsequenzen
# Vollschritt-Sequenz
full_step_sequence = [
    [1, 0, 0, 1],
    [1, 0, 1, 0],
    [0, 1, 1, 0],
    [0, 1, 0, 1]
]

# Halbschritt-Sequenz
half_step_sequence = [
    [1, 0, 0, 0],
    [1, 0, 1, 0],
    [0, 0, 1, 0],
    [0, 1, 1, 0],
    [0, 1, 0, 0],
    [0, 1, 0, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1]
]

# Microstep-Sequenz (simuliert mit Halbschritten)
microstep_sequence = half_step_sequence

# Motorparameter
STEPS_PER_REV = 200
current_speed = 5  # U/min (RPM)


def set_step(step):
    """Setzt die GPIO Pins entsprechend der Schrittsequenz"""
    GPIO.output(IN1, step[0])
    GPIO.output(IN2, step[1])
    GPIO.output(IN3, step[2])
    GPIO.output(IN4, step[3])


def calculate_delay(speed_rpm, step_mode='MICROSTEP'):
    """
    Berechnet die Verzögerung zwischen Schritten basierend auf RPM

    Args:
        speed_rpm: Geschwindigkeit in Umdrehungen pro Minute
        step_mode: 'SINGLE', 'DOUBLE', 'MICROSTEP'
    """
    if step_mode == 'MICROSTEP':
        steps = STEPS_PER_REV * 2  # Doppelte Schritte im Halbschrittmodus
    else:
        steps = STEPS_PER_REV

    # Verzögerung in Sekunden pro Schritt
    delay = 60.0 / (speed_rpm * steps)
    return delay


def step_motor(steps, direction='FORWARD', step_mode='MICROSTEP'):
    """
    Bewegt den Motor um eine bestimmte Anzahl von Schritten

    Args:
        steps: Anzahl der Schritte
        direction: 'FORWARD' oder 'BACKWARD'
        step_mode: 'SINGLE', 'DOUBLE', 'MICROSTEP'
    """
    # Wähle die richtige Sequenz
    if step_mode == 'MICROSTEP':
        sequence = microstep_sequence
    elif step_mode == 'DOUBLE':
        sequence = full_step_sequence
    else:  # SINGLE
        sequence = full_step_sequence

    delay = calculate_delay(current_speed, step_mode)

    # Bestimme die Richtung
    seq = sequence if direction == 'FORWARD' else list(reversed(sequence))

    # Führe die Schritte aus
    for _ in range(abs(steps)):
        for step in seq:
            set_step(step)
            time.sleep(delay)


def release_motor():
    """Gibt alle Spulen frei (Motor stromlos)"""
    GPIO.output(IN1, 0)
    GPIO.output(IN2, 0)
    GPIO.output(IN3, 0)
    GPIO.output(IN4, 0)


def get_char():
    """Liest ein einzelnes Zeichen von der Tastatur"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def cleanup():
    """Aufräumen der GPIO Pins"""
    release_motor()
    GPIO.cleanup()


# Hauptprogramm
if __name__ == "__main__":
    print("=" * 50)
    print("Stepper Kontrolle bereit!")
    print("=" * 50)
    print("Befehle:")
    print("  f = Vorwärts 200 Schritte")
    print("  b = Rückwärts 200 Schritte")
    print("  s = Stop (Motor stromlos)")
    print("  1 = Geschwindigkeit: 3 RPM")
    print("  2 = Geschwindigkeit: 5 RPM")
    print("  3 = Geschwindigkeit: 60 RPM")
    print("  q = Programm beenden")
    print("=" * 50)
    print(f"Aktuelle Geschwindigkeit: {current_speed} RPM")
    print()

    try:
        while True:
            command = get_char().lower()

            if command == 'f':
                print("→ Vorwärts 200 Schritte")
                step_motor(200, 'FORWARD', 'MICROSTEP')
                print("  Fertig!")

            elif command == 'b':
                print("← Rückwärts 200 Schritte")
                step_motor(200, 'BACKWARD', 'MICROSTEP')
                print("  Fertig!")

            elif command == 's':
                print("⏸ Motor Stop")
                release_motor()

            elif command == '1':
                current_speed = 3
                print(f"⚙ Geschwindigkeit: {current_speed} RPM")

            elif command == '2':
                current_speed = 5
                print(f"⚙ Geschwindigkeit: {current_speed} RPM")

            elif command == '3':
                current_speed = 60
                print(f"⚙ Geschwindigkeit: {current_speed} RPM")

            elif command == 'q':
                print("\n👋 Programm wird beendet...")
                break

            elif command == '\x03':  # Ctrl+C
                break

    except KeyboardInterrupt:
        print("\n\n⚠ Programm durch Benutzer abgebrochen")

    finally:
        cleanup()
        print("✓ GPIO Pins aufgeräumt")
        print("Auf Wiedersehen!")