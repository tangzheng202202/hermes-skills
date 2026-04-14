#!/usr/bin/env python3
"""
Automated Video Generator v4.0 - Complete Example
Multi-platform export + BGM + Screen recording integration

Usage:
    1. Prepare footage/ directory with screen recordings (optional)
    2. Prepare bgm/ directory with background music (optional)
    3. Run: python3 v4-complete-example.py
    4. Select platforms interactively
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Configuration
OUTPUT_DIR = "output"
TEMP_DIR = "temp"
FOOTAGE_DIR = "footage"
BGM_DIR = "bgm"

# Multi-platform configs
PLATFORMS = {
    "douyin": {"name": "Douyin", "resolution": (1080, 1920), "ratio": "9:16"},
    "bilibili": {"name": "Bilibili", "resolution": (1920, 1080), "ratio": "16:9"},
    "xiaohongshu": {"name": "Xiaohongshu", "resolution": (1080, 1440), "ratio": "3:4"},
    "shipinhao": {"name": "Video Channel", "resolution": (1080, 1260), "ratio": "6:7"},
}

# Example script - customize this for your content
SCRIPT = [
    {
        "type": "hook",
        "duration": 5,
        "text": "❌ Problem 1\n❌ Problem 2\n❌ Problem 3",
        "voice": "If you've tried X but still struggle, it's not your fault..."
    },
    {
        "type": "footage",
        "duration": 12,
        "title": "Pain Points",
        "file": "screen_01_demo.mp4",  # User-provided
        "voice": "Many tutorials tell you to do this and that, but...",
        "fallback": "content",
        "fallback_points": ["Issue 1", "Issue 2", "Issue 3"]
    },
    {
        "type": "chapter",
        "duration": 5,
        "num": "01",
        "title": "Solution 1",
        "subtitle": "The first thing to configure",
        "color": "#FFD700",
        "voice": "First, do this. Not that, but this."
    },
    {
        "type": "summary",
        "duration": 10,
        "title": "Summary",
        "points": ["Point 1", "Point 2", "Point 3", "Point 4", "Point 5"],
        "voice": "These 5 things will transform your experience..."
    },
    {
        "type": "cta",
        "duration": 8,
        "text": "Next time: Advanced tips\nStay tuned!",
        "voice": "Next time we'll cover advanced techniques..."
    }
]


def get_font(size):
    """Get system font with fallback"""
    system = "darwin" if sys.platform == "darwin" else "linux"
    font_paths = {
        "darwin": "/System/Library/Fonts/PingFang.ttc",
        "linux": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    }
    font_path = font_paths.get(system, "")
    
    if os.path.exists(font_path):
        try:
            return ImageFont.truetype(font_path, size)
        except:
            pass
    return ImageFont.load_default()


def create_chapter_card(number, title, subtitle, color_hex, output_path, res):
    """Generate chapter intro card"""
    img = Image.new('RGB', res, '#1a1a1a')
    draw = ImageDraw.Draw(img)
    color = tuple(int(color_hex[i:i+2], 16) for i in (1, 3, 5))
    
    # Responsive font sizing
    if res[1] > res[0]:  # Vertical
        font_num = get_font(200)
        font_title = get_font(100)
        font_sub = get_font(40)
        y_num, y_title, y_sub = res[1]//3, res[1]//2, res[1]//2 + 150
    else:  # Horizontal
        font_num = get_font(150)
        font_title = get_font(80)
        font_sub = get_font(35)
        y_num, y_title, y_sub = res[1]//3, res[1]//2, res[1]//2 + 100
    
    draw.text((res[0]//2, y_num), number, fill=color, font=font_num, anchor="mm")
    draw.text((res[0]//2, y_title), title, fill='#FFFFFF', font=font_title, anchor="mm")
    draw.text((res[0]//2, y_sub), subtitle, fill='#AAAAAA', font=font_sub, anchor="mm")
    
    img.save(output_path)
    return output_path


def generate_voice(text, output_path, voice="zh-CN-XiaoxiaoNeural"):
    """Generate AI voice with edge-tts"""
    cmd = ["edge-tts", "--voice", voice, "--text", text, "--write-media", output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def image_to_video(image_path, duration, output_path, res):
    """Convert image to video segment"""
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", image_path,
        "-c:v", "libx264",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        "-vf", f"fps=30,scale={res[0]}:{res[1]}:force_original_aspect_ratio=decrease,pad={res[0]}:{res[1]}:(ow-iw)/2:(oh-ih)/2",
        "-an", output_path
    ]
    subprocess.run(cmd, capture_output=True, check=True)


def merge_audio_video(video_path, audio_path, output_path):
    """Combine video and audio"""
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest", output_path
    ]
    subprocess.run(cmd, capture_output=True, check=True)


def add_bgm(video_path, bgm_path, output_path, bgm_volume=0.15):
    """Add background music with fade effects"""
    if not bgm_path:
        os.rename(video_path, output_path)
        return True
    
    # Get video duration
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
           "-of", "default=noprint_wrappers=1:nokey=1", video_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    duration = float(result.stdout.strip())
    
    # Mix with BGM
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-stream_loop", "-1", "-i", bgm_path,
        "-filter_complex", 
        f"[1:a]volume={bgm_volume},afade=t=in:ss=0:d=2,afade=t=out:st={duration-3}:d=3[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=3[outa]",
        "-map", "0:v",
        "-map", "[outa]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-t", str(duration),
        "-shortest", output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def concatenate_videos(video_list, output_path):
    """Join video segments"""
    list_file = tempfile.mktemp(suffix=".txt")
    with open(list_file, "w") as f:
        for v in video_list:
            f.write(f"file '{os.path.abspath(v)}'\n")
    
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    os.remove(list_file)
    return result.returncode == 0


def generate_for_platform(platform_key, config, bgm_path):
    """Generate complete video for a platform"""
    res = config["resolution"]
    platform_temp = os.path.join(TEMP_DIR, platform_key)
    os.makedirs(platform_temp, exist_ok=True)
    
    segments = []
    
    for i, seg in enumerate(SCRIPT):
        img_path = os.path.join(platform_temp, f"seg_{i:02d}.png")
        video_path = os.path.join(platform_temp, f"seg_{i:02d}_v.mp4")
        
        # Generate visual based on type
        if seg["type"] == "chapter":
            create_chapter_card(seg["num"], seg["title"], seg["subtitle"], 
                              seg["color"], img_path, res)
        # Add more segment types as needed
        
        image_to_video(img_path, seg["duration"], video_path, res)
        
        # Generate voice (only once per segment, reuse for all platforms)
        audio_path = os.path.join(TEMP_DIR, f"seg_{i:02d}.mp3")
        if not os.path.exists(audio_path):
            generate_voice(seg["voice"], audio_path)
        
        merged_path = os.path.join(platform_temp, f"seg_{i:02d}.mp4")
        merge_audio_video(video_path, audio_path, merged_path)
        segments.append(merged_path)
    
    # Concatenate and add BGM
    merged = os.path.join(platform_temp, "merged.mp4")
    concatenate_videos(segments, merged)
    
    final = os.path.join(OUTPUT_DIR, f"video_{platform_key}.mp4")
    add_bgm(merged, bgm_path, final)
    
    return final


def main():
    print("🎬 Automated Video Generator v4.0")
    print("=" * 50)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # Check for BGM
    bgm_path = None
    if os.path.exists(BGM_DIR):
        bgm_files = [f for f in os.listdir(BGM_DIR) if f.endswith(('.mp3', '.wav', '.aac'))]
        if bgm_files:
            bgm_path = os.path.join(BGM_DIR, bgm_files[0])
            print(f"🎵 Found BGM: {bgm_files[0]}")
    
    # Platform selection
    print("\nSelect platforms to generate:")
    selected = []
    for key, config in PLATFORMS.items():
        response = input(f"  {config['name']} ({config['ratio']})? [Y/n]: ").strip().lower()
        if response in ['', 'y', 'yes']:
            selected.append(key)
    
    if not selected:
        selected = ["douyin"]
    
    # Generate for each platform
    for platform in selected:
        config = PLATFORMS[platform]
        print(f"\n🎬 Generating {config['name']}...")
        output = generate_for_platform(platform, config, bgm_path)
        print(f"  ✅ Saved: {output}")
    
    print("\n🎉 Done! Check output/ directory")


if __name__ == "__main__":
    main()
