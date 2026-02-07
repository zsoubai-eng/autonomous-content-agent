"""
THE UPLOAD ENGINE
Module 5: Handles YouTube video uploads.

Authenticates and uploads videos to YouTube.
"""

import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = "client_secrets.json"

# Pool of 50 relevant tags for Dark Psychology / Human Behavior niche
TAG_POOL = [
    "psychology", "dark psychology", "mind tricks", "psychology facts",
    "human behavior", "manipulation", "influence", "mindset",
    "psychology hacks", "behavioral psychology", "social psychology",
    "psychology tips", "psychology 101", "mental health", "self improvement",
    "personality", "psychology videos", "psychology facts", "brain hacks",
    "persuasion", "body language", "nonverbal communication", "cognitive bias",
    "psychology tricks", "mental tricks", "psychology secrets", "hidden psychology",
    "psychology explained", "psychology lessons", "psychology insights",
    "psychology techniques", "psychology strategies", "human psychology",
    "psychology knowledge", "psychology science", "psychology research",
    "psychology study", "psychology theory", "psychology principles",
    "psychology concepts", "psychology discoveries", "psychology facts daily",
    "psychology shorts", "psychology content", "psychology education",
    "psychology learning", "psychology awareness", "psychology wisdom",
    "psychology truth", "psychology reality", "psychology understanding"
]

# Horror-specific tag pool
HORROR_TAG_POOL = [
    "horror stories", "scary stories", "true horror", "horror shorts", "horror stories",
    "scary", "creepy", "spooky", "horror", "nightmare", "haunted", "ghost stories",
    "urban legends", "creepypasta", "scary story", "horror story", "dark stories",
    "mysterious", "eerie", "horror content", "scary shorts", "horror youtube",
    "true stories", "real horror", "horror story time", "scary story time",
    "horror narration", "horror story narration", "dark tales", "horror tales",
    "scary tales", "paranormal", "supernatural", "horror story channel",
    "creepy stories", "horror stories short", "scary stories short", "horror short",
    "horror storytime", "scary storytime", "horror story reading", "scary story reading",
    "horror content creator", "horror story teller", "scary story teller"
]


def _get_rotated_tags(base_tags: list = None, num_tags: int = None, horror_mode: bool = False) -> list:
    """
    Rotate through tag pool and select random tags for Trust Score protection.
    
    Ensures tag variety to avoid detection as spam/automation.
    
    Args:
        base_tags: Optional base tags to always include
        num_tags: Number of random tags to select (5-10, default: random 7-9)
        horror_mode: If True, use horror-specific tag pool
        
    Returns:
        List of tags with base tags + random selection from pool
    """
    import random
    
    if num_tags is None:
        num_tags = random.randint(7, 9)  # Random 7-9 tags
    
    # Choose appropriate tag pool and essential tags
    if horror_mode:
        tag_pool = HORROR_TAG_POOL
        essential_tags = ["YouTube Shorts", "horror stories", "scary stories"]
    else:
        tag_pool = TAG_POOL
        essential_tags = ["YouTube Shorts", "psychology", "dark psychology"]
    
    # Combine base tags and essential tags
    final_tags = []
    if base_tags:
        final_tags.extend(base_tags)
    final_tags.extend(essential_tags)
    
    # Remove duplicates and normalize
    final_tags = list(set([tag.lower().strip() for tag in final_tags]))
    
    # Select random tags from pool (excluding already included)
    available_pool = [tag for tag in tag_pool if tag.lower() not in [t.lower() for t in final_tags]]
    
    # Randomly select additional tags
    if len(available_pool) > 0:
        num_additional = min(num_tags - len(final_tags), len(available_pool))
        if num_additional > 0:
            additional_tags = random.sample(available_pool, num_additional)
            final_tags.extend(additional_tags)
    
    # Shuffle for variety
    random.shuffle(final_tags)
    
    # Limit to YouTube's tag limit (500 tags max, but we'll use reasonable amount)
    return final_tags[:15]  # Use up to 15 tags (good balance)


