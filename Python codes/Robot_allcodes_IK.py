# Final Humanoid Robot Pipeline

import serial
import time
import cv2
import numpy as np
import math


# SERIAL CONFIG

COM_PORT  = '/dev/ttyACM0'
BAUD_RATE = 115200


# ROBOT GEOMETRY (METERS)

L1 = 0.065
L2 = 0.055


# VISION CONFIG

LOWER_BALL = np.array([125, 50, 50])
UPPER_BALL = np.array([155, 255, 255])

REAL_BALL_DIAMETER = 6.0
FOCAL_LENGTH = 700


# FSM CONFIG

KICK_DISTANCE = 20
KICK_COOLDOWN = 3.0

# SERVO NEUTRAL POSE

# t1 = left hip
# t2 = left knee
# t3 = left ankle
#
# t4 = right hip
# t5 = right knee
# t6 = right ankle

N = [80, 95, 95, 80, 90, 100]


# SIMPLE HANDCRAFTED WALKING

STEP = 6
LEAN = 5
LIFT = 5

R1 = [80, 95, 100, 80, 90, 100]

R2 = [82, 95, 100, 86, 85, 100]

L1_POSE = [80, 95, 95, 80, 90, 95]

L2_POSE = [74, 100, 95, 78, 90, 95]


arduino = None

# CONNECT TO ARDUINO

def connect_arduino():

    global arduino

    print(f"Connecting to Arduino on {COM_PORT}...")

    try:

        arduino = serial.Serial(
            COM_PORT,
            BAUD_RATE,
            timeout=1
        )

        time.sleep(2)

        arduino.reset_input_buffer()

        print("Arduino connected")

        return True

    except Exception as e:

        print(f"Connection failed: {e}")

        return False

# SEND ANGLES

def send_angles(t1, t2, t3, t4, t5, t6):

    if arduino is None or not arduino.is_open:
        return

    t1, t2, t3, t4, t5, t6 = map_servos(t1, t2, t3, t4, t5, t6)

    cmd = f"t1:{t1:.1f},t2:{t2:.1f},t3:{t3:.1f},t4:{t4:.1f},t5:{t5:.1f},t6:{t6:.1f}\n"

    arduino.write(cmd.encode())
    time.sleep(0.02)



def map_servos(t1, t2, t3, t4, t5, t6):


    lhip  = t1
    lknee = t2
    lank  = t3

    rhip  = t4

    rknee = t5

    rank = t6 - 3


    return lhip, lknee, lank, rhip, rknee, rank



# SMOOTH INTERPOLATION

def smooth(start, end, frames=10):

    poses = []

    for i in range(frames):

        p = []

        for j in range(6):

            value = (
                start[j]
                +
                (end[j] - start[j])
                *
                i
                /
                (frames - 1)
            )

            p.append(value)

        poses.append(tuple(p))

    return poses

# SEND SMOOTH

def send_smooth(poses, pause=0.08):

    for p in poses:

        send_angles(*p)

        time.sleep(pause)


# STAND

def stand():

    send_angles(*N)


# WALKING POSES

A = [
    80, 95, 100,
    82, 95, 98
]

B = [
    76, 92, 100,
    86, 95, 98
]

C = [
    72, 88, 100,
    88, 98, 98
]

D = [
    78, 95, 100,
    84, 95, 100
]

# WALK CYCLE

walk_offset = 0
def generate_poses():

    global walk_offset

    # forward progression
    walk_offset += 2

    N = [
        80 + walk_offset, 95, 100,
        80 + walk_offset, 95, 100
    ]

    A = [
        80 + walk_offset - 4, 98, 100,   # slight lean forward
        82 + walk_offset, 95, 98
    ]

    B = [
        76 + walk_offset, 92, 100,       # LEFT support shift
        86 + walk_offset, 95, 98
    ]

    C = [
        72 + walk_offset, 88, 100,       # swing phase
        88 + walk_offset, 98, 98
    ]

    D = [
        78 + walk_offset, 95, 100,       # placement forward
        84 + walk_offset, 95, 100
    ]

    return N, A, B, C, D




