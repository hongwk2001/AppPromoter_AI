import os
import sys
import argparse
import asyncio
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import edge_tts
from moviepy.editor import (
    AudioFileClip,
    ImageClip,
    concatenate_videoclips,
    concatenate_audioclips,
    CompositeVideoClip
)

# ---------------------------------------------------------
# Default Fallback Script (If no matching txt files are found)
# ---------------------------------------------------------
DEFAULT_SCRIPT = {
    "1": "Let's analyze this golf swing.",
    "2.1": "[Bird chirping]",
    "2.2": "And a closer look at the posture.",
    "3": "First, record a video of your swing from the side.",
    "4": "Next, upload your swing video to the App.",
    "5": "The AI will process and analyze your form.",
    "6": "Oh no, the analysis shows you are casting the club!",
    "7": "Don't worry, here are some recommended drills on YouTube.",
    "8": "outtakes. Thank you for watching. Visit jigsawpuzzlehelper.com/golfswingai/",
    "9": "Create impact position.",
    "10": "Pretty good, can we make downswing position so I can have nice sequence ?",
    "11": "I said downswing, try again",
    "12": "wow good looking, but downswing please",
    "13": "Just adjust the pose slightly.",
    "14": "Thank you for watching. Visit jigsawpuzzlehelper.com/golfswingai/"
}

# Image and Text matching definitions
STEPS = [
    {"key": "1",   "img_pattern": "1.begin1.png", "txt_prefix": "1."},
    {"key": "2.1", "img_pattern": "2.1_zoomout_finish.png", "txt_prefix": "2.1."},
    {"key": "2.2", "img_pattern": "2.2._zoomout_finish.png", "txt_prefix": "2.2."},
    {"key": "3",   "img_pattern": "3.take_video_.png", "txt_prefix": "3."},
    {"key": "4",   "img_pattern": "4.upload_to_swingai.png", "txt_prefix": "4."},
    {"key": "5",   "img_pattern": "5.upload_to_swingai.png", "txt_prefix": "5."},
    {"key": "6",   "img_pattern": "6.You_are_casting!!.png", "txt_prefix": "6."},
    {"key": "7",   "img_pattern": "7.Drills_for_you_in_Youtube.png", "txt_prefix": "7."},
    {"key": "8",   "img_pattern": None, "txt_prefix": "8."},
    {"key": "9",   "img_pattern": "9.2.bot_impact1.png", "txt_prefix": "9.1."},
    {"key": "10",  "img_pattern": "10.2.create_down_swing.png", "txt_prefix": "10.1."},
    {"key": "11",  "img_pattern": "11.2.I_said_golf_swing_casting-pincel-ai-portrait.png", "txt_prefix": "11.1."},
    {"key": "12",  "img_pattern": "12.2.I_said_golf_swing-pincel-ai-portrait.png", "txt_prefix": "12.1."},
    {"key": "13",  "img_pattern": "13.2only_change_pose-pincel-ai-portrait.png", "txt_prefix": "13.2."},
    {"key": "14",  "img_pattern": None, "txt_prefix": "14."}
]

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

def get_text_size(text, font, draw):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    return w, h

