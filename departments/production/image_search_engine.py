"""
IMAGE SEARCH ENGINE (Horror Stories)
Module: Downloads real horror-related images from Unsplash API.

Finds and downloads appropriate images based on horror story content.
"""

import os
import requests
import random
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

# Image API Keys
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")  # Optional, will work without but with limits
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")  # Optional, free tier available

# Horror-related search keywords (for when story doesn't provide good keywords)
HORROR_KEYWORDS = [
    "dark forest", "abandoned house", "ghost", "haunted", "nightmare", 
    "creepy", "spooky", "horror", "scary", "mysterious", "eerie",
    "foggy", "shadow", "abandoned", "old building", "cemetery", "graveyard"
]


def _apply_horror_color_grading(img):
    """
    Apply horror color grading to match cinematics aesthetic (Expert-optimized).
    
    Processing:
    - Darken image (reduce brightness 20%) - was 35%, now lighter for better mobile visibility
    - Increase contrast (30%) - was 20%, now more dramatic
    - Desaturate (40% less color) - was 30%, now more moody
    - Add dark vignette (stronger)
    - Add film grain (5-8% for realism and premium feel)
    
    Args:
        img: PIL Image object
        
    Returns:
        Processed PIL Image matching horror aesthetic
    """
    from PIL import Image as PILImage, ImageEnhance, ImageDraw, ImageChops
    import numpy as np
    
    # 1. Reduce brightness (20% darker - expert recommendation for mobile visibility)
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(0.80)  # 20% darker (was 0.65 = 35%)
    
    # 2. Increase contrast (30% more - expert recommendation for dramatic horror look)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.3)  # 30% more contrast (was 1.2 = 20%)
    
    # 3. Desaturate colors (40% less saturation - expert recommendation for moody horror)
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(0.6)  # 40% less saturation (was 0.7 = 30%)
    
    # 4. Add dark vignette effect (matches cinematic vignette)
    width, height = img.size
    center_x, center_y = width // 2, height // 2
    
    # Create vignette overlay
    vignette = PILImage.new('L', (width, height), 255)  # White = no darkening
    draw = ImageDraw.Draw(vignette)
    
    # Draw radial gradient (darker at edges) using ellipses
    for i in range(15):
        radius_factor = 1.0 - (i * 0.06)
        darkness = int(60 * (i / 15.0))  # Increase darkness toward edges
        
        ellipse_w = int(width * radius_factor)
        ellipse_h = int(height * radius_factor)
        x1 = center_x - ellipse_w // 2
        y1 = center_y - ellipse_h // 2
        x2 = center_x + ellipse_w // 2
        y2 = center_y + ellipse_h // 2
        
        # Draw darker ellipse
        draw.ellipse([x1, y1, x2, y2], fill=255 - darkness)
    
    # Apply vignette to image
    img = img.convert('RGB')
    vignette_rgb = vignette.convert('RGB')
    
    # Use multiply blend mode to darken edges (stronger vignette)
    img = ImageChops.multiply(img, vignette_rgb)
    img = ImageEnhance.Brightness(img).enhance(1.05)  # Slight brighten back (was 1.1)
    
    # 5. Add film grain (5-8% for realism - expert recommendation)
    # Convert to numpy array for grain
    img_array = np.array(img).astype(np.float32)
    
    # Generate random grain (5-7% intensity)
    grain_intensity = np.random.uniform(0.05, 0.08)  # 5-8% grain
    noise = np.random.normal(0, grain_intensity * 255, img_array.shape).astype(np.float32)
    
    # Apply grain (additive, then clamp)
    img_array = img_array + noise
    img_array = np.clip(img_array, 0, 255).astype(np.uint8)
    
    # Convert back to PIL Image
    img = PILImage.fromarray(img_array)
    
    return img