def walk_cycle():

    STEP = 18
    LIFT = 25

    # PHASE 1 — RIGHT SUPPORT, LEFT SWING

    # LOCK RIGHT LEG (support = zero motion)
    send_angles(
        80, 95, 100,     # LEFT (ready to move)
        92, 96, 96       # RIGHT (fully locked support)
    )
    time.sleep(0.3)

    # lift LEFT leg ONLY
    send_angles(
        80, 95 - LIFT, 100,
        92, 96, 96
    )
    time.sleep(0.3)

    # swing LEFT leg forward
    send_angles(
        80 - STEP, 95 - LIFT, 100,
        92, 96, 96
    )
    time.sleep(0.3)

    # place LEFT foot
    send_angles(
        80 - STEP, 95, 100,
        92, 96, 96
    )
    time.sleep(0.3)

    # PHASE 2 — LEFT SUPPORT, RIGHT SWING

    # LOCK LEFT LEG
    send_angles(
        80, 95, 100,
        92, 96, 96
    )
    time.sleep(0.3)

    # lift RIGHT leg
    send_angles(
        80, 95, 100,
        92, 96 - LIFT, 96
    )
    time.sleep(0.3)

    # swing RIGHT leg forward
    send_angles(
        80, 95, 100,
        92 + STEP, 96 - LIFT, 96
    )
    time.sleep(0.3)

    # place RIGHT foot
    send_angles(
        80, 95, 100,
        92 + STEP, 96, 96
    )
    time.sleep(0.3)


# FORWARD KINEMATICS:

# input:
# hip angle
# knee angle
#
# output:
# foot x,y position


def forward_kinematics(theta1_deg, theta2_deg):

    theta1 = math.radians(theta1_deg)
    theta2 = math.radians(theta2_deg)

    x = (
        L1 * math.cos(theta1)
        +
        L2 * math.cos(theta1 + theta2)
    )

    y = (
        L1 * math.sin(theta1)
        +
        L2 * math.sin(theta1 + theta2)
    )

    return x, y

# INVERSE KINEMATICS:

# input:
# desired foot x,y
#
# output:
# hip angle
# knee angle


def inverse_kinematics(x, y):

    distance = math.sqrt(x**2 + y**2)

    max_reach = L1 + L2 - 0.001

    if distance > max_reach:

        scale = max_reach / distance

        x *= scale
        y *= scale

    cos_theta2 = (
        x**2 + y**2 - L1**2 - L2**2
    ) / (2 * L1 * L2)

    cos_theta2 = max(-1.0, min(1.0, cos_theta2))

    theta2 = math.acos(cos_theta2)

    theta1 = (
        math.atan2(y, x)
        -
        math.atan2(
            L2 * math.sin(theta2),
            L1 + L2 * math.cos(theta2)
        )
    )

    theta1_deg = math.degrees(theta1)
    theta2_deg = math.degrees(theta2)

    return theta1_deg, theta2_deg

# FK VALIDATION

# validates IK output


def validate_ik(target_x, target_y, hip, knee):

    fk_x, fk_y = forward_kinematics(
        hip,
        knee
    )

    error = math.sqrt(
        (target_x - fk_x)**2
        +
        (target_y - fk_y)**2
    )

    print(f"FK Validation Error: {error:.5f} m")

    return error

# SERVO MAPPING:
# converts IK angles to actual servo angles


def right_leg_servo_map(hip_deg, knee_deg):

    # Stable neutral pose
    base_hip = 86
    base_knee = 92

    # Moderate IK scaling
    hip_offset = hip_deg * 0.18
    knee_offset = knee_deg * 0.10

    servo_hip = base_hip + hip_offset
    servo_knee = base_knee - knee_offset

    # Wider safe range
    servo_hip = max(78, min(98, servo_hip))
    servo_knee = max(84, min(102, servo_knee))

    return servo_hip, servo_knee



def left_leg_servo_map(hip_deg, knee_deg):

    # LEFT leg moves opposite direction

    servo_hip = 64

    servo_knee = 106

    # safety clamp
    servo_hip = max(55, min(75, servo_hip))
    servo_knee = max(95, min(115, servo_knee))

    return servo_hip, servo_knee


# IK-BASED KICK:
# THIS is where IK is used in the real robot.

# walking remains handcrafted.


def ik_kick():

    print("IK Kick Started")

    # STEP 1 : RIGHT LEG SUPPORT
    # LEFT LEG FREE

    support_pose = [
        80,   # left hip
        95,   # left knee
        100,  # left ankle

        92,   # right hip
        96,   # right knee
        96    # right ankle
    ]

    send_smooth(
        smooth(N, support_pose, frames=6),
        pause=0.05
    )

    # STEP 2 : LIFT LEFT LEG

    lift_pose = [
        80,
        80,   # lift LEFT knee
        100,

        92,
        96,
        96
    ]

    send_smooth(
        smooth(support_pose, lift_pose, frames=4),
        pause=0.05
    )

    # STEP 3 : IK TARGET

    target_x = 0.055
    target_y = -0.070

    hip_angle, knee_angle = inverse_kinematics(
        target_x,
        target_y
    )

    validate_ik(
        target_x,
        target_y,
        hip_angle,
        knee_angle
    )

    print(f"Hip IK  = {hip_angle:.2f}")
    print(f"Knee IK = {knee_angle:.2f}")

    # STEP 4 : HYBRID IK → SERVO MAPPING

    IK_GAIN_HIP = 0.75
    IK_GAIN_KNEE = 0.55

    # LEFT leg calibrated neutral pose
    BASE_HIP = 60
    BASE_KNEE = 95

    servo_hip = BASE_HIP + (hip_angle * IK_GAIN_HIP)
    servo_knee = BASE_KNEE - (knee_angle * IK_GAIN_KNEE)

    # safety limits (prevent instability)
    servo_hip = max(50, min(85, servo_hip))
    servo_knee = max(80, min(120, servo_knee))

    # STEP 5 — PREP + SNAP KICK

    kick_pose = [
        servo_hip,
        servo_knee,
        100,

        92,
        96,
        96
    ]

    # small motion into strike position (stability)
    send_smooth(
        smooth(lift_pose, kick_pose, frames=3),
        pause=0.03
    )

    time.sleep(0.05)

    # SNAP IMPACT (this creates real kick force)
    send_angles(*kick_pose)

    time.sleep(0.12)

    # STEP 6 : RETURN TO NEUTRAL

    send_smooth(
        smooth(kick_pose, N, frames=6),
        pause=0.05
    )

    print("IK Kick Finished")



