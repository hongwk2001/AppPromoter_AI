import os
import sys
import asyncio
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import edge_tts
from moviepy.editor import (
    AudioFileClip,
    ImageClip,
    concatenate_videoclips,
    concatenate_audioclips,
    CompositeVideoClip
)

# Reuse helpers from stitcher.py
def extract_voiceover_text(audio_field):
    if "Narrator:" in audio_field:
        parts = audio_field.split("Narrator:", 1)
        text = parts[1].strip()
    else:
        text = audio_field.strip()
    return text.strip('"').strip('“').strip('”')

async def synthesize_scene_tts(text, voice, audio_path):
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
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]

def render_subtitle_frame(words, active_idx, width, height):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    font_size = 32
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
        
    x = (width - total_width) / 2
    y = int(height * 0.8) # Positioned lower on screen
    
    for idx, w in enumerate(words):
        if idx == active_idx:
            color = (255, 215, 0, 255) # Highlighted yellow
        else:
            color = (255, 255, 255, 255)
            
        draw.text((x, y), w, font=font, fill=color, stroke_width=3, stroke_fill=(0, 0, 0, 255))
        x += word_widths[idx] + space_width
        
    return img

def group_words_into_cards(words, max_words=4, max_gap=1.2):
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

async def make_video():
    output_dir = r"d:\git_repo\AppPromoter_AI\output\kb_html"
    voiceover_path = os.path.join(output_dir, "launch_voiceover.mp3")
    final_output_path = os.path.join(output_dir, "reddit_replier_launch.mp4")
    
    # 2-minute visual showcase script
    video_script = [
        {
            "Image": "error_403.png",
            "Audio": "We wanted to build a simple tool to scan Reddit and draft helpful community replies. But we immediately hit a wall: Reddit aggressively blocks automated scripts with HTTP 403 Forbidden errors."
        },
        {
            "Image": "cli_menu.png",
            "Audio": "Instead of giving up or setting up complex API apps, we hacked around it by scraping Reddit's public RSS search feeds. By filtering results locally and caching history files, we made sure we never review the same post twice."
        },
        {
            "Image": "gemini_token_limit.png",
            "Audio": "Initially, everything went through the Gemini API. But we quickly hit the Gemini token limit when analyzing large chunks of context. Since we couldn't rely on the cloud, we tried running Gemma 2 locally—and getting it running on our machine was easier than we expected."
        },
        {
            "Image": "error_403.png", # Fallback visual or we can just use error_403.png/cli_menu.png if no dedicated Ollama timeout screen exists
            "Audio": "We wanted this 100 percent local, so we plugged in Ollama running Google's 7.2 gigabyte Gemma model. The catch? It takes forever to load into memory on the first run. Standard HTTP requests timed out, so we increased the timeout to 120 seconds and built a one-click cloud fallback to Gemini if Ollama stalls."
        },
        {
            "Image": "reddit_review_screenshot.png",
            "Audio": "Copy-pasting details between terminal and browser is exhausting. So we built a custom GUI popup using standard Tkinter: original post on top for context, editable draft on bottom, and a save button that automatically copies to clipboard and opens the thread."
        },
        {
            "Image": "reddit_review_screenshot.png",
            "Audio": "Today's win? A fully organized, open-weights dashboard, with all progress notes compiled to HTML and deployed live. Next up, I'm thinking to make an email aggregator that can help me clean up emails. Let's see if it will come out all right. Keep hacking."
        }
    ]
    
    voice = "en-US-SteffanNeural"
    global_words = []
    accum_duration = 0.0
    audio_clips = []
    image_clips = []
    
    print("\n=== Stage 1: Synthesizing voiceover audio tracks ===")
    for i, scene in enumerate(video_script):
        audio_text = extract_voiceover_text(scene["Audio"])
        scene_audio_path = os.path.join(output_dir, f"launch_scene_{i}.mp3")
        
        # Synthesize audio and get timings
        scene_words = await synthesize_scene_tts(audio_text, voice, scene_audio_path)
        
        clip = AudioFileClip(scene_audio_path)
        duration = clip.duration
        audio_clips.append(clip)
        
        # Add absolute timings
        for w in scene_words:
            global_words.append({
                "word": w["word"],
                "start": accum_duration + w["start"],
                "end": accum_duration + w["start"] + w["duration"]
            })
            
        # Create image slide clip matching the duration of this audio clip
        img_path = os.path.join(output_dir, scene["Image"])
        if not os.path.exists(img_path):
            print(f"Error: Screenshot '{img_path}' not found. Cannot proceed.")
            sys.exit(1)
            
        img_clip = ImageClip(img_path).set_duration(duration).set_start(accum_duration)
        image_clips.append(img_clip)
        
        accum_duration += duration

    print("Concatenating scene audios...")
    voiceover_clip = concatenate_audioclips(audio_clips)
    voiceover_clip.write_audiofile(voiceover_path, logger=None)
    voiceover_clip.close()
    for clip in audio_clips:
        clip.close()
        
    final_audio = AudioFileClip(voiceover_path)
    
    # Concatenate the slides into a base video
    base_video = concatenate_videoclips(image_clips, method="compose")
    base_video = base_video.set_audio(final_audio)
    
    # 1280x720 standard resolution or adapt to first image size
    # We will resize slides to a standard 1280x720 layout
    width, height = 1280, 720
    
    # Resize base video clips to fit the 1280x720 target frame
    resized_image_clips = []
    accum_time = 0.0
    for i, scene in enumerate(video_script):
        img_path = os.path.join(output_dir, scene["Image"])
        duration = base_video.clips[i].duration
        
        # Load and resize using PIL to preserve quality
        pil_img = Image.open(img_path)
        pil_img = pil_img.resize((width, height), Image.Resampling.LANCZOS)
        frame_np = np.array(pil_img)
        
        img_clip = ImageClip(frame_np).set_duration(duration).set_start(accum_time)
        resized_image_clips.append(img_clip)
        accum_time += duration
        
    base_video = concatenate_videoclips(resized_image_clips, method="compose")
    base_video = base_video.set_audio(final_audio)
    
    # Group words into subtitle cues
    cards = group_words_into_cards(global_words, max_words=4)
    print(f"Generated {len(cards)} subtitle cues.")
    
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
                
            frame = render_subtitle_frame(card_words, idx, width, height)
            frame_np = np.array(frame)
            
            img_clip = ImageClip(frame_np).set_start(start_time).set_duration(duration)
            subtitle_clips.append(img_clip)

    print("Composing video slides, audio, and subtitles...")
    final_video = CompositeVideoClip([base_video] + subtitle_clips)
    
    print(f"Rendering final launch video: '{final_output_path}'")
    final_video.write_videofile(
        final_output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        logger=None
    )
    
    # Close handles
    final_video.close()
    base_video.close()
    final_audio.close()
    for c in subtitle_clips:
        c.close()
    for c in resized_image_clips:
        c.close()
        
    # Cleanup temp audios
    for i in range(len(video_script)):
        temp_path = os.path.join(output_dir, f"launch_scene_{i}.mp3")
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    print(f"\nLaunch video successfully saved: '{final_output_path}'")

if __name__ == "__main__":
    asyncio.run(make_video())
