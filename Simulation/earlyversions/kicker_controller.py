"""
Biped Kicker Robot Controller
Half-body bipedal robot - kicks a ball forward
"""

from controller import Robot

# ── Setup ──────────────────────────────────────────────────────────────────
robot = Robot()
timestep = int(robot.getBasicTimeStep())  # 32ms

# Get all 6 motors
hip_r   = robot.getDevice("hip_right")
knee_r  = robot.getDevice("knee_right")
ankle_r = robot.getDevice("ankle_right")
hip_l   = robot.getDevice("hip_left")
knee_l  = robot.getDevice("knee_left")
ankle_l = robot.getDevice("ankle_left")

all_motors = [hip_r, knee_r, ankle_r, hip_l, knee_l, ankle_l]

# Set velocity limit for all motors
for m in all_motors:
    m.setVelocity(2.0)

# ── Poses ──────────────────────────────────────────────────────────────────
# Each pose = [hip_r, knee_r, ankle_r, hip_l, knee_l, ankle_l]  (radians)

STAND = [
    0.0,   # hip_right    - upright
    0.3,   # knee_right   - slight bend
   -0.3,   # ankle_right  - compensate
    0.0,   # hip_left
    0.3,   # knee_left
   -0.3    # ankle_left
]

WINDUP = [
    0.5,   # hip_right    - swing back (wind up)
    0.8,   # knee_right   - bend knee back
   -0.4,   # ankle_right
    0.0,   # hip_left     - support leg stays
    0.3,   # knee_left
   -0.3    # ankle_left
]

KICK = [
   -0.6,  # hip_right    - swing forward FAST (the kick)
    0.1,  # knee_right   - extend knee
   -0.1,  # ankle_right  - point foot
    0.0,  # hip_left
    0.3,  # knee_left
   -0.3   # ankle_left
]

FOLLOW_THROUGH = [
   -0.3,  # hip_right    - follow through
    0.2,  # knee_right
   -0.2,  # ankle_right
    0.0,  # hip_left
    0.3,  # knee_left
   -0.3   # ankle_left
]

RETURN = [
    0.0,  # hip_right    - return to stand
    0.3,  # knee_right
   -0.3,  # ankle_right
    0.0,  # hip_left
    0.3,  # knee_left
   -0.3   # ankle_left
]

# ── Kick sequence: (time_in_seconds, pose) ────────────────────────────────
sequence = [
    (0.0,  STAND),           # stand still at start
    (1.5,  WINDUP),          # wind up the kick
    (2.5,  KICK),            # kick!
    (3.2,  FOLLOW_THROUGH),  # follow through
    (4.5,  RETURN),          # return to stand
    (6.0,  STAND),           # hold stand
]

# ── Helper function ────────────────────────────────────────────────────────
def apply_pose(pose):
    for motor, angle in zip(all_motors, pose):
        motor.setPosition(angle)

# ── Main control loop ──────────────────────────────────────────────────────
current_pose_index = 0
print("Biped Kicker: Starting up...")
print("Biped Kicker: Will kick at t=2.5 seconds")

while robot.step(timestep) != -1:
    t = robot.getTime()

    # Advance to next pose when time is reached
    if current_pose_index < len(sequence) - 1:
        next_time = sequence[current_pose_index + 1][0]
        if t >= next_time:
            current_pose_index += 1
            pose_name = ["STAND","WINDUP","KICK","FOLLOW_THROUGH","RETURN","STAND"]
            print(f"Biped Kicker: t={t:.2f}s -> {pose_name[current_pose_index]}")

    # Apply current pose
    apply_pose(sequence[current_pose_index][1])
