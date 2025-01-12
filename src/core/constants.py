"""Game constants.

This module re-exports all constants from the config package for backwards compatibility.
New code should import directly from src.core.config.
"""

from .config.display import *
from .config.gameplay import *
from .config.entities import *
from .config.audio import *
from .config.input import *
from .config.effects import * 