# Gumroad Ebook Test

First goal: put one ebook on Gumroad by hand, end to end, to learn the form.
Automate only after that (same pattern as the other platforms: inspect the
form over CDP, then fill it and pause before publishing).

## 1. Prepare the listing text

```
python gumroad/gumroad_0_prepare_metadata.py --book secret_garden --lang ko
```

Writes `notes/gumroad_secret_garden_ko.json` from the existing
`notes/d2d_metadata_secret_garden_ko.json`: name, summary, description
(with a translator / public-domain credit line added), price, tags, and the
paths of the EPUB and cover.

- Price defaults to the same price as the other stores ($3.99), so Gumroad
  never undercuts KDP or Google.
- `--free` makes it $0+ pay-what-you-want. Use it only for titles that are
  not on Amazon.
- No ISBN: the D2D-assigned ISBN is for D2D distribution only.

## 2. Create the product by hand

Gumroad's screens change, so treat these as a guide:

1. Gumroad → **Products → New product**. Choose the ebook type.
2. **Name** and **price**: copy from the JSON.
3. **Description**: paste `description` from the JSON.
4. **Cover**: upload the cover JPG. Also add a square **thumbnail**
   (600×600) if asked; a portrait cover may look letterboxed.
5. **Content / files**: upload the `.epub`.
6. **Summary** and **tags**: copy from the JSON if Gumroad offers these fields.
7. **Save, but do not publish.** Open the preview and check the page, the
   price and the file download.
8. Publish only when the preview looks right. You can unpublish any time.

## 3. Write down what you saw

Note the button names, field order and any surprises (file size limits,
required fields, tax or payout prompts). Those notes are what the
automation script will be built from.

## Before publishing any title

- The title is not in KDP Select.
- The price on Gumroad is not lower than on Amazon (unless the title is off Amazon).
- The source text is public domain (hold Odyssey, Beowulf and Gilgamesh until
  their translation source is confirmed).
- Gumroad can pay out to you (country / bank / PayPal set up in Settings → Payouts).
