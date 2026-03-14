"""
Attribution Models Package

Provides five attribution models for multi-touch marketing analysis:
- First-touch: all credit to the first interaction
- Last-touch: all credit to the last interaction before conversion
- Linear: equal credit across all touchpoints
- Time-decay: exponential decay weighting toward conversion
- Markov chain: data-driven removal effect attribution
"""

from models.first_touch import first_touch_attribution
from models.last_touch import last_touch_attribution
from models.linear import linear_attribution
from models.time_decay import time_decay_attribution
from models.markov import markov_attribution

__all__ = [
    "first_touch_attribution",
    "last_touch_attribution",
    "linear_attribution",
    "time_decay_attribution",
    "markov_attribution",
]