def _extract_keywords_from_story(story_text: str, story_title: str) -> List[str]:
    """
    Extract psychologically-matched keywords from horror story for image search.
    
    Intelligently extracts the MAIN VISUAL SCENE - what the viewer should visualize
    while listening. Prioritizes narrative action, key moments, and scene composition
    over generic terms for better psychological connection.
    
    Args:
        story_text: Full story text
        story_title: Story title
        
    Returns:
        List of keywords for image search (prioritized by narrative relevance)
    """
    import re
    
    # Combine title and story for analysis
    combined_text = (story_title + " " + story_text).lower()
    sentences = re.split(r'[.!?]+', story_text)
    
    # STEP 1: Identify the MAIN VISUAL SUBJECT (what the story is about)
    # Extract key nouns that represent the core subject
    main_subjects = []
    
    # Historical events/places (often in titles)
    historical_terms = ["colony", "murder", "disappearance", "mystery", "case", "incident", 
                       "event", "tragedy", "disaster", "vanishing", "missing"]
    for term in historical_terms:
        if term in combined_text:
            main_subjects.append(term)
    
    # STEP 2: Extract the PRIMARY LOCATION (where the action happens)
    location_keywords = [
        "hotel", "house", "room", "building", "cottage", "cabin", "mansion", "castle",
        "forest", "woods", "road", "street", "alley", "path", "trail",
        "cemetery", "graveyard", "church", "hospital", "school", "library",
        "basement", "attic", "hallway", "corridor", "staircase", "stairs",
        "beach", "island", "mountain", "valley", "field", "meadow",
        "bridge", "tunnel", "cave", "warehouse", "factory", "farm",
        "colony", "settlement", "village", "town", "city"
    ]
    
    found_locations = []
    for location in location_keywords:
        if location in combined_text:
            found_locations.append(location)
    
    # STEP 3: Extract ACTION/EVENT keywords (what's happening visually)
    # These create psychological connection - viewer visualizes the action
    action_patterns = {
        "disappearance": ["disappeared", "vanished", "missing", "gone", "lost"],
        "murder": ["killed", "murdered", "death", "died", "slain"],
        "mystery": ["mysterious", "unknown", "unexplained", "strange", "puzzling"],
        "encounter": ["saw", "met", "found", "encountered", "discovered", "witnessed"],
        "haunting": ["haunted", "ghost", "spirit", "apparition", "phantom"],
        "isolation": ["alone", "isolated", "abandoned", "deserted", "empty"],
        "danger": ["dangerous", "threat", "fear", "terrified", "scared"]
    }
    
    found_actions = []
    for action_type, patterns in action_patterns.items():
        if any(pattern in combined_text for pattern in patterns):
            found_actions.append(action_type)
    
    # STEP 4: Extract KEY OBJECTS/FEATURES (visual anchors)
    object_keywords = [
        "door", "window", "mirror", "picture", "photo", "frame",
        "bed", "chair", "table", "desk", "dresser", "wardrobe",
        "car", "vehicle", "truck", "boat", "ship", "plane",
        "tree", "fence", "gate", "wall", "roof", "chimney",
        "cross", "statue", "monument", "grave", "tombstone",
        "letter", "note", "message", "diary", "journal"
    ]
    
    found_objects = []
    for obj in object_keywords:
        if obj in combined_text:
            found_objects.append(obj)
    
    # STEP 5: Extract ATMOSPHERE (mood/feeling - critical for horror)
    atmosphere_keywords = [
        "night", "dark", "foggy", "misty", "stormy", "rainy", "snowy",
        "cold", "winter", "autumn", "fall", "evening", "dawn", "dusk",
        "abandoned", "empty", "deserted", "isolated", "remote", "lonely"
    ]
    
    found_atmosphere = []
    for atmos in atmosphere_keywords:
        if atmos in combined_text:
            found_atmosphere.append(atmos)
    
    # STEP 6: Build PSYCHOLOGICALLY-OPTIMIZED keyword list
    keywords = []
    
    # Helper function to add keyword only if not already present
    def add_unique(keyword):
        if keyword and keyword not in keywords:
            keywords.append(keyword)
    
    # PRIORITY 1: Main subject (what the story is about - viewer's mental anchor)
    if main_subjects:
        add_unique(main_subjects[0])
    
    # PRIORITY 2: Primary location (where it happens - spatial visualization)
    if found_locations:
        # Use the most specific location mentioned
        add_unique(found_locations[0])
        if len(found_locations) > 1 and len(keywords) < 3:
            add_unique(found_locations[1])
    
    # PRIORITY 3: Key action/event (what's happening - narrative visualization)
    if found_actions:
        add_unique(found_actions[0])
    
    # PRIORITY 4: Important object (visual detail that enhances scene)
    if found_objects and len(keywords) < 4:
        add_unique(found_objects[0])
    
    # PRIORITY 5: Atmosphere (mood/feeling - emotional connection)
    if found_atmosphere:
        add_unique(found_atmosphere[0])
    else:
        # Add mood descriptor for horror aesthetic
        mood_descriptor = random.choice(["dark", "moody", "creepy", "mysterious", "eerie"])
        add_unique(mood_descriptor)
    
    # STEP 7: Fallback to title-based extraction if keywords are sparse
    if len(keywords) < 3:
        # Extract meaningful words from title
        title_words = story_title.lower().split()
        common_words = ["the", "a", "an", "of", "in", "on", "at", "to", "for", "with", "from", "and"]
        title_keywords = [w for w in title_words if w not in common_words and len(w) > 3]
        if title_keywords:
            # Add title keywords that aren't already in our list
            for word in title_keywords[:2]:
                add_unique(word)
                if len(keywords) >= 4:
                    break
    
    # STEP 8: Final fallback
    if not keywords:
        keywords = ["dark", "horror", "mysterious", "eerie"]
    
    # Limit to 4-5 keywords for optimal search results
    # More specific = better psychological match
    return keywords[:5]


