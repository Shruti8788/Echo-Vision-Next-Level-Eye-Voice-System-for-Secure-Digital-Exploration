import argparse
import time
from typing import Optional

import cv2

from config import Config
from vision.tracker import FaceTracker
from gestures.detector import GestureDetector
from control.instagram import InstagramController
from control.youtube_shorts import YouTubeShortsController
from voice.recognizer import VoiceRecognizer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Eye & Voice Controlled Social Interaction")
    parser.add_argument("--instagram", type=str, default="https://www.instagram.com/reels/",
                        help="Instagram URL to open (default: Reels)")
    parser.add_argument("--youtube", type=str, default="https://www.youtube.com/shorts",
                        help="YouTube Shorts URL to open")
    parser.add_argument("--platform", choices=["instagram", "youtube"], default="instagram",
                        help="Target platform controlled by gestures/voice")
    parser.add_argument("--no-preview", action="store_true", help="Disable camera preview window")
    parser.add_argument("--camera", type=int, default=None, help="Camera index override")
    parser.add_argument("--no-voice", action="store_true", help="Disable voice recognition")
    parser.add_argument("--voice-only", action="store_true", help="Voice commands only (no gestures)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = Config()
    if args.no_preview:
        cfg.ui.show_preview = False
    if args.camera is not None:
        cfg.video.camera_index = args.camera

    if args.platform == "youtube":
        controller = YouTubeShortsController(args.youtube)
    else:
        controller = InstagramController(args.instagram)

    controller.open()

    tracker = FaceTracker(cfg)
    detector = GestureDetector(cfg)
    
    # Initialize voice recognition (optional)
    voice_recognizer = None
    if not args.no_voice:
        try:
            voice_recognizer = VoiceRecognizer(cfg)
            voice_recognizer.start_listening(detector.handle_voice_command)
            print("Voice recognition enabled!")
        except Exception as e:
            print(f"Voice recognition failed to start: {e}")
            print("   Continuing with gesture-only mode...")
            voice_recognizer = None

    last_frame_time_ms: Optional[int] = None

    try:
        for frame_bgr, metrics in tracker.frames():
            now_ms = int(time.time() * 1000)
            dt_ms = 0 if last_frame_time_ms is None else now_ms - last_frame_time_ms
            last_frame_time_ms = now_ms

            events = detector.update(metrics, now_ms, dt_ms)

            if events.scroll:
                controller.scroll(direction=events.scroll)
            if events.like:
                controller.like()
            if events.unlike:
                controller.unlike()
            if events.save:
                controller.save()
            if events.unsave:
                controller.unsave()
            if events.share_target:
                share_target = events.share_target.strip()
                if share_target:
                    print(f"📤 SHARE EVENT TRIGGERED: '{share_target}'")
                    share_action = getattr(controller, "share", None)
                    if callable(share_action):
                        print(f"   → Calling controller.share('{share_target}')")
                        share_action(share_target)
                    else:
                        print(f"   ✗ Share action not supported on this platform.")
                else:
                    print("   ✗ Share target is empty")
            
            if events.navigate_target:
                navigate_target = events.navigate_target.strip()
                if navigate_target:
                    print(f"🧭 NAVIGATION EVENT TRIGGERED: '{navigate_target}'")
                    navigate_action = getattr(controller, "navigate", None)
                    if callable(navigate_action):
                        print(f"   → Calling controller.navigate('{navigate_target}')")
                        navigate_action(navigate_target)
                    else:
                        print(f"   ✗ Navigation not supported on this platform.")
                else:
                    print("   ✗ Navigation target is empty")

            if cfg.ui.show_preview:
                display = tracker.draw_overlay(frame_bgr.copy(), metrics, events)
                cv2.imshow("Eye & Voice IG Control", display)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    finally:
        if voice_recognizer:
            voice_recognizer.stop_listening()
        tracker.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    url = "https://www.instagram.com/reels/"
    
    bot = InstagramController(url)
    bot.open()