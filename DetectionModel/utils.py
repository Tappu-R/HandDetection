# Small Helper functions
from .config import Config

def ExpoMovingAverage(new_value, smoothing_value):
    if smoothing_value is None:
        smoothing_value = new_value
    else:
        smoothing_value = Config.EMA_ALFA*new_value + (1-Config.EMA_ALFA)*smoothing_value
    return smoothing_value


