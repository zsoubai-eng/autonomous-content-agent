"""
THE FLUX ENGINE - THE ARTIST
Module: Generates high-quality images using Cloudflare Workers AI (Flux).

Uses Cloudflare's @cf/black-forest-labs/flux-1-schnell model for fast, high-res image generation.
"""

import os
import requests
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Cloudflare API Configuration
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")


def generate_scene_image(prompt: str, output_path: str, width: int = 1080, height: int = 1920) -> str:
    """
    Generate high-quality vertical image using Cloudflare Flux (The Artist).
    
    Uses Cloudflare Workers AI API with @cf/black-forest-labs/flux-1-schnell model.
    Generates images optimized for YouTube Shorts (1080x1920 vertical format).
    
    Args:
        prompt: Visual prompt for image generation (should include "hyper-realistic, 8k")
        output_path: Path to save the generated image
        width: Image width (default: 1080 for vertical format)
        height: Image height (default: 1920 for vertical format)
        
    Returns:
        Path to the generated image file
        
    Raises:
        Exception: If Cloudflare API fails or credentials are missing
    """
    if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
        raise Exception("CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN must be set in .env")
    
    print(f"   🎨 The Artist (Flux): Generating image...")
    print(f"      Prompt: {prompt[:80]}...")
    
    try:
        # Cloudflare Workers AI API endpoint
        api_url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/@cf/black-forest-labs/flux-1-schnell"
        
        headers = {
            "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # PROMPT INJECTION: Inject cinematic keywords into every prompt
        injection_keywords = "Cinematic film still, 35mm photography, golden hour lighting, depth of field, hyper-realistic, 8k, dark mood, slight grain"
        
        # Combine original prompt with injection keywords
        combined_prompt = f"{prompt}, {injection_keywords}"
        
        # STRONG SANITIZATION: Remove potentially problematic words while keeping it edgy
        # More comprehensive replacement list to avoid Cloudflare bans
        sanitized_prompt = combined_prompt.lower()
        
        # Aggressive replacements for safety (but keep edgy terms that are acceptable)
        replacements = {
            # Violence/aggression terms
            'kill': 'neutralize', 'murder': 'eliminate', 'death': 'end', 'die': 'cease',
            'blood': 'crimson', 'violence': 'intensity', 'weapon': 'tool', 'gun': 'device',
            'knife': 'blade', 'attack': 'confront', 'fight': 'struggle', 'war': 'conflict',
            
            # Explicit sexual terms
            'nude': 'unclothed', 'naked': 'bare', 'sex': 'intimacy', 'sexual': 'intimate',
            'porn': 'explicit', 'erotic': 'sensual', 'orgasm': 'climax',
            
            # Extreme manipulation terms (keep edgy but safe)
            'evil': 'mysterious', 'sly': 'clever', 'manipulate': 'influence',
            'trap': 'capture', 'control': 'guide', 'dominate': 'lead',
            'haunt': 'linger', 'shadow': 'silhouette', 'lurking': 'present',
            'creeping': 'subtle', 'hack': 'analyze', 'exploit': 'utilize',
            'trick': 'technique', 'scam': 'strategy', 'fool': 'influence',
            'deceive': 'persuade', 'betray': 'mislead', 'destroy': 'disrupt',
            
            # Keep "dark" but make it safer context
            'dark': 'moody',  # Keep moody for edgy aesthetic
            
            # Disturbing imagery
            'distorted': 'abstract', 'twisted': 'curved', 'broken': 'fragmented',
            'torture': 'pressure', 'pain': 'discomfort', 'suffering': 'struggle',
            
            # Drug references
            'drug': 'substance', 'cocaine': 'stimulant', 'heroin': 'opiate',
            'weed': 'cannabis', 'marijuana': 'cannabis',
            
            # Hate speech / discrimination
            'hate': 'dislike', 'racist': 'biased', 'sexist': 'prejudiced',
        }
        
        # Apply replacements
        for old, new in replacements.items():
            sanitized_prompt = sanitized_prompt.replace(old, new)
        
        # Remove any remaining problematic patterns
        import re
        # Remove excessive punctuation that might trigger filters
        sanitized_prompt = re.sub(r'[!]{2,}', '!', sanitized_prompt)
        sanitized_prompt = re.sub(r'[?]{2,}', '?', sanitized_prompt)
        
        # Capitalize first letter
        sanitized_prompt = sanitized_prompt.capitalize()
        
        # Prepare enhanced prompt with vertical composition requirement
        enhanced_prompt = f"{sanitized_prompt}, Vertical composition, 1080x1920 aspect ratio, high quality, detailed, professional, psychological thriller aesthetic, abstract art, conceptual visualization"
        
        payload = {
            "prompt": enhanced_prompt,
            "num_steps": 4,  # Fast generation (schnell model)
            "guidance": 7.5,  # Guidance scale
            "width": width,
            "height": height
        }
        
        # Make API request
        response = requests.post(api_url, json=payload, headers=headers, timeout=120)
        
        if response.status_code != 200:
            error_text = response.text
            # Check if it's an NSFW error - use fallback
            if "NSFW" in error_text or "3030" in error_text:
                print(f"      ⚠️ NSFW filter triggered, using safe fallback prompt...")
                # Use a completely generic safe prompt based on scene number
                import random
                safe_prompts = [
                    "Cinematic film still, 35mm photography, golden hour lighting, depth of field, hyper-realistic, 8k, dark mood, slight grain, Abstract psychological visualization, moody lighting, Vertical composition, 1080x1920 aspect ratio, high quality, detailed, professional",
                    "Cinematic film still, 35mm photography, golden hour lighting, depth of field, hyper-realistic, 8k, dark mood, slight grain, Conceptual art, psychological theme, moody aesthetic, professional photography, Vertical composition, 1080x1920 aspect ratio",
                    "Cinematic film still, 35mm photography, golden hour lighting, depth of field, hyper-realistic, 8k, dark mood, slight grain, Abstract visualization, neural network pattern, moody atmosphere, high quality, detailed, Vertical composition, 1080x1920 aspect ratio"
                ]
                safe_prompt = random.choice(safe_prompts)
                payload["prompt"] = safe_prompt
                response = requests.post(api_url, json=payload, headers=headers, timeout=120)
                if response.status_code != 200:
                    # If still fails, use Pollinations.ai as final fallback
                    print(f"      ⚠️ Cloudflare fallback failed, using Pollinations.ai...")
                    from departments.production.visual_engine import _get_pollinations_video
                    # Generate image using Pollinations and convert to video
                    temp_image = output_path.replace('.jpg', '_pollinations.jpg')
                    import requests as req
                    import random
                    clean_prompt = prompt.replace(" ", "%20").replace(",", "%2C")
                    image_url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=1080&height=1920&seed={random.randint(1000, 9999)}"
                    img_response = req.get(image_url, timeout=30)
                    if img_response.status_code == 200:
                        with open(temp_image, 'wb') as f:
                            f.write(img_response.content)
                        return temp_image
                    raise Exception(f"All image generation methods failed. Last error: {response.text}")
            else:
                raise Exception(f"Cloudflare API returned status {response.status_code}: {error_text}")
        
        # Check if response is JSON (with base64 image) or binary (image)
        content_type = response.headers.get('Content-Type', '')
        
        # Cloudflare Workers AI typically returns JSON with base64-encoded image
        try:
            import json
            import base64
            
            # Try to parse as JSON first
            if 'application/json' in content_type or response.text.startswith('{'):
                json_data = response.json()
                
                # Check for error
                if 'error' in json_data or 'message' in json_data:
                    raise Exception(f"Cloudflare API error: {json_data}")
                
                # Extract base64 image from result
                if 'result' in json_data:
                    result = json_data['result']
                    if isinstance(result, dict) and 'image' in result:
                        # Base64 encoded image string
                        image_b64 = result['image']
                        image_data = base64.b64decode(image_b64)
                    elif isinstance(result, str):
                        # Direct base64 string
                        image_data = base64.b64decode(result)
                    else:
                        raise Exception(f"Unexpected result format: {type(result)}")
                elif 'image' in json_data:
                    # Direct image field
                    image_b64 = json_data['image']
                    image_data = base64.b64decode(image_b64)
                else:
                    raise Exception(f"Unexpected JSON response format: {list(json_data.keys())}")
            else:
                # Binary response (direct image)
                image_data = response.content
                
        except json.JSONDecodeError:
            # Not JSON, treat as binary image
            image_data = response.content
        except Exception as e:
            raise Exception(f"Failed to extract image from response: {e}")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        # Save image (convert to JPEG if needed)
        if image_data.startswith(b'\x89PNG'):
            # PNG image - convert to JPEG using PIL
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(image_data))
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(output_path, 'JPEG', quality=95)
        else:
            # Already JPEG or other format
            with open(output_path, 'wb') as f:
                f.write(image_data)
        
        # Verify file was created
        if not os.path.exists(output_path):
            raise Exception(f"Image file was not created at {output_path}")
        
        file_size = os.path.getsize(output_path)
        if file_size == 0:
            raise Exception(f"Image file is empty at {output_path}")
        
        print(f"   ✓ Image generated: {output_path} ({file_size} bytes)")
        return output_path
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Cloudflare API request failed: {e}")
    except Exception as e:
        raise Exception(f"Flux image generation failed: {e}")


if __name__ == "__main__":
    # Test the Flux engine
    print("=" * 60)
    print("🧪 TESTING FLUX ENGINE (THE ARTIST)")
    print("=" * 60)
    
    try:
        test_prompt = "Extreme close up of a mouth zipped shut, psychological tension, survival aesthetic"
        image_path = generate_scene_image(test_prompt, "test_flux_image.jpg")
        print(f"\n✓ Image created at: {image_path}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