def _extract_story_segments(story_text: str, story_title: str, num_segments: int = 5) -> List[dict]:
    """
    Extract story segments for multi-image psychological matching.
    
    Divides the story into narrative moments, each requiring a different visual.
    Uses sentence analysis to identify key moments: setup, tension, climax, resolution.
    
    Args:
        story_text: Full story text
        story_title: Story title
        num_segments: Number of segments to extract (5-7 recommended)
        
    Returns:
        List of segment dicts with 'text', 'keywords', 'moment_type'
    """
    import re
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', story_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) < num_segments:
        # Not enough sentences, use word-based splitting
        words = story_text.split()
        words_per_segment = len(words) // num_segments
        segments = []
        for i in range(num_segments):
            start_idx = i * words_per_segment
            end_idx = (i + 1) * words_per_segment if i < num_segments - 1 else len(words)
            segment_text = ' '.join(words[start_idx:end_idx])
            segments.append(segment_text)
    else:
        # Use sentence-based splitting (better for narrative flow)
        sentences_per_segment = len(sentences) // num_segments
        segments = []
        for i in range(num_segments):
            start_idx = i * sentences_per_segment
            end_idx = (i + 1) * sentences_per_segment if i < num_segments - 1 else len(sentences)
            segment_text = '. '.join(sentences[start_idx:end_idx])
            segments.append(segment_text)
    
    # Identify moment types for better image matching
    moment_types = ['setup', 'tension', 'climax', 'resolution', 'mystery']
    
    # Extract keywords for each segment
    segment_data = []
    for i, segment_text in enumerate(segments):
        # Determine moment type based on position
        if i == 0:
            moment_type = 'setup'
        elif i == len(segments) - 1:
            moment_type = 'resolution'
        elif i == len(segments) // 2:
            moment_type = 'climax'
        else:
            moment_type = moment_types[i % len(moment_types)]
        
        # Extract keywords for this segment
        keywords = _extract_keywords_from_story(segment_text, story_title)
        
        segment_data.append({
            'text': segment_text,
            'keywords': keywords,
            'moment_type': moment_type,
            'index': i
        })
    
    return segment_data


