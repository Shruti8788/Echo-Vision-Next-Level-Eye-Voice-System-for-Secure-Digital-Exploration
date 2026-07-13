import speech_recognition as sr
import threading
import time
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum

from config import Config


class VoiceCommand(Enum):
    LIKE = "like"
    UNLIKE = "unlike" 
    SCROLL_NEXT = "scroll next"
    SCROLL_PREVIOUS = "scroll previous"
    SAVE = "save"
    UNSAVE = "unsave"
    SHARE = "share"
    NAVIGATE = "navigate"
    NONE = "none"


@dataclass
class VoiceEvents:
    command: VoiceCommand
    confidence: float
    raw_text: str
    target: Optional[str] = None


class VoiceRecognizer:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.recognizer = sr.Recognizer()
        
        # Try to find and use the default microphone
        try:
            # List available microphones
            mic_list = sr.Microphone.list_microphone_names()
            print(f"Available microphones: {mic_list}")
            
            # Use default microphone
            self.microphone = sr.Microphone()
            print(f"Using microphone: {self.microphone.device_index}")
            
            # Adjust for ambient noise with longer duration
            print("Adjusting microphone for ambient noise...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print("Microphone calibrated!")
            
            # Set energy threshold lower for better detection
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            
        except Exception as e:
            print(f"Microphone setup error: {e}")
            raise
        
        # Voice command mappings - optimized for reliable recognition
        self.command_mappings = {
            # LIKE commands
            "like": VoiceCommand.LIKE,
            "like the post": VoiceCommand.LIKE,
            "like post": VoiceCommand.LIKE,
            "like this": VoiceCommand.LIKE,
            "heart": VoiceCommand.LIKE,
            "love": VoiceCommand.LIKE,
            "love it": VoiceCommand.LIKE,
            "thumbs up": VoiceCommand.LIKE,
            
            # UNLIKE commands - optimized for fast recognition
            "unlike": VoiceCommand.UNLIKE,
            "unlike the post": VoiceCommand.UNLIKE,
            "unlike post": VoiceCommand.UNLIKE,
            "unlike this": VoiceCommand.UNLIKE,
            "remove like": VoiceCommand.UNLIKE,
            "dislike": VoiceCommand.UNLIKE,
            
            # SCROLL DOWN commands - ONLY "scroll down" allowed
            "scroll down": VoiceCommand.SCROLL_NEXT,
            
            # SCROLL UP commands (previous reel) - keep "scroll previous" as primary
            "scroll previous": VoiceCommand.SCROLL_PREVIOUS,
            "previous": VoiceCommand.SCROLL_PREVIOUS,
            "scroll up": VoiceCommand.SCROLL_PREVIOUS,
            "up": VoiceCommand.SCROLL_PREVIOUS,
            "previous reel": VoiceCommand.SCROLL_PREVIOUS,
            "previous video": VoiceCommand.SCROLL_PREVIOUS,
            "go back": VoiceCommand.SCROLL_PREVIOUS,
            "back": VoiceCommand.SCROLL_PREVIOUS,
            
            # SAVE commands
            "save": VoiceCommand.SAVE,
            "save the reel": VoiceCommand.SAVE,
            "save reel": VoiceCommand.SAVE,
            "save this": VoiceCommand.SAVE,
            "save this reel": VoiceCommand.SAVE,
            "bookmark": VoiceCommand.SAVE,
            "bookmark this": VoiceCommand.SAVE,
            
            # UNSAVE commands - simplified to just "unsave" for fast recognition
            "unsave": VoiceCommand.UNSAVE,
            "remove bookmark": VoiceCommand.UNSAVE,
            "unbookmark": VoiceCommand.UNSAVE,
        }
        
        self.is_listening = False
        self.callback: Optional[Callable[[VoiceEvents], None]] = None
        
    def start_listening(self, callback: Callable[[VoiceEvents], None]):
        """Start continuous voice recognition in a separate thread."""
        self.callback = callback
        self.is_listening = True
        
        def listen_loop():
            print("Voice recognition started! Say commands like:")
            print("   - 'like the post' - to like")
            print("   - 'unlike the post' - to unlike") 
            print("   - 'scroll down' - to go to next reel")
            print("   - 'scroll previous' - to go to previous reel")
            print("   - 'save the reel' - to save the current reel")
            print("   - 'unsave' - to unsave the current reel")
            print("   - 'share to <friend name>' - to share the reel to that friend")
            print("   Navigation commands:")
            print("   YouTube: 'go to home', 'go to shorts', 'go to subscriptions', 'go to history', etc.")
            print("   Instagram: 'go to home', 'go to search', 'go to explore', 'go to reels',")
            print("              'go to messages', 'go to notifications', 'go to create', 'go to profile'")
            
            while self.is_listening:
                try:
                    with self.microphone as source:
                        # Listen for audio with longer timeout for better detection
                        print("Listening for voice commands...")
                        # Longer phrase time limit for "share to <name>" commands
                        audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=5)
                    
                    try:
                        # Recognize speech using Google's service
                        text = self.recognizer.recognize_google(audio, language='en-US').lower().strip()
                        print(f"Voice heard: '{text}'")
                        
                        # Process the recognized text
                        command = self._process_command(text)
                        if command.command != VoiceCommand.NONE:
                            print(f"COMMAND DETECTED: {command.command.value}")
                            if self.callback:
                                self.callback(command)
                        else:
                            print(f"No command found for: '{text}'")
                                
                    except sr.UnknownValueError:
                        # Speech was unintelligible, continue listening
                        print("Could not understand speech")
                    except sr.RequestError as e:
                        print(f"Speech recognition error: {e}")
                        
                except sr.WaitTimeoutError:
                    # No speech detected, continue listening
                    pass
                except Exception as e:
                    print(f"Voice recognition error: {e}")
                    time.sleep(0.1)
        
        # Start listening in a separate thread
        self.listen_thread = threading.Thread(target=listen_loop, daemon=True)
        self.listen_thread.start()
        
    def stop_listening(self):
        """Stop voice recognition."""
        self.is_listening = False
        print("Voice recognition stopped.")
        
    def _process_command(self, text: str) -> VoiceEvents:
        """Process recognized text and map to voice commands."""
        print(f"Processing command: '{text}'")
        
        # Check for dynamic share commands (e.g., "share to alex")
        share_phrases = [
            "share to ",
            "share reel to ",
            "share with ",
            "share this to ",
            "share this reel to ",
            "send to ",
            "send reel to ",
            "share to",
            "send to",
        ]
        for prefix in share_phrases:
            if text.startswith(prefix):
                recipient = text[len(prefix):].strip()
                if recipient:
                    print(f"✓ Share command detected! Recipient: '{recipient}'")
                    return VoiceEvents(
                        command=VoiceCommand.SHARE,
                        confidence=1.0,
                        raw_text=text,
                        target=recipient,
                    )
        
        # Also check if text contains "share" and "to" (more flexible)
        words = text.split()
        if "share" in words and "to" in words:
            to_index = words.index("to")
            if to_index + 1 < len(words):
                recipient = " ".join(words[to_index + 1:]).strip()
                if recipient:
                    print(f"✓ Share command detected (flexible)! Recipient: '{recipient}'")
                    return VoiceEvents(
                        command=VoiceCommand.SHARE,
                        confidence=0.9,
                        raw_text=text,
                        target=recipient,
                    )
        
        # Check for navigation commands (e.g., "go to home", "go to shorts")
        navigation_phrases = {
            # YouTube navigation
            "go to home": "home",
            "go home": "home",
            "home": "home",
            "go to shorts": "shorts",
            "go shorts": "shorts",
            "shorts": "shorts",
            "go to subscriptions": "subscriptions",
            "go subscriptions": "subscriptions",
            "subscriptions": "subscriptions",
            "go to history": "history",
            "go history": "history",
            "history": "history",
            "go to playlists": "playlists",
            "go playlists": "playlists",
            "playlists": "playlists",
            "go to your videos": "your videos",
            "go your videos": "your videos",
            "your videos": "your videos",
            "go to your courses": "your courses",
            "go your courses": "your courses",
            "your courses": "your courses",
            "go to watch later": "watch later",
            "go watch later": "watch later",
            "watch later": "watch later",
            "go to liked videos": "liked videos",
            "go liked videos": "liked videos",
            "liked videos": "liked videos",
            "go to downloads": "downloads",
            "go downloads": "downloads",
            "downloads": "downloads",
            # Instagram navigation
            "go to search": "search",
            "go search": "search",
            "search": "search",
            "go to explore": "explore",
            "go explore": "explore",
            "explore": "explore",
            "go to reels": "reels",
            "go reels": "reels",
            "reels": "reels",
            "go to messages": "messages",
            "go messages": "messages",
            "messages": "messages",
            "go to notifications": "notifications",
            "go notifications": "notifications",
            "notifications": "notifications",
            "go to create": "create",
            "go create": "create",
            "create": "create",
            "go to profile": "profile",
            "go profile": "profile",
            "profile": "profile",
        }
        
        text_lower = text.lower().strip()
        for phrase, target in navigation_phrases.items():
            if text_lower == phrase or text_lower.endswith(phrase) or text_lower.startswith(phrase):
                print(f"✓ Navigation command detected! Target: '{target}'")
                return VoiceEvents(
                    command=VoiceCommand.NAVIGATE,
                    confidence=1.0,
                    raw_text=text,
                    target=target,
                )
        
        # Check for exact matches first
        if text in self.command_mappings:
            command = self.command_mappings[text]
            print(f"Exact match found: {command.value}")
            return VoiceEvents(command=command, confidence=1.0, raw_text=text)
        
        # Check for partial matches with better logic
        best_match = None
        best_confidence = 0.0
        
        for keyword, command in self.command_mappings.items():
            # Check if keyword is contained in text
            if keyword in text:
                confidence = len(keyword) / len(text)
                print(f"Partial match: '{keyword}' in '{text}' (confidence: {confidence:.2f})")
                if confidence > best_confidence:
                    best_match = command
                    best_confidence = confidence
        
        # Also check for individual words
        words = text.split()
        for word in words:
            if word in self.command_mappings:
                command = self.command_mappings[word]
                print(f"Word match: '{word}' -> {command.value}")
                return VoiceEvents(command=command, confidence=0.8, raw_text=text)
        
        if best_match:
            return VoiceEvents(command=best_match, confidence=best_confidence, raw_text=text)
        
        # No command found
        print(f"No command found for: '{text}'")
        return VoiceEvents(command=VoiceCommand.NONE, confidence=0.0, raw_text=text)
