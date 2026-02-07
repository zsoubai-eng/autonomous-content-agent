"""
THUMBNAIL GENERATOR
Module: Generates high-contrast, engaging thumbnails for horror videos.

Research-based: High-contrast + emotional elements = +35-50% CTR
"""

import os
from PIL import Image, ImageDraw, ImageFont
from typing import Optional
import random


def generate_thumbnail(
    title: str,
    output_path: str,
    width: int = 1280,
    height: int = 720
) -> str:
    """
    Generate horror-themed thumbnail with high contrast and engaging design.
    
    Features:
    - Dark background (horror aesthetic)
    - Bright red title text (high contrast)
    - "TRUE STORY" badge (credibility)
    - Horror visual elements (eerie, engaging)
    
    Args:
        title: Video title (will be truncated if too long)
        output_path: Path to save thumbnail
        width: Thumbnail width (default: 1280 for YouTube)
        height: Thumbnail height (default: 720 for YouTube)
        
    Returns:
        Path to generated thumbnail
    """
    print(f"   🖼️ Generating thumbnail: {title}")
    
    # Create dark background (horror aesthetic)
    bg_color = (10, 10, 15)  # Very dark blue-gray
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to load a bold font
    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    
    title_font = None
    badge_font = None
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                title_font = ImageFont.truetype(font_path, 80)
                badge_font = ImageFont.truetype(font_path, 40)
                break
            except:
                continue
    
    if title_font is None:
        # Fallback to default font
        title_font = ImageFont.load_default()
        badge_font = ImageFont.load_default()
    
    # EXPERT OPTIMIZATION: Simplify title (3-4 words max for high CTR)
    # Extract key words from title (prefer short, impactful phrases)
    words = title.split()
    
    # Try to keep to 3-4 words for maximum impact
    if len(words) > 4:
        # Take first 3-4 meaningful words
        key_words = []
        skip_words = {'the', 'a', 'an', 'of', 'in', 'on', 'at', 'to', 'for'}
        for word in words:
            if word.lower() not in skip_words or len(key_words) == 0:
                key_words.append(word)
            if len(key_words) >= 4:
                break
        display_title = ' '.join(key_words)
    else:
        display_title = title
    
    # Max 1 line for high CTR (expert recommendation)
    lines = [display_title]
    
    # Calculate text position (center)
    line_height = 100
    total_text_height = len(lines) * line_height
    start_y = (height - total_text_height) // 2
    
    # EXPERT OPTIMIZATION: High-CTR color scheme
    # Red text (#E20000) with 2px black stroke for maximum visibility
    text_color = (226, 0, 0)  # #E20000 (expert-recommended red)
    stroke_color = (0, 0, 0)  # Black stroke
    stroke_width = 2  # 2px stroke (expert recommendation)
    
    for i, line in enumerate(lines):
        # Calculate text size and position
        bbox = draw.textbbox((0, 0), line, font=title_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = start_y + i * line_height
        
        # Draw text with stroke (outline)
        for adj in range(-stroke_width, stroke_width + 1):
            for adj2 in range(-stroke_width, stroke_width + 1):
                if adj != 0 or adj2 != 0:
                    draw.text((x + adj, y + adj2), line, font=title_font, fill=stroke_color)
        
        # Draw main text
        draw.text((x, y), line, font=title_font, fill=text_color)
    
    # EXPERT OPTIMIZATION: "TRUE STORY" badge (top-right, inside safe zone, 80% opacity)
    badge_text = "TRUE STORY"
    badge_bg_color = (255, 0, 0)  # Red background
    badge_text_color = (255, 255, 255)  # White text
    badge_opacity = 204  # 80% opacity (0.8 * 255)
    
    # Calculate badge size
    badge_bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
    badge_width = (badge_bbox[2] - badge_bbox[0]) + 30
    badge_height = (badge_bbox[3] - badge_bbox[1]) + 20
    
    badge_x = width - badge_width - 20
    badge_y = 20
    
    # Draw badge background with opacity (using RGBA overlay)
    badge_bg = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    badge_draw = ImageDraw.Draw(badge_bg)
    badge_draw.rectangle(
        [badge_x, badge_y, badge_x + badge_width, badge_y + badge_height],
        fill=(badge_bg_color[0], badge_bg_color[1], badge_bg_color[2], badge_opacity),
        outline=(0, 0, 0, 255),
        width=2
    )
    img = Image.alpha_composite(img.convert('RGBA'), badge_bg).convert('RGB')
    draw = ImageDraw.Draw(img)  # Recreate draw after composite
    
    # Draw badge text
    badge_text_bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
    badge_text_x = badge_x + (badge_width - (badge_text_bbox[2] - badge_text_bbox[0])) // 2
    badge_text_y = badge_y + (badge_height - (badge_text_bbox[3] - badge_text_bbox[1])) // 2
    draw.text((badge_text_x, badge_text_y), badge_text, font=badge_font, fill=badge_text_color)
    
    # Add subtle gradient overlay (more depth)
    gradient = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    gradient_draw = ImageDraw.Draw(gradient)
    
    # Vignette effect (darker corners)
    for y_pos in range(height):
        for x_pos in range(width):
            # Distance from center
            center_x, center_y = width // 2, height // 2
            distance = ((x_pos - center_x) ** 2 + (y_pos - center_y) ** 2) ** 0.5
            max_distance = ((width // 2) ** 2 + (height // 2) ** 2) ** 0.5
            
            # Vignette opacity (0 at center, increases toward edges)
            opacity = int(30 * (distance / max_distance))
            gradient.putpixel((x_pos, y_pos), (0, 0, 0, opacity))
    
    img = Image.alpha_composite(img.convert('RGBA'), gradient).convert('RGB')
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    
    # Save thumbnail
    img.save(output_path, 'PNG', quality=95)
    print(f"      ✓ Thumbnail saved: {output_path}")
    
    return output_path


if __name__ == "__main__":
    # Test
    print("=" * 60)
    print("🧪 TESTING THUMBNAIL GENERATOR")
    print("=" * 60)
    
    test_thumbnail = generate_thumbnail(
        title="The Vanishing Hotel Mystery (UNSOLVED)",
        output_path="test_thumbnail.png"
    )
    print(f"✓ Test thumbnail created: {test_thumbnail}")
