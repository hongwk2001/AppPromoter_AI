"""
automate_ar_publish.py
Complete 4-Tab Playwright Automation Engine for Authors Republic
URL: https://www.authorsrepublic.com/the-republic/projects/publish-a-book

Workflow Steps:
  Tab 1: Get Started (Title, Subtitle, AI Voice, Author/Narrator Contributors, Series, Publisher)
  Tab 2: Metadata (Description, Language, Explicit, Abridged, BISAC Categories, Keywords, Sales Rights, Copyright, MSRP)
  Tab 3: Audio & Cover Art (Cover image, Opening/Closing/Sample tracks, Chapter tracks batched upload <45MB)
  Tab 4: Agreement (Rights agreement review)
"""

import os
import sys
import json
import time
import argparse
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(os.path.dirname(BASE_DIR), "notes")

def load_payload(book_name="beowulf", lang="ko"):
    payload_path = os.path.join(NOTES_DIR, f"ar_payload_{book_name}_{lang}.json")
    if not os.path.exists(payload_path):
        print(f"Payload file not found: {payload_path}. Generating metadata...")
        if book_name == "beowulf":
            from prepare_authors_republic_metadata import prepare_beowulf_metadata, prepare_beowulf_en_metadata
            return prepare_beowulf_en_metadata() if lang == "en" else prepare_beowulf_metadata()
        elif book_name == "gilgamesh":
            from prepare_authors_republic_metadata import prepare_gilgamesh_metadata, prepare_gilgamesh_en_metadata
            return prepare_gilgamesh_en_metadata() if lang == "en" else prepare_gilgamesh_metadata()
        elif book_name == "scaramouche_book3":
            from prepare_authors_republic_metadata import prepare_scaramouche_book3_ko_metadata, prepare_scaramouche_book3_en_metadata
            return prepare_scaramouche_book3_en_metadata() if lang == "en" else prepare_scaramouche_book3_ko_metadata()
        elif book_name == "scaramouche_book2":
            from prepare_authors_republic_metadata import prepare_scaramouche_book2_ko_metadata, prepare_scaramouche_book2_en_metadata
            return prepare_scaramouche_book2_en_metadata() if lang == "en" else prepare_scaramouche_book2_ko_metadata()
        elif book_name == "scaramouche_book1":
            from prepare_authors_republic_metadata import prepare_scaramouche_book1_ko_metadata, prepare_scaramouche_book1_en_metadata
            return prepare_scaramouche_book1_en_metadata() if lang == "en" else prepare_scaramouche_book1_ko_metadata()
        elif book_name == "odyssey":
            from prepare_authors_republic_metadata import prepare_odyssey_en_metadata
            return prepare_odyssey_en_metadata()
        elif book_name == "secret_garden":
            from prepare_authors_republic_metadata import prepare_secret_garden_en_metadata
            return prepare_secret_garden_en_metadata()
        elif book_name == "dracula":
            from prepare_authors_republic_metadata import prepare_dracula_en_metadata
            return prepare_dracula_en_metadata()
        elif book_name == "richest_man_in_babylon":
            from prepare_authors_republic_metadata import prepare_richest_man_in_babylon_metadata
            return prepare_richest_man_in_babylon_metadata()
        else:
            from prepare_authors_republic_metadata import prepare_blue_castle_metadata
            return prepare_blue_castle_metadata()
    with open(payload_path, "r", encoding="utf-8") as f:
        return json.load(f)

