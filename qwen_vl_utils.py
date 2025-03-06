def smart_resize(height, width, min_pixels=512*28*28, max_pixels=2048*28*28):
    """
    Resize dimensions while maintaining aspect ratio within pixel constraints.
    
    Args:
        height (int): Original height
        width (int): Original width
        min_pixels (int): Minimum number of pixels
        max_pixels (int): Maximum number of pixels
        
    Returns:
        tuple: (new_height, new_width) resized within constraints
    """
    # Calculate current number of pixels
    current_pixels = height * width
    
    # If current pixels are within range, return original dimensions
    if min_pixels <= current_pixels <= max_pixels:
        return height, width
        
    # Calculate the scaling factor
    if current_pixels < min_pixels:
        # Scale up
        scale = (min_pixels / current_pixels) ** 0.5
    else:
        # Scale down
        scale = (max_pixels / current_pixels) ** 0.5
        
    # Calculate new dimensions maintaining aspect ratio
    new_height = int(height * scale)
    new_width = int(width * scale)
    
    return new_height, new_width
