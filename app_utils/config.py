"""Configuration management for the application."""

import os
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


# Color scheme - Dark Mode OKLCH palette converted to hex/rgb
class Colors:
    """Dark mode color palette."""
    
    # Backgrounds
    BG_MAIN = "#1F1F1F"      # Main background (Darker for contrast)
    BG_CARD = "#2B2B2B"      # Card background
    BG_INPUT = "#383838"     # Input field background
    BG_HOVER = "#404040"     # Generic hover state
    
    # Brand Colors (Active/Inactive Scheme)
    ACTIVE_RED = "#FF0000"   # YouTube Red for Active states
    INACTIVE_DARK = "#383838" # Dark Gray for Inactive states
    
    # Primary colors (Keeping existing purple as secondary accent if needed, but prioritizing Red/Dark)
    PRIMARY = "#FF0000"      # Replaced Purple with Red as primary active color per request
    PRIMARY_HOVER = "#CC0000" # Darker red for hover
    
    # Text colors
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#AAAAAA"
    TEXT_DISABLED = "#666666"
    
    # Borders
    BORDER_LIGHT = "#404040"
    BORDER_FOCUS = "#FF0000"
    
    # Status
    SUCCESS = "#4CAF50"
    ERROR = "#F44336"
    WARNING = "#FFC107"


class Fonts:
    """Font families and sizes."""
    
    FAMILY = "Poppins"  # Enforced globally
    
    # Legacy font tuples retained for backwards compatibility with prior UI code
    
    @staticmethod
    def h1(): return (Fonts.FAMILY, 22, "bold")  # Reduced from 28
    @staticmethod
    def h2(): return (Fonts.FAMILY, 18, "bold")  # Reduced from 24
    @staticmethod
    def h3(): return (Fonts.FAMILY, 16, "bold")  # Reduced from 20
    @staticmethod
    def body(): return (Fonts.FAMILY, 13, "normal") # Reduced from 14
    @staticmethod
    def body_bold(): return (Fonts.FAMILY, 13, "bold") # Reduced from 14
    @staticmethod
    def button(): return (Fonts.FAMILY, 13, "bold") # Reduced from 14
    @staticmethod
    def small(): return (Fonts.FAMILY, 11, "normal") # Reduced from 12
    
    # Legacy constants for compatibility (will refactor usage)
    PRIMARY = "Poppins"
    SECONDARY = "Poppins"
    SIZE_TITLE = 22
    SIZE_BUTTON = 13
    SIZE_BODY = 13
    SIZE_LABEL = 11


class Spacing:
    """Spacing and sizing constants."""
    
    # Padding & Margins
    XS = 4
    SM = 8
    MD = 12  # Reduced from 16
    LG = 20  # Reduced from 24
    XL = 24  # Reduced from 32
    
    # Component Dimensions
    BUTTON_HEIGHT = 40      # Reduced from 45
    INPUT_HEIGHT = 40       # Reduced from 45
    RADIUS_SM = 6
    RADIUS_MD = 8
    RADIUS_LG = 12
    
    # Legacy mapping
    PADDING_SMALL = SM
    PADDING_MEDIUM = MD
    PADDING_LARGE = LG
    GAP_SMALL = SM
    GAP_MEDIUM = MD
    GAP_LARGE = LG
    RADIUS_SMALL = RADIUS_SM


class Animation:
    """Animation constants."""
    DURATION = 200  # ms
    STEPS = 10      # Number of steps for smooth transition


class Config:
    """General application configuration."""
    
    # Window settings
    VERSION = "7.0.0"
    WINDOW_TITLE = "CtrlSTube"
    WINDOW_WIDTH = 480  # Compact width
    WINDOW_HEIGHT = 600 # Compact height

    
    # Icon paths
    ICON_VIDEO_RED = "ui/asset/video_red.png"
    ICON_VIDEO_DARK = "ui/asset/video_dark.png"
    ICON_AUDIO_RED = "ui/asset/audio_red.png"
    ICON_AUDIO_DARK = "ui/asset/audio_dark.png"
    
    # Download settings
    MAX_RECENT_DOWNLOADS = 10
    HISTORY_FILE = "downloads_history.json"
    AUDIO_BITRATE = "320"
    
    # Standard video heights
    STANDARD_VIDEO_HEIGHTS = {2160, 1440, 1080, 720, 480, 360, 240, 144}