def run_authors_republic_autofill(book_name="beowulf", lang="ko", port=9222,
                                  phase="all", accept_agreement=False):
    payload = load_payload(book_name, lang)
    print(f"\n🚀 Initiating Authors Republic Full 4-Tab Submission for: {payload['title']}")
    print(f"  Author:           {payload['author_first']} {payload['author_last']}")
    print(f"  Narrator:         {payload['narrator_first']} {payload['narrator_last']}")
    print(f"  Publisher:        {payload.get('publisher', 'TKPROF LLC')}")
    print(f"  AI Voice:         {payload.get('is_ai_voice', True)} ({payload.get('ai_engine', 'Microsoft')})")
    print(f"  Cover Image:      {payload['cover_path']}")
    print(f"  Audio Tracks:     {len(payload.get('audio_tracks', []))} tracks\n")

    cdp_url = f"http://127.0.0.1:{port}"
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(cdp_url)
            context = browser.contexts[0]
        except Exception as e:
            print(f"⚠️ CDP connection on port {port} failed ({e}). Launching persistent Chrome context...")
            try:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=r"C:\tmp\chrome_dev_user",
                    headless=False,
                    executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    args=[f"--remote-debugging-port={port}"]
                )
            except Exception as e2:
                print(f"❌ Failed launching persistent Chrome: {e2}")
                return
        page = None
        for page_obj in context.pages:
            try:
                if "authorsrepublic.com" in page_obj.url:
                    page = page_obj
                    break
            except Exception:
                pass

        if page is None:
            print("➡️ Opening new tab for Authors Republic...")
            page = context.new_page()

        if "new-project" not in page.url and "publish-a-book" not in page.url and "/projects/" not in page.url:
            print("➡️ Navigating to Authors Republic 'New Audiobook' wizard...")
            try:
                page.goto("https://www.authorsrepublic.com/the-republic/projects/new-project", wait_until="domcontentloaded")
            except Exception as nav_err:
                print(f"Navigation warning: {nav_err}. Creating fresh page...")
                page = context.new_page()
                page.goto("https://www.authorsrepublic.com/the-republic/projects/new-project", wait_until="domcontentloaded")
            time.sleep(5)

        print(f"Active Tab URL: {page.url}")

        active_tab_name = "Get Started"
        for _ in range(5):
            try:
                active_tab_name = page.evaluate("""() => {
                    const active = document.querySelector('.w-20.active, .nav-tabs .active, .wizard-steps .active, [aria-selected="true"]');
                    return active ? active.innerText.trim() : 'Get Started';
                }""")
                break
            except Exception:
                time.sleep(2)

        print(f"Currently active tab: {active_tab_name}")

        # =====================================================================
        # TAB 1: GET STARTED
        # =====================================================================
        if phase != "audio" and ("Get Started" in active_tab_name or page.is_visible("#Project_ProjectName")):
            print("\n--- [TAB 1] Filling 'Get Started' ---")
            
            if page.is_visible("#Project_ProjectName"):
                page.fill("#Project_ProjectName", payload['title'])

            if page.is_visible("#Project_SubTitle") and payload.get('subtitle'):
                page.fill("#Project_SubTitle", payload['subtitle'])

            # Contributors are idempotent: on a resubmission the project already carries
            # rows, so reconcile against the payload instead of blindly adding duplicates.
            def sync_contributor(kind, list_sel, btn_sel, people):
                """people: list of (first, last).

                List-aware because AR supports several narrators and Dracula now
                has two. A single-person version called twice would treat the
                first narrator as stale and delete it on the second call.
                """
                people = [(f, (l if l else ".")) for f, l in people]

                existing = page.evaluate("""(sel) => {
                    const box = document.querySelector(sel);
                    if (!box) return [];
                    return Array.from(box.querySelectorAll('.contributor')).map(c => {
                        const g = n => {
                            const el = c.querySelector(`input[name$=".${n}"]`);
                            return el ? el.value : '';
                        };
                        return { first: g('FirstName'), last: g('LastName') };
                    });
                }""", list_sel)

                # AR stamps "AI Voice " onto the first name of an AI narrator on
                # save, so an already-correct row reads back prefixed. Match through it.
                def matches(e, first, last):
                    return e['last'] == last and e['first'].replace("AI Voice ", "", 1) == first

                present, stale = [], []
                for e in existing:
                    hit = next((p for p in people if matches(e, *p)), None)
                    if hit and hit not in present:
                        present.append(hit)
                        print(f"  {kind} already set: {hit[0]} {hit[1]}")
                    else:
                        stale.append(e)

                for e in stale:
                    print(f"  Removing stale {kind}: {e['first']} {e['last']}")
                    page.evaluate("""({sel, first, last}) => {
                        const box = document.querySelector(sel);
                        if (!box) return;
                        for (const c of box.querySelectorAll('.contributor')) {
                            const g = n => {
                                const el = c.querySelector(`input[name$=".${n}"]`);
                                return el ? el.value : '';
                            };
                            if (g('FirstName') === first && g('LastName') === last) {
                                const x = c.querySelector('.rm-contrib');
                                if (x) x.click(); else c.remove();
                                return;
                            }
                        }
                    }""", {"sel": list_sel, "first": e['first'], "last": e['last']})
                    time.sleep(1.0)

                for first, last in people:
                    if (first, last) in present:
                        continue
                    if page.is_visible(btn_sel):
                        print(f"  Adding {kind}: {first} {last}")
                        page.click(btn_sel)
                        page.wait_for_selector("#ContributorFirstName", state="visible", timeout=5000)
                        page.fill("#ContributorFirstName", first)
                        page.fill("#ContributorLastName", last)
                        page.click("#AddContributor")
                        time.sleep(1.0)

            sync_contributor("Author", "#AuthorsList", "#NewAuthorBtn",
                             [(payload['author_first'], payload['author_last'])])

            if payload.get('is_ai_voice'):
                engine = payload.get('ai_engine', 'Microsoft')
                print(f"Selecting AI Voice: Yes (#AiYes) -> {engine}")
                if page.is_visible("#AiYes"):
                    page.click("#AiYes")
                    time.sleep(0.5)
                    if page.is_visible("#aiEngineSelect"):
                        # The dropdown is a fixed vendor list; anything else goes through
                        # "Other (Write In)" and the free-text #aiEngineOtherInput.
                        options = page.eval_on_selector_all(
                            "#aiEngineSelect option",
                            "opts => opts.map(o => o.innerText.trim())"
                        )
                        match = next((o for o in options if o.lower() == engine.lower()), None)
                        if match:
                            page.select_option("#aiEngineSelect", label=match)
                        else:
                            other = next((o for o in options if "Other" in o), None)
                            if other:
                                print(f"  '{engine}' not in vendor list -> '{other}' + write-in")
                                page.select_option("#aiEngineSelect", label=other)
                                time.sleep(0.5)
                                if page.is_visible("#aiEngineOtherInput"):
                                    page.fill("#aiEngineOtherInput", engine)
                            else:
                                print(f"  ⚠️ Could not place engine '{engine}'; options: {options}")
            else:
                if page.is_visible("#AiNo"):
                    page.click("#AiNo")

            # "narrators" (list of [first, last]) wins when present; the old
            # narrator_first/narrator_last pair still works for every other book.
            narrators = payload.get('narrators') or [
                (payload['narrator_first'], payload['narrator_last'])]
            sync_contributor("Narrator", "#NarratorList", "#NewNarratorBtn",
                             [tuple(n) for n in narrators])

            if payload.get('is_series'):
                if page.is_visible("#SeriesYes"):
                    page.click("#SeriesYes")
                    time.sleep(0.5)
                    if page.is_visible("#Project_Series"):
                        page.fill("#Project_Series", payload['series_name'])
                    if page.is_visible("#Project_SeriesNumber"):
                        page.fill("#Project_SeriesNumber", str(payload['series_number']))
            else:
                if page.is_visible("#SeriesNo"):
                    page.click("#SeriesNo")

            if payload.get('has_publisher') and payload.get('publisher'):
                if page.is_visible("#PubYes"):
                    page.click("#PubYes")
                    time.sleep(0.5)
                    if page.is_visible("#Project_Publisher"):
                        page.fill("#Project_Publisher", payload['publisher'])
            else:
                if page.is_visible("#PubNo"):
                    page.click("#PubNo")

            print("Submitting Tab 1 (#SaveContinue)...")
            if page.is_visible("#SaveContinue"):
                page.click("#SaveContinue")
                time.sleep(3.0)

        # =====================================================================
        # TAB 2: METADATA
        # =====================================================================
        active_tab_name = page.evaluate("""() => {
            const active = document.querySelector('.w-20.active, .nav-tabs .active, .wizard-steps .active, [aria-selected="true"]');
            return active ? active.innerText.trim() : 'Metadata';
        }""")

        if phase != "audio" and ("Metadata" in active_tab_name or page.is_visible("#ProjectMeta_Description")):
            print("\n--- [TAB 2] Filling 'Metadata' ---")

            # AI Written Text Radio: "Was this book's written text created using AI?"
            is_ai_text = payload.get('is_ai_text', payload.get('is_ai_content', True))
            if is_ai_text:
                if page.is_visible("input[name='ProjectMeta.IsAIContent'][value='true']"):
                    print("Selecting AI Written Text: Yes")
                    page.click("input[name='ProjectMeta.IsAIContent'][value='true']")
            else:
                if page.is_visible("input[name='ProjectMeta.IsAIContent'][value='false']"):
                    print("Selecting AI Written Text: No")
                    page.click("input[name='ProjectMeta.IsAIContent'][value='false']")

            if page.is_visible("#ProjectMeta_Description"):
                page.fill("#ProjectMeta_Description", payload['description'])

            if page.is_visible("#ProjectMeta_LanguageId"):
                try:
                    page.select_option("#ProjectMeta_LanguageId", label=payload['language_name'])
                except Exception as e:
                    print(f"  Language select note: {e}")

            if page.is_visible("#ExplicitNo"):
                page.click("#ExplicitNo")

            if page.is_visible("#AbridgedNo"):
                page.click("#AbridgedNo")

            # BISAC Genres: driven by payload['categories'] ("TOP / Sub" or "TOP / Sub / Sub2").
            # Two-level selects: #allGenreListN picks the heading, #GenreN the subcategory.
            for slot, category in enumerate(payload.get('categories', [])[:3], 1):
                top, _, sub = category.partition(" / ")
                top, sub = top.strip(), sub.strip()
                list_sel, genre_sel = f"#allGenreList{slot}", f"#Genre{slot}"
                if not page.is_visible(list_sel):
                    continue
                try:
                    top_opts = page.eval_on_selector_all(
                        f"{list_sel} option",
                        "opts => opts.map(o => ({val: o.value, txt: o.innerText.trim()}))"
                    )
                    top_opt = next((o for o in top_opts if o['txt'].upper() == top.upper()), None) \
                        or next((o for o in top_opts if top.upper() in o['txt'].upper()), None)
                    if not top_opt:
                        print(f"  ⚠️ Genre{slot}: no heading match for '{top}'")
                        continue
                    page.select_option(list_sel, value=top_opt['val'])
                    time.sleep(1.0)

                    sub_opts = page.eval_on_selector_all(
                        f"{genre_sel} option",
                        "opts => opts.map(o => ({val: o.value, txt: o.innerText.trim()}))"
                    )
                    sub_opts = [o for o in sub_opts if o['val']]
                    sub_opt = next((o for o in sub_opts if o['txt'].upper() == sub.upper()), None) \
                        or next((o for o in sub_opts if sub.upper() in o['txt'].upper()), None) \
                        or next((o for o in sub_opts if sub.split(" / ")[0].upper() in o['txt'].upper()), None)
                    if not sub_opt:
                        print(f"  ⚠️ Genre{slot}: heading '{top_opt['txt']}' set, no subcategory match for '{sub}'")
                        continue
                    page.select_option(genre_sel, value=sub_opt['val'])
                    print(f"  Genre{slot}: {top_opt['txt']} / {sub_opt['txt']}")
                except Exception as e:
                    print(f"  Genre{slot} note: {e}")

            if page.is_visible("#ProjectMeta_Keywords"):
                raw_kw = payload.get('keywords', "Richest Man in Babylon, personal finance, money, investing, audiobook, wealth")
                # Remove dots, clean spaces, support both comma and semicolon delimiters
                delimiters = [',', ';']
                raw_split = [raw_kw]
                for d in delimiters:
                    new_split = []
                    for item in raw_split:
                        new_split.extend(item.split(d))
                    raw_split = new_split
                parts = [k.strip().replace('.', '') for k in raw_split if k.strip()]
                formatted_kw = ""
                for part in parts:
                    candidate = f"{formatted_kw}; {part}" if formatted_kw else part
                    if len(candidate) <= 100:
                        formatted_kw = candidate
                    else:
                        break
                print(f"Filling Keywords ({len(formatted_kw)} chars): {formatted_kw}")
                page.fill("#ProjectMeta_Keywords", formatted_kw)

            if page.is_visible("#distribution_worldwide_radio"):
                page.click("#distribution_worldwide_radio")

            if page.is_visible("#ProjectMeta_AudiobookOwnerName"):
                page.fill("#ProjectMeta_AudiobookOwnerName", payload['publisher'])

            if page.is_visible("#ProjectMeta_AudiobookCopyrightYear"):
                page.fill("#ProjectMeta_AudiobookCopyrightYear", "2026")

            if page.is_visible("#ProjectMeta_MSRP"):
                page.fill("#ProjectMeta_MSRP", payload['price_usd'])

            print("Submitting Tab 2 (#SaveContinue)...")
            if page.is_visible("#SaveContinue"):
                page.click("#SaveContinue")
                time.sleep(3.0)

        # =====================================================================
        # TAB 3: AUDIO & COVER ART
        # =====================================================================
        if phase == "meta":
            print()
            print("⏹ phase=meta: Tabs 1-2 saved. Stopping before Tab 3 (audio & cover).")
            return

        print("\n--- [TAB 3] Uploading Cover Art & Audio Tracks ---")

        # 1. Cover Image Upload
        cover_input = page.query_selector("#square-cover-file")
        if cover_input and payload.get('cover_path') and os.path.exists(payload['cover_path']):
            print(f"Uploading Cover Image: {payload['cover_path']}")
            try:
                page.set_input_files("#square-cover-file", payload['cover_path'], timeout=120000)
                print("✅ Cover Image set on #square-cover-file successfully!")
            except Exception as e:
                print(f"  Direct input error: {e}, attempting file chooser click...")
                try:
                    with page.expect_file_chooser(timeout=3000) as fc_info:
                        page.click(".cover-select label", force=True)
                    fc_info.value.set_files(payload['cover_path'])
                except Exception as e2:
                    print(f"  File chooser fallback note: {e2}")
            time.sleep(3.0)

        # 2. Audio Tracks Upload (by explicit data-segment-id via CDP + Playwright fallback)
        def upload_single_segment(seg_id, file_path, name):
            if file_path and os.path.exists(file_path):
                print(f"Uploading {name} (segment {seg_id}): {file_path}")
                try:
                    # Native CDP setting
                    client = page.context.new_cdp_session(page)
                    client.send("DOM.enable")
                    res = client.send("DOM.getFlattenedDocument", {"depth": -1, "pierce": True})
                    target_node_id = None
                    for node in res.get("nodes", []):
                        if node.get("nodeName") == "INPUT":
                            attrs = node.get("attributes", [])
                            attr_dict = dict(zip(attrs[::2], attrs[1::2]))
                            if attr_dict.get("data-segment-id") == str(seg_id):
                                target_node_id = node.get("nodeId")
                                break
                    if target_node_id:
                        client.send("DOM.setFileInputFiles", {
                            "files": [file_path],
                            "nodeId": target_node_id
                        })
                except Exception as cdp_err:
                    print(f"  CDP segment {seg_id} note: {cdp_err}")

                try:
                    page.set_input_files(f'input[data-segment-id="{seg_id}"]', file_path)
                except Exception:
                    pass

                page.evaluate(f"""() => {{
                    const el = document.querySelector('input[data-segment-id="{seg_id}"]');
                    if (el) {{
                        el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    }}
                }}""")
                time.sleep(2.0)

        upload_single_segment("1", payload.get('opening_track'), "Opening Track")
        upload_single_segment("2", payload.get('closing_track'), "Closing Track")
        upload_single_segment("3", payload.get('sample_track'), "Sample Track")

        # Chapter Tracks (Segment ID 0 via CDP) - exclude intro, opening, ending, closing, copyright, sample
        chapter_files = [
            f for f in payload['audio_tracks']
            if not any(k in os.path.basename(f).lower() for k in ["opening", "ending", "intro", "closing", "copyright", "sample", "podcast"])
        ]
        if chapter_files:
            print(f"Uploading {len(chapter_files)} Chapter Tracks via Native CDP (Segment ID 0)...")
            try:
                client = page.context.new_cdp_session(page)
                client.send("DOM.enable")
                res = client.send("DOM.getFlattenedDocument", {"depth": -1, "pierce": True})
                target_node_id = None
                for node in res.get("nodes", []):
                    if node.get("nodeName") == "INPUT":
                        attrs = node.get("attributes", [])
                        attr_dict = dict(zip(attrs[::2], attrs[1::2]))
                        if attr_dict.get("data-segment-id") == "0":
                            target_node_id = node.get("nodeId")
                            break

                if target_node_id:
                    client.send("DOM.setFileInputFiles", {
                        "files": chapter_files,
                        "nodeId": target_node_id
                    })
                    time.sleep(1.0)
                    page.evaluate("""() => {
                        const el = document.querySelector('input[data-segment-id="0"]');
                        if (el) {
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                    }""")
                    time.sleep(3.0)
                    print("✅ Chapter Tracks list injected via CDP successfully!")
            except Exception as e:
                print(f"  CDP chapter upload note: {e}")

        # Verification Loop: Wait for hidden flags to confirm all uploads before continuing
        print("⏳ Waiting for all track upload confirmation flags (#HasOpeningTrackHidden, #HasClosingTrackHidden, #HasSampleTrackHidden)...")
        need_cover = bool(payload.get('cover_path'))
        need_opening = bool(payload.get('opening_track'))
        need_closing = bool(payload.get('closing_track'))
        need_sample = bool(payload.get('sample_track'))

        for attempt in range(40):
            try:
                status = page.evaluate("""() => {
                    const cover = document.querySelector('#HasCoverImageHidden');
                    const opening = document.querySelector('#HasOpeningTrackHidden');
                    const closing = document.querySelector('#HasClosingTrackHidden');
                    const sample = document.querySelector('#HasSampleTrackHidden');
                    const chapters = document.querySelector('#HasChapterTrackHidden');

                    return {
                        cover: cover ? cover.value : '',
                        opening: opening ? opening.value : '',
                        closing: closing ? closing.value : '',
                        sample: sample ? sample.value : '',
                        chapters: chapters ? chapters.value : '',
                        modal: !!document.querySelector('#UploadProgressModal.show')
                    };
                }""")
                
                cover_ok = not need_cover or status['cover'] == "True"
                opening_ok = not need_opening or status['opening'] == "True"
                closing_ok = not need_closing or status['closing'] == "True"
                sample_ok = not need_sample or status['sample'] == "True"

                if (cover_ok and opening_ok and closing_ok and sample_ok and not status['modal']):
                    print(f"✅ All track upload flags confirmed! (Cover={status['cover']}, Opening={status['opening']}, Closing={status['closing']}, Sample={status['sample']}, Chapters={status['chapters']})")
                    break
            except Exception as eval_err:
                print(f"  Verification note ({attempt+1}): {eval_err}")
            
            time.sleep(3.0)

        # Wait for any active upload modal or progress toast to hide
        print("Waiting for upload modals & processing to finish...")
        for _ in range(30):
            try:
                if page.is_visible("#UploadProgressModal") or page.is_visible(".modal-backdrop"):
                    time.sleep(2.0)
                else:
                    break
            except Exception:
                time.sleep(1.0)

        if not accept_agreement:
            print()
            print("⏹ Tab 3 complete. Stopping before Tab 4 (Agreement).")
            print("   The rights agreement is a legal acceptance - review and submit it")
            print("   yourself, or re-run with --accept-agreement to tick the boxes.")
            return

        # Continue to Tab 4
        print("\nNavigating to Tab 4 (#AgreementBtn)...")
        if page.is_visible("#AgreementBtn"):
            try:
                page.click("#AgreementBtn", timeout=10000)
            except Exception as click_err:
                print(f"Standard click failed ({click_err}), triggering direct JS click on #AgreementBtn...")
                page.evaluate("() => { const b = document.querySelector('#AgreementBtn'); if(b) b.click(); }")
            time.sleep(3.0)

        # =====================================================================
        # TAB 4: AGREEMENT
        # =====================================================================
        print("\n--- [TAB 4] Final Agreement & Review ---")
        print("Checking rights agreement checkboxes on Tab 4...")
        page.evaluate("""() => {
            const checkboxes = document.querySelectorAll("input[type='checkbox']");
            checkboxes.forEach(cb => {
                if (!cb.checked) {
                    cb.checked = true;
                    cb.dispatchEvent(new Event('change', { bubbles: true }));
                    cb.dispatchEvent(new Event('click', { bubbles: true }));
                }
            });
        }""")
        time.sleep(1.0)

        print("\n🎉 Authors Republic Autofill workflow completed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Authors Republic Complete Playwright Script")
    parser.add_argument("--book", default="beowulf", help="Book identifier")
    parser.add_argument("--lang", default="ko", help="Language code")
    parser.add_argument("--port", type=int, default=9222, help="Chrome CDP port")
    parser.add_argument("--phase", default="all", choices=["all", "meta", "audio"],
                        help="meta = Tabs 1-2 only; audio = Tab 3 only; all = both")
    parser.add_argument("--accept-agreement", action="store_true",
                        help="Also tick the Tab 4 rights-agreement checkboxes (off by default)")
    args = parser.parse_args()

    run_authors_republic_autofill(args.book, args.lang, args.port,
                                  phase=args.phase, accept_agreement=args.accept_agreement)
