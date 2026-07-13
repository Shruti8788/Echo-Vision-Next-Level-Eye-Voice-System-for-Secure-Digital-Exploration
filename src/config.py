from dataclasses import dataclass, field


@dataclass
class Thresholds:
    eyebrow_raise_delta: float = 0.04  # absolute delta (legacy)
    eyebrow_raise_relative: float = 0.06  # safer: trigger at +6% over baseline
    eyebrow_hold_ms: int = 50  # very brief hold for quicker response
    brow_smooth_alpha: float = 0.3  # smoothing for eyebrow signal
    rearm_drop_ratio: float = 0.4  # must drop to 40% of raise over baseline to rearm
    double_raise_window_ms: int = 2000  # longer window for 2 raises
    blink_ear_threshold: float = 0.2  # more sensitive to blinks
    blink_min_duration_ms: int = 100  # shorter blink detection
    fixation_ms: int = 700


@dataclass
class Debounce:
    action_cooldown_ms: int = 1000  # longer cooldown to prevent accidental rapid scrolling


@dataclass
class Video:
    camera_index: int = 0
    width: int = 960
    height: int = 540
    flip_horizontal: bool = True


@dataclass
class UI:
    show_preview: bool = True
    draw_landmarks: bool = False


@dataclass
class Config:
    thresholds: Thresholds = field(default_factory=Thresholds)
    debounce: Debounce = field(default_factory=Debounce)
    video: Video = field(default_factory=Video)
    ui: UI = field(default_factory=UI)
