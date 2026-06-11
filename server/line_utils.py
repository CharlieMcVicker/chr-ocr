from PIL import Image

def crop_pad_normalize_line(image, bbox, padding_x, padding_y, target_height_range=(30, 33)):
    """
    Crop a line from an image with padding, and normalize its height.
    If the height is too large, it scales the image down using Lanczos
    while dynamically expanding the padding before scaling to ensure
    the final output maintains the exact padding sizes requested.
    """
    lx1, ly1, lx2, ly2 = bbox
    unpadded_height = max(1, int(ly2) - int(ly1))
    target_height = target_height_range[0]
    
    if unpadded_height < 30 or unpadded_height <= 1.5 * target_height:
        # No scaling needed, just pad normally
        lx1_pad = max(0, int(lx1) - padding_x)
        ly1_pad = max(0, int(ly1) - padding_y)
        lx2_pad = min(image.width, int(lx2) + padding_x)
        ly2_pad = min(image.height, int(ly2) + padding_y)
        
        line_crop = image.crop((lx1_pad, ly1_pad, lx2_pad, ly2_pad))
        return line_crop, [lx1_pad, ly1_pad, lx2_pad, ly2_pad]
    else:
        # Scaling needed. Option A: Calculate dynamic padding to preserve exact margin sizes after scale.
        ratio = target_height / unpadded_height
        dynamic_pad_x = int(padding_x / ratio)
        dynamic_pad_y = int(padding_y / ratio)
        
        lx1_pad = max(0, int(lx1) - dynamic_pad_x)
        ly1_pad = max(0, int(ly1) - dynamic_pad_y)
        lx2_pad = min(image.width, int(lx2) + dynamic_pad_x)
        ly2_pad = min(image.height, int(ly2) + dynamic_pad_y)
        
        line_crop = image.crop((lx1_pad, ly1_pad, lx2_pad, ly2_pad))
        
        new_width = int(line_crop.width * ratio)
        new_height = int(line_crop.height * ratio)
        line_crop = line_crop.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # We return the original coordinate bounding box where it was cropped
        return line_crop, [lx1_pad, ly1_pad, lx2_pad, ly2_pad]
