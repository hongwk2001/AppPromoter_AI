"""
_pd_reminder.py
Reminder shown before any Draft2Digital script runs (see CLAUDE.md).

Draft2Digital warned this account on 2026-11-12: no public-domain works or
derivatives (translations, adaptations, modernized or bilingual editions).
Relisting a blocked title violates their Terms of Service. The owner decided
not to send anything public-domain to D2D again.

The script continues only if you type ORIGINAL, confirming the title is a
fully original work you own.
"""

import sys

REMINDER = """
================================================================
 REMINDER: Draft2Digital warning on file (2026-11-12)
----------------------------------------------------------------
 D2D does not accept public-domain works or anything based on
 them, including translations and modernized/bilingual editions.
 You decided: nothing public-domain goes to D2D again.

 Every book in TKprof_book/books is public-domain derived.
================================================================
"""


def confirm():
    sys.stderr.write(REMINDER)
    if not sys.stdin or not sys.stdin.isatty():
        sys.stderr.write(" Not an interactive terminal: stopping.\n")
        raise SystemExit(1)
    answer = input(" Type ORIGINAL if this title is your own original work: ").strip()
    if answer != "ORIGINAL":
        sys.stderr.write(" Stopped. Nothing was sent to Draft2Digital.\n")
        raise SystemExit(1)


confirm()
