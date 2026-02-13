import RPi.GPIO as GPIO
import time
import sys
import tty
import termios

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# ─── Pin-Belegung (je ein L298N pro Motor) ────────────────────
MOTOR1_PINS = (10, 9, 25, 11)  # L298N #1: IN1, IN2, IN3, IN4
MOTOR2_PINS = (17, 22, 23, 24)  # L298N #2: IN1, IN2, IN3, IN4

# ─── Schrittsequenzen für L298N (Bipolar / H-Brücke) ─────────
# Vollschritt – Zwei Spulen gleichzeitig aktiv → mehr Drehmoment
FULL_STEP = [
    [1, 0, 1, 0],
    [0, 1, 1, 0],
    [0, 1, 0, 1],
    [1, 0, 0, 1],
]

# Halbschritt – Feinere Auflösung, weniger Drehmoment
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

# Wave-Drive – Nur eine Spule aktiv → weniger Strom, schwächer
WAVE_STEP = [
    [1, 0, 0, 0],
    [0, 0, 1, 0],
    [0, 1, 0, 0],
    [0, 0, 0, 1],
]

# ─── Positions-Definitionen (in Grad) ────────────────────────
POSITIONS = {
    0: 0,  # Standardposition (Home)
    1: 45,  # Position 1
    2: 90,  # Position 2
    3: 180,  # Position 3
    4: 270,  # Position 4
}


class StepperMotor:
    """Steuert einen Schrittmotor über L298N H-Brücke mit Positionsverfolgung."""

    def __init__(self, pins, name="Motor", steps_per_rev=200):
        """
        Args:
            pins:         Tuple (IN1, IN2, IN3, IN4) GPIO-Nummern
            name:         Bezeichnung für Log-Ausgaben
            steps_per_rev: Schritte pro Umdrehung (NEMA17=200, 28BYJ=2048)
        """
        self.pins = pins
        self.name = name
        self.steps_per_rev = steps_per_rev
        self.current_position = 0  # Aktuelle Position in Grad

        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)

    def _set_step(self, step):
        for pin, value in zip(self.pins, step):
            GPIO.output(pin, value)

    def rotate(self, steps, delay=0.005, clockwise=True, mode="full"):
        """
        Dreht den Motor.

        Args:
            steps:     Anzahl Schritte
            delay:     Sekunden zwischen Schritten (min. 0.003 für L298N!)
            clockwise: Drehrichtung
            mode:      "full", "half", oder "wave"
        """
        if mode == "half":
            sequence = HALF_STEP
        elif mode == "wave":
            sequence = WAVE_STEP
        else:
            sequence = FULL_STEP

        seq_len = len(sequence)

        for i in range(steps):
            index = i % seq_len
            if not clockwise:
                index = seq_len - 1 - index
            self._set_step(sequence[index])
            time.sleep(delay)

    def rotate_degrees(self, degrees, delay=0.005, clockwise=True, mode="full"):
        """Dreht um einen bestimmten Winkel in Grad."""
        multiplier = 2 if mode == "half" else 1
        steps = int((abs(degrees) / 360.0) * self.steps_per_rev * multiplier)
        print(f"  {self.name}: {degrees}° → {steps} Schritte")
        self.rotate(steps, delay, clockwise, mode)

        # Position aktualisieren
        if clockwise:
            self.current_position = (self.current_position + degrees) % 360
        else:
            self.current_position = (self.current_position - degrees) % 360

    def move_to_position(self, position_num, delay=0.005, mode="full"):
        """
        Bewegt Motor zu einer vordefinierten Position.

        Args:
            position_num: Position 0-4 (0 = Home)
            delay:        Verzögerung zwischen Schritten
            mode:         Schritt-Modus
        """
        if position_num not in POSITIONS:
            print(f"  ⚠ Ungültige Position: {position_num}")
            return

        target_degrees = POSITIONS[position_num]

        # Berechne kürzesten Weg
        diff = target_degrees - self.current_position

        # Normalisiere auf -180 bis +180 Grad
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360

        # Bestimme Drehrichtung
        clockwise = diff >= 0
        degrees_to_move = abs(diff)

        print(f"  {self.name}: Position {position_num} ({target_degrees}°)")
        print(
            f"    Von {self.current_position:.1f}° → {target_degrees}° ({degrees_to_move:.1f}° {'CW' if clockwise else 'CCW'})")

        if degrees_to_move > 0.1:  # Nur bewegen wenn nötig
            self.rotate_degrees(degrees_to_move, delay, clockwise, mode)

        # Präzise Position setzen
        self.current_position = target_degrees

    def move_to_home(self, delay=0.005, mode="full"):
        """Bewegt Motor zur Standardposition (0°)."""
        print(f"  {self.name}: Zurück zur Home-Position...")
        self.move_to_position(0, delay, mode)

    def stop(self):
        """Alle Spulen stromlos → Motor dreht frei."""
        for pin in self.pins:
            GPIO.output(pin, 0)

    def hold(self):
        """Hält die aktuelle Position (Spulen bleiben bestromt)."""
        self._set_step(FULL_STEP[0])

    def reset_position(self):
        """Setzt die aktuelle Position als 0° (Kalibrierung)."""
        self.current_position = 0
        print(f"  {self.name}: Position zurückgesetzt (0°)")