# BALL DETECTION


def detect_ball(frame):

    blurred = cv2.GaussianBlur(
        frame,
        (5, 5),
        0
    )

    hsv = cv2.cvtColor(
        blurred,
        cv2.COLOR_BGR2HSV
    )

    mask = cv2.inRange(
        hsv,
        LOWER_BALL,
        UPPER_BALL
    )

    mask = cv2.erode(mask, None, iterations=2)

    mask = cv2.dilate(mask, None, iterations=2)

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    ball_visible = False

    center_x = -1

    distance = 999.0

    if contours:

        c = max(contours, key=cv2.contourArea)

        area = cv2.contourArea(c)

        if area > 500:

            (x, y), radius = cv2.minEnclosingCircle(c)

            if radius > 5:

                ball_visible = True

                center_x = int(x)

                pixel_diameter = radius * 2

                distance = (
                    REAL_BALL_DIAMETER
                    *
                    FOCAL_LENGTH
                ) / pixel_diameter

                cv2.circle(
                    frame,
                    (int(x), int(y)),
                    int(radius),
                    (0,255,0),
                    3
                )

                cv2.putText(
                    frame,
                    f"Ball {distance:.1f}cm",
                    (int(x), int(y) - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0,255,0),
                    2
                )

    return (
        ball_visible,
        center_x,
        distance,
        frame,
        mask
    )

# FSM STATES

WAITING = "WAITING"
WALKING = "WALKING"
KICKING = "KICKING"


class RobotFSM:

    def __init__(self):

        self.state = WAITING

        self.last_kick_time = 0

        self.has_kicked = False

    def update(
        self,
        ball_visible,
        center_x,
        distance_cm
    ):

        print(
            f"[FSM] {self.state:8s} | "
            f"Ball={'YES' if ball_visible else 'NO '} | "
            f"Distance={distance_cm:.1f}"
        )

        # WAITING

        if self.state == WAITING:

            stand()

            self.has_kicked = False

            if ball_visible:

                self.state = WALKING

        # WALKING

        elif self.state == WALKING:

            if not ball_visible:

                self.state = WAITING

                return

            if (
                distance_cm <= KICK_DISTANCE
                and
                not self.has_kicked
            ):

                self.state = KICKING

            else:

                walk_cycle()


        # KICKING

        elif self.state == KICKING:

            now = time.time()

            if (
                now - self.last_kick_time
                >
                KICK_COOLDOWN
            ):

                ik_kick()

                self.last_kick_time = now

                self.has_kicked = True

                self.state = WAITING


# MAIN


def main():

    print("=" * 50)
    print(" HUMANOID ROBOT SYSTEM ")
    print("=" * 50)

    if not connect_arduino():
        return

    print("Standing...")

    stand()

    time.sleep(1)

    print("Opening webcam...")

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():

        print("Could not open webcam")

        return

    print("Webcam ready")

    fsm = RobotFSM()

    try:

        while True:

            ret, frame = cap.read()

            if not ret:
                break

            (
                ball_visible,
                center_x,
                distance,
                debug_frame,
                mask
            ) = detect_ball(frame)

            fsm.update(
                ball_visible,
                center_x,
                distance
            )

            cv2.putText(
                debug_frame,
                f"State: {fsm.state}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255,255,255),
                2
            )

            cv2.imshow(
                "Robot Vision",
                debug_frame
            )

            cv2.imshow(
                "Ball Mask",
                mask
            )

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:

        print("Interrupted")

    finally:

        print("Shutting down...")

        stand()

        cap.release()

        cv2.destroyAllWindows()

        if arduino and arduino.is_open:
            arduino.close()

        print("Done")

# START

if __name__ == "__main__":

    main()








