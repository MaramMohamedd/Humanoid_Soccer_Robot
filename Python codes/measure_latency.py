
import cv2
import numpy as np
import time

LOWER_BALL = np.array([125, 50,  50])
UPPER_BALL = np.array([155, 255, 255])

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Could not open webcam")
    exit()

print("Running latency test...")
print("Move the ball in and out of frame while this runs.")
print("Press Q to stop and see results.\n")

latencies = []

while True:
    ret, frame = cap.read()
    if not ret:
        break

    start = time.time()

    # DETECTION (same as real vision code)
    blurred = cv2.GaussianBlur(frame, (5, 5), 0)
    hsv     = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    mask    = cv2.inRange(hsv, LOWER_BALL, UPPER_BALL)
    mask    = cv2.erode(mask,  None, iterations=2)
    mask    = cv2.dilate(mask, None, iterations=2)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
    ball_visible = False
    if contours:
        c = max(contours, key=cv2.contourArea)
        if cv2.contourArea(c) > 500:
            (x, y), radius = cv2.minEnclosingCircle(c)
            if radius > 5:
                ball_visible = True
                cv2.circle(frame, (int(x), int(y)), int(radius), (0,255,0), 2)

    #  STOP TIMER
    end = time.time()
    latency_ms = (end - start) * 1000
    latencies.append(latency_ms)

    # live display
    status = "BALL DETECTED" if ball_visible else "no ball"
    cv2.putText(frame, f"Latency: {latency_ms:.1f} ms", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
    cv2.putText(frame, f"Frames: {len(latencies)}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
    cv2.putText(frame, status, (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,200,255), 2)
    cv2.imshow("Latency Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

#  RESULTS
if not latencies:
    print("No frames captured.")
else:
    avg = sum(latencies) / len(latencies)
    mn  = min(latencies)
    mx  = max(latencies)
    fps = 1000 / avg

    print("=" * 40)
    print("LATENCY RESULTS")
    print("=" * 40)
    print(f"Total frames measured : {len(latencies)}")
    print(f"Average latency       : {avg:.1f} ms")
    print(f"Minimum latency       : {mn:.1f} ms")
    print(f"Maximum latency       : {mx:.1f} ms")
    print(f"Effective FPS         : {fps:.1f}")
    print("=" * 40)
