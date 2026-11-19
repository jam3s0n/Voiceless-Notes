
import cv2
import mediapipe as mp
import math
import time

from PyQt6.QtCore import QThread, pyqtSignal


# calibration settings
OPEN_THRESHOLD = 0.50
CLOSE_THRESHOLD = 0.35

HOLD_TIME = 0.600
DOUBLE_GAP = 0.800
MIN_PULSE = 0.080

STRETCH_THRESHOLD = 1.15
STRETCH_RELEASE = 1.08
STRETCH_HOLD = 0.400

CALIBRATION_TIME = 3.0


def calculate_mar(landmarks, width, height):
    upper = landmarks[13]
    lower = landmarks[14]
    left = landmarks[61]
    right = landmarks[291]

    vertical = math.hypot(
        (upper.x - lower.x) * width,
        (upper.y - lower.y) * height
    )

    horizontal = math.hypot(
        (left.x - right.x) * width,
        (left.y - right.y) * height
    )

    return vertical / max(horizontal, 1e-6)


def calculate_mouth_width(landmarks):
    left = landmarks[61]
    right = landmarks[291]

    return math.hypot(
        right.x - left.x,
        right.y - left.y
    )


class GestureDetector(QThread):

    gesture_detected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = True

    def stop(self):
        self.running = False
        self.wait()

    def run(self):
        mp_face_mesh = mp.solutions.face_mesh
        camera = cv2.VideoCapture(0)

        if not camera.isOpened():
            print("Could not open webcam")
            return

        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        mouth_open = False
        open_start = None
        first_pulse_end = None
        gesture_triggered = False

        neutral_width = None
        calibration_start = None
        calibration_samples = []

        stretch_start = None
        stretch_triggered = False

        with mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        ) as face_mesh:

            while self.running:
                success, frame = camera.read()

                if not success:
                    break

                frame = cv2.flip(frame, 1)
                height, width = frame.shape[:2]

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = face_mesh.process(rgb)

                now = time.perf_counter()
                status = "NO FACE"

                if results.multi_face_landmarks:
                    landmarks = (
                        results.multi_face_landmarks[0].landmark
                    )

                    mar = calculate_mar(
                        landmarks, width, height
                    )

                    mouth_width = calculate_mouth_width(
                        landmarks
                    )

                    if neutral_width is None:
                        if calibration_start is None:
                            calibration_start = now

                        if mar < CLOSE_THRESHOLD:
                            calibration_samples.append(
                                mouth_width
                            )

                        elapsed = now - calibration_start
                        remaining = max(
                            0, CALIBRATION_TIME - elapsed
                        )

                        status = (
                            f"CALIBRATING: {remaining:.1f}s"
                        )

                        if elapsed >= CALIBRATION_TIME:
                            if calibration_samples:
                                neutral_width = (
                                    sum(calibration_samples)
                                    / len(calibration_samples)
                                )
                                print("Calibration complete!")
                            else:
                                calibration_start = now

                    else:
                        stretch_ratio = (
                            mouth_width / max(
                                neutral_width, 1e-6
                            )
                        )

                        # Horizontal stretch
                        if not stretch_triggered:
                            if (
                                stretch_ratio >= STRETCH_THRESHOLD
                                and mar < CLOSE_THRESHOLD
                            ):
                                if stretch_start is None:
                                    stretch_start = now

                                if (
                                    now - stretch_start
                                    >= STRETCH_HOLD
                                ):
                                    self.gesture_detected.emit(
                                        "UNDO"
                                    )
                                    status = "UNDO DETECTED"
                                    stretch_triggered = True
                                    first_pulse_end = None
                            else:
                                stretch_start = None
                        else:
                            if (
                                stretch_ratio
                                <= STRETCH_RELEASE
                            ):
                                stretch_triggered = False
                                stretch_start = None

                        # Expire old pulse
                        if (
                            first_pulse_end is not None
                            and not mouth_open
                            and now - first_pulse_end
                            > DOUBLE_GAP
                        ):
                            first_pulse_end = None

                        # Mouth opens
                        if (
                            not mouth_open
                            and mar >= OPEN_THRESHOLD
                        ):
                            mouth_open = True
                            open_start = now
                            gesture_triggered = False
                            stretch_start = None

                        # Mouth closes
                        elif (
                            mouth_open
                            and mar <= CLOSE_THRESHOLD
                        ):
                            duration = now - open_start
                            mouth_open = False
                            open_start = None

                            if not gesture_triggered:
                                if (
                                    MIN_PULSE
                                    <= duration
                                    < HOLD_TIME
                                ):
                                    if (
                                        first_pulse_end
                                        is not None
                                        and now
                                        - first_pulse_end
                                        <= DOUBLE_GAP
                                    ):
                                        self.gesture_detected.emit(
                                            "IMPORTANT"
                                        )
                                        status = (
                                            "DOUBLE PULSE DETECTED"
                                        )
                                        first_pulse_end = None
                                    else:
                                        first_pulse_end = now
                                else:
                                    first_pulse_end = None

                            gesture_triggered = False

                        # Sustained mouth open
                        if (
                            mouth_open
                            and open_start is not None
                        ):
                            elapsed = now - open_start

                            if (
                                elapsed >= HOLD_TIME
                                and not gesture_triggered
                            ):
                                self.gesture_detected.emit(
                                    "NEW_LINE"
                                )
                                gesture_triggered = True
                                first_pulse_end = None

                            if gesture_triggered:
                                status = "NEW LINE DETECTED"
                            else:
                                status = (
                                    f"OPEN: {elapsed:.2f}s"
                                )

                        elif status not in (
                            "UNDO DETECTED",
                            "DOUBLE PULSE DETECTED"
                        ):
                            status = "MOUTH CLOSED"

                        cv2.putText(
                            frame,
                            f"Stretch: {stretch_ratio:.2f}",
                            (30, 150),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 255, 255),
                            2
                        )

                    cv2.putText(
                        frame,
                        f"MAR: {mar:.3f}",
                        (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2
                    )

                    for index in [13, 14, 61, 291]:
                        point = landmarks[index]

                        x = int(point.x * width)
                        y = int(point.y * height)

                        cv2.circle(
                            frame,
                            (x, y),
                            4,
                            (0, 0, 255),
                            -1
                        )

                else:
                    mouth_open = False
                    open_start = None
                    first_pulse_end = None
                    gesture_triggered = False
                    stretch_start = None
                    stretch_triggered = False
                    calibration_start = None
                    calibration_samples = []

                cv2.putText(
                    frame,
                    status,
                    (30, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2
                )

                cv2.imshow(
                    "SilentNotes - Webcam Preview",
                    frame
                )

                if (
                    cv2.waitKey(1) & 0xFF
                    == ord("q")
                ):
                    break

        camera.release()
        cv2.destroyAllWindows()