def download_multiple_horror_images(
    story_text: str,
    story_title: str,
    output_dir: str,
    num_images: int = 6,
    width: int = 1080,
    height: int = 1920
) -> List[str]:
    """
    Download multiple horror-related images for different story moments.
    
    Creates visual variety throughout the video - viewer sees different images
    as the story progresses, enhancing psychological engagement.
    
    Args:
        story_text: Full horror story text
        story_title: Story title
        output_dir: Directory to save images
        num_images: Number of images to download (5-7 recommended)
        width: Image width (default: 1080 for Shorts)
        height: Image height (default: 1920 for Shorts)
        
    Returns:
        List of paths to downloaded images
    """
    import os
    import random
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"   🖼️ Downloading {num_images} images for story moments...")
    
    # Extract story segments
    segments = _extract_story_segments(story_text, story_title, num_images)
    
    downloaded_images = []
    
    for i, segment in enumerate(segments):
        segment_keywords = segment['keywords']
        moment_type = segment['moment_type']
        
        # Build search query for this segment
        search_query = " ".join(segment_keywords)
        
        # Add moment-specific keywords for better matching
        if moment_type == 'setup':
            search_query += " dark mysterious"
        elif moment_type == 'tension':
            search_query += " eerie creepy"
        elif moment_type == 'climax':
            search_query += " horror intense"
        elif moment_type == 'resolution':
            search_query += " moody atmospheric"
        else:
            search_query += " spooky haunted"
        
        # Create output path for this image
        image_filename = f"horror_image_{i+1}.jpg"
        output_path = os.path.join(output_dir, image_filename)
        
        print(f"      📸 Image {i+1}/{num_images} ({moment_type}): {search_query[:50]}...")
        
        # Download image using existing function logic
        image_path = _download_single_image(search_query, output_path, width, height)
        
        if image_path:
            downloaded_images.append(image_path)
        else:
            # If download failed, use placeholder
            print(f"      ⚠️ Image {i+1} download failed, using placeholder...")
            placeholder_path = _create_placeholder_image(output_path, width, height)
            if placeholder_path:
                downloaded_images.append(placeholder_path)
    
    print(f"      ✓ Downloaded {len(downloaded_images)}/{num_images} images")
    return downloaded_images


