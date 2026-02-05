import RPi.GPIO as GPIO
import time


motor1_in1 = 10
motor1_in2 = 9
motor1_in3 = 25
motor1_in4 = 11

motor2_in1 = 17
motor2_in2 = 22
motor2_in3 = 23
motor2_in4 = 24

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(motor1_in1, GPIO.OUT)
GPIO.setup(motor1_in2, GPIO.OUT)
GPIO.setup(motor1_in3, GPIO.OUT)
GPIO.setup(motor1_in4, GPIO.OUT)

GPIO.setup(motor2_in1, GPIO.OUT)
GPIO.setup(motor2_in2, GPIO.OUT)
GPIO.setup(motor2_in3, GPIO.OUT)
GPIO.setup(motor2_in4, GPIO.OUT)


ganz_schritt = [
    [1, 0, 0, 1],
    [1, 0, 1, 0],
    [0, 1, 1, 0],
    [0, 1, 0, 1]
]


halb_schritt = [
    [1, 0, 0, 0],
    [1, 0, 1, 0],
    [0, 0, 1, 0],
    [0, 1, 1, 0],
    [0, 1, 0, 0],
    [0, 1, 0, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1]
]


class StepperMotor:

    def __init__(self, in1, in2, in3, in4, name="Motor"):
        self.in1 = in1
        self.in2 = in2
        self.in3 = in3
        self.in4 = in4
        self.name = name

    def set_step(self, step):
        GPIO.output(self.in1, step[0])
        GPIO.output(self.in2, step[1])
        GPIO.output(self.in3, step[2])
        GPIO.output(self.in4, step[3])

    def rotate(self, steps, delay=0.002, clockwise=True, half_step=False):
        sequence = halb_schritt if half_step else ganz_schritt

        for i in range(steps):
            for step in (sequence if clockwise else reversed(sequence)):
                self.set_step(step)
                time.sleep(delay)

    def rotate_degrees(self, degrees, delay=0.002, clockwise=True, half_step=False):

        steps_per_revolution = 400 if half_step else 200
        steps = int((degrees / 360.0) * steps_per_revolution)
        self.rotate(steps, delay, clockwise, half_step)

    def stop(self):
        GPIO.output(self.in1, 0)
        GPIO.output(self.in2, 0)
        GPIO.output(self.in3, 0)
        GPIO.output(self.in4, 0)


def rotate_both_motors(motor1, motor2, steps, delay=0.002,
                       m1_clockwise=True, m2_clockwise=True, half_step=False):

    sequence = halb_schritt if half_step else ganz_schritt

    for j in range(steps):
        for i in range(len(sequence)):
            step1 = sequence[i] if m1_clockwise else sequence[-(i + 1)]
            step2 = sequence[i] if m2_clockwise else sequence[-(i + 1)]

            motor1.set_step(step1)
            motor2.set_step(step2)
            time.sleep(delay)


def cleanup():
    GPIO.cleanup()


motor1 = StepperMotor(motor1_in1, motor1_in2, motor1_in3, motor1_in4, "Motor 1")
motor2 = StepperMotor(motor2_in1, motor2_in2, motor2_in3, motor2_in4, "Motor 2")


if __name__ == "__main__":
    try:

        print("Test1")
        rotate_both_motors(motor1, motor2, 200, delay=0.002,
                           m1_clockwise=True, m2_clockwise=True)
        time.sleep(1)

        print("Test2")
        rotate_both_motors(motor1, motor2, 200, delay=0.002,
                           m1_clockwise=True, m2_clockwise=False)
        time.sleep(1)

        print("Motor 1 90 Grad")
        motor1.rotate_degrees(90, delay=0.002, clockwise=True)
        time.sleep(1)

        print("Motor 2 90 Grad")
        motor2.rotate_degrees(90, delay=0.002, clockwise=True)
        time.sleep(1)


        print("Erst 1 dann 2")
        motor1.rotate_degrees(180, delay=0.002, clockwise=True, half_step=True)
        motor2.rotate_degrees(180, delay=0.002, clockwise=True, half_step=True)
        time.sleep(1)

        print("Beide lange")
        start_time = time.time()
        while time.time() - start_time < 5:
            rotate_both_motors(motor1, motor2, 10, delay=0.001,
                               m1_clockwise=True, m2_clockwise=True, half_step=True)


    except KeyboardInterrupt:
        print("\n\nAbbruch")

    finally:
        motor1.stop()
        motor2.stop()
        cleanup()