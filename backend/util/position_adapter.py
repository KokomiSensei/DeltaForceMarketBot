"""
Position Adapter Module

This module provides an adapter layer for position-related functions to work with
any container type that allows random access to indices 0 and 1.
"""
from backend import utils as utils
from typing import Any, List

# Define a type for position-like objects - we use Any since we want to 
# accept any object with index access, regardless of its actual type
PositionLike = Any

def adapt_position(position: Any) -> List[float]:
    """
    Adapts various position-like containers to a list format expected by utility functions.
    
    Args:
        position: Any container supporting index access to elements 0 and 1
        
    Returns:
        A list containing the x and y coordinates
    """
    # Convert any position-like object to a list with two elements
    return [float(position[0]), float(position[1])]

# Wrapper functions for the original utility functions
def mouse_move(position: PositionLike) -> None:
    """
    Adapter for mouse_move function that works with any position-like object.
    
    Args:
        position: Any object that has index access to elements 0 and 1
    """
    
    utils.mouse_move(adapt_position(position))

def mouse_click(position: PositionLike, num: int = 1) -> None:
    """
    Adapter for mouse_click function that works with any position-like object.
    
    Args:
        position: Any object that has index access to elements 0 and 1
        num: Number of clicks, default is 1
    """
    
    utils.mouse_click(adapt_position(position), num)

# Additional adapter functions for other position-related utilities
def get_windowshot(range_coords: Any, debug_mode = False):
    """
    Adapter for get_windowshot function that works with any range-like object.
    
    Args:
        range_coords: Any sequence with indices 0, 1, 2, 3 for left, top, right, bottom
        debug_mode: Whether to save the screenshot for debugging
    """
    
    # Convert to list with exactly 4 elements
    adapted_range = [float(range_coords[0]), float(range_coords[1]), 
                   float(range_coords[2]), float(range_coords[3])]
    return utils.get_windowshot(adapted_range, debug_mode)

def get_window_position(target_app: str):
    """
    Adapter for get_window_postion function.
    
    Args:
        target_app: Title of the target application window
    
    Returns:
        List containing window coordinates [left, top, right, bottom]
    """
    
    return utils.get_window_postion(target_app)
