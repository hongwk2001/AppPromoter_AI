import os
import sys
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(os.path.dirname(BASE_DIR), "notes")
os.makedirs(NOTES_DIR, exist_ok=True)

def calculate_runtime_price(audio_files):
    """Calculates price_usd based on total runtime: Hours = Dollars, Minutes = Cents (e.g. 5h 53m -> $5.53)"""
    total_sec = 0
    for f in audio_files:
        if os.path.exists(f):
            try:
                res = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', f], capture_output=True, text=True)
                dur = float(json.loads(res.stdout).get('format', {}).get('duration', 0))
                total_sec += dur
            except Exception:
                pass
    hrs = int(total_sec // 3600)
    mins = int((total_sec % 3600) // 60)
    return f"{hrs}.{mins:02d}"

def prepare_blue_castle_metadata():
    audio_dir = r"C:\git_repo\TKprof_book\books\blue_castle\final_audio_ko_ready"
    cover_path = r"C:\git_repo\TKprof_book\books\blue_castle\cover_ko_illustrated_2400.jpg"

    if not os.path.exists(cover_path):
        print("Generating 2400x2400 illustrated audiobook cover image...")
        from create_illustrated_audiobook_cover import generate_illustrated_cover
        generate_illustrated_cover()

    if not os.path.exists(audio_dir) or len(os.listdir(audio_dir)) == 0:
        print(f"Directory {audio_dir} not ready. Running split_large_tracks.py...")
        from split_large_tracks import prepare_ready_tracks
        prepare_ready_tracks()

    # List all audio files
    mp3s = sorted([f for f in os.listdir(audio_dir) if f.endswith(".mp3")])
    intro = [f for f in mp3s if "intro" in f]
    closing = [f for f in mp3s if "closing" in f]
    chapters = [f for f in mp3s if f.startswith("final_track_") and "intro" not in f]

    audio_files = [os.path.join(audio_dir, f) for f in intro + chapters + closing]

    payload = {
        "book_id": "blue_castle",
        "language_code": "ko",
        "language_name": "Korean",
        "title": "블루 캐슬 (The Blue Castle) - 오디오북",
        "subtitle": "L. M. 몽고메리가 선사하는 가슴 설레는 고전 로맨스 성장 소설",
        "author_first": "L. M.",
        "author_last": "몽고메리",
        "narrator_first": "TKPROF",
        "narrator_last": "AI",
        "is_ai_voice": True,
        "ai_engine": "Microsoft",
        "is_ai_text": True,
        "is_series": False,
        "series_name": "",
        "series_number": "",
        "has_publisher": True,
        "publisher": "TKPROF LLC",
        "description": "루시 모드 몽고메리(L. M. Montgomery)의 숨겨진 대표작이자 성인 독자를 위한 클래식 로맨스 『블루 캐슬 (The Blue Castle)』 한국어 완역본.\n\n답답하고 억압적인 가부장적 가문에서 29살 노처녀로 구박받던 발랜시 스털링. 어느 날 시한부 1년 선고를 받은 그녀는 집안의 족쇄를 끊어버리고 세상에서 가장 통쾌하고 아름다운 반항을 시작합니다. 잃을 것이 없어진 여자의 시원한 사이다 행보, 캐나다 머스코카 숲속 오두막에서 펼쳐지는 힐링 라이프, 그리고 미스터리한 남자 바니 스네이스와의 계약 결혼!\n\n오늘날 현대 로맨스 판타지의 원형이자, 지친 독자들에게 완벽한 힐링과 감동을 선사하는 고전 로맨스 소설입니다.",
        "categories": [
            "FICTION / Classics",
            "FICTION / Romance / General"
        ],
        "price_usd": "9.99",
        "cover_path": cover_path,
        "audio_dir": audio_dir,
        "opening_track": os.path.join(audio_dir, "final_track_00_intro.mp3"),
        "closing_track": os.path.join(audio_dir, "closing.mp3"),
        "sample_track": os.path.join(audio_dir, "sample_retail.mp3"),
        "audio_tracks": audio_files
    }

    out_file = os.path.join(NOTES_DIR, "ar_payload_blue_castle_ko.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"✅ Ready metadata payload ({len(audio_files)} tracks) saved to {out_file}")
    return payload

def prepare_beowulf_metadata():
    audio_dir = r"C:\git_repo\TKprof_book\books\beowulf\final_audio_ko"
    cover_path = r"C:\git_repo\TKprof_book\books\beowulf\beowulfcover2400_ko.jpg"

    mp3s = sorted([f for f in os.listdir(audio_dir) if f.endswith(".mp3")])
    chapters = [f for f in mp3s if f.startswith("final_track_") and "intro" not in f]

    audio_files = [os.path.join(audio_dir, f) for f in chapters]

    payload = {
        "book_id": "beowulf",
        "language_code": "ko",
        "language_name": "Korean",
        "title": "베오울프: 스펙터클 현대 한국어판 (Beowulf)",
        "subtitle": "Beowulf: Modern Korean Edition",
        "author_first": "작자",
        "author_last": "미상",
        "narrator_first": "TKPROF",
        "narrator_last": "AI",
        "is_ai_voice": True,
        "ai_engine": "Microsoft",
        "is_ai_text": True,
        "is_series": False,
        "series_name": "",
        "series_number": "",
        "has_publisher": True,
        "publisher": "TKPROF LLC",
        "description": "★ 영문학 최고의 고전 서사시, 압도적 몰입감의 현대 웹소설 스타일로 재탄생! ★\n\n괴물 그렌델의 피비린내 나는 습격, 핏빛 늪속 수중 굴에서의 사투, 그리고 화염을 뿜어내는 마지막 거룡과의 멸망전!\n800년 역사를 가진 인류 위대한 고전 《베오울프》가 현대 판타지 웹소설의 스펙터클한 문법과 속도감 넘치는 현대 한국어로 새롭게 찾아왔습니다.\n\n■ 작품 특징\n- 속도감 넘치는 웹소설 스타일: 지루하고 딱딱한 고어 직역을 벗어나, 액션과 긴장감이 살아 숨쉬는 현대적 문체 적용.\n- 웅장한 전설의 완성: 헤오로트 대연회장의 비극부터 영웅의 마지막 용 사냥까지 숨막히는 서사를 한 권에 담았습니다.\n- 고품질 일러스트 탑재: 괴물 그렌델, 물마녀, 거룡과의 전투 장면을 담은 고해상도 일러스트레이션 수록.\n\n■ 줄거리\n6세기 스칸디나비아, 덴마크 왕국의 대연회장 헤오로트는 매일 밤 괴물 그렌델의 잔혹한 학살로 피로 물든다.\n절망에 빠진 왕국을 구하기 위해 바다를 건너온 게아트족의 영웅 베오울프.\n맨손으로 괴물의 팔을 뽑아버린 첫 승리 뒤에는 더 끔찍한 그렌델의 어미와 사나운 화룡과의 사투가 그를 기다리고 있는데...\n\n판타지 로판, 무협, 웹소설을 즐기는 현대 독자라면 반드시 읽어야 할 고전 영웅 서사의 원점!",
        "categories": [
            "FICTION / Classics",
            "FICTION / Action & Adventure"
        ],
        "keywords": "베오울프, 오디오북, 고전소설, 웹소설, 판타지, 영웅서사시, 그렌델, Beowulf, audiobook",
        "price_usd": "9.99",
        "cover_path": cover_path,
        "audio_dir": audio_dir,
        "opening_track": os.path.join(audio_dir, "final_track_00_intro.mp3"),
        "closing_track": os.path.join(audio_dir, "closing.mp3"),
        "sample_track": os.path.join(audio_dir, "sample.mp3"),
        "audio_tracks": audio_files
    }

    out_file = os.path.join(NOTES_DIR, "ar_payload_beowulf_ko.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"✅ Ready metadata payload ({len(audio_files)} tracks) saved to {out_file}")
    return payload

def prepare_beowulf_en_metadata():
    audio_dir = r"C:\git_repo\TKprof_book\books\beowulf\final_audio"
    cover_path = r"C:\git_repo\TKprof_book\books\beowulf\beowulf_cover_en.jpg"

    mp3s = sorted([f for f in os.listdir(audio_dir) if f.endswith(".mp3")])
    intro = [f for f in mp3s if "intro" in f]
    closing = [f for f in mp3s if "closing" in f]
    chapters = [f for f in mp3s if f.startswith("final_track_") and "intro" not in f]

    audio_files = [os.path.join(audio_dir, f) for f in intro + chapters + closing]

    description_text = (
        "Welcome to one of the most important and foundational works of English literature. "
        "Beowulf is an epic poem composed in Old English, consisting of 3,182 alliterative lines. "
        "The story was originally passed down orally by scops in Anglo-Saxon England and survives in a single medieval manuscript (Nowell Codex). "
        "Set in 6th-century Scandinavia, it follows the heroic exploits of Beowulf, champion of the Geats, as he faces the demonic monster Grendel, "
        "Grendel's vengeful mother, and a fiery dragon. This edition presents the epic poem adapted into a modern, fast-paced prose narrative."
    )

    payload = {
        "book_id": "beowulf",
        "language_code": "en",
        "language_name": "English",
        "title": "Beowulf: Spectacular Modern English Edition (Audiobook)",
        "subtitle": "Modern English Edition Audiobook",
        "author_first": "Anonymous",
        "author_last": "",
        "narrator_first": "TKPROF",
        "narrator_last": "LLC",
        "is_ai_voice": True,
        "ai_engine": "Microsoft",
        "is_ai_text": True,
        "is_series": False,
        "series_name": "",
        "series_number": "",
        "has_publisher": True,
        "publisher": "TKPROF LLC",
        "description": description_text,
        "categories": [
            "FICTION / Classics",
            "FICTION / Action & Adventure"
        ],
        "keywords": "Beowulf;audiobook;classics;epic poem;grendel;monsters;heroic fantasy;dark ages",
        "price_usd": "9.99",
        "cover_path": cover_path,
        "audio_dir": audio_dir,
        "opening_track": os.path.join(audio_dir, "final_track_00_intro.mp3"),
        "closing_track": os.path.join(audio_dir, "closing.mp3"),
        "sample_track": os.path.join(audio_dir, "final_track_00.mp3"),
        "audio_tracks": audio_files
    }

    out_file = os.path.join(NOTES_DIR, "ar_payload_beowulf_en.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"✅ Ready metadata payload ({len(audio_files)} tracks) saved to {out_file}")
    return payload

def prepare_secret_garden_en_metadata():
    audio_dir = r"C:\git_repo\TKprof_book\books\secret_garden\final_audio"
    cover_path = r"C:\git_repo\TKprof_book\books\secret_garden\cover_en_2400.jpg"

    mp3s = sorted([f for f in os.listdir(audio_dir) if f.endswith(".mp3")])
    chapters = [f for f in mp3s if f.startswith("final_track_") and "intro" not in f]

    audio_files = [os.path.join(audio_dir, f) for f in chapters]

    description_text = (
        "Mary Lennox is a sour, unloved, and neglected child born in India. When a cholera outbreak leaves her orphaned, "
        "she is sent to live with her reclusive uncle in the gloomy Misselthwaite Manor on the Yorkshire moors.\n\n"
        "Lonely and angry, Mary has nothing to do but wander the corridors and gardens of the estate. One day, she discovers a key "
        "to a secret garden that has been locked for ten years. As she begins to care for the neglected garden with the help of Dickon, "
        "a local nature-loving boy, and Colin, her sickly, bedridden cousin, she witnesses a magical transformation. In restoring the garden, "
        "they restore themselves—finding health, friendship, and the true power of hope.\n\n"
        "The Secret Garden is Frances Hodgson Burnett's timeless masterpiece of healing and growth. This special edition has been "
        "carefully modernized for casual readers and English language learners."
    )

    payload = {
        "book_id": "secret_garden",
        "language_code": "en",
        "language_name": "English",
        "title": "The Secret Garden: Modernized Classic Edition",
        "subtitle": "A Modernized Classic for Casual Readers and ESL Learners",
        "author_first": "Frances Hodgson",
        "author_last": "Burnett",
        "narrator_first": "TKPROF",
        "narrator_last": "AI",
        "is_ai_voice": True,
        "ai_engine": "Microsoft",
        "is_ai_text": True,
        "is_series": False,
        "series_name": "",
        "series_number": "",
        "has_publisher": True,
        "publisher": "TKPROF LLC",
        "description": description_text,
        "categories": [
            "FICTION / Classics",
            "FICTION / Action & Adventure"
        ],
        "keywords": "The Secret Garden, Frances Hodgson Burnett, classic literature, audiobooks, healing fiction, coming of age, classic novel",
        "price_usd": "14.99",
        "cover_path": cover_path,
        "audio_dir": audio_dir,
        "opening_track": os.path.join(audio_dir, "final_track_00_intro.mp3"),
        "closing_track": os.path.join(audio_dir, "closing.mp3"),
        "sample_track": os.path.join(audio_dir, "sample.mp3"),
        "audio_tracks": audio_files
    }

    out_file = os.path.join(NOTES_DIR, "ar_payload_secret_garden_en.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"✅ Ready metadata payload ({len(audio_files)} tracks) saved to {out_file}")
    return payload

def prepare_dracula_en_metadata():
    """English-only resubmission. Replaces the bilingual edition rejected 2026-08-17
    for narration quality. Source of truth: books/dracula/english_audiobook_metadata.md
    and books/dracula/google_play_audiobook_metadata.json."""
    # final_audio_en held the build AR rejected 2026-09-14 and has been deleted.
    # final_audio_en_v2 is the 2026-09-15 rebuild: two voices, 154 wpm, merged
    # units, no steady-tone artefacts. 20/20 on ar_submission_audit.py.
    audio_dir = r"C:\git_repo\TKprof_book\books\dracula\final_audio_en_v2"
    # AR requires an alphanumeric cover filename (no symbols or spaces).
    cover_path = r"C:\git_repo\TKprof_book\books\dracula\cover_en_2400_v2.jpg"

    mp3s = sorted([f for f in os.listdir(audio_dir) if f.endswith(".mp3")])
    chapters = [f for f in mp3s if f.startswith("dracula_ch_") and f.endswith("_en.mp3")]

    audio_files = [os.path.join(audio_dir, f) for f in chapters]

    description_text = (
        "Bram Stoker's 1897 masterpiece of Gothic horror, presented in full.\n\n"
        "Told through the journals, letters and diaries of those who hunted him, Dracula follows "
        "solicitor Jonathan Harker from a remote Transylvanian castle to the streets of London, "
        "where Mina Harker, Dr. John Seward and Professor Van Helsing race to stop a predator who "
        "has crossed the sea to find them.\n\n"
        "This unabridged recording uses two narrators, one voice for the men's journals and "
        "one for the women's letters, so the novel's overlapping accounts stay clear as the "
        "chorus of testimony Stoker intended."
    )

    payload = {
        "book_id": "dracula",
        "language_code": "en",
        "language_name": "English",
        "title": "Dracula",
        "subtitle": "Bram Stoker's Gothic Classic",
        "author_first": "Bram",
        "author_last": "Stoker",
        # Two voices since the recast: bm_fable reads 72.6%, af_bella 27.4%.
        # The cover art was re-lettered to match on 2026-09-15.
        "narrators": [["Fable", "AI"], ["Bella", "AI"]],
        "narrator_first": "Fable",      # fallback for any single-narrator path
        "narrator_last": "AI",
        "is_ai_voice": True,
        "ai_engine": "Kokoro-82M",
        "is_ai_text": False,
        "is_series": False,
        "series_name": "",
        "series_number": "",
        "has_publisher": True,
        "publisher": "TKPROF LLC",
        "description": description_text,
        "categories": [
            "FICTION / Classics",
            "FICTION / Horror",
            "FICTION / Gothic"
        ],
        "keywords": "Dracula, Bram Stoker, gothic horror, vampire, classic literature, Van Helsing, audiobook",
        "price_usd": "14.99",
        "cover_path": cover_path,
        "audio_dir": audio_dir,
        "opening_track": os.path.join(audio_dir, "opening_credits.mp3"),
        "closing_track": os.path.join(audio_dir, "closing_credits.mp3"),
        "sample_track": os.path.join(audio_dir, "dracula_retail_sample.mp3"),
        "audio_tracks": audio_files
    }

    out_file = os.path.join(NOTES_DIR, "ar_payload_dracula_en.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"✅ Ready metadata payload ({len(audio_files)} tracks) saved to {out_file}")
    return payload

def prepare_odyssey_en_metadata():
    audio_dir = r"C:\git_repo\TKprof_book\books\odyssey\final_audio"
    cover_path = r"C:\git_repo\TKprof_book\books\odyssey\cover_en_2400.jpg"

    audio_files = [os.path.join(audio_dir, f"final_track_{i:02d}.mp3") for i in range(1, 25) if os.path.exists(os.path.join(audio_dir, f"final_track_{i:02d}.mp3"))]

    description_text = (
        "After the Trojan War, the wily hero Odysseus sets sail for his island home of Ithaca, where his beloved wife Penelope and son Telemachus await. "
        "But his journey is anything but smooth. Enraged when Odysseus blinds his son, the Cyclops, the sea god Poseidon curses him with ten years of "
        "relentless trials and storms, determined to prevent his return.\n\n"
        "From the one-eyed giant Polyphemus and the Sirens whose enchanting songs lure sailors to their doom, to the sorceress Circe who turns men into swine, "
        "and the monstrous Scylla and Charybdis, Odysseus faces a parade of mythical beasts and mortal dangers.\n\n"
        "This modern edition reimagines Homer's foundational epic in a dynamic prose style, making it vivid, accessible, and thrilling for modern listeners and classic fantasy enthusiasts alike."
    )

    payload = {
        "book_id": "odyssey",
        "language_code": "en",
        "language_name": "English",
        "title": "The Odyssey: Modernized Classic Edition",
        "subtitle": "Modernized Epic Adventure Audiobook",
        "author_first": "Homer",
        "author_last": "",
        "narrator_first": "TKPROF",
        "narrator_last": "AI",
        "is_ai_voice": True,
        "ai_engine": "Microsoft",
        "is_ai_text": True,
        "is_series": False,
        "series_name": "",
        "series_number": "",
        "has_publisher": True,
        "publisher": "TKPROF LLC",
        "description": description_text,
        "categories": [
            "FICTION / Classics",
            "FICTION / Action & Adventure"
        ],
        "keywords": "The Odyssey, Homer, Greek mythology, classic literature, epic poem, audiobooks, ancient greece, Ulysses",
        "price_usd": "14.99",
        "cover_path": cover_path,
        "audio_dir": audio_dir,
        "opening_track": os.path.join(audio_dir, "final_track_01.mp3"),
        "closing_track": os.path.join(audio_dir, "final_track_24.mp3"),
        "sample_track": os.path.join(audio_dir, "sample.mp3"),
        "audio_tracks": audio_files
    }

    out_file = os.path.join(NOTES_DIR, "ar_payload_odyssey_en.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"✅ Ready metadata payload ({len(audio_files)} tracks) saved to {out_file}")
    return payload

def prepare_odyssey_ko_metadata():
    audio_dir = r"C:\git_repo\TKprof_book\books\odyssey\final_audio"
    cover_path = r"C:\git_repo\TKprof_book\books\odyssey\cover_ko_2400.jpg"

    audio_files = [os.path.join(audio_dir, f"final_track_ko_{i:02d}.mp3") for i in range(1, 25) if os.path.exists(os.path.join(audio_dir, f"final_track_ko_{i:02d}.mp3"))]

    description_text = (
        "★ 트로이의 함락 후, 고향으로 돌아가기 위한 영웅 오디세우스의 10년간의 위대한 여정이 펼쳐진다! ★\n\n"
        "지략이 뛰어난 영웅 오디세우스는 10년간의 트로이 전쟁이 끝난 후 사랑하는 아내 페넬로페와 아들 텔레마코스가 기다리는 고향 이타카 섬으로 향합니다. "
        "하지만 바다의 신 포세이돈의 분노를 사 드넓은 지중해를 표류하며 온갖 시련을 겪게 됩니다. 외눈박이 거인 폴리페모스, 목소리로 선원을 유혹하는 사이렌, "
        "마녀 키르케와 바다 괴물 스킬라까지, 신화 속 존재들과 마주하는 오디세우스의 처절한 모험담!\n\n"
        "그동안 고향 이타카에서는 오디세우스가 죽었다고 생각한 수많은 구혼자들이 왕비 페넬로페를 차지하고 왕국을 빼앗기 위해 왕궁의 재산을 낭비하며 난동을 부립니다. "
        "아들 텔레마코스는 아버지를 찾기 위해 먼 항해를 떠나고, 페넬로페는 뛰어난 지혜로 구혼자들을 따돌립니다. 마침내 돌아온 오디세우스와 그를 돕는 전쟁의 여신 아테나가 함께 준비하는 장엄한 복수극!\n\n"
        "본 현대어 개정판은 고전 문학 특유의 딱딱함과 번역투를 완전히 탈피하여 청소년부터 일반 독자까지 누구나 재미있게 감상할 수 있도록 흥미진진한 판타지 모험 소설 형식으로 다듬었습니다."
    )

    payload = {
        "book_id": "odyssey",
        "language_code": "ko",
        "language_name": "Korean",
        "title": "오디세이아: 스펙터클 현대 한국어판 (Odysseia)",
        "subtitle": "Odysseia: Modern Korean Edition",
        "author_first": "호메로스",
        "author_last": "",
        "narrator_first": "TKPROF",
        "narrator_last": "AI",
        "is_ai_voice": True,
        "ai_engine": "Microsoft",
        "is_ai_text": True,
        "is_series": False,
        "series_name": "",
        "series_number": "",
        "has_publisher": True,
        "publisher": "TKPROF LLC",
        "description": description_text,
        "categories": [
            "FICTION / Classics",
            "FICTION / Action & Adventure"
        ],
        "keywords": "오디세이아; 호메로스; 그리스 신화; 고전문학; 영웅담; 모험 소설; Odysseia; Homer",
        "price_usd": "14.99",
        "cover_path": cover_path,
        "audio_dir": audio_dir,
        "opening_track": os.path.join(audio_dir, "final_track_ko_01.mp3"),
        "closing_track": os.path.join(audio_dir, "final_track_ko_24.mp3"),
        "sample_track": os.path.join(audio_dir, "sample.mp3"),
        "audio_tracks": audio_files
    }

    out_file = os.path.join(NOTES_DIR, "ar_payload_odyssey_ko.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"✅ Ready metadata payload ({len(audio_files)} tracks) saved to {out_file}")
    return payload

def prepare_gilgamesh_metadata():
    audio_dir = r"C:\git_repo\TKprof_book\books\gilgamesh\audio"
    cover_path = r"C:\git_repo\TKprof_book\books\gilgamesh\cover_ko_2400.jpg"

    mp3s = sorted([f for f in os.listdir(audio_dir) if f.endswith(".mp3") and f.endswith("_ko.mp3") and "podcast" not in f and "retail_sample" not in f])
    intro = [f for f in mp3s if "opening" in f]
    closing = [f for f in mp3s if "ending" in f]
    chapters = [f for f in mp3s if f.startswith("ch_")]

    audio_files = [os.path.join(audio_dir, f) for f in intro + chapters + closing]

    description_text = (
        "★ 인류 문학사 최초의 위대한 대서사시 《길가메시 서사시》, 4천 년의 시공을 넘어 현대 오디오북으로 완전 재탄생! ★\n\n"
        "우루크 도시의 오만한 영웅 왕 길가메시와 야성의 동반자 엔키두의 맹세, 괴물 훔바바와의 죽음을 무릅쓴 사투, "
        "그리고 죽음의 공포를 넘어 영생의 비밀을 찾아 떠나는 장대한 모험!\n\n"
        "■ 작품 특징\n"
        "- 메소포타미아 점토판 고전 서사시를 현대 구어체로 완판 재번역\n"
        "- 전 6장의 스펙터클한 액션과 입체적 내레이션 연출\n"
        "- 인류 최초의 위대한 유산과 영원한 우정을 담은 명작\n\n"
        "저작권 안내: 한국어 번역 및 출판 TKPROF LLC."
    )

    payload = {
        "book_id": "gilgamesh",
        "language_code": "ko",
        "language_name": "Korean",
        "title": "길가메시 서사시: 스펙터클 현대 한국어판 (The Epic of Gilgamesh)",
        "subtitle": "인류 최초의 위대한 고전 서사시 오디오북",
        "author_first": "작자",
        "author_last": "미상",
        "narrator_first": "TKPROF",
        "narrator_last": "LLC",
        "is_ai_voice": True,
        "ai_engine": "Microsoft",
        "is_ai_text": True,
        "is_series": False,
        "series_name": "",
        "series_number": "",
        "has_publisher": True,
        "publisher": "TKPROF LLC",
        "description": description_text,
        "categories": [
            "FICTION / Classics",
            "FICTION / Action & Adventure"
        ],
        "keywords": "길가메시;서사시;메소포타미아;고전소설;오디오북;엔키두;Gilgamesh;audiobook",
        "price_usd": "9.99",
        "cover_path": cover_path,
        "audio_dir": audio_dir,
        "opening_track": os.path.join(audio_dir, "opening_credits_ko.mp3"),
        "closing_track": os.path.join(audio_dir, "ending_credits_ko.mp3"),
        "sample_track": os.path.join(audio_dir, "retail_sample_ko.mp3"),
        "audio_tracks": audio_files
    }

    out_file = os.path.join(NOTES_DIR, "ar_payload_gilgamesh_ko.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"✅ Ready metadata payload ({len(audio_files)} tracks) saved to {out_file}")
    return payload

def prepare_gilgamesh_en_metadata():
    audio_dir = r"C:\git_repo\TKprof_book\books\gilgamesh\audio"
    cover_path = r"C:\git_repo\TKprof_book\books\gilgamesh\cover_en_2400.jpg"

    if not os.path.exists(cover_path):
        from create_audiobook_square_cover_en import create_square_english_cover
        create_square_english_cover()

    mp3s = sorted([f for f in os.listdir(audio_dir) if f.endswith(".mp3") and f.endswith("_en.mp3") and "podcast" not in f and "retail_sample" not in f])
    intro = [f for f in mp3s if "opening" in f]
    closing = [f for f in mp3s if "ending" in f]
    chapters = [f for f in mp3s if f.startswith("ch_")]

    audio_files = [os.path.join(audio_dir, f) for f in intro + chapters + closing]

    overview_path = r"C:\git_repo\TKprof_book\books\gilgamesh\overview_en.txt"
    if os.path.exists(overview_path):
        with open(overview_path, "r", encoding="utf-8") as f:
            description_text = f.read()
    else:
        description_text = (
            "★ The Oldest Story in Human History Reborn into a Modern Fantasy Epic ★\n\n"
            "Over 4,000 years ago in ancient Mesopotamia, the legend of King Gilgamesh was carved onto clay tablets. "
            "Today, humanity's first epic hero returns in a fast-paced, modern narrative optimized for contemporary readers and listening flow.\n\n"
            "Gilgamesh, two-thirds god and one-third man, rules Uruk with an iron fist until the gods forge Enkidu. "
            "Experience the epic bonds of brotherhood, the battle against Humbaba, the Bull of Heaven, and the secret of eternal life."
        )

    payload = {
        "book_id": "gilgamesh",
        "language_code": "en",
        "language_name": "English",
        "title": "The Epic of Gilgamesh: Modern English Edition",
        "subtitle": "Modern English Edition Audiobook",
        "author_first": "Anonymous",
        "author_last": "",
        "narrator_first": "TKPROF",
        "narrator_last": "LLC",
        "is_ai_voice": True,
        "ai_engine": "Microsoft",
        "is_ai_text": True,
        "is_series": False,
        "series_name": "",
        "series_number": "",
        "has_publisher": True,
        "publisher": "TKPROF LLC",
        "description": description_text,
        "categories": [
            "FICTION / Classics",
            "FICTION / Action & Adventure"
        ],
        "keywords": "Gilgamesh;epic poem;mesopotamia;enkidu;humbaba;classics;audiobook;heroic fantasy",
        "price_usd": "9.99",
        "cover_path": cover_path,
        "audio_dir": audio_dir,
        "opening_track": os.path.join(audio_dir, "opening_credits_en.mp3"),
        "closing_track": os.path.join(audio_dir, "ending_credits_en.mp3"),
        "sample_track": os.path.join(audio_dir, "retail_sample_en.mp3"),
        "audio_tracks": audio_files
    }

    out_file = os.path.join(NOTES_DIR, "ar_payload_gilgamesh_en.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"✅ Ready metadata payload ({len(audio_files)} tracks) saved to {out_file}")
    return payload

def prepare_richest_man_in_babylon_metadata():
    ready_dir = r"C:\git_repo\TKprof_book\books\richest_man_in_babylon\final_audio_ar_ready"
    raw_dir = r"C:\git_repo\TKprof_book\books\richest_man_in_babylon\final_audio"
    audio_dir = ready_dir if (os.path.exists(ready_dir) and len(os.listdir(ready_dir)) > 0) else raw_dir
    cover_path = r"C:\git_repo\TKprof_book\books\richest_man_in_babylon\cover_en_2400.jpg"

    if not os.path.exists(cover_path):
        from create_audiobook_square_cover_en import create_square_english_cover
        create_square_english_cover()

    mp3s = sorted([f for f in os.listdir(audio_dir) if f.endswith(".mp3")])
    intro = [f for f in mp3s if "intro" in f]
    closing = [f for f in mp3s if "copyright" in f]
    chapters = [f for f in mp3s if f.startswith("final_ch_")]

    audio_files = [os.path.join(audio_dir, f) for f in intro + chapters + closing]

    intro_path = r"C:\git_repo\TKprof_book\books\richest_man_in_babylon\introduction_en.txt"
    if os.path.exists(intro_path):
        with open(intro_path, "r", encoding="utf-8") as f:
            description_text = f.read()
    else:
        description_text = (
            "★ The Timeless Personal Finance Classic Reborn for Modern Readers ★\n\n"
            "Originally published in 1926 by George S. Clason, this classic collection of Babylonian parables "
            "contains the fundamental secrets of financial independence, wealth accumulation, and smart investing.\n\n"
            "■ ABOUT THIS EDITION\n"
            "- Modernized Narrative Flow: Clear, vivid prose optimized for listening flow while preserving the classic wisdom.\n"
            "- Key Lessons: Learn the 7 Cures for a Lean Purse, the 5 Laws of Gold, and the proven rules for building lasting financial security."
        )

    payload = {
        "book_id": "richest_man_in_babylon",
        "language_code": "en",
        "language_name": "English",
        "title": "The Richest Man in Babylon: Modern English Edition",
        "subtitle": "The Success Secrets of the Ancients - Personal Finance Classic",
        "author_first": "George S.",
        "author_last": "Clason",
        "narrator_first": "TKPROF",
        "narrator_last": "LLC",
        "is_ai_voice": True,
        "ai_engine": "Microsoft",
        "is_ai_text": True,
        "is_series": False,
        "series_name": "",
        "series_number": "",
        "has_publisher": True,
        "publisher": "TKPROF LLC",
        "description": description_text,
        "categories": [
            "BUSINESS & ECONOMICS / Personal Finance / General",
            "FICTION / Classics"
        ],
        "keywords": "Richest Man in Babylon; personal finance; George Clason; money; investing; audiobook; wealth",
        "price_usd": "9.99",
        "cover_path": cover_path,
        "audio_dir": audio_dir,
        "opening_track": os.path.join(audio_dir, "final_intro.mp3"),
        "closing_track": os.path.join(audio_dir, "final_copyright.mp3"),
        "sample_track": os.path.join(audio_dir, "final_ch_00.mp3"),
        "audio_tracks": audio_files
    }

    out_file = os.path.join(NOTES_DIR, "ar_payload_richest_man_in_babylon_en.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"✅ Ready metadata payload ({len(audio_files)} tracks) saved to {out_file}")
    return payload

def prepare_scaramouche_book1_ko_metadata():
    audio_dir = r"C:\git_repo\TKprof_book\books\scaramouche\final_audio_book1"
    cover_path = r"C:\git_repo\TKprof_book\books\scaramouche\cover_b1_ko_2400.jpg"

    audio_files = [os.path.join(audio_dir, f"final_track_{i:02d}_ko.mp3") for i in range(1, 10) if os.path.exists(os.path.join(audio_dir, f"final_track_{i:02d}_ko.mp3"))]

    description_text = (
        "★ 프랑스 혁명의 불길 속에서 탄생한 비극과 웃음의 모험 대서사시! ★\n\n"
        "라파엘 사바티니(Rafael Sabatini)의 세계적인 거장 역사 모험 소설 《스카라무슈》 제1부: 법복 (The Robe) 편입니다.\n\n"
        "18세기 프랑스 혁명 직전, 차가운 이성과 비범한 기지를 지닌 법학도 앙드레 루이 모로. "
        "절친한 친구 필립 드 빌모랭이 오만한 귀족 라 투르 다르지르 후작의 검에 무참히 살해당하자, "
        "앙드레 루이는 세상을 향한 복수와 정의를 맹세하며 혁명의 불길 속으로 뛰어듭니다."
    )

    payload = {
        "book_id": "scaramouche_book1",
        "language_code": "ko",
        "language_name": "Korean",
        "title": "스카라무슈 1: 법의 옷 (Scaramouche)",
        "subtitle": "Scaramouche: Book 1 - The Robe",
        "author_first": "라파엘",
        "author_last": "사바티니",
        "narrator_first": "TKPROF",
        "narrator_last": "AI",
        "is_ai_voice": True,
        "ai_engine": "Microsoft",
        "is_ai_text": True,
        "is_series": True,
        "series_name": "Scaramouche",
        "series_number": "1",
        "has_publisher": True,
        "publisher": "TKPROF LLC",
        "description": description_text,
        "categories": [
            "FICTION / Classics",
            "FICTION / Action & Adventure"
        ],
        "keywords": "스카라무슈; Scaramouche; 라파엘 사바티니; 프랑스 혁명; 역사 모험 소설; 고전 소설; 활극",
        "price_usd": calculate_runtime_price(audio_files),
        "cover_path": cover_path,
        "audio_dir": audio_dir,
        "opening_track": os.path.join(audio_dir, "final_track_01_ko.mp3"),
        "closing_track": os.path.join(audio_dir, "final_track_09_ko.mp3"),
        "sample_track": os.path.join(audio_dir, "sample.mp3"),
        "audio_tracks": audio_files
    }

    out_file = os.path.join(NOTES_DIR, "ar_payload_scaramouche_book1_ko.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"✅ Ready metadata payload ({len(audio_files)} tracks) saved to {out_file}")
    return payload

def prepare_scaramouche_book1_en_metadata():
    audio_dir = r"C:\git_repo\TKprof_book\books\scaramouche\final_audio_book1"
    cover_path = r"C:\git_repo\TKprof_book\books\scaramouche\cover_b1_en_2400.jpg"

    audio_files = [os.path.join(audio_dir, f"final_track_{i:02d}_en.mp3") for i in range(1, 10) if os.path.exists(os.path.join(audio_dir, f"final_track_{i:02d}_en.mp3"))]

    description_text = (
        "Set against the turbulent backdrop of the French Revolution, Scaramouche tells the unforgettable tale of Andre-Louis Moreau, "
        "a young lawyer whose life is upended when his closest friend is murdered in a duel by the ruthless aristocrat Marquis de La Tour d'Azyr.\n\n"
        "Swearing vengeance, Andre-Louis flees into hiding and joins a troupe of itinerant commedia dell'arte actors, adopting the cunning stage persona of Scaramouche. "
        "As the fires of revolution ignite across Paris, his quest for justice leads him from the theatrical stage to the floor of the National Assembly, and finally to a deadly duel of honor.\n\n"
        "Featuring sharp wit, soaring romance, political intrigue, and masterly swashbuckling swordplay, Book 1: The Robe marks the dramatic opening volume of Rafael Sabatini's masterpiece of historical fiction."
    )

    opening_track = os.path.join(audio_dir, "final_track_01_en.mp3") if os.path.exists(os.path.join(audio_dir, "final_track_01_en.mp3")) else ""
    closing_track = os.path.join(audio_dir, "final_track_09_en.mp3") if os.path.exists(os.path.join(audio_dir, "final_track_09_en.mp3")) else ""
    sample_track = os.path.join(audio_dir, "sample.mp3") if os.path.exists(os.path.join(audio_dir, "sample.mp3")) else ""

    payload = {
        "book_id": "scaramouche_book1",
        "language_code": "en",
        "language_name": "English",
        "title": "Scaramouche: Book 1 - The Robe",
        "subtitle": "Modern English Edition",
        "author_first": "Rafael",
        "author_last": "Sabatini",
        "narrator_first": "TKPROF",
        "narrator_last": "AI",
        "is_ai_voice": True,
        "ai_engine": "Microsoft",
        "is_ai_text": True,
        "is_series": True,
        "series_name": "Scaramouche",
        "series_number": "1",
        "has_publisher": True,
        "publisher": "TKPROF LLC",
        "description": description_text,
        "categories": [
            "FICTION / Classics",
            "FICTION / Action & Adventure"
        ],
        "keywords": "scaramouche; rafael sabatini; french revolution; swashbuckler; classic literature",
        "price_usd": calculate_runtime_price(audio_files),
        "cover_path": cover_path,
        "audio_dir": audio_dir,
        "opening_track": "",
        "closing_track": "",
        "sample_track": os.path.join(audio_dir, "sample_en.mp3") if os.path.exists(os.path.join(audio_dir, "sample_en.mp3")) else "",
        "audio_tracks": audio_files
    }

    out_file = os.path.join(NOTES_DIR, "ar_payload_scaramouche_book1_en.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"✅ Ready metadata payload ({len(audio_files)} tracks) saved to {out_file}")
    return payload

def prepare_scaramouche_book2_en_metadata():
    audio_dir = r"C:\git_repo\TKprof_book\books\scaramouche\final_audio_book2"
    cover_path = r"C:\git_repo\TKprof_book\books\scaramouche\cover_b2_en_2400.jpg"

    audio_files = [os.path.join(audio_dir, f"final_track_{i:02d}_en.mp3") for i in range(1, 12) if os.path.exists(os.path.join(audio_dir, f"final_track_{i:02d}_en.mp3"))]

    description_text = (
        "Hiding from royal justice under the guise of a commedia dell'arte performer, Andre-Louis Moreau assumes the cunning stage mask of Scaramouche. "
        "Joining the troupe of Binet, his sharp wit and improvised satires turn the theatrical stage into a weapon against aristocrat corruption, winning the hearts of the Parisian populace.\n\n"
        "Book 2: The Buskin captures the dramatic rise of a fugitive into a hero of the people amidst the gathering storm of the French Revolution."
    )

    sample_track = os.path.join(audio_dir, "sample_en.mp3") if os.path.exists(os.path.join(audio_dir, "sample_en.mp3")) else ""

    payload = {
        "book_id": "scaramouche_book2",
        "language_code": "en",
        "language_name": "English",
        "title": "Scaramouche: Book 2 - The Buskin",
        "subtitle": "Modern English Edition",
        "author_first": "Rafael",
        "author_last": "Sabatini",
        "narrator_first": "TKPROF",
        "narrator_last": "AI",
        "is_ai_voice": True,
        "ai_engine": "Microsoft",
        "is_ai_text": True,
        "is_series": True,
        "series_name": "Scaramouche",
        "series_number": "2",
        "has_publisher": True,
        "publisher": "TKPROF LLC",
        "description": description_text,
        "categories": [
            "FICTION / Classics",
            "FICTION / Action & Adventure"
        ],
        "keywords": "scaramouche; rafael sabatini; french revolution; swashbuckler; classic literature",
        "price_usd": calculate_runtime_price(audio_files),
        "cover_path": cover_path,
        "audio_dir": audio_dir,
        "opening_track": "",
        "closing_track": "",
        "sample_track": sample_track,
        "audio_tracks": audio_files
    }

    out_file = os.path.join(NOTES_DIR, "ar_payload_scaramouche_book2_en.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"✅ Ready metadata payload ({len(audio_files)} tracks) saved to {out_file}")
    return payload

def prepare_scaramouche_book3_en_metadata():
    audio_dir = r"C:\git_repo\TKprof_book\books\scaramouche\final_audio_book3"
    cover_path = r"C:\git_repo\TKprof_book\books\scaramouche\cover_b3_en_2400.jpg"

    audio_files = [os.path.join(audio_dir, f"final_track_{i:02d}_en.mp3") for i in range(1, 17) if os.path.exists(os.path.join(audio_dir, f"final_track_{i:02d}_en.mp3"))]

    description_text = (
        "Rising to become Paris's most masterly fencing instructor amidst the turmoil of the French Revolution, Andre-Louis Moreau is thrust onto the floor of the National Assembly as a champion of the Third Estate. "
        "As political factions clash and the reign of terror looms, Andre-Louis faces his ultimate reckoning in a long-awaited duel of honor against his sworn enemy, the ruthless Marquis de La Tour d'Azyr.\n\n"
        "Book 3: The Sword delivers the breathtaking climax to Rafael Sabatini's epic masterpiece of vengeance, romance, and revelation."
    )

    sample_track = os.path.join(audio_dir, "sample_en.mp3") if os.path.exists(os.path.join(audio_dir, "sample_en.mp3")) else ""

    payload = {
        "book_id": "scaramouche_book3",
        "language_code": "en",
        "language_name": "English",
        "title": "Scaramouche: Book 3 - The Sword",
        "subtitle": "Modern English Edition",
        "author_first": "Rafael",
        "author_last": "Sabatini",
        "narrator_first": "TKPROF",
        "narrator_last": "AI",
        "is_ai_voice": True,
        "ai_engine": "Microsoft",
        "is_ai_text": True,
        "is_series": True,
        "series_name": "Scaramouche",
        "series_number": "3",
        "has_publisher": True,
        "publisher": "TKPROF LLC",
        "description": description_text,
        "categories": [
            "FICTION / Classics",
            "FICTION / Action & Adventure"
        ],
        "keywords": "scaramouche; rafael sabatini; french revolution; swashbuckler; classic literature",
        "price_usd": calculate_runtime_price(audio_files),
        "cover_path": cover_path,
        "audio_dir": audio_dir,
        "opening_track": "",
        "closing_track": "",
        "sample_track": sample_track,
        "audio_tracks": audio_files
    }

    out_file = os.path.join(NOTES_DIR, "ar_payload_scaramouche_book3_en.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"✅ Ready metadata payload ({len(audio_files)} tracks) saved to {out_file}")
    return payload

def prepare_scaramouche_book2_ko_metadata():
    audio_dir = r"C:\git_repo\TKprof_book\books\scaramouche\final_audio_book2"
    cover_path = r"C:\git_repo\TKprof_book\books\scaramouche\cover_b2_ko_2400.jpg"

    audio_files = [os.path.join(audio_dir, f"final_track_{i:02d}_ko.mp3") for i in range(1, 12) if os.path.exists(os.path.join(audio_dir, f"final_track_{i:02d}_ko.mp3"))]

    description_text = (
        "★ 무대 위의 광대에서 민중의 영웅으로 거듭나는 역동적인 대서사시! ★\n\n"
        "라파엘 사바티니(Rafael Sabatini)의 세계적인 거장 역사 모험 소설 《스카라무슈》 제2부: 반장화 (The Buskin) 편입니다.\n\n"
        "당국의 수배를 피해 유랑 극단에 몸을 숨긴 앙드레 루이 모로. 그는 가면 극단의 광대 '스카라무슈'로 변신하여 날카로운 풍자와 해학으로 귀족과 세상을 조롱하며 "
        "민중의 폭발적인 사랑을 받게 됩니다. 무대 위의 광대에서 민중의 영웅으로 성장하는 역동적인 전개가 펼쳐집니다."
    )

    payload = {
        "book_id": "scaramouche_book2",
        "language_code": "ko",
        "language_name": "Korean",
        "title": "스카라무슈 2: 배우의 신발 (Scaramouche)",
        "subtitle": "Scaramouche: Book 2 - The Buskin",
        "author_first": "라파엘",
        "author_last": "사바티니",
        "narrator_first": "TKPROF",
        "narrator_last": "AI",
        "is_ai_voice": True,
        "ai_engine": "Microsoft",
        "is_ai_text": True,
        "is_series": True,
        "series_name": "Scaramouche",
        "series_number": "2",
        "has_publisher": True,
        "publisher": "TKPROF LLC",
        "description": description_text,
        "categories": [
            "FICTION / Classics",
            "FICTION / Action & Adventure"
        ],
        "keywords": "스카라무슈; Scaramouche; 라파엘 사바티니; 프랑스 혁명; 역사 모험 소설; 고전 소설; 활극",
        "price_usd": calculate_runtime_price(audio_files),
        "cover_path": cover_path,
        "audio_dir": audio_dir,
        "opening_track": os.path.join(audio_dir, "final_track_01_ko.mp3"),
        "closing_track": os.path.join(audio_dir, "final_track_11_ko.mp3"),
        "sample_track": os.path.join(audio_dir, "sample.mp3"),
        "audio_tracks": audio_files
    }

    out_file = os.path.join(NOTES_DIR, "ar_payload_scaramouche_book2_ko.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"✅ Ready metadata payload ({len(audio_files)} tracks) saved to {out_file}")
    return payload

def prepare_scaramouche_book3_ko_metadata():
    audio_dir = r"C:\git_repo\TKprof_book\books\scaramouche\final_audio_book3"
    cover_path = r"C:\git_repo\TKprof_book\books\scaramouche\cover_b3_ko_2400.jpg"

    audio_files = [os.path.join(audio_dir, f"final_track_{i:02d}_ko.mp3") for i in range(1, 17) if os.path.exists(os.path.join(audio_dir, f"final_track_{i:02d}_ko.mp3"))]

    description_text = (
        "★ 서슬 퍼런 검 끝 위에서 펼쳐지는 숙명적 결투와 장엄한 대단원! ★\n\n"
        "라파엘 사바티니(Rafael Sabatini)의 세계적인 거장 역사 모험 소설 《스카라무슈》 제3부: 검의 언어 (The Sword) 완결편입니다.\n\n"
        "프랑스 혁명 파리의 혼란 속에서 펜싱 스승으로 이름을 날리는 앙드레 루이 모로. 마침내 펜싱 사범으로서 원수 라 투르 다르지르 후작과의 마지막 숙명적 결투에 "
        "임하게 됩니다. 서슬 퍼런 검 끝 위에서 밝혀지는 충격적인 혈연의 진실과 장엄한 대단원의 막!"
    )

    payload = {
        "book_id": "scaramouche_book3",
        "language_code": "ko",
        "language_name": "Korean",
        "title": "스카라무슈 3: 검의 언어 (Scaramouche)",
        "subtitle": "Scaramouche: Book 3 - The Sword",
        "author_first": "라파엘",
        "author_last": "사바티니",
        "narrator_first": "TKPROF",
        "narrator_last": "AI",
        "is_ai_voice": True,
        "ai_engine": "Microsoft",
        "is_ai_text": True,
        "is_series": True,
        "series_name": "Scaramouche",
        "series_number": "3",
        "has_publisher": True,
        "publisher": "TKPROF LLC",
        "description": description_text,
        "categories": [
            "FICTION / Classics",
            "FICTION / Action & Adventure"
        ],
        "keywords": "스카라무슈; Scaramouche; 라파엘 사바티니; 프랑스 혁명; 역사 모험 소설; 고전 소설; 활극",
        "price_usd": calculate_runtime_price(audio_files),
        "cover_path": cover_path,
        "audio_dir": audio_dir,
        "opening_track": "",
        "closing_track": "",
        "sample_track": "",
        "audio_tracks": audio_files
    }

    out_file = os.path.join(NOTES_DIR, "ar_payload_scaramouche_book3_ko.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"✅ Ready metadata payload ({len(audio_files)} tracks) saved to {out_file}")
    return payload

def prepare_scaramouche_ko_metadata():
    audio_dir = r"C:\git_repo\TKprof_book\books\scaramouche\final_audio"
    cover_path = r"C:\git_repo\TKprof_book\books\scaramouche\cover_b1_ko_2400.jpg"

    audio_files = [os.path.join(audio_dir, f"track_{i:02d}_ko.mp3") for i in range(1, 37) if os.path.exists(os.path.join(audio_dir, f"track_{i:02d}_ko.mp3"))]

    description_text = (
        "\"그는 세상이 미쳤다는 감각과, 웃음의 선물을 타고났다.\"\n\n"
        "18세기 프랑스 혁명의 거대한 소용돌이 속에서 펼쳐지는 복수와 검술, 사랑과 운명의 대서사시! "
        "라파엘 사바티니의 세계적인 모험 명작 《스카라무슈》(Scaramouche)가 현대 독자의 감각에 맞춘 최고급 한국어판으로 재탄생했습니다.\n\n"
        "【작품 소개】\n"
        "차가운 이성과 비범한 기지를 지닌 청년 앙드레 루이 모로. 이상주의 사제였던 절친한 친구 필립 드 빌모랭이 오만한 귀족 라 투르 다르지르 후작에게 결투를 빙자해 무참히 살해당하자, 앙드레 루이는 세상의 불의에 맞서 복수를 맹세합니다.\n\n"
        "지명수배를 피해 유랑 극단에 몸을 숨긴 그는 가면 극단의 광대 '스카라무슈'가 되어 날카로운 풍자와 해학으로 세상을 조롱하며 민중의 뜨거운 환호를 받습니다. 이어 파리 최고의 펜싱 사범으로 성장한 그는 프랑스 혁명의 격동기 속에서 제3신분의 수호자이자 전설적인 검술가로 거듭납니다.\n\n"
        "【본 편역본의 특징】\n"
        "- 전 3부(1부: 법복, 2부: 반장화, 3부: 장검) 전편 완역\n"
        "- 18세기 프랑스 혁명기의 시대상과 이탈리아 가면 극단의 생생한 분위기 보존\n"
        "- 몰입도 높은 대화와 현대적이고 세련된 어휘로 완성된 최상급 가독성"
    )

    payload = {
        "book_id": "scaramouche",
        "language_code": "ko",
        "language_name": "Korean",
        "title": "스카라무슈: 완역 현대 한국어판 (Scaramouche)",
        "subtitle": "Scaramouche: Modern Korean Edition (Complete Edition)",
        "author_first": "라파엘",
        "author_last": "사바티니",
        "narrator_first": "TKPROF",
        "narrator_last": "AI",
        "is_ai_voice": True,
        "ai_engine": "Microsoft",
        "is_ai_text": True,
        "is_series": False,
        "series_name": "",
        "series_number": "",
        "has_publisher": True,
        "publisher": "TKPROF LLC",
        "description": description_text,
        "categories": [
            "FICTION / Classics",
            "FICTION / Action & Adventure"
        ],
        "keywords": "스카라무슈; Scaramouche; 라파엘 사바티니; 프랑스 혁명; 역사 모험 소설; 고전 소설; 활극",
        "price_usd": "19.99",
        "cover_path": cover_path,
        "audio_dir": audio_dir,
        "opening_track": os.path.join(audio_dir, "track_01_ko.mp3"),
        "closing_track": os.path.join(audio_dir, "track_36_ko.mp3"),
        "sample_track": os.path.join(audio_dir, "sample.mp3"),
        "audio_tracks": audio_files
    }

    out_file = os.path.join(NOTES_DIR, "ar_payload_scaramouche_ko.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"✅ Ready metadata payload ({len(audio_files)} tracks) saved to {out_file}")
    return payload

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", default="richest_man_in_babylon")
    parser.add_argument("--lang", default="en", choices=["en", "ko"])
    args = parser.parse_args()

    if args.book == "richest_man_in_babylon":
        prepare_richest_man_in_babylon_metadata()
    elif args.book == "scaramouche":
        prepare_scaramouche_ko_metadata()
    elif args.book == "scaramouche_book3":
        if args.lang == "en":
            prepare_scaramouche_book3_en_metadata()
        else:
            prepare_scaramouche_book3_ko_metadata()
    elif args.book == "scaramouche_book2":
        if args.lang == "en":
            prepare_scaramouche_book2_en_metadata()
        else:
            prepare_scaramouche_book2_ko_metadata()
    elif args.book == "scaramouche_book1":
        if args.lang == "en":
            prepare_scaramouche_book1_en_metadata()
        else:
            prepare_scaramouche_book1_ko_metadata()
    elif args.book == "odyssey":
        if args.lang == "en":
            prepare_odyssey_en_metadata()
        else:
            prepare_odyssey_ko_metadata()
    elif args.book == "secret_garden":
        prepare_secret_garden_en_metadata()
    elif args.book == "dracula":
        prepare_dracula_en_metadata()
    elif args.book == "gilgamesh":
        if args.lang == "en":
            prepare_gilgamesh_en_metadata()
        else:
            prepare_gilgamesh_metadata()
    elif args.book == "beowulf":
        if args.lang == "en":
            prepare_beowulf_en_metadata()
        else:
            prepare_beowulf_metadata()
    else:
        prepare_blue_castle_metadata()



