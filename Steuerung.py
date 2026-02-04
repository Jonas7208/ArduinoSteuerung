import RPi.GPIO as GPIO
import time

# GPIO Pin Konfiguration gemäß deiner Verkabelung
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

# Schrittsequenz für 2-spuligen Schrittmotor (4 Schritte - Vollschrittmodus)
# Jede Zeile aktiviert bestimmte Spulen
step_sequence = [
    [1, 0, 0, 1],  # Schritt 1
    [1, 0, 1, 0],  # Schritt 2
    [0, 1, 1, 0],  # Schritt 3
    [0, 1, 0, 1]  # Schritt 4
]

# Alternative: Halbschrittmodus für sanftere Bewegung (8 Schritte)
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


def set_step(step):
    """Setzt die GPIO Pins entsprechend der Schrittsequenz"""
    GPIO.output(IN1, step[0])
    GPIO.output(IN2, step[1])
    GPIO.output(IN3, step[2])
    GPIO.output(IN4, step[3])


def rotate_motor(steps, delay=0.002, clockwise=True, half_step=False):
    """
    Dreht den Motor um eine bestimmte Anzahl von Schritten

    Args:
        steps: Anzahl der Schritte
        delay: Verzögerung zwischen Schritten in Sekunden (bestimmt die Geschwindigkeit)
        clockwise: True für Uhrzeigersinn, False für Gegenuhrzeigersinn
        half_step: True für Halbschrittmodus, False für Vollschrittmodus
    """
    sequence = half_step_sequence if half_step else step_sequence

    for _ in range(steps):
        for step in (sequence if clockwise else reversed(sequence)):
            set_step(step)
            time.sleep(delay)


def rotate_degrees(degrees, delay=0.002, clockwise=True, half_step=False):
    """
    Dreht den Motor um eine bestimmte Gradzahl

    Args:
        degrees: Gradzahl der Drehung
        delay: Verzögerung zwischen Schritten
        clockwise: Drehrichtung
        half_step: Schrittmodus

    Hinweis: Für typische Schrittmotoren mit 200 Schritten/Umdrehung
    Bei Halbschritt: 400 Schritte = 360°
    Bei Vollschritt: 200 Schritte = 360°
    """
    steps_per_revolution = 400 if half_step else 200
    steps = int((degrees / 360.0) * steps_per_revolution)
    rotate_motor(steps, delay, clockwise, half_step)


def stop_motor():
    """Stoppt den Motor und setzt alle Pins auf LOW"""
    GPIO.output(IN1, 0)
    GPIO.output(IN2, 0)
    GPIO.output(IN3, 0)
    GPIO.output(IN4, 0)


def cleanup():
    """Aufräumen der GPIO Pins"""
    stop_motor()
    GPIO.cleanup()


# Beispiele für die Verwendung
if __name__ == "__main__":
    try:
        print("Schrittmotor Test gestartet...")

        # Beispiel 1: 200 Schritte im Uhrzeigersinn (Vollschritt)
        print("1. Drehe 200 Schritte im Uhrzeigersinn (Vollschritt)")
        rotate_motor(200, delay=0.002, clockwise=True, half_step=False)
        time.sleep(1)

        # Beispiel 2: 200 Schritte gegen den Uhrzeigersinn (Vollschritt)
        print("2. Drehe 200 Schritte gegen den Uhrzeigersinn (Vollschritt)")
        rotate_motor(200, delay=0.002, clockwise=False, half_step=False)
        time.sleep(1)

        # Beispiel 3: 180 Grad Drehung (Halbschritt)
        print("3. Drehe 180 Grad (Halbschritt)")
        rotate_degrees(180, delay=0.001, clockwise=True, half_step=True)
        time.sleep(1)

        # Beispiel 4: Kontinuierliche Drehung
        print("4. Kontinuierliche Drehung für 5 Sekunden")
        start_time = time.time()
        while time.time() - start_time < 5:
            rotate_motor(10, delay=0.001, clockwise=True, half_step=True)

        print("Test abgeschlossen!")

    except KeyboardInterrupt:
        print("\nProgramm durch Benutzer abgebrochen")

    finally:
        cleanup()
        print("GPIO Pins aufgeräumt")