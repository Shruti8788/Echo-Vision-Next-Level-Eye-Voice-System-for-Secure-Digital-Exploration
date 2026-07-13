from typing import Generator, Tuple

import cv2
import numpy as np
import mediapipe as mp

from config import Config
from gestures.types import FaceMetrics


class FaceTracker:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.cap = cv2.VideoCapture(cfg.video.camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.video.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.video.height)
        
        # Initialize MediaPipe Face Mesh for facial landmarks
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize MediaPipe Hands for thumb detection
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Eyebrow baseline tracking for normalization
        self.left_eyebrow_baseline: float = None
        self.right_eyebrow_baseline: float = None
        self.baseline_alpha = 0.1

    def close(self) -> None:
        if self.cap:
            self.cap.release()
        if hasattr(self, 'face_mesh'):
            self.face_mesh.close()
        if hasattr(self, 'hands'):
            self.hands.close()

    def frames(self) -> Generator[Tuple[np.ndarray, FaceMetrics], None, None]:
        while True:
            ok, frame = self.cap.read()
            if not ok:
                break
            if self.cfg.video.flip_horizontal:
                frame = cv2.flip(frame, 1)

            # Convert BGR to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_results = self.face_mesh.process(rgb_frame)
            hand_results = self.hands.process(rgb_frame)

            # Detect thumb positions
            left_thumb_down, right_thumb_down = self._detect_thumbs_down(hand_results)

            if face_results.multi_face_landmarks:
                face_landmarks = face_results.multi_face_landmarks[0]
                
                # Extract eyebrow and eye metrics
                left_eyebrow_y, right_eyebrow_y = self._extract_eyebrow_positions(face_landmarks)
                ear = self._compute_ear_from_landmarks(face_landmarks)
                eyebrow_norm = (left_eyebrow_y + right_eyebrow_y) / 2  # Legacy compatibility
                
                metrics = FaceMetrics(
                    has_face=True,
                    eyebrow_norm=eyebrow_norm,
                    left_eyebrow_y=left_eyebrow_y,
                    right_eyebrow_y=right_eyebrow_y,
                    ear=ear,
                    left_thumb_down=left_thumb_down,
                    right_thumb_down=right_thumb_down
                )
            else:
                # Reset baselines when no face detected
                self.left_eyebrow_baseline = None
                self.right_eyebrow_baseline = None
                metrics = FaceMetrics(
                    has_face=False,
                    eyebrow_norm=0.0,
                    left_eyebrow_y=0.5,
                    right_eyebrow_y=0.5,
                    ear=1.0,
                    left_thumb_down=left_thumb_down,
                    right_thumb_down=right_thumb_down
                )

            yield frame, metrics

    def draw_overlay(self, frame: np.ndarray, metrics: FaceMetrics, events) -> np.ndarray:
        h, w = frame.shape[:2]
        text = f"L_brow: {metrics.left_eyebrow_y:.3f}  R_brow: {metrics.right_eyebrow_y:.3f}  ear: {metrics.ear:.3f}"
        
        # Add thumb status
        thumb_status = []
        if metrics.left_thumb_down:
            thumb_status.append("L_thumb↓")
        if metrics.right_thumb_down:
            thumb_status.append("R_thumb↓")
        if thumb_status:
            text += "  |  " + " ".join(thumb_status)
        
        if events and (events.scroll or events.like or events.unsave):
            flags = []
            if events.scroll:
                flags.append(f"scroll:{events.scroll}")
            if events.like:
                flags.append("like")
            if events.unsave:
                flags.append("UNSAVE")
            if flags:
                text += "  |  " + ", ".join(flags)
        cv2.putText(frame, text, (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        return frame

    def _extract_eyebrow_positions(self, landmarks) -> Tuple[float, float]:
        """Extract normalized eyebrow positions from MediaPipe landmarks.
        Returns (left_eyebrow_y, right_eyebrow_y) where lower values = more raised eyebrows.
        """
        # MediaPipe face mesh landmark indices for eyebrows
        # Left eyebrow: 70, 63, 105, 66, 107
        # Right eyebrow: 296, 334, 293, 300, 276
        
        left_eyebrow_indices = [70, 63, 105, 66, 107]
        right_eyebrow_indices = [296, 334, 293, 300, 276]
        
        # Get average Y position for each eyebrow
        left_y = sum(landmarks.landmark[i].y for i in left_eyebrow_indices) / len(left_eyebrow_indices)
        right_y = sum(landmarks.landmark[i].y for i in right_eyebrow_indices) / len(right_eyebrow_indices)
        
        # Update baselines with exponential moving average
        if self.left_eyebrow_baseline is None:
            self.left_eyebrow_baseline = left_y
        else:
            self.left_eyebrow_baseline = (1 - self.baseline_alpha) * self.left_eyebrow_baseline + self.baseline_alpha * left_y
            
        if self.right_eyebrow_baseline is None:
            self.right_eyebrow_baseline = right_y
        else:
            self.right_eyebrow_baseline = (1 - self.baseline_alpha) * self.right_eyebrow_baseline + self.baseline_alpha * right_y
        
        # Return normalized positions (0-1, where lower = more raised)
        left_normalized = max(0.0, min(1.0, (self.left_eyebrow_baseline - left_y) / 0.1 + 0.5))
        right_normalized = max(0.0, min(1.0, (self.right_eyebrow_baseline - right_y) / 0.1 + 0.5))
        
        return left_normalized, right_normalized

    @staticmethod
    def _compute_ear_from_landmarks(landmarks) -> float:
        """Compute Eye Aspect Ratio from MediaPipe landmarks."""
        # MediaPipe face mesh landmark indices for eyes
        # Left eye: [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        # Right eye: [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        
        left_eye_indices = [33, 133, 157, 158, 159, 160, 161, 144, 145, 153, 154, 155]
        right_eye_indices = [362, 263, 387, 388, 390, 249, 373, 374, 380, 381, 382, 466]
        
        def compute_ear_for_eye(eye_indices):
            # Get eye landmarks
            eye_points = [(landmarks.landmark[i].x, landmarks.landmark[i].y) for i in eye_indices]
            
            # Calculate distances for EAR formula
            # EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)
            # Using simplified version with available points
            if len(eye_points) >= 6:
                # Vertical distances (eyeball height)
                v1 = abs(eye_points[1][1] - eye_points[5][1])
                v2 = abs(eye_points[2][1] - eye_points[4][1])
                
                # Horizontal distance (eyeball width)
                h = abs(eye_points[0][0] - eye_points[3][0])
                
                if h > 0:
                    return (v1 + v2) / (2.0 * h)
            
            return 0.3  # Default value for closed eye
        
        left_ear = compute_ear_for_eye(left_eye_indices)
        right_ear = compute_ear_for_eye(right_eye_indices)
        
        return (left_ear + right_ear) / 2.0
    
    def _detect_thumbs_down(self, hand_results) -> Tuple[bool, bool]:
        """Detect if left or right thumb is pointing downward.
        Returns (left_thumb_down, right_thumb_down)
        """
        left_thumb_down = False
        right_thumb_down = False
        
        if not hand_results.multi_hand_landmarks:
            return left_thumb_down, right_thumb_down
        
        for hand_landmarks, handedness in zip(hand_results.multi_hand_landmarks, hand_results.multi_handedness):
            # Get hand label (Left or Right from camera's perspective)
            hand_label = handedness.classification[0].label
            
            # MediaPipe hand landmark indices:
            # Thumb tip: 4
            # Thumb MCP (base): 2
            # Index finger tip: 8
            # Wrist: 0
            
            thumb_tip = hand_landmarks.landmark[4]
            thumb_mcp = hand_landmarks.landmark[2]
            wrist = hand_landmarks.landmark[0]
            index_tip = hand_landmarks.landmark[8]
            
            # Check if thumb is pointing downward
            # Thumb is down if:
            # 1. Thumb tip Y is greater than thumb MCP Y (thumb pointing down)
            # 2. Thumb tip Y is significantly lower than wrist Y
            
            thumb_tip_y = thumb_tip.y
            thumb_mcp_y = thumb_mcp.y
            wrist_y = wrist.y
            
            # Thumb is down if tip is below MCP (thumb extended downward)
            is_thumb_down = thumb_tip_y > thumb_mcp_y + 0.05  # 0.05 threshold for detection
            
            # Also check if thumb tip is significantly below wrist
            if thumb_tip_y > wrist_y + 0.1:
                is_thumb_down = True
            
            # Determine if this is left or right hand (from user's perspective)
            # MediaPipe returns "Left" or "Right" from camera's view
            # We need to flip it if camera is mirrored
            if self.cfg.video.flip_horizontal:
                # If camera is flipped, swap left/right
                if hand_label == "Left":
                    right_thumb_down = is_thumb_down
                else:
                    left_thumb_down = is_thumb_down
            else:
                # Normal camera view
                if hand_label == "Left":
                    left_thumb_down = is_thumb_down
                else:
                    right_thumb_down = is_thumb_down
        
        return left_thumb_down, right_thumb_down
