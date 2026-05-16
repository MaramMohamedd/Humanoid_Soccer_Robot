

import serial
import time

COM_PORT = '/dev/ttyACM0'
BAUD_RATE = 9600

arduino = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
time.sleep(2)
arduino.reset_input_buffer()
print(" Connected\n")


# neutral : send all to 90 first
def send_raw(t1, t2, t3, t4, t5, t6):
    cmd = f"t1:{t1},t2:{t2},t3:{t3},t4:{t4},t5:{t5},t6:{t6}\n"
    arduino.write(cmd.encode())
    time.sleep(0.3)


def all_neutral():
    send_raw(90, 90, 90, 90, 90, 90)
    time.sleep(1)


print("Sending all servos to 90°...")
all_neutral()
print("All at 90°. Observe the robot.\n")

results = {}

joints = [
    ('t1', 'LEFT  HIP', [2, 3, 4, 5, 6]),
    ('t2', 'LEFT  KNEE', [2, 3, 4, 5, 6]),
    ('t3', 'LEFT  ANKLE', [2, 3, 4, 5, 6]),
    ('t4', 'RIGHT HIP', [2, 3, 4, 5, 6]),
    ('t5', 'RIGHT KNEE', [2, 3, 4, 5, 6]),
    ('t6', 'RIGHT ANKLE', [2, 3, 4, 5, 6]),
]

# index mapping for sending
slot = {'t1': 0, 't2': 1, 't3': 2, 't4': 3, 't5': 4, 't6': 5}


def send_one(joint, angle, others_at=90):
    vals = [others_at] * 6
    vals[slot[joint]] = angle
    send_raw(*vals)


for joint, name, _ in joints:
    print("=" * 45)
    print(f"TESTING: {name}  ({joint})")
    print("=" * 45)

    # reset all to 90
    all_neutral()
    time.sleep(0.5)

    # ── STEP 1: find neutral ─────────────────────────────────────
    print(f"\nSTEP 1 — Find neutral angle")
    print("Current angle: 90°")
    print("The joint should look straight/neutral.")
    print("If it doesn't, type an angle to try (or press Enter to keep 90°):")

    neutral = 90
    while True:
        user = input(f"  Try angle [{neutral}]: ").strip()
        if user == '':
            break
        try:
            neutral = int(user)
            send_one(joint, neutral)
            print(f"  Moved to {neutral}°. Does it look neutral now? (Enter=yes, type new angle=no)")
        except:
            print("  Invalid input")

    results[joint] = {'neutral': neutral, 'min': None, 'max': None}
    print(f"  Neutral set to {neutral}°")

    # ── STEP 2: find minimum angle ───────────────────────────────
    print(f"\nSTEP 2 : Find minimum angle (moving DOWN from {neutral}°)")
    print("Watch carefully. Type 's' and Enter the MOMENT you see/hear:")
    print("   The joint hit its physical limit")
    print("   The servo makes a struggling sound")
    print("   The movement looks wrong or dangerous")
    print("Starting slow sweep...")

    current = neutral
    min_angle = 10  # absolute floor
    for angle in range(neutral, 9, -2):  # slow steps of 2°
        send_one(joint, angle)
        current = angle
        print(f"  angle: {angle}°", end='\r')

        # check for input without blocking
        import sys, select

        if sys.stdin in select.select([sys.stdin], [], [], 0.1)[0]:
            user = sys.stdin.readline().strip()
            if user.lower() == 's':
                min_angle = current + 5  # back off 5° from where they stopped
                print(f"\n   Stopped at {current}°. Safe minimum = {min_angle}°")
                break
    else:
        min_angle = current
        print(f"\n  Reached floor. Minimum = {min_angle}°")

    results[joint]['min'] = min_angle
    send_one(joint, neutral)
    time.sleep(0.5)

    #  STEP 3: find maximum angle
    print(f"\nSTEP 3 — Find maximum angle (moving UP from {neutral}°)")
    print("Same as before — type 's' + Enter when limit is reached.")

    max_angle = 170
    for angle in range(neutral, 171, 2):
        send_one(joint, angle)
        current = angle
        print(f"  angle: {angle}°", end='\r')

        if sys.stdin in select.select([sys.stdin], [], [], 0.1)[0]:
            user = sys.stdin.readline().strip()
            if user.lower() == 's':
                max_angle = current - 5
                print(f"\n   Stopped at {current}°. Safe maximum = {max_angle}°")
                break
    else:
        max_angle = current
        print(f"\n  Reached ceiling. Maximum = {max_angle}°")

    results[joint]['max'] = max_angle
    send_one(joint, neutral)
    time.sleep(0.5)

    print(f"\n  {name} summary:")
    print(f"    Neutral = {results[joint]['neutral']}°")
    print(f"    Min     = {results[joint]['min']}°")
    print(f"    Max     = {results[joint]['max']}°")
    input("  Press Enter for next joint...\n")

# FINAL RESULTS
all_neutral()

print("\n" + "=" * 45)
print("FINAL RESULTS : ")
print("=" * 45)
print("OFFSETS = {")
offset_map = {
    't1': 'L_HIP',
    't2': 'L_KNEE',
    't3': 'L_ANKLE',
    't4': 'R_HIP',
    't5': 'R_KNEE',
    't6': 'R_ANKLE',
}
for joint, data in results.items():
    offset = data['neutral'] - 90
    key = offset_map[joint]
    sign = '+' if offset >= 0 else ''
    print(f"    '{key}': {offset},  # servo neutral is {data['neutral']}°")

print("}\n")
all_mins = [d['min'] for d in results.values() if d['min']]
all_maxs = [d['max'] for d in results.values() if d['max']]
if all_mins and all_maxs:
    print(f"  const int SERVO_MIN = {max(all_mins)};")
    print(f"  const int SERVO_MAX = {min(all_maxs)};")

print("\nFull per-joint breakdown:")
for joint, data in results.items():
    name = [n for j, n, _ in joints if j == joint][0]
    print(f"  {name:15s}: neutral={data['neutral']}°  "
          f"range=[{data['min']}° → {data['max']}°]")

arduino.close()
