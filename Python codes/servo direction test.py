

import serial
import time


COM_PORT  = '/dev/ttyACM0'
BAUD_RATE = 9600


#  neutral angles from range finder
NEUTRAL = {
    't1': 80,    # Left  Hip
    't2': 90,    # Left  Knee
    't3': 90,    # Left  Ankle
    't4': 80,    # Right Hip
    't5': 100,   # Right Knee
    't6': 100,   # Right Ankle
}


print("Connecting...")
arduino = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
time.sleep(2)
arduino.reset_input_buffer()
print(" Connected\n")

def send_raw(t1, t2, t3, t4, t5, t6):
    cmd = f"t1:{t1},t2:{t2},t3:{t3},t4:{t4},t5:{t5},t6:{t6}\n"
    arduino.write(cmd.encode())
    time.sleep(0.5)   # give servo time to reach position

def all_neutral():
    n = NEUTRAL
    send_raw(n['t1'], n['t2'], n['t3'], n['t4'], n['t5'], n['t6'])
    time.sleep(1)

def send_one(joint, angle):
    """Send angle to one joint, all others at neutral."""
    n = NEUTRAL.copy()
    n[joint] = angle
    send_raw(n['t1'], n['t2'], n['t3'], n['t4'], n['t5'], n['t6'])

# ── JOINTS TO TEST ────────────────────────────────────────────────
joints = [
    ('t1', 'LEFT  HIP',   'When angle increases: does leg swing FORWARD or BACKWARD?'),
    ('t2', 'LEFT  KNEE',  'When angle increases: does shin swing FORWARD or BACKWARD?'),
    ('t3', 'LEFT  ANKLE', 'When angle increases: does foot tilt UP or DOWN?'),
    ('t4', 'RIGHT HIP',   'When angle increases: does leg swing FORWARD or BACKWARD?'),
    ('t5', 'RIGHT KNEE',  'When angle increases: does shin swing FORWARD or BACKWARD?'),
    ('t6', 'RIGHT ANKLE', 'When angle increases: does foot tilt UP or DOWN?'),
]

results = {}

print("=" * 55)
print("SERVO DIRECTION TEST")
print("=" * 55)
print("For each joint:")
print("  1. Look at it moving +10 degrees from neutral")
print("  2. Look at it moving -10 degrees from neutral")
print("  3. Answer the question about its direction")
print("=" * 55)

for joint, name, question in joints:
    neutral = NEUTRAL[joint]

    print(f"\n{'='*55}")
    print(f"JOINT: {name}  (neutral = {neutral} deg)")
    print(f"{'='*55}")

    # go to neutral first
    print(f"\nGoing to neutral ({neutral} deg)...")
    all_neutral()
    time.sleep(0.5)
    input("Press Enter to see +10 degrees...")

    # increase by 10
    plus = min(neutral + 10, 170)
    print(f"Moving to {plus} deg (+10)...")
    send_one(joint, plus)
    time.sleep(0.5)

    # back to neutral
    input("Observe. Press Enter to see -10 degrees...")
    all_neutral()
    time.sleep(0.3)

    # decrease by 10
    minus = max(neutral - 10, 10)
    print(f"Moving to {minus} deg (-10)...")
    send_one(joint, minus)
    time.sleep(0.5)

    input("Observe. Press Enter to answer...")
    all_neutral()

    # ask direction
    print(f"\n{question}")

    if 'HIP' in name:
        print("  f = Forward when increased")
        print("  b = Backward when increased")
        ans = input("  Your answer (f/b): ").strip().lower()
        results[joint] = 'forward' if ans == 'f' else 'backward'

    elif 'KNEE' in name:
        print("  f = Shin goes forward when increased")
        print("  b = Shin goes backward when increased")
        ans = input("  Your answer (f/b): ").strip().lower()
        results[joint] = 'forward' if ans == 'f' else 'backward'

    elif 'ANKLE' in name:
        print("  l = left")
        print("  r = right")
        ans = input("  Your answer (l/r): ").strip().lower()
        results[joint] = 'left' if ans == 'l' else 'right'

    print(f"  Recorded: {joint} → {results[joint]}")

# RESULTS
all_neutral()

print("\n" + "=" * 55)
print("RESULTS")
print("=" * 55)
for joint, name, _ in joints:
    if joint in results:
        print(f"  {name:<15}: increases → {results[joint]}")

arduino.close()