def _download_single_image(search_query: str, output_path: str, width: int, height: int) -> Optional[str]:
    """
    Download a single image using the search query.
    Internal helper function for multi-image downloads.
    """
    # Priority 1: Try Unsplash API
    if UNSPLASH_ACCESS_KEY:
        try:
            api_url = "https://api.unsplash.com/photos/random"
            headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
            params = {
                "query": search_query,
                "orientation": "portrait",
                "w": width,
                "h": height
            }
            
            response = requests.get(api_url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                image_url = data.get("urls", {}).get("regular") or data.get("urls", {}).get("full")
                
                if image_url:
                    img_response = requests.get(image_url, timeout=15)
                    if img_response.status_code == 200:
                        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
                        with open(output_path, 'wb') as f:
                            f.write(img_response.content)
                        
                        from PIL import Image
                        img = Image.open(output_path)
                        img = img.convert('RGB')
                        img = img.resize((width, height), Image.Resampling.LANCZOS)
                        img = _apply_horror_color_grading(img)
                        img.save(output_path, 'JPEG', quality=95)
                        return output_path
        except Exception:
            pass
    
    # Priority 2: Try Pexels API
    if PEXELS_API_KEY:
        try:
            pexels_url = "https://api.pexels.com/v1/search"
            headers = {"Authorization": PEXELS_API_KEY}
            params = {
                "query": search_query,
                "per_page": 1,
                "orientation": "portrait"
            }
            
            response = requests.get(pexels_url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('photos') and len(data['photos']) > 0:
                    photo = data['photos'][0]
                    image_url = photo.get('src', {}).get('large') or photo.get('src', {}).get('original')
                    
                    if image_url:
                        img_response = requests.get(image_url, timeout=15)
                        if img_response.status_code == 200:
                            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
                            with open(output_path, 'wb') as f:
                                f.write(img_response.content)
                            
                            from PIL import Image
                            img = Image.open(output_path)
                            img = img.convert('RGB')
                            img = img.resize((width, height), Image.Resampling.LANCZOS)
                            img = _apply_horror_color_grading(img)
                            img.save(output_path, 'JPEG', quality=95)
                            return output_path
        except Exception:
            pass
    
    # Priority 3: Unsplash Source
    try:
        fallback_url = f"https://source.unsplash.com/{width}x{height}/?{search_query.replace(' ', ',')}"
        img_response = requests.get(fallback_url, timeout=15, allow_redirects=True)
        if img_response.status_code == 200 and len(img_response.content) > 10000:
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(img_response.content)
            
            from PIL import Image
            img = Image.open(output_path)
            img = img.convert('RGB')
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            img = _apply_horror_color_grading(img)
            img.save(output_path, 'JPEG', quality=95)
            return output_path
    except Exception:
        pass
    
    return None


def _create_placeholder_image(output_path: str, width: int, height: int) -> Optional[str]:
    """Create a dark placeholder image."""
    try:
        from PIL import Image as PILImage
        import numpy as np
        
        img = PILImage.new('RGB', (width, height), color=(10, 10, 15))
        img_array = np.array(img)
        center_x, center_y = width // 2, height // 2
        
        y_coords, x_coords = np.ogrid[:height, :width]
        distances = np.sqrt((x_coords - center_x)**2 + (y_coords - center_y)**2)
        max_dist = np.sqrt(center_x**2 + center_y**2)
        
        brightness_factor = 1.0 - (distances / max_dist) * 0.3
        brightness_factor = np.clip(brightness_factor, 0.7, 1.0)
        
        for c in range(3):
            img_array[:, :, c] = (img_array[:, :, c] * brightness_factor).astype(np.uint8)
        
        img = PILImage.fromarray(img_array)
        img = _apply_horror_color_grading(img)
        
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        img.save(output_path, 'JPEG', quality=95)
        return output_path
    except Exception:
        return None


def download_horror_image(
    story_text: str,
    story_title: str,
    output_path: str,
    width: int = 1080,
    height: int = 1920
) -> Optional[str]:
    """
    Download a horror-related image from Unsplash based on story content.
    
    Args:
        story_text: Full horror story text
        story_title: Story title
        output_path: Path to save downloaded image
        width: Image width (default: 1080 for Shorts)
        height: Image height (default: 1920 for Shorts)
        
    Returns:
        Path to downloaded image, or None if download failed
    """
    import random
    
    print(f"   🖼️ Searching for horror image...")
    
    # Extract keywords from story (psychologically-matched to narrative)
    keywords = _extract_keywords_from_story(story_text, story_title)
    
    # Build descriptive search query (prioritizes narrative flow)
    # Format: "subject location action atmosphere" for better psychological match
    search_query = " ".join(keywords)
    
    print(f"      🎯 Narrative-matched search query: {search_query}")
    print(f"      📍 Story elements: {', '.join(keywords[:4])}")
    
    # Priority 1: Try Unsplash API (if key provided)
    if UNSPLASH_ACCESS_KEY:
        # Use official API
        api_url = "https://api.unsplash.com/photos/random"
        headers = {
            "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
        }
        params = {
            "query": search_query,
            "orientation": "portrait",
            "w": width,
            "h": height
        }
        
        try:
            response = requests.get(api_url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                image_url = data.get("urls", {}).get("regular") or data.get("urls", {}).get("full")
                
                if image_url:
                    # Download image
                    img_response = requests.get(image_url, timeout=15)
                    if img_response.status_code == 200:
                        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
                        with open(output_path, 'wb') as f:
                            f.write(img_response.content)
                        
                        # Resize and process image for horror aesthetic
                        from PIL import Image, ImageEnhance
                        img = Image.open(output_path)
                        img = img.convert('RGB')
                        img = img.resize((width, height), Image.Resampling.LANCZOS)
                        
                        # Apply horror color grading to match cinematics
                        img = _apply_horror_color_grading(img)
                        
                        img.save(output_path, 'JPEG', quality=95)
                        
                        print(f"      ✓ Image downloaded and processed: {output_path}")
                        return output_path
        except Exception as e:
            print(f"      ⚠️ Unsplash API failed: {e}, trying Pexels...")
    
    # Priority 2: Try Pexels API (if key provided - more reliable than Unsplash Source)
    if PEXELS_API_KEY:
        print(f"      🔄 Trying Pexels API...")
        try:
            pexels_url = "https://api.pexels.com/v1/search"
            headers = {
                "Authorization": PEXELS_API_KEY  # Pexels uses API key directly as Authorization header
            }
            params = {
                "query": search_query,
                "per_page": 1,
                "orientation": "portrait"
            }
            
            response = requests.get(pexels_url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('photos') and len(data['photos']) > 0:
                    photo = data['photos'][0]
                    image_url = photo.get('src', {}).get('large') or photo.get('src', {}).get('original')
                    
                    if image_url:
                        img_response = requests.get(image_url, timeout=15)
                        if img_response.status_code == 200:
                            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
                            with open(output_path, 'wb') as f:
                                f.write(img_response.content)
                            
                            # Process image
                            from PIL import Image
                            img = Image.open(output_path)
                            img = img.convert('RGB')
                            img = img.resize((width, height), Image.Resampling.LANCZOS)
                            img = _apply_horror_color_grading(img)
                            img.save(output_path, 'JPEG', quality=95)
                            
                            print(f"      ✓ Image downloaded from Pexels: {output_path}")
                            return output_path
        except Exception as e:
            print(f"      ⚠️ Pexels API failed: {e}, trying Unsplash Source...")
    
    # Priority 3: Fallback to Unsplash Source (free, no API key needed but less reliable)
    try:
        fallback_url = f"https://source.unsplash.com/{width}x{height}/?{search_query.replace(' ', ',')}"
        print(f"      Using Unsplash Source (fallback)...")
        
        img_response = requests.get(fallback_url, timeout=15, allow_redirects=True)
        if img_response.status_code == 200 and len(img_response.content) > 10000:  # Ensure valid image
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(img_response.content)
            
            # Resize and process image for horror aesthetic
            from PIL import Image, ImageEnhance
            img = Image.open(output_path)
            img = img.convert('RGB')
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            
            # Apply horror color grading to match cinematics
            img = _apply_horror_color_grading(img)
            
            img.save(output_path, 'JPEG', quality=95)
            
            print(f"      ✓ Image downloaded and processed (Unsplash Source): {output_path}")
            return output_path
    except Exception as e:
        print(f"      ⚠️ Unsplash Source failed: {e}")
    
    # Last resort: Use a dark horror-themed placeholder (NO TEXT - just dark gradient)
    print(f"      ⚠️ All image sources failed, using dark placeholder...")
    try:
        from PIL import Image as PILImage, ImageDraw
        import numpy as np
        
        # Create dark gradient background (more interesting than solid color)
        img = PILImage.new('RGB', (width, height), color=(10, 10, 15))  # Very dark blue-gray
        
        # Add subtle gradient from center using numpy for efficiency
        img_array = np.array(img)
        center_x, center_y = width // 2, height // 2
        
        y_coords, x_coords = np.ogrid[:height, :width]
        distances = np.sqrt((x_coords - center_x)**2 + (y_coords - center_y)**2)
        max_dist = np.sqrt(center_x**2 + center_y**2)
        
        # Create gradient (lighter in center, darker at edges)
        brightness_factor = 1.0 - (distances / max_dist) * 0.3
        brightness_factor = np.clip(brightness_factor, 0.7, 1.0)
        
        # Apply gradient to all channels
        for c in range(3):
            img_array[:, :, c] = (img_array[:, :, c] * brightness_factor).astype(np.uint8)
        
        img = PILImage.fromarray(img_array)
        
        # Apply horror color grading even to placeholder
        img = _apply_horror_color_grading(img)
        
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        img.save(output_path, 'JPEG', quality=95)
        
        print(f"      ⚠️ Dark placeholder created (no actual image): {output_path}")
        return output_path
    except Exception as e:
        print(f"      ❌ Failed to create placeholder: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Test
    print("=" * 60)
    print("🧪 TESTING IMAGE SEARCH ENGINE")
    print("=" * 60)
    
    test_story = "In the abandoned hotel on Elm Street, a mysterious figure appeared in the foggy night. The old building had been empty for decades, but tonight, something was watching from the broken windows."
    test_title = "The Vanishing Hotel"
    
    test_image = download_horror_image(test_story, test_title, "test_horror_image.jpg")
    if test_image:
        print(f"\n✓ Test image saved: {test_image}")
    else:
        print("\n❌ Test failed")
