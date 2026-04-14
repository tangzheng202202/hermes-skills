#!/usr/bin/env python3
"""
Hermes Agent 视频全自动生成脚本
一键生成：配音 + 字幕 + 章节卡片 + 最终视频

使用: python3 auto_video_generator.py
输出: output/final_video.mp4
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import shutil

# 配置
OUTPUT_DIR = "output"
TEMP_DIR = "temp"
RESOLUTION = (1080, 1920)  # 9:16 竖屏
FPS = 30

# 字体配置
FONT_CONFIG = {
    "darwin": "/System/Library/Fonts/PingFang.ttc",  # macOS
    "linux": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
}


def get_font(size):
    """获取系统字体"""
    system = "darwin" if sys.platform == "darwin" else "linux"
    font_path = FONT_CONFIG.get(system, "")
    
    if os.path.exists(font_path):
        try:
            return ImageFont.truetype(font_path, size)
        except:
            pass
    
    return ImageFont.load_default()


def create_chapter_card(number, title, subtitle, color_hex, output_path):
    """创建章节卡片"""
    img = Image.new('RGB', RESOLUTION, '#1a1a1a')
    draw = ImageDraw.Draw(img)
    
    color = tuple(int(color_hex[i:i+2], 16) for i in (1, 3, 5))
    
    font_num = get_font(200)
    font_title = get_font(100)
    font_sub = get_font(40)
    
    draw.text((RESOLUTION[0]//2, 600), number, fill=color, font=font_num, anchor="mm")
    draw.text((RESOLUTION[0]//2, 900), title, fill='#FFFFFF', font=font_title, anchor="mm")
    draw.text((RESOLUTION[0]//2, 1050), subtitle, fill='#AAAAAA', font=font_sub, anchor="mm")
    draw.rectangle([340, 750, 740, 760], fill=color)
    
    img.save(output_path)
    return output_path


def create_black_screen(text, output_path):
    """创建黑屏文字"""
    img = Image.new('RGB', RESOLUTION, 'black')
    draw = ImageDraw.Draw(img)
    font = get_font(60)
    
    lines = text.split('\\n')
    y_offset = -50 * (len(lines) - 1)
    
    for i, line in enumerate(lines):
        draw.text((RESOLUTION[0]//2, RESOLUTION[1]//2 + y_offset + i * 100), 
                  line, fill='white', font=font, anchor="mm")
    
    img.save(output_path)
    return output_path


def create_content_screen(title, points, code=None, output_path=None):
    """创建内容屏幕"""
    img = Image.new('RGB', RESOLUTION, '#1a1a1a')
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(70)
    font_point = get_font(45)
    font_code = get_font(35)
    
    draw.text((RESOLUTION[0]//2, 200), title, fill='white', font=font_title, anchor="mm")
    
    y = 450
    for point in points[:4]:
        draw.text((100, y), f"• {point}", fill='#CCCCCC', font=font_point)
        y += 80
    
    if code:
        y += 50
        draw.rectangle([80, y, RESOLUTION[0]-80, y + 120], fill='#2d2d2d', outline='#444444', width=2)
        code_lines = code.split('\\n')
        for i, line in enumerate(code_lines):
            draw.text((100, y + 20 + i * 35), line, fill='#00ff00', font=font_code)
    
    img.save(output_path)
    return output_path


def generate_voice(text, output_path, voice="zh-CN-XiaoxiaoNeural"):
    """生成AI配音"""
    cmd = [
        "edge-tts",
        "--voice", voice,
        "--text", text,
        "--write-media", output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def image_to_video(image_path, duration, output_path):
    """图片转视频"""
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", image_path,
        "-c:v", "libx264",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        "-vf", f"fps={FPS},scale={RESOLUTION[0]}:{RESOLUTION[1]}",
        "-an", output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def merge_audio_video(video_path, audio_path, output_path):
    """合并视频和音频"""
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest", output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def concatenate_videos(video_list, output_path):
    """拼接视频"""
    list_file = tempfile.mktemp(suffix=".txt")
    with open(list_file, "w") as f:
        for v in video_list:
            f.write(f"file '{os.path.abspath(v)}'\\n")
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", list_file,
        "-c", "copy", output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    os.remove(list_file)
    return result.returncode == 0


def main():
    print("🎬 视频自动生成脚本")
    print("=" * 50)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # 示例脚本 - 修改此处自定义内容
    SCRIPT = [
        {"type": "hook", "duration": 5, "text": "❌ 问题1\\n❌ 问题2", 
         "voice": "你的配音文案"},
        {"type": "chapter", "duration": 5, "num": "01", "title": "标题", 
         "subtitle": "副标题", "color": "#FFD700",
         "voice": "第一章配音"},
        {"type": "content", "duration": 10, "title": "详解",
         "points": ["要点1", "要点2"],
         "voice": "详细说明"},
    ]
    
    segments = []
    
    for i, seg in enumerate(SCRIPT):
        print(f"\\n--- 片段 {i+1}/{len(SCRIPT)} ---")
        
        img_path = os.path.join(TEMP_DIR, f"seg_{i:02d}.png")
        video_path = os.path.join(TEMP_DIR, f"seg_{i:02d}_v.mp4")
        
        if seg["type"] == "chapter":
            create_chapter_card(seg["num"], seg["title"], 
                              seg["subtitle"], seg["color"], img_path)
        elif seg["type"] in ["hook", "cta"]:
            create_black_screen(seg["text"], img_path)
        elif seg["type"] == "content":
            create_content_screen(seg["title"], seg.get("points", []), 
                                seg.get("code"), img_path)
        
        print("   🎬 生成视频...")
        image_to_video(img_path, seg["duration"], video_path)
        
        if "voice" in seg:
            print("   🎤 生成AI配音...")
            audio_path = os.path.join(TEMP_DIR, f"seg_{i:02d}.mp3")
            generate_voice(seg["voice"], audio_path)
            
            print("   🔗 合并...")
            merged_path = os.path.join(TEMP_DIR, f"seg_{i:02d}.mp4")
            merge_audio_video(video_path, audio_path, merged_path)
            segments.append(merged_path)
        else:
            segments.append(video_path)
    
    print("\\n🔗 拼接最终视频...")
    final_output = os.path.join(OUTPUT_DIR, "final_video.mp4")
    
    if concatenate_videos(segments, final_output):
        print(f"\\n✅ 成功: {final_output}")
        return 0
    else:
        print("\\n❌ 失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
