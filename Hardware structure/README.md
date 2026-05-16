## 🔌 Hardware Architecture & Implementation

> **Lead by:** [Maram Mohamed] – circuit design, circuit simulation, physical implementation

### ⚡ The Core Problem We Solved
Servos require more current than the Arduino's 5V pin can supply. Without proper power design, the Arduino resets randomly during movement.

### 🧠 Our Solution Architecture

| Issue | Our Fix |
|-------|---------|
| Insufficient servo power | Separate 7.2V battery + buck converter |
| Arduino resets on servo startup | 1000µF capacitor (energy buffer) |
| Electrical noise interference | 100nF decoupling capacitor |
| Ground loops / floating signals | **Common GND** for all components |
| Arduino power | USB from laptop (stable, isolated) |

### 📐 System Diagram
<table>
  <tr>
    <td><img width="565" height="350" alt="image" src="https://github.com/user-attachments/assets/378afebb-21a5-4df2-a3f0-967c578d656e" />
</td>
    <td><img width="520" height="420" alt="image" src="https://github.com/user-attachments/assets/38f843f7-64b2-4e4d-9b41-c92ff307b7a2" />
</td>
  </tr>
  <tr>
    <td align="center">Simulation</td>
    <td align="center">Circuit design </td>
  </tr>
</table>
*Tinkercad simulation (buck converter not available in simulator)*

### 🔧 Real Wiring Table

| Component | Connection Point |
|-----------|------------------|
| Battery (-ve) | Buck converter -IN |
| Battery (+ve) | Buck converter +IN |
| Buck +OUT | Breadboard (+ve rail) |
| Buck -OUT | Breadboard (-ve rail) |
| 1000µF Cap (+ve) | (+ve rail) |
| 1000µF Cap (-ve) | (-ve rail) |
| 100nF Cap | Across (+ve) and (-ve) rails |
| All Servos VCC | (+ve rail) |
| All Servos GND | (-ve rail) ← **Common GND** |
| Arduino GND | (-ve rail) |

### 🦿 Servo to Arduino Pin Mapping

| Servo | Position | Arduino PWM Pin |
|-------|----------|-----------------|
| Left Hip | Leg | Pin 3 |
| Left Knee | Leg | Pin 5 |
| Left Ankle | Foot | Pin 6 |
| Right Hip | Leg | Pin 9 |
| Right Knee | Leg | Pin 10 |
| Right Ankle | Foot | Pin 11 |

### 📸 Real Implementation
![Real robot wiring](Hardware structure/circuit diagram handwritten.png)

### 🧪 Simulation Limitations (Honest Engineering)
> *"We simulated on Tinkercad and Wokwi, but neither had a buck converter component. We documented the theoretical circuit separately and validated on real hardware."*

### ✅ Hardware Validation
- [x] Servos operate without Arduino resets
- [x] Stable 5V delivered via LM2596 buck converter
- [x] No noise interference (100nF cap working)
- [x] All 6 servos powered simultaneously
