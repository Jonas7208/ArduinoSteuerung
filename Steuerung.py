import RPi.GPIO as GPIO
import time
import sys
import tty
import termios

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

MOTOR1_PINS = (10, 9, 25, 11)
MOTOR2_PINS = (17, 22, 23, 24)

FULL_STEP = [
    [1, 0, 1, 0],
    [0, 1, 1, 0],
    [0, 1, 0, 1],
    [1, 0, 0, 1],
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

WAVE_STEP = [
    [1, 0, 0, 0],
    [0, 0, 1, 0],
    [0, 1, 0, 0],
    [0, 0, 0, 1],
]

POSITIONS = {
    0: 0,
    1: 45,
    2: 90,
    3: 180,
    4: 270,
}

SEQUENCES = {
    "full": FULL_STEP,
    "half": HALF_STEP,
    "wave": WAVE_STEP,
}


class StepperMotor:

    def __init__(self, pins, name="Motor", steps_per_rev=200):
        self.pins = pins
        self.name = name
        self.steps_per_rev = steps_per_rev
        self.current_position = 0.0

        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)

    def _set_step(self, step):
        for pin, value in zip(self.pins, step):
            GPIO.output(pin, value)

    def _get_sequence(self, mode):
        return SEQUENCES.get(mode, FULL_STEP)

    def rotate(self, steps, delay=0.005, clockwise=True, mode="full"):
        sequence = self._get_sequence(mode)
        seq_len = len(sequence)

        for i in range(steps):
            index = i % seq_len
            if not clockwise:
                index = seq_len - 1 - index
            self._set_step(sequence[index])
            time.sleep(delay)

    def rotate_degrees(self, degrees, delay=0.005, clockwise=True, mode="full"):
        multiplier = 2 if mode == "half" else 1
        steps = int((abs(degrees) / 360.0) * self.steps_per_rev * multiplier)
        print(f"  {self.name}: {degrees}° → {steps} Schritte")
        self.rotate(steps, delay, clockwise, mode)

        direction = 1 if clockwise else -1
        self.current_position = (self.current_position + direction * degrees) % 360

    def move_to_position(self, position_num, delay=0.005, mode="full"):
        if position_num not in POSITIONS:
            print(f"  ⚠ Ungültige Position: {position_num}")
            return

        target = POSITIONS[position_num]
        diff = target - self.current_position

        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360

        clockwise = diff >= 0
        degrees_to_move = abs(diff)

        direction = "CW" if clockwise else "CCW"
        print(f"  {self.name}: Position {position_num} ({target}°)")
        print(f"    {self.current_position:.1f}° → {target}° ({degrees_to_move:.1f}° {direction})")

        if degrees_to_move > 0.1:
            self.rotate_degrees(degrees_to_move, delay, clockwise, mode)

        self.current_position = target

    def move_to_home(self, delay=0.005, mode="full"):
        print(f"  {self.name}: Zurück zur Home-Position...")
        self.move_to_position(0, delay, mode)

    def stop(self):
        for pin in self.pins:
            GPIO.output(pin, 0)

    def hold(self):
        self._set_step(FULL_STEP[0])

    def reset_position(self):
        self.current_position = 0.0
        print(f"  {self.name}: Position zurückgesetzt (0°)")


def get_char():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def print_menu(delay):
    print("=" * 60)
    print("  L298N Schrittmotor-Steuerung mit Positionssystem")
    print("=" * 60)
    print("  POSITIONEN:")
    for num, deg in POSITIONS.items():
        label = "Home" if num == 0 else f"Position {num}"
        print(f"    {num} = {label} ({deg}°)")
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


if __name__ == "__main__":
    motor1 = StepperMotor(MOTOR1_PINS, "Motor 1", steps_per_rev=200)
    motor2 = StepperMotor(MOTOR2_PINS, "Motor 2", steps_per_rev=200)
    motors = [motor1, motor2]

    delay = 0.005
    print_menu(delay)

    try:
        while True:
            cmd = get_char().lower()

            if cmd in "01234":
                pos = int(cmd)
                print(f"\n→ Bewege zu Position {pos}")
                for m in motors:
                    m.move_to_position(pos, delay)
                    m.stop()
                time.sleep(1)

                print("→ Zurück zur Home-Position")
                for m in motors:
                    m.move_to_home(delay)
                    m.stop()
                print("  ✓\n")

            elif cmd == "h":
                print("→ Fahre zu Home-Position")
                for m in motors:
                    m.move_to_home(delay)
                    m.stop()
                print("  ✓")

            elif cmd == "r":
                print("→ Kalibrierung: Aktuelle Position = 0°")
                for m in motors:
                    m.reset_position()
                print("  ✓")

            elif cmd == "s":
                for m in motors:
                    m.stop()
                print("⏸ Gestoppt (stromlos)")

            elif cmd == "p":
                print("📍 Aktuelle Positionen:")
                for m in motors:
                    print(f"   {m.name}: {m.current_position:.1f}°")

            elif cmd == "+":
                delay = max(0.003, delay - 0.001)
                print(f"⚙ Schneller (delay={delay:.4f}s)")

            elif cmd == "-":
                delay = min(0.020, delay + 0.001)
                print(f"⚙ Langsamer (delay={delay:.4f}s)")

            elif cmd in ("q", "\x03"):
                print("\n👋 Beende...")
                break

    except KeyboardInterrupt:
        print("\n⚠ Abbruch")

    finally:
        for m in motors:
            m.stop()
        GPIO.cleanup()
        print("✓ GPIO aufgeräumt")