def upload_video(file_path: str, title: str, description: str, tags: list = None, category_id: str = "20", horror_mode: bool = False, schedule_time: str = None, thumbnail_path: str = None) -> str:
    """
    Upload video to YouTube (with optional scheduling).
    
    Args:
        file_path: Path to video file
        title: Video title
        description: Video description
        tags: List of tags (default: ["YouTube Shorts", "Viral", "AI Generated"])
        category_id: YouTube category ID (default: "20" for Gaming)
        horror_mode: If True, use horror-specific tag pool
        schedule_time: ISO 8601 datetime string for scheduled publishing (e.g., "2025-12-26T08:00:00-05:00" for 8 AM EST)
                       If None, publishes immediately
        
    Returns:
        YouTube video ID
        
    Raises:
        Exception: If upload fails
    """
    # Check for client_secrets.json
    if not os.path.exists(CLIENT_SECRETS_FILE):
        # Also check parent directory
        parent_dir = os.path.dirname(os.getcwd())
        parent_secrets = os.path.join(parent_dir, CLIENT_SECRETS_FILE)
        if not os.path.exists(parent_secrets):
            raise FileNotFoundError(
                f"client_secrets.json not found. Please download it from Google Cloud Console "
                f"and place it in the project root: {os.getcwd()}"
            )
    
    print("⬆️ Uploading video to YouTube...")
    
    # Rotate tags for Trust Score protection (avoids spam detection)
    if tags is None:
        tags = _get_rotated_tags(horror_mode=horror_mode)
    else:
        # Even if tags provided, rotate through pool for variety
        tags = _get_rotated_tags(base_tags=tags, horror_mode=horror_mode)
    
    print(f"   Using {len(tags)} rotated tags (Trust Score protection)")
    print(f"   Tags: {', '.join(tags[:5])}{'...' if len(tags) > 5 else ''}")
    
    creds = None
    token_path = 'token.json'
    
    # Check for existing credentials
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception as e:
            print(f"   ⚠️ Could not load existing credentials: {e}")
            creds = None
    
    # If no (valid) credentials, refresh or authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("   Refreshing credentials...")
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"   ⚠️ Could not refresh credentials: {e}")
                creds = None
        
        if not creds:
            # Search for client_secrets.json
            current_dir = os.getcwd()
            parent_dir = os.path.dirname(current_dir)
            client_secrets_paths = [
                os.path.join(current_dir, CLIENT_SECRETS_FILE),
                os.path.join(parent_dir, CLIENT_SECRETS_FILE)
            ]
            
            found_secrets_file = None
            for path in client_secrets_paths:
                if os.path.exists(path):
                    found_secrets_file = path
                    break
            
            if not found_secrets_file:
                raise FileNotFoundError(
                    f"client_secrets.json not found in {current_dir} or {parent_dir}. "
                    "Please download it from Google Cloud Console and place it in the project root."
                )
            
            print(f"   Authenticating with {found_secrets_file}...")
            flow = InstalledAppFlow.from_client_secrets_file(found_secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        print("   ✓ Credentials saved")
    
    # Build YouTube API service
    youtube = build('youtube', 'v3', credentials=creds)
    
    # Prepare video metadata
    status_dict = {
        "privacyStatus": "private" if schedule_time else "public"  # Scheduled videos must be private first
    }
    
    # Add scheduled publishing time if provided
    if schedule_time:
        status_dict["publishAt"] = schedule_time
        print(f"   📅 Scheduled for: {schedule_time}")
    
    body = {
        "snippet": {
            "title": title[:100],  # YouTube title limit
            "description": description[:5000],  # YouTube description limit
            "tags": tags[:500],  # YouTube tags limit
            "categoryId": category_id
        },
        "status": status_dict
    }
    
    # Upload video
    print(f"   Uploading: {title}")
    print(f"   File: {file_path} ({os.path.getsize(file_path)} bytes)")
    
    media_body = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media_body
    )
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            progress = int(status.progress() * 100)
            print(f"   Upload progress: {progress}%")
    
    video_id = response['id']
    print(f"✓ Video uploaded successfully!")
    print(f"   Video ID: {video_id}")
    print(f"   URL: https://www.youtube.com/watch?v={video_id}")
    
    # Set custom thumbnail if provided
    if thumbnail_path and os.path.exists(thumbnail_path):
        try:
            print(f"   🖼️ Setting custom thumbnail...")
            # MediaFileUpload already imported at top
            thumbnail_media = MediaFileUpload(thumbnail_path, mimetype='image/png', resumable=True)
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=thumbnail_media
            ).execute()
            print(f"      ✓ Thumbnail set successfully")
        except Exception as e:
            print(f"      ⚠️ Could not set thumbnail: {e}")
            print(f"      Note: Thumbnail can be set manually in YouTube Studio")
    
    return video_id


if __name__ == "__main__":
    # Test the upload engine
    print("=" * 60)
    print("🧪 TESTING UPLOAD ENGINE")
    print("=" * 60)
    
    print("Note: Run full pipeline test via main.py")

