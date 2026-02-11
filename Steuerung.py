import RPi.GPIO as GPIO
import time
import sys
import tty
import termios

# ─── GPIO Setup ───────────────────────────────────────────────
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# ─── Pin-Belegung ─────────────────────────────────────────────
MOTOR1_PINS = (10, 9, 25, 11)
MOTOR2_PINS = (17, 22, 23, 24)

# ─── Schrittsequenzen ──────────────────────────────��─────────
FULL_STEP = [
    [1, 0, 0, 1],
    [1, 0, 1, 0],
    [0, 1, 1, 0],
    [0, 1, 0, 1],
]

HALF_STEP = [
    [1, 0, 0, 0],
    [1, 0, 1, 0],
    [0, 0, 1, 0],
    [0, 1, 1, 0],
    [0, 1, 0, 0],
    [0, 1, 0, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1],
]


# ─── Motor-Klasse ────────────────────────────────────────────
class StepperMotor:
    """Steuert einen einzelnen 4-Phasen-Schrittmotor."""

    STEPS_PER_REV_FULL = 200
    STEPS_PER_REV_HALF = 400

    def __init__(self, pins, name="Motor"):
        """
        Args:
            pins: Tuple mit 4 GPIO-Pin-Nummern (IN1, IN2, IN3, IN4)
            name: Bezeichnung des Motors für Log-Ausgaben
        """
        self.pins = pins
        self.name = name
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)

    def _set_step(self, step):
        """Setzt die 4 GPIO-Pins auf die Werte einer Schrittsequenz."""
        for pin, value in zip(self.pins, step):
            GPIO.output(pin, value)

    def _get_sequence(self, half_step):
        """Gibt die passende Schrittsequenz zurück."""
        return HALF_STEP if half_step else FULL_STEP

    def rotate(self, steps, delay=0.002, clockwise=True, half_step=False):
        """
        Dreht den Motor um eine bestimmte Anzahl Schritte.

        Args:
            steps:     Anzahl der Schritte
            delay:     Pause zwischen Schritten in Sekunden
            clockwise: True = Uhrzeigersinn, False = Gegenuhrzeigersinn
            half_step: True = Halbschrittmodus (feinere Auflösung)
        """
        sequence = self._get_sequence(half_step)
        seq_len = len(sequence)

        for i in range(steps):
            index = i % seq_len
            if not clockwise:
                index = seq_len - 1 - index
            self._set_step(sequence[index])
            time.sleep(delay)

    def rotate_degrees(self, degrees, delay=0.002, clockwise=True, half_step=False):
        """
        Dreht den Motor um einen bestimmten Winkel in Grad.

        Args:
            degrees:   Drehwinkel in Grad
            delay:     Pause zwischen Schritten in Sekunden
            clockwise: Drehrichtung
            half_step: Schrittmodus
        """
        steps_per_rev = self.STEPS_PER_REV_HALF if half_step else self.STEPS_PER_REV_FULL
        steps = int((degrees / 360.0) * steps_per_rev)
        self.rotate(steps, delay, clockwise, half_step)

    def rotate_rpm(self, revolutions, rpm, clockwise=True, half_step=False):
        """
        Dreht den Motor mit einer bestimmten Drehzahl (RPM).

        Args:
            revolutions: Anzahl Umdrehungen
            rpm:         Umdrehungen pro Minute
            clockwise:   Drehrichtung
            half_step:   Schrittmodus
        """
        steps_per_rev = self.STEPS_PER_REV_HALF if half_step else self.STEPS_PER_REV_FULL
        delay = 60.0 / (rpm * steps_per_rev)
        total_steps = int(revolutions * steps_per_rev)
        self.rotate(total_steps, delay, clockwise, half_step)

    def stop(self):
        """Schaltet alle Spulen stromlos (Motor freigeben)."""
        for pin in self.pins:
            GPIO.output(pin, 0)


# ─── Dual-Motor-Steuerung ────────────────────────────────────
def rotate_both(motor1, motor2, steps, delay=0.002,
                m1_clockwise=True, m2_clockwise=True, half_step=False):
    """
    Bewegt beide Motoren gleichzeitig (synchron).

    Args:
        motor1, motor2: StepperMotor-Instanzen
        steps:          Anzahl Schritte
        delay:          Pause zwischen Schritten
        m1_clockwise:   Drehrichtung Motor 1
        m2_clockwise:   Drehrichtung Motor 2
        half_step:      Schrittmodus
    """
    sequence = HALF_STEP if half_step else FULL_STEP
    seq_len = len(sequence)

    for i in range(steps):
        idx = i % seq_len

        idx1 = idx if m1_clockwise else (seq_len - 1 - idx)
        idx2 = idx if m2_clockwise else (seq_len - 1 - idx)

        motor1._set_step(sequence[idx1])
        motor2._set_step(sequence[idx2])
        time.sleep(delay)


# ─── Tastatur-Eingabe ────────────────────────────────────────
def get_char():
    """Liest ein einzelnes Zeichen von der Tastatur (ohne Enter)."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def cleanup():
    """Räumt alle GPIO-Pins auf."""
    GPIO.cleanup()


# ─── Hauptprogramm ───────────────────────────────────────────
if __name__ == "__main__":
    motor1 = StepperMotor(MOTOR1_PINS, "Motor 1")
    motor2 = StepperMotor(MOTOR2_PINS, "Motor 2")

    current_speed = 5  # RPM

    print("=" * 50)
    print("  Stepper-Motor Steuerung")
    print("=" * 50)
    print("  f = Beide vorwärts (200 Schritte)")
    print("  b = Beide rückwärts (200 Schritte)")
    print("  d = Demo-Sequenz starten")
    print("  s = Stop (Motoren stromlos)")
    print("  1 = Geschwindigkeit:  3 RPM")
    print("  2 = Geschwindigkeit:  5 RPM")
    print("  3 = Geschwindigkeit: 60 RPM")
    print("  q = Beenden")
    print("=" * 50)
    print(f"  Aktuelle Geschwindigkeit: {current_speed} RPM\n")

    try:
        while True:
            command = get_char().lower()

            if command == 'f':
                steps_per_rev = motor1.STEPS_PER_REV_HALF
                delay = 60.0 / (current_speed * steps_per_rev)
                print("→ Beide vorwärts (200 Schritte)")
                rotate_both(motor1, motor2, 200, delay=delay,
                            m1_clockwise=True, m2_clockwise=True, half_step=True)
                print("  Fertig!")

            elif command == 'b':
                steps_per_rev = motor1.STEPS_PER_REV_HALF
                delay = 60.0 / (current_speed * steps_per_rev)
                print("← Beide rückwärts (200 Schritte)")
                rotate_both(motor1, motor2, 200, delay=delay,
                            m1_clockwise=False, m2_clockwise=False, half_step=True)
                print("  Fertig!")

            elif command == 'd':
                print("\n🔧 Demo-Sequenz gestartet...\n")

                print("  [1/5] Beide vorwärts (Vollschritt)")
                rotate_both(motor1, motor2, 200, delay=0.002,
                            m1_clockwise=True, m2_clockwise=True)
                time.sleep(1)

                print("  [2/5] Gegenläufig (Vollschritt)")
                rotate_both(motor1, motor2, 200, delay=0.002,
                            m1_clockwise=True, m2_clockwise=False)
                time.sleep(1)

                print("  [3/5] Motor 1 → 90°")
                motor1.rotate_degrees(90, delay=0.002, clockwise=True)
                time.sleep(1)

                print("  [4/5] Motor 2 → 90°")
                motor2.rotate_degrees(90, delay=0.002, clockwise=True)
                time.sleep(1)

                print("  [5/5] Beide 180° Halbschritt (nacheinander)")
                motor1.rotate_degrees(180, delay=0.002, clockwise=True, half_step=True)
                motor2.rotate_degrees(180, delay=0.002, clockwise=True, half_step=True)

                print("\n  ✓ Demo abgeschlossen!\n")

            elif command == 's':
                print("⏸ Motoren gestoppt")
                motor1.stop()
                motor2.stop()

            elif command == '1':
                current_speed = 3
                print(f"⚙ Geschwindigkeit: {current_speed} RPM")

            elif command == '2':
                current_speed = 5
                print(f"⚙ Geschwindigkeit: {current_speed} RPM")

            elif command == '3':
                current_speed = 60
                print(f"⚙ Geschwindigkeit: {current_speed} RPM")

            elif command in ('q', '\x03'):  # q oder Ctrl+C
                print("\n👋 Programm wird beendet...")
                break

    except KeyboardInterrupt:
        print("\n\n⚠ Abbruch durch Benutzer")

    finally:
        motor1.stop()
        motor2.stop()
        cleanup()
        print("✓ GPIO aufgeräumt. Auf Wiedersehen!")