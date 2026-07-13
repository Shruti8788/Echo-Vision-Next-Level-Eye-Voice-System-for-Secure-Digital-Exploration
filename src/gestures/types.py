from dataclasses import dataclass
from typing import Optional


@dataclass
class FaceMetrics:
    has_face: bool
    eyebrow_norm: float 
    left_eyebrow_y: float  
    right_eyebrow_y: float 
    ear: float  
    left_thumb_down: bool = False 
    right_thumb_down: bool = False  


@dataclass
class GestureEvents:
    scroll: Optional[str]  
    like: bool
    unlike: bool = False 
    save: bool = False 
    unsave: bool = False  
    share_target: Optional[str] = None 
    navigate_target: Optional[str] = None  