def render_vertical_frame(image_path, width, height):
    """
    Renders a vertical 1080x1920 frame.
    Uses a blurred, scaled version of the image as background, and fits the original image in the foreground.
    """
    bg = Image.new("RGB", (width, height), (18, 18, 18)) # Dark charcoal fallback
    
    if not image_path or not os.path.exists(image_path):
        # Text-only slide background - dark gradient/solid
        draw = ImageDraw.Draw(bg)
        # Create a nice vertical gradient
        for y in range(height):
            r = int(18 + (30 - 18) * (y / height))
            g = int(18 + (30 - 18) * (y / height))
            b = int(24 + (40 - 24) * (y / height))
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        return bg

    fg_img = Image.open(image_path)
    fg_w, fg_h = fg_img.size

    # 1. Create blurred background
    scale_bg = max(width / fg_w, height / fg_h)
    bg_w, bg_h = int(fg_w * scale_bg), int(fg_h * scale_bg)
    bg_img = fg_img.resize((bg_w, bg_h), Image.Resampling.LANCZOS)
    bg_img = bg_img.crop(((bg_w - width) // 2, (bg_h - height) // 2, (bg_w + width) // 2, (bg_h + height) // 2))
    bg_img = bg_img.convert("RGB")
    bg_img = bg_img.filter(ImageFilter.GaussianBlur(radius=25))
    
    # Darken background
    darken = Image.new("RGB", bg_img.size, (0, 0, 0))
    bg_img = Image.blend(bg_img, darken, alpha=0.55)

    # 2. Fit foreground image preserving aspect ratio
    scale_fg = min(width / fg_w, height / fg_h)
    new_w, new_h = int(fg_w * scale_fg), int(fg_h * scale_fg)
    fg_resized = fg_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    x_offset = (width - new_w) // 2
    y_offset = (height - new_h) // 2
    bg_img.paste(fg_resized, (x_offset, y_offset))
    return bg_img

def render_subtitle_frame(words, active_idx, width, height, text_only_slide=False):
    """
    Renders a subtitle frame. For text-only slides, displays text larger in the center.
    For regular slides, displays karaoke highlighted subtitles in the lower third.
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if text_only_slide:
        # Render a beautiful centered block of text
        font_size = 56
        font = load_font(font_size)
        text_str = " ".join(words)
        
        # Word wrapping for text slide
        lines = []
        words_list = list(words)
        current_line = []
        for word in words_list:
            test_line = " ".join(current_line + [word])
            w_width = get_text_width(test_line, font, draw)
            if w_width < width * 0.85:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))
            
        # Draw wrapped lines centered
        line_heights = [get_text_size(line, font, draw)[1] for line in lines]
        total_text_height = sum(line_heights) + 20 * (len(lines) - 1)
        y = (height - total_text_height) // 2
        
        # Highlight active word
        flat_words_in_lines = []
        for line in lines:
            flat_words_in_lines.append(line.split())
            
        word_counter = 0
        for line_idx, line_words in enumerate(flat_words_in_lines):
            line_str = " ".join(line_words)
            w_line, h_line = get_text_size(line_str, font, draw)
            x = (width - w_line) / 2
            
            space_w = get_text_width(" ", font, draw)
            for w in line_words:
                color = (255, 215, 0, 255) if word_counter == active_idx else (255, 255, 255, 255)
                draw.text((x, y), w, font=font, fill=color, stroke_width=4, stroke_fill=(0, 0, 0, 255))
                x += get_text_width(w, font, draw) + space_w
                word_counter += 1
            y += h_line + 20
            
    else:
        # Standard lower-third karaoke style subtitle
        font_size = 46
        font = load_font(font_size)
        space_width = get_text_width(" ", font, draw)
        
        # Limit subtitles per card to look clean in vertical format (wrap to lines)
        lines = []
        current_line = []
        for idx, w in enumerate(words):
            test_line = " ".join([item[1] for item in current_line] + [w])
            w_width = get_text_width(test_line, font, draw)
            if w_width < width * 0.85:
                current_line.append((idx, w))
            else:
                lines.append(current_line)
                current_line = [(idx, w)]
        if current_line:
            lines.append(current_line)
            
        line_heights = [get_text_size(" ".join([w[1] for w in line]), font, draw)[1] for line in lines]
        total_height = sum(line_heights) + 15 * (len(lines) - 1)
        y = int(height * 0.75) # Lower third
        
        for line in lines:
            line_str = " ".join([w[1] for w in line])
            line_w, line_h = get_text_size(line_str, font, draw)
            x = (width - line_w) / 2
            for idx, w in line:
                color = (255, 215, 0, 255) if idx == active_idx else (255, 255, 255, 255)
                draw.text((x, y), w, font=font, fill=color, stroke_width=4, stroke_fill=(0, 0, 0, 255))
                x += get_text_width(w, font, draw) + space_width
            y += line_h + 15
            
    return img

def group_words_into_cards(words, max_words=3, max_gap=1.0):
    """Groups timed words into individual subtitle screens/cards."""
    cards = []
    current_card = []
    for w in words:
        if not current_card:
            current_card.append(w)
            continue
        prev_w = current_card[-1]
        gap = w["start"] - prev_w["end"]
        
        should_split = len(current_card) >= max_words or gap > max_gap or any(prev_w["word"].endswith(c) for c in [".", "?", "!", ";"])
        if should_split:
            cards.append(current_card)
            current_card = [w]
        else:
            current_card.append(w)
    if current_card:
        cards.append(current_card)
    return cards

async def synthesize_tts(text, voice, audio_path):
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
                    "duration": chunk["duration"] / 10000000.0,
                    "end": (chunk["offset"] + chunk["duration"]) / 10000000.0
                })
    return words

def find_text_file(directory, prefix):
    """Finds any text file matching the prefix (e.g. 1.casting.txt matches 1.)"""
    for file in os.listdir(directory):
        if file.lower().startswith(prefix.lower()) and file.lower().endswith(".txt"):
            return os.path.join(directory, file)
    return None

def find_audio_file(directory, key, sound_name_clean):
    """Searches for a matching sound file in the directory."""
    extensions = [".mp3", ".wav", ".m4a", ".ogg"]
    # Check by key first (e.g. 2.1.mp3)
    for ext in extensions:
        filename = f"{key}{ext}"
        path = os.path.join(directory, filename)
        if os.path.exists(path):
            return path
            
    # Check by sound name clean (e.g. bird_chirping.mp3)
    for ext in extensions:
        filename = f"{sound_name_clean}{ext}"
        path = os.path.join(directory, filename)
        if os.path.exists(path):
            return path
    return None

async def test_voices_preview():
    voices = {
        "Steffan (Male)": "en-US-SteffanNeural",
        "Guy (Male)": "en-US-GuyNeural",
        "Emma (Female)": "en-US-EmmaNeural",
        "Jenny (Female)": "en-US-JennyNeural",
        "Sonia (Female - GB)": "en-GB-SoniaNeural"
    }
    sample_text = "Let's check out your golf swing using the golf swing AI app."
    print("\n=== Voice Preview Mode ===")
    for name, voice in voices.items():
        print(f"Generating preview audio for {name} ({voice})...")
        filename = f"preview_{voice}.mp3"
        await synthesize_tts(sample_text, voice, filename)
        print(f"Saved: {filename}. Please play it to verify!")
    print("\nPreviews generated successfully. Choose your favorite voice and run with --voice <name>")

async def generate_video(voice, width=1080, height=1920):
    output_dir = "D:/git_repo/AppPromoter_AI/golfswing_ai"
    final_output_path = os.path.join(output_dir, "golfswing_short.mp4")
    temp_audio_dir = os.path.join(output_dir, "temp_audio")
    os.makedirs(temp_audio_dir, exist_ok=True)
    
    accum_duration = 0.0
    global_words = []
    audio_clips = []
    image_clips = []
    
    print("\n=== Stage 1: Parsing Files and Processing Audio ===")
    for idx, step in enumerate(STEPS):
        key = step["key"]
        img_pattern = step["img_pattern"]
        txt_prefix = step["txt_prefix"]
        
        # Determine voiceover/sound text
        found_txt = find_text_file(output_dir, txt_prefix)
        if found_txt:
            print(f"Step {key}: Found text file '{os.path.basename(found_txt)}'")
            with open(found_txt, "r", encoding="utf-8") as f:
                text = f.read().strip()
        else:
            text = DEFAULT_SCRIPT[key]
            print(f"Step {key}: No text file found. Using default script.")
            
        # Append URL for step 8 specifically as per user instruction
        if key == "8":
            if "jigsawpuzzlehelper" not in text:
                text += " Thank you for watching. Visit jigsawpuzzlehelper.com/golfswingai/"

        print(f"  Text: \"{text}\"")
        
        # Check if text is a sound effect in brackets (e.g. [Bird chirping])
        is_sound_effect = text.startswith("[") and text.endswith("]")
        
        scene_audio_path = os.path.join(temp_audio_dir, f"scene_{key}.mp3")
        
        if is_sound_effect:
            sound_name_clean = text[1:-1].strip().lower().replace(" ", "_")
            # Search for a matching audio file
            sound_file = find_audio_file(output_dir, key, sound_name_clean)
            
            if sound_file:
                print(f"  -> Found sound effect file: '{os.path.basename(sound_file)}'")
                clip = AudioFileClip(sound_file)
                duration = clip.duration
                audio_clips.append(clip)
            else:
                # Fallback: silent audio for 3.0 seconds
                print(f"  -> Sound file for '{text}' not found. Falling back to 3 seconds of silence.")
                # We can generate silence by creating an empty audio file or silent moviepy clip
                # Write an empty WAV file containing silence
                import wave
                silence_wav_path = os.path.join(temp_audio_dir, f"silence_{key}.wav")
                with wave.open(silence_wav_path, "wb") as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(44100)
                    wav_file.writeframes(b'\x00' * 44100 * 2 * 3) # 3 seconds
                clip = AudioFileClip(silence_wav_path)
                duration = 3.0
                audio_clips.append(clip)
                
            # Add a single timestamp entry for the sound effect so it shows the subtitle
            global_words.append({
                "word": text,
                "start": accum_duration,
                "end": accum_duration + duration,
                "step_key": key
            })
            
        else:
            # Standard Text-To-Speech
            scene_words = await synthesize_tts(text, voice, scene_audio_path)
            clip = AudioFileClip(scene_audio_path)
            duration = clip.duration
            audio_clips.append(clip)
            
            # Save timestamps
            for w in scene_words:
                global_words.append({
                    "word": w["word"],
                    "start": accum_duration + w["start"],
                    "end": accum_duration + w["end"],
                    "step_key": key
                })
            
        # Construct foreground/background composite image
        img_path = os.path.join(output_dir, img_pattern) if img_pattern else None
        frame_pil = render_vertical_frame(img_path, width, height)
        frame_np = np.array(frame_pil)
        
        img_clip = ImageClip(frame_np).set_duration(duration).set_start(accum_duration)
        image_clips.append(img_clip)
        
        accum_duration += duration

    # Combine audio
    print("\n=== Stage 2: Concatenating Audio Track ===")
    voiceover_path = os.path.join(temp_audio_dir, "combined_voiceover.mp3")
    combined_audio = concatenate_audioclips(audio_clips)
    combined_audio.write_audiofile(voiceover_path, logger=None)
    combined_audio.close()
    for clip in audio_clips:
        clip.close()
        
    final_audio = AudioFileClip(voiceover_path)
    base_video = concatenate_videoclips(image_clips, method="compose")
    base_video = base_video.set_audio(final_audio)

    # Subtitle cards generation
    print("\n=== Stage 3: Generating Highlighted Subtitle Cards ===")
    
    # We group words, but handle sound effects separately so they stay as a single card
    cards = []
    current_card = []
    for w in global_words:
        # If it's a sound effect, place it in its own card
        if w["word"].startswith("[") and w["word"].endswith("]"):
            if current_card:
                cards.append(current_card)
                current_card = []
            cards.append([w])
            continue
            
        if not current_card:
            current_card.append(w)
            continue
            
        # Don't group sound effects with regular words
        prev_w = current_card[-1]
        if prev_w["word"].startswith("[") and prev_w["word"].endswith("]"):
            cards.append(current_card)
            current_card = [w]
            continue
            
        gap = w["start"] - prev_w["end"]
        should_split = len(current_card) >= 3 or gap > 1.0 or any(prev_w["word"].endswith(c) for c in [".", "?", "!", ";"])
        if should_split:
            cards.append(current_card)
            current_card = [w]
        else:
            current_card.append(w)
    if current_card:
        cards.append(current_card)
        
    subtitle_clips = []
    for card in cards:
        card_words = [w["word"] for w in card]
        step_key = card[0]["step_key"]
        is_text_only = (step_key in ["8", "14"])
        
        # If it's a sound effect card
        if len(card) == 1 and card[0]["word"].startswith("[") and card[0]["word"].endswith("]"):
            start_time = card[0]["start"]
            end_time = card[0]["end"]
            duration = end_time - start_time
            if duration <= 0:
                continue
            # Render sound effect centered in the screen
            frame = render_subtitle_frame(card_words, 0, width, height, text_only_slide=True)
            frame_np = np.array(frame)
            sub_clip = ImageClip(frame_np).set_start(start_time).set_duration(duration)
            subtitle_clips.append(sub_clip)
        else:
            for i, word_info in enumerate(card):
                start_time = word_info["start"]
                end_time = card[i+1]["start"] if i < len(card) - 1 else word_info["end"]
                
                duration = end_time - start_time
                if duration <= 0:
                    continue
                    
                frame = render_subtitle_frame(card_words, i, width, height, text_only_slide=is_text_only)
                frame_np = np.array(frame)
                
                sub_clip = ImageClip(frame_np).set_start(start_time).set_duration(duration)
                subtitle_clips.append(sub_clip)

    print("\n=== Stage 4: Rendering Final Short-Form Video ===")
    final_video = CompositeVideoClip([base_video] + subtitle_clips)
    final_video.write_videofile(
        final_output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        logger=None
    )
    
    # Cleanup handles and temp files
    final_video.close()
    base_video.close()
    final_audio.close()
    for c in subtitle_clips:
        c.close()
    for c in image_clips:
        c.close()
        
    # Clean temporary files
    for step in STEPS:
        temp_path = os.path.join(temp_audio_dir, f"scene_{step['key']}.mp3")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        silence_path = os.path.join(temp_audio_dir, f"silence_{step['key']}.wav")
        if os.path.exists(silence_path):
            os.remove(silence_path)
            
    if os.path.exists(voiceover_path):
        os.remove(voiceover_path)
    os.rmdir(temp_audio_dir)
    
    print(f"\nSuccess! Short-form video saved to: '{final_output_path}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Golfswing AI Video Generator")
    parser.add_argument("--preview", action="store_true", help="Generate speech previews for available voices")
    parser.add_argument("--voice", type=str, default="en-US-SteffanNeural", help="TTS voice key to use")
    args = parser.parse_args()
    
    if args.preview:
        asyncio.run(test_voices_preview())
    else:
        asyncio.run(generate_video(args.voice))
