# 🤖 Humanoid Soccer Robot  

## Overview

This project implements a fully functional humanoid soccer robot capable of autonomously detecting a ball, walking toward it using a gait pattern, and kicking the ball when close enough. The robot operates using a finite state machine (FSM) that transitions between three states: Waiting, Walking, and Kicking. The system integrates computer vision for ball detection, inverse kinematics for precise kicking motion, and a web-based dashboard for real-time monitoring. Simulation is implemented in PyBullet, and the physical robot is built using Arduino UNO and SG90 servos.

## Features

- **Ball Detection**: Uses HSV color segmentation to detect the ball and separate it from the environment
- **Walking Gait**: Custom-implemented walking pattern for stable bipedal locomotion
- **Kicking Motion**: Inverse kinematics (IK) for precise and controlled kicking
- **Finite State Machine (FSM)**: States: Waiting → Walking → Kicking
- **Web Dashboard**: Real-time display of ball coordinates, distance from camera to ball, and robot state
- **PyBullet Simulation**: Physics-based simulation environment for testing
- **Hardware Implementation**: 6 DOF humanoid robot (3 DOF per leg) using SG90 servos and Arduino UNO

## System Architecture

The project includes three main diagrams:
- **Software Architecture Diagram**
- **Hardware Architecture Diagram**
- **System Overall Diagram**

## Hardware Components

| Component | Specification |
|-----------|---------------|
| Microcontroller | Arduino UNO |
| Servo Motors | SG90 (6 units, 3 per leg) |
| Battery | 7.2V LiPo |
| Voltage Regulator | Buck Converter |
| Power Switch | Toggle switch |
| Capacitors | For power smoothing |
| Connecting Wires | Jumper wires |

**Total Degrees of Freedom**: 6 (3 DOF per leg)

## Software Stack

### Languages
- C/C++ (Arduino firmware)
- Python (Vision, Web app, Simulation, IK calculations)

### Key Libraries
- **OpenCV** – HSV color detection and image processing
- **Flask** – Web dashboard for real-time monitoring
- **NumPy** – Mathematical computations and IK
- **PyBullet** – Robot simulation
- **Serial** – Communication between Python and Arduino

## Ball Detection Performance

| Metric | Value |
|--------|-------|
| Total frames measured | 1178 |
| Average detection latency | 2.9 ms |
| Minimum latency (best case) | 0.8 ms |
| Maximum latency (worst case) | 8.3 ms |
| Effective processing rate | 345.5 FPS |

The ball is consistently detected with high speed and low latency, enabling real-time decision making.

## Finite State Machine (FSM)

The robot operates using three states:

1. **Waiting** – Robot scans for the ball. No movement.
2. **Walking** – Ball detected but not within kicking range. Robot walks toward the ball using gait pattern.
3. **Kicking** – Ball is within kicking distance. Robot executes IK-based kick, then returns to Waiting.

State transitions are handled automatically based on ball coordinates and distance.

## Walking Gait

A custom walking pattern was implemented for bipedal locomotion. The gait ensures stability while moving toward the ball. Each leg has 3 servos (hip, knee, ankle) coordinated through timing and angle sequences.

## Inverse Kinematics (IK) for Kicking

A custom IK solver calculates the required joint angles to position the kicking leg accurately toward the ball. The kick is triggered only when the ball is within a predefined distance threshold.

## Web Dashboard

A Flask-based web application displays:
- **Ball coordinates** (X, Y) in the camera frame
- **Distance** between the camera and the ball
- **Current FSM state** (Waiting / Walking / Kicking)

The dashboard refreshes in real time, providing full visibility into the robot's decision process.

## Simulation (PyBullet)

The robot was simulated in PyBullet to test walking and kicking behaviors before hardware deployment. The simulation includes:
- Physics-based ground interaction
- Joint control via position commands
- Ball detection emulation

## How to Run the Project

### 1. Hardware Setup
- Assemble the robot with 6 SG90 servos (3 per leg)
- Connect servos to Arduino UNO PWM pins
- Power the system using 7.2V LiPo battery through buck converter
- Upload the Arduino firmware (C++)

### 2. Vision & Control (Python)
```bash
git clone https://github.com/yourusername/Humanoid-Soccer-Robot.git
cd Humanoid-Soccer-Robot
pip install opencv-python numpy flask pybullet pyserial
python main.py
