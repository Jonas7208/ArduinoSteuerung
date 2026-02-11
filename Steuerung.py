import RPi.GPIO as GPIO
import time
import sys
import tty
import termios

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# ─── Pin-Belegung (je ein L298N pro Motor) ────────────────────
MOTOR1_PINS = (10, 9, 25, 11)    # L298N #1: IN1, IN2, IN3, IN4
MOTOR2_PINS = (17, 22, 23, 24)   # L298N #2: IN1, IN2, IN3, IN4

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


class StepperMotor:
    """Steuert einen Schrittmotor über L298N H-Brücke."""

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

        # Nach Drehung: Spulen halten oder freigeben
        # self.stop()  # Einkommentieren wenn Motor frei drehen soll

    def rotate_degrees(self, degrees, delay=0.005, clockwise=True, mode="full"):
        """Dreht um einen bestimmten Winkel in Grad."""
        multiplier = 2 if mode == "half" else 1
        steps = int((degrees / 360.0) * self.steps_per_rev * multiplier)
        print(f"  {self.name}: {degrees}° → {steps} Schritte")
        self.rotate(steps, delay, clockwise, mode)

    def rotate_rpm(self, revolutions, rpm, clockwise=True, mode="full"):
        """Dreht mit bestimmter Geschwindigkeit (RPM)."""
        multiplier = 2 if mode == "half" else 1
        total_steps = int(revolutions * self.steps_per_rev * multiplier)
        delay = 60.0 / (rpm * self.steps_per_rev * multiplier)
        # L298N braucht mindestens 3ms
        delay = max(delay, 0.003)
        print(f"  {self.name}: {revolutions} Umdr. @ {rpm} RPM (delay={delay:.4f}s)")
        self.rotate(total_steps, delay, clockwise, mode)

    def stop(self):
        """Alle Spulen stromlos → Motor dreht frei."""
        for pin in self.pins:
            GPIO.output(pin, 0)

    def hold(self):
        """Hält die aktuelle Position (Spulen bleiben bestromt)."""
        # Letzte Vollschritt-Position aktivieren
        self._set_step(FULL_STEP[0])


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

    speed = 5  # RPM
    delay = 0.005  # Standard-Delay für L298N

    print("=" * 50)
    print("  L298N Schrittmotor-Steuerung")
    print("=" * 50)
    print("  f = Beide vorwärts")
    print("  b = Beide rückwärts")
    print("  g = Gegenläufig")
    print("  d = Demo-Sequenz")
    print("  s = Stop (stromlos)")
    print("  h = Halten (Position fixieren)")
    print("  1/2/3 = Geschwindigkeit (langsam/mittel/schnell)")
    print("  q = Beenden")
    print("=" * 50)
    print(f"  Delay: {delay}s | Speed: {speed} RPM\n")

    try:
        while True:
            cmd = get_char().lower()

            if cmd == 'f':
                print("→ Beide vorwärts")
                rotate_both(motor1, motor2, 200, delay, True, True)
                motor1.stop()
                motor2.stop()
                print("  ✓")

            elif cmd == 'b':
                print("← Beide rückwärts")
                rotate_both(motor1, motor2, 200, delay, False, False)
                motor1.stop()
                motor2.stop()
                print("  ✓")

            elif cmd == 'g':
                print("↔ Gegenläufig")
                rotate_both(motor1, motor2, 200, delay, True, False)
                motor1.stop()
                motor2.stop()
                print("  ✓")

            elif cmd == 'd':
                print("\n🔧 Demo...\n")
                print("  [1] Beide vorwärts")
                rotate_both(motor1, motor2, 200, delay)
                motor1.stop(); motor2.stop()
                time.sleep(0.5)

                print("  [2] Gegenläufig")
                rotate_both(motor1, motor2, 200, delay, True, False)
                motor1.stop(); motor2.stop()
                time.sleep(0.5)

                print("  [3] Motor 1 → 90°")
                motor1.rotate_degrees(90, delay)
                motor1.stop()
                time.sleep(0.5)

                print("  [4] Motor 2 → 90°")
                motor2.rotate_degrees(90, delay)
                motor2.stop()
                time.sleep(0.5)

                print("\n  ✓ Demo fertig!\n")

            elif cmd == 's':
                motor1.stop()
                motor2.stop()
                print("⏸ Gestoppt (stromlos)")

            elif cmd == 'h':
                motor1.hold()
                motor2.hold()
                print("🔒 Position gehalten")

            elif cmd == '1':
                motor1.rotate_degrees(90, delay)
                motor1.stop()


            elif cmd == '5':
                delay = 0.010
                print(f"⚙ Langsam (delay={delay}s)")
            elif cmd == '6':
                delay = 0.005
                print(f"⚙ Mittel (delay={delay}s)")
            elif cmd == '7':
                delay = 0.003
                print(f"⚙ Schnell (delay={delay}s)")


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