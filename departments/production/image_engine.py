"""
THE IMAGE ENGINE
Module: Generates AI image hooks using Pollinations.ai (No API Key needed).

Creates stunning visual hooks for the first 3 seconds of videos.
"""

import os
import urllib.parse
import urllib.request
from typing import Optional


def generate_image_hook(topic: str, output_path: str = "hook_image.jpg") -> str:
    """
    Generate an AI image hook using Pollinations.ai (No API Key needed).
    
    Args:
        topic: Topic/keywords for image generation (e.g., "Dark Psychology, mind control")
        output_path: Path to save the generated image
        
    Returns:
        Path to the generated image file
        
    Raises:
        Exception: If image generation or download fails
    """
    print(f"🎨 Generating AI image hook: {topic}...")
    
    # Create prompt based on topic
    # Enhance with cinematic keywords for high quality
    prompt = f"{topic}, cinematic lighting, hyper-realistic, 8k, dramatic, professional photography"
    
    # Construct Pollinations.ai URL
    # Format: https://pollinations.ai/p/{encoded_prompt}?width=1080&height=1920
    encoded_prompt = urllib.parse.quote(prompt)
    image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1080&height=1920"
    
    print(f"   Prompt: {prompt}")
    print(f"   Downloading from Pollinations.ai...")
    
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        # Download image
        urllib.request.urlretrieve(image_url, output_path)
        
        # Verify file was created
        if not os.path.exists(output_path):
            raise Exception(f"Image file was not created at {output_path}")
        
        file_size = os.path.getsize(output_path)
        if file_size == 0:
            raise Exception(f"Image file is empty at {output_path}")
        
        print(f"   ✓ AI image hook generated: {output_path} ({file_size} bytes)")
        return output_path
        
    except Exception as e:
        raise Exception(f"Failed to generate image hook: {e}")


if __name__ == "__main__":
    # Test the image engine
    print("=" * 60)
    print("🧪 TESTING IMAGE ENGINE")
    print("=" * 60)
    
    try:
        image_path = generate_image_hook("Dark Psychology, mind control, cinematic", "test_hook.jpg")
        print(f"\n✓ Image created at: {image_path}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

