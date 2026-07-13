from dataclasses import dataclass
from typing import Optional

from config import Config
from gestures.types import FaceMetrics, GestureEvents
from voice.recognizer import VoiceCommand, VoiceEvents


@dataclass
class _RaiseState:
    last_raise_ms: Optional[int] = None
    pending_raises: int = 0
    left_eyebrow_raising: bool = False  
    right_eyebrow_raising: bool = False 
    both_eyebrows_raising: bool = False  
    raise_start_ms: Optional[int] = None 
    left_raise_start_ms: Optional[int] = None 
    right_raise_start_ms: Optional[int] = None 


@dataclass
class _BlinkState:
    is_blinking: bool = False
    blink_start_ms: Optional[int] = None
    blink_count: int = 0
    last_blink_ms: Optional[int] = None


@dataclass
class _ThumbState:
    left_thumb_down: bool = False
    right_thumb_down: bool = False
    last_thumb_unsave_ms: Optional[int] = None


class GestureDetector:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self._raise = _RaiseState()
        self._blink = _BlinkState()
        self._thumb = _ThumbState()
        self._last_action_ms: Optional[int] = None
       
        self.eyebrow_raise_threshold = 0.3
        
        self.pending_voice_command: Optional[VoiceEvents] = None

    def handle_voice_command(self, voice_event: VoiceEvents) -> None:
        """Handle incoming voice commands."""
        if voice_event.command != VoiceCommand.NONE:
            self.pending_voice_command = voice_event
            print(
                f"Voice command received: {voice_event.command.value}"
                f" (confidence: {voice_event.confidence:.2f})"
                + (f" target='{voice_event.target}'" if getattr(voice_event, "target", None) else "")
            )

    def update(self, metrics: FaceMetrics, now_ms: int, dt_ms: int) -> GestureEvents:
        like = False
        unlike = False
        save = False
        unsave = False
        scroll: Optional[str] = None
        share_target: Optional[str] = None
        navigate_target: Optional[str] = None

        if not metrics.has_face:
           
            self._raise.pending_raises = 0
            self._raise.last_raise_ms = None
            self._raise.left_eyebrow_raising = False
            self._raise.right_eyebrow_raising = False
            self._raise.both_eyebrows_raising = False
            self._raise.left_raise_start_ms = None
            self._raise.right_raise_start_ms = None
           
            left_raised = False
            right_raised = False
        else:
           
            left_raised = metrics.left_eyebrow_y <= self.eyebrow_raise_threshold
            right_raised = metrics.right_eyebrow_y <= self.eyebrow_raise_threshold
        
        if metrics.has_face and now_ms % 1000 < 50:  # Print roughly every second
            left_status = "RAISED" if left_raised else "normal"
            right_status = "RAISED" if right_raised else "normal"
            both_status = "BOTH RAISED!" if (left_raised and right_raised) else "not both"
            print(f"DEBUG: L_brow={metrics.left_eyebrow_y:.3f} ({left_status}), R_brow={metrics.right_eyebrow_y:.3f} ({right_status}), {both_status}")
            print(f"THRESHOLD: {self.eyebrow_raise_threshold:.3f} (lower = more sensitive)")
      
        if metrics.has_face:
            if left_raised and not self._raise.left_eyebrow_raising:
                self._raise.left_eyebrow_raising = True
                self._raise.left_raise_start_ms = now_ms
                print(f"Left eyebrow raised - {metrics.left_eyebrow_y:.3f}")
            elif not left_raised and self._raise.left_eyebrow_raising:
                self._raise.left_eyebrow_raising = False
                self._raise.left_raise_start_ms = None
                print(f"Left eyebrow lowered")
                
            if right_raised and not self._raise.right_eyebrow_raising:
                self._raise.right_eyebrow_raising = True
                self._raise.right_raise_start_ms = now_ms
                print(f"Right eyebrow raised - {metrics.right_eyebrow_y:.3f}")
            elif not right_raised and self._raise.right_eyebrow_raising:
                self._raise.right_eyebrow_raising = False
                self._raise.right_raise_start_ms = None
                print(f"Right eyebrow lowered")
        
        
        if metrics.has_face:
            both_raised = left_raised and right_raised
        else:
            both_raised = False
        
        if both_raised and not self._raise.both_eyebrows_raising:
            self._raise.both_eyebrows_raising = True
            self._raise.raise_start_ms = now_ms
            print(f"BOTH EYEBROWS RAISED SIMULTANEOUSLY!")
            
            if self._cooldown_ready(now_ms):
                scroll = "down"
                self._set_cooldown(now_ms)
                self._raise.last_raise_ms = now_ms
                print("STRICT SCROLL - BOTH EYEBROWS DETECTED!")
                self._raise.raise_start_ms = None 
                
        elif not both_raised and self._raise.both_eyebrows_raising:
            
            self._raise.both_eyebrows_raising = False
        
            if self._raise.raise_start_ms is not None:
                held_ms = now_ms - self._raise.raise_start_ms
                print(f"Both eyebrows held for {held_ms}ms")
                
                if (held_ms >= self.cfg.thresholds.eyebrow_hold_ms and 
                    self._cooldown_ready(now_ms)):
                    
                    scroll = "down"
                    self._set_cooldown(now_ms)
                    self._raise.last_raise_ms = now_ms
                    print("BOTH EYEBROWS HELD SUFFICIENTLY - SCROLLING TO NEXT REEL!")
                else:
                    print(f"Both eyebrows held for {held_ms}ms but not long enough (need {self.cfg.thresholds.eyebrow_hold_ms}ms)")
            
            self._raise.raise_start_ms = None

      
        if metrics.has_face and metrics.ear < self.cfg.thresholds.blink_ear_threshold:
            if not self._blink.is_blinking:
                self._blink.is_blinking = True
                self._blink.blink_start_ms = now_ms
        else:
            if self._blink.is_blinking:
                duration = now_ms - (self._blink.blink_start_ms or now_ms)
                self._blink.is_blinking = False
                self._blink.blink_start_ms = None
                
                if duration >= self.cfg.thresholds.blink_min_duration_ms:
                   
                    self._blink.blink_count += 1
                    self._blink.last_blink_ms = now_ms
                    print(f"Blink detected! Count: {self._blink.blink_count}")
                    
                    
                    if self._blink.blink_count == 3:
                        if self._cooldown_ready(now_ms):
                            like = True
                            self._set_cooldown(now_ms)
                            print("3 BLINKS DETECTED - LIKING POST!")
                        self._blink.blink_count = 0  # Reset counter
        
        
        if self._blink.last_blink_ms and now_ms - self._blink.last_blink_ms > 2000:
            self._blink.blink_count = 0

       
        left_thumb_down_now = metrics.left_thumb_down
        right_thumb_down_now = metrics.right_thumb_down
        
        
        if (left_thumb_down_now or right_thumb_down_now):
         
            if not self._thumb.left_thumb_down and not self._thumb.right_thumb_down:
                
                thumb_cooldown_ready = (self._thumb.last_thumb_unsave_ms is None or 
                                      now_ms - self._thumb.last_thumb_unsave_ms >= 500)  # 500ms cooldown
                
                if thumb_cooldown_ready:
                    unsave = True
                    self._thumb.last_thumb_unsave_ms = now_ms
                    thumb_side = "LEFT" if left_thumb_down_now else "RIGHT"
                    print(f"THUMB DOWN DETECTED ({thumb_side}) - UNSAVING REEL!")
            
           
            self._thumb.left_thumb_down = left_thumb_down_now
            self._thumb.right_thumb_down = right_thumb_down_now
        else:
           
            self._thumb.left_thumb_down = False
            self._thumb.right_thumb_down = False

        unlike_cooldown_ready = (self._last_action_ms is None or 
                                now_ms - self._last_action_ms >= 300)  
        other_cooldown_ready = self._cooldown_ready(now_ms)
        
        if self.pending_voice_command:
            cmd = self.pending_voice_command
            if cmd.command == VoiceCommand.LIKE and other_cooldown_ready:
                like = True
                self._set_cooldown(now_ms)
                print("VOICE: Liking post!")
                self.pending_voice_command = None
            elif cmd.command == VoiceCommand.UNLIKE and unlike_cooldown_ready:
                unlike = True
                # Use shorter cooldown for unlike
                self._last_action_ms = now_ms
                print("VOICE: Unliking post (FAST)!")
                self.pending_voice_command = None
            elif cmd.command == VoiceCommand.SCROLL_NEXT and other_cooldown_ready:
                scroll = "down"
                self._set_cooldown(now_ms)
                print("VOICE: Scrolling DOWN to next reel!")
                self.pending_voice_command = None
            elif cmd.command == VoiceCommand.SCROLL_PREVIOUS and other_cooldown_ready:
                scroll = "up"
                self._set_cooldown(now_ms)
                print("VOICE: Scrolling UP to previous reel!")
                self.pending_voice_command = None
            elif cmd.command == VoiceCommand.SAVE and other_cooldown_ready:
                save = True
                self._set_cooldown(now_ms)
                print("VOICE: Saving reel!")
                self.pending_voice_command = None
            elif cmd.command == VoiceCommand.UNSAVE and unlike_cooldown_ready:
                unsave = True
                self._last_action_ms = now_ms
                print("VOICE: Unsaving reel (FAST)!")
                self.pending_voice_command = None
            elif cmd.command == VoiceCommand.SHARE and cmd.target and other_cooldown_ready:
                share_target = cmd.target
                self._set_cooldown(now_ms)
                print(f"VOICE: Sharing reel to {share_target}!")
                self.pending_voice_command = None
            elif cmd.command == VoiceCommand.SHARE and not cmd.target:
                # Drop invalid share command
                print("VOICE: Share command received without recipient - ignoring")
                self.pending_voice_command = None
            elif cmd.command == VoiceCommand.NAVIGATE and cmd.target and other_cooldown_ready:
                navigate_target = cmd.target
                self._set_cooldown(now_ms)
                print(f"VOICE: Navigating to {navigate_target}!")
                self.pending_voice_command = None

        return GestureEvents(
            scroll=scroll,
            like=like,
            unlike=unlike,
            save=save,
            unsave=unsave,
            share_target=share_target,
            navigate_target=navigate_target,
        )

    def _cooldown_ready(self, now_ms: int) -> bool:
        return self._last_action_ms is None or now_ms - self._last_action_ms >= self.cfg.debounce.action_cooldown_ms

    def _set_cooldown(self, now_ms: int) -> None:
        self._last_action_ms = now_ms