def rotate_both(m1, m2, steps, delay=0.005,
                m1_cw=True, m2_cw=True, mode="full"):
    """Bewegt beide Motoren synchron."""
    if mode == "half":
        sequence = HALF_STEP
    elif mode == "wave":
        sequence = WAVE_STEP
    else:
        sequence = FULL_STEP

    seq_len = len(sequence)

    for i in range(steps):
        idx = i % seq_len
        idx1 = idx if m1_cw else (seq_len - 1 - idx)
        idx2 = idx if m2_cw else (seq_len - 1 - idx)
        m1._set_step(sequence[idx1])
        m2._set_step(sequence[idx2])
        time.sleep(delay)


def get_char():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


# ─── Hauptprogramm ───────────────────────────────────────────
if __name__ == "__main__":
    motor1 = StepperMotor(MOTOR1_PINS, "Motor 1", steps_per_rev=200)
    motor2 = StepperMotor(MOTOR2_PINS, "Motor 2", steps_per_rev=200)

    delay = 0.005  # Standard-Delay für L298N

    print("=" * 60)
    print("  L298N Schrittmotor-Steuerung mit Positionssystem")
    print("=" * 60)
    print("  POSITIONEN:")
    print("    0 = Home (0°) - Standardposition")
    print("    1 = Position 1 (45°)")
    print("    2 = Position 2 (90°)")
    print("    3 = Position 3 (180°)")
    print("    4 = Position 4 (270°)")
    print()
    print("  BEFEHLE:")
    print("    0-4 = Beide Motoren zu Position bewegen + zurück zu Home")
    print("    h   = Beide Motoren zu Home-Position")
    print("    r   = Position zurücksetzen (Kalibrierung)")
    print("    s   = Stop (stromlos)")
    print("    p   = Aktuelle Position anzeigen")
    print("    +/- = Geschwindigkeit ändern")
    print("    q   = Beenden")
    print("=" * 60)
    print(f"  Delay: {delay}s\n")

    try:
        while True:
            cmd = get_char().lower()

            # Positionsbefehle
            if cmd in '01234':
                pos = int(cmd)
                print(f"\n→ Bewege zu Position {pos}")
                motor1.move_to_position(pos, delay)
                motor2.move_to_position(pos, delay)
                motor1.stop()
                motor2.stop()
                time.sleep(1)

                # Automatisch zurück zur Home-Position
                print("→ Zurück zur Home-Position")
                motor1.move_to_home(delay)
                motor2.move_to_home(delay)
                motor1.stop()
                motor2.stop()
                print("  ✓\n")

            elif cmd == 'h':
                print("→ Fahre zu Home-Position")
                motor1.move_to_home(delay)
                motor2.move_to_home(delay)
                motor1.stop()
                motor2.stop()
                print("  ✓")

            elif cmd == 'r':
                print("→ Kalibrierung: Aktuelle Position = 0°")
                motor1.reset_position()
                motor2.reset_position()
                print("  ✓")

            elif cmd == 's':
                motor1.stop()
                motor2.stop()
                print("⏸ Gestoppt (stromlos)")

            elif cmd == 'p':
                print(f"📍 Aktuelle Positionen:")
                print(f"   Motor 1: {motor1.current_position:.1f}°")
                print(f"   Motor 2: {motor2.current_position:.1f}°")

            elif cmd == '+':
                delay = max(0.003, delay - 0.001)
                print(f"⚙ Schneller (delay={delay:.4f}s)")

            elif cmd == '-':
                delay = min(0.020, delay + 0.001)
                print(f"⚙ Langsamer (delay={delay:.4f}s)")

            elif cmd in ('q', '\x03'):
                print("\n👋 Beende...")
                break

    except KeyboardInterrupt:
        print("\n⚠ Abbruch")

    finally:
        motor1.stop()
        motor2.stop()
        GPIO.cleanup()
        print("✓ GPIO aufgeräumt")