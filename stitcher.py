import os
import sys
import json
import asyncio
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import edge_tts
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    ImageClip,
    concatenate_videoclips,
    concatenate_audioclips,
    CompositeVideoClip
)

def extract_voiceover_text(audio_field):
    """Extracts spoken text from the video script Audio field, removing narrator tags and quotes."""
    if "Narrator:" in audio_field:
        parts = audio_field.split("Narrator:", 1)
        text = parts[1].strip()
    else:
        text = audio_field.strip()
    
    # Strip straight and curly double quotes if they surround the text
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1].strip()
    elif text.startswith('“') and text.endswith('”'):
        text = text[1:-1].strip()
        
    return text

async def synthesize_scene_tts(text, voice, audio_path):
    """Synthesizes text to an MP3 file using edge-tts and retrieves word boundary timestamps."""
    communicate = edge_tts.Communicate(text, voice, boundary="WordBoundary")
    words = []
    with open(audio_path, "wb") as fp:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                fp.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append({
                    "word": chunk["text"],
                    "start": chunk["offset"] / 10000000.0,
                    "duration": chunk["duration"] / 10000000.0
                })
    return words

def load_font(size):
    """Safely loads a bold true-type font from Windows directories or falls back."""
    paths = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/Arial.ttf",
        "arialbd.ttf",
        "Arial.ttf"
    ]
    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except IOError:
            continue
    return ImageFont.load_default()

def get_text_width(text, font, draw):
    """Returns the width of text rendered with the specified font."""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]

def render_subtitle_frame(words, active_idx, width, height):
    """Renders a transparent RGBA image frame with centered text and highlighted active word."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Dynamically select font size to fit width without overflow
    font_size = 28
    space_width = 0
    word_widths = []
    total_width = 0
    font = None
    
    while font_size > 14:
        font = load_font(font_size)
        space_width = get_text_width(" ", font, draw)
        word_widths = [get_text_width(w, font, draw) for w in words]
        total_width = sum(word_widths) + space_width * (len(words) - 1)
        if total_width < width * 0.85:
            break
        font_size -= 2
        
    # Draw centered on screen width, positioned at 70% height
    x = (width - total_width) / 2
    y = int(height * 0.7)
    
    for idx, w in enumerate(words):
        if idx == active_idx:
            # Highlighted active word: bold bright yellow
            color = (255, 215, 0, 255)
        else:
            # Default word: clean white
            color = (255, 255, 255, 255)
            
        # Draw with thick black outline for maximum readability on varying video backgrounds
        draw.text((x, y), w, font=font, fill=color, stroke_width=3, stroke_fill=(0, 0, 0, 255))
        x += word_widths[idx] + space_width
        
    return img

def group_words_into_cards(words, max_words=4, max_gap=1.2):
    """Groups a list of timed words into individual subtitle cards."""
    cards = []
    current_card = []
    
    for w in words:
        if not current_card:
            current_card.append(w)
            continue
            
        prev_w = current_card[-1]
        gap = w["start"] - prev_w["end"]
        
        should_split = False
        if len(current_card) >= max_words:
            should_split = True
        elif gap > max_gap:
            should_split = True
        elif any(prev_w["word"].endswith(char) for char in [".", "?", "!", ";"]):
            should_split = True
            
        if should_split:
            cards.append(current_card)
            current_card = [w]
        else:
            current_card.append(w)
            
    if current_card:
        cards.append(current_card)
        
    return cards

async def main_stitch(app_key):
    # Paths setup
    output_dir = os.path.join("output", app_key)
    assets_path = os.path.join(output_dir, "marketing_assets.json")
    video_path = os.path.join(output_dir, "raw_recording.webm")
    voiceover_path = os.path.join(output_dir, "voiceover.mp3")
    final_output_path = os.path.join(output_dir, "final_shorts.mp4")
    
    if not os.path.exists(assets_path):
        print(f"Error: Marketing assets file not found at '{assets_path}'", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(video_path):
        print(f"Error: Raw screen recording file not found at '{video_path}'", file=sys.stderr)
        sys.exit(1)
        
    # Read marketing script
    with open(assets_path, "r", encoding="utf-8") as f:
        assets = json.load(f)
        
    video_script = assets.get("video_script", [])
    if not video_script:
        print("Error: No video_script array found in marketing_assets.json", file=sys.stderr)
        sys.exit(1)
        
    voice = "en-US-GuyNeural"
    global_words = []
    accum_duration = 0.0
    audio_clips = []
    
    print("\n=== Stage 1: Synthesizing voiceover audio tracks ===")
    for i, scene in enumerate(video_script):
        audio_text = extract_voiceover_text(scene.get("Audio", ""))
        if not audio_text:
            continue
            
        scene_audio_path = os.path.join(output_dir, f"scene_{i}.mp3")
        print(f"Synthesizing scene {i+1}/{len(video_script)}: '{audio_text[:50]}...'")
        
        # Synthesize audio file and get word-level timings
        scene_words = await synthesize_scene_tts(audio_text, voice, scene_audio_path)
        
        # Load audio clip temporarily to check duration
        clip = AudioFileClip(scene_audio_path)
        duration = clip.duration
        audio_clips.append(clip)
        
        # Add scene words to absolute timing list
        for w in scene_words:
            global_words.append({
                "word": w["word"],
                "start": accum_duration + w["start"],
                "end": accum_duration + w["start"] + w["duration"]
            })
            
        accum_duration += duration

    # Concatenate all scene audios into a single continuous file
    print("Concatenating scene audios into single voiceover file...")
    voiceover_clip = concatenate_audioclips(audio_clips)
    voiceover_clip.write_audiofile(voiceover_path, logger=None)
    voiceover_clip.close()
    for clip in audio_clips:
        clip.close()
        
    print(f"Voiceover synthesis completed. Total duration: {accum_duration:.2f}s")
    
    # Reload final voiceover file
    final_audio = AudioFileClip(voiceover_path)
    
    # Group words into subtitle cards/cues
    cards = group_words_into_cards(global_words, max_words=4)
    print(f"Generated {len(cards)} subtitle cards.")
    
    # Load base video to inspect resolution
    base_video = VideoFileClip(video_path)
    width, height = base_video.size
    print(f"Base video resolution: {width}x{height}, duration: {base_video.duration:.2f}s")
    
    # Generate transparent overlay ImageClips for each subtitle state
    subtitle_clips = []
    for card in cards:
        card_words = [w["word"] for w in card]
        for idx, active_word_info in enumerate(card):
            start_time = active_word_info["start"]
            if idx < len(card) - 1:
                end_time = card[idx + 1]["start"]
            else:
                end_time = active_word_info["end"]
                
            duration = end_time - start_time
            if duration <= 0:
                continue
                
            # Render PIL frame with the current word highlighted
            frame = render_subtitle_frame(card_words, idx, width, height)
            frame_np = np.array(frame)
            
            # Construct MoviePy clip with timing
            img_clip = ImageClip(frame_np).set_start(start_time).set_duration(duration)
            subtitle_clips.append(img_clip)

    # Process and align video length with voiceover length
    extended_video = None
    if base_video.duration < accum_duration:
        # Extend video by freezing the last frame
        print(f"Video is shorter than audio. Freezing final frame for {accum_duration - base_video.duration:.2f}s...")
        last_frame = base_video.get_frame(base_video.duration - 0.1)
        freeze_clip = ImageClip(last_frame).set_duration(accum_duration - base_video.duration)
        extended_video = concatenate_videoclips([base_video, freeze_clip])
    else:
        # Trim video to match audio
        print(f"Video is longer than audio. Trimming to match voiceover...")
        extended_video = base_video.subclip(0, accum_duration)
        
    # Bind synthesized audio
    video_with_audio = extended_video.set_audio(final_audio)
    
    # Compose everything
    print("Composing video, voiceover, and subtitle overlays...")
    final_video = CompositeVideoClip([video_with_audio] + subtitle_clips)
    
    # Render final output
    print(f"Rendering final stitched video to: '{final_output_path}'")
    final_video.write_videofile(
        final_output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        logger=None
    )
    
    # Close all handles to release file locks on Windows
    final_video.close()
    video_with_audio.close()
    if base_video.duration < accum_duration:
        freeze_clip.close()
    extended_video.close()
    base_video.close()
    final_audio.close()
    for c in subtitle_clips:
        c.close()
        
    # Clean up scene-specific temporary audio files
    for i in range(len(video_script)):
        temp_path = os.path.join(output_dir, f"scene_{i}.mp3")
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as ex:
                print(f"Warning: Could not clean up temporary file {temp_path}: {ex}")
                
    print(f"\nStitching complete! Final video saved successfully: '{final_output_path}'")

if __name__ == "__main__":
    app_key_arg = sys.argv[1] if len(sys.argv) > 1 else "npc-aggregator"
    asyncio.run(main_stitch(app_key_arg))
