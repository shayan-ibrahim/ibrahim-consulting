#!/usr/bin/env python3
"""
Weekly blog publisher for ibrahimconsulting.com
Runs via GitHub Actions every Monday at 14:00 UTC (9am CDT / 10am CST).
Determines which post to publish based on weeks since Sep 14 2026,
then updates the blog section in index.html between marker comments.
"""
import json, sys
from datetime import date, timedelta
from pathlib import Path

START_DATE = date(2026, 9, 14)   # Blog_01 publish date
TOTAL_POSTS = 20

REPO_ROOT = Path(__file__).parent.parent  # preview/
POSTS_FILE = Path(__file__).parent / "posts.json"
INDEX_FILE = REPO_ROOT / "index.html"


def get_week_index():
    today = date.today()
    delta = (today - START_DATE).days
    week = delta // 7
    if week < 0 or week >= TOTAL_POSTS:
        print(f"No post to publish today (week {week} out of range 0-{TOTAL_POSTS-1}). Done.")
        sys.exit(0)
    return week


def fmt_date(iso):
    d = date.fromisoformat(iso)
    return d.strftime("%b %-d, %Y")


def fmt_datetime(iso):
    """Return publish date + time, e.g. 'Sep 14, 2026 · 9:00am CT'"""
    return fmt_date(iso) + " · 9:00am CT"


def read_time(post):
    rt = post.get("read_time", "")
    if rt and rt.isdigit():
        return rt
    words = sum(len(p.split()) for p in post.get("body", []))
    return str(max(3, round(words / 200)))


def esc(s):
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))


def excerpt(body, max_chars=280):
    text = " ".join(body)[:max_chars]
    if len(" ".join(body)) > max_chars:
        text += "…"
    return esc(text)


# ── Desktop featured card ────────────────────────────────────────────────────

def desktop_featured(p):
    title = esc(p["title"])
    cat = esc(p["category"].title())
    pub = fmt_datetime(p["publish_date"])
    rt = read_time(p)
    ex = excerpt(p["body"], 320)
    num = f"{p['number']:02d}"
    tag_words = [w for w in p["category"].split() if len(w) > 2][:3]
    tags = "".join(
        f'<span style="font-size:10px;font-weight:600;color:rgba(255,255,255,.4);background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);border-radius:4px;padding:3px 8px">#{esc(w.title())}</span>'
        for w in tag_words
    )
    return f'''      <!-- Featured -->
      <article style="grid-column:1/3;grid-row:1/3;background:var(--color-obsidian);border:1px solid rgba(255,170,0,.15);border-radius:16px;overflow:hidden;display:flex;flex-direction:column;cursor:pointer;transition:box-shadow .2s,transform .2s;position:relative" onmouseenter="this.style.transform='translateY(-3px)';this.style.boxShadow='0 12px 48px rgba(0,0,0,.25)'" onmouseleave="this.style.transform='';this.style.boxShadow=''">
        <div style="flex:1;min-height:200px;position:relative;padding:44px 40px 36px;display:flex;flex-direction:column;justify-content:space-between">
          <div style="position:absolute;inset:0;background-image:linear-gradient(rgba(255,170,0,.06) 1px,transparent 1px),linear-gradient(90deg,rgba(255,170,0,.06) 1px,transparent 1px);background-size:36px 36px"></div>
          <div style="position:absolute;top:-60px;right:-60px;width:280px;height:280px;background:radial-gradient(circle,rgba(255,170,0,.12) 0%,transparent 70%);pointer-events:none"></div>
          <div style="position:relative">
            <div style="display:inline-flex;align-items:center;gap:5px;font-size:10px;font-weight:800;letter-spacing:1.4px;text-transform:uppercase;color:var(--color-amber);border:1px solid rgba(255,170,0,.35);border-radius:4px;padding:5px 10px;margin-bottom:20px">
              <span style="width:5px;height:5px;border-radius:50%;background:var(--color-amber);animation:blog-blink 1.8s ease-in-out infinite;display:inline-block"></span>
              {cat}
            </div>
            <h3 style="font-size:clamp(26px,3vw,38px);font-weight:900;color:#fff;line-height:1.1;letter-spacing:-1px;text-wrap:balance">{title}</h3>
          </div>
          <div style="position:relative;display:flex;gap:0;padding-top:20px;border-top:1px solid rgba(255,170,0,.12)">
            <div style="flex:1;text-align:center"><div style="font-size:24px;font-weight:900;color:#fff;letter-spacing:-1px;line-height:1">{num}</div><div style="font-size:9px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:rgba(255,255,255,.3);margin-top:4px">Post</div></div>
            <div style="flex:1;text-align:center;border-left:1px solid rgba(255,170,0,.1)"><div style="font-size:24px;font-weight:900;color:#fff;letter-spacing:-1px;line-height:1">{rt}</div><div style="font-size:9px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:rgba(255,255,255,.3);margin-top:4px">Min Read</div></div>
            <div style="flex:1;text-align:center;border-left:1px solid rgba(255,170,0,.1)"><div style="font-size:24px;font-weight:900;color:#fff;letter-spacing:-1px;line-height:1">SI</div><div style="font-size:9px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:rgba(255,255,255,.3);margin-top:4px">Author</div></div>
          </div>
        </div>
        <div style="padding:32px 40px;border-top:1px solid rgba(255,255,255,.07);display:flex;flex-direction:column;gap:16px">
          <p style="font-size:14px;color:rgba(255,255,255,.55);line-height:1.75">{ex}</p>
          <div style="display:flex;flex-wrap:wrap;gap:6px">{tags}</div>
          <div style="display:flex;align-items:center;justify-content:space-between">
            <div style="display:flex;align-items:center;gap:8px">
              <div style="width:30px;height:30px;border-radius:50%;background:linear-gradient(135deg,#1a1a22,#2a2a34);border:1.5px solid rgba(255,170,0,.4);display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:800;color:var(--color-amber);flex-shrink:0">SI</div>
              <div><div style="font-size:12px;font-weight:700;color:rgba(255,255,255,.7)">Shayan Ibrahim</div><div style="font-size:11px;color:rgba(255,255,255,.3)">{pub}</div></div>
            </div>
          </div>
        </div>
      </article>'''


def desktop_small(p, col, row):
    if p is None:
        return f'''      <!-- Card coming soon -->
      <article style="grid-column:{col};grid-row:{row};background:var(--color-snow);border:1px solid var(--color-fog);border-radius:14px;padding:28px 24px;display:flex;flex-direction:column;gap:10px;opacity:.6;cursor:pointer;transition:box-shadow .2s,transform .2s" onmouseenter="this.style.transform='translateY(-2px)';this.style.boxShadow='0 6px 24px rgba(0,0,0,.07)'" onmouseleave="this.style.transform='';this.style.boxShadow=''">
        <div style="font-size:10px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;color:var(--color-amber)">Coming Soon</div>
        <h3 style="font-size:16px;font-weight:700;color:var(--color-obsidian);line-height:1.3;letter-spacing:-0.2px;text-wrap:balance;flex:1">More insights on the way</h3>
        <div style="display:flex;align-items:center;justify-content:space-between;padding-top:14px;border-top:1px solid var(--color-fog);margin-top:4px">
          <span style="font-size:9px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--color-steel);background:var(--color-mist);border:1px solid var(--color-fog);border-radius:4px;padding:3px 7px">Stay tuned</span>
        </div>
      </article>'''
    title = esc(p["title"])
    cat = esc(p["category"].title())
    pub = fmt_datetime(p["publish_date"])
    return f'''      <!-- Card {p['number']:02d} -->
      <article style="grid-column:{col};grid-row:{row};background:var(--color-snow);border:1px solid var(--color-fog);border-radius:14px;padding:28px 24px;display:flex;flex-direction:column;gap:10px;opacity:.6;cursor:pointer;transition:box-shadow .2s,transform .2s" onmouseenter="this.style.transform='translateY(-2px)';this.style.boxShadow='0 6px 24px rgba(0,0,0,.07)'" onmouseleave="this.style.transform='';this.style.boxShadow=''">
        <div style="font-size:10px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;color:var(--color-amber)">{cat}</div>
        <h3 style="font-size:16px;font-weight:700;color:var(--color-obsidian);line-height:1.3;letter-spacing:-0.2px;text-wrap:balance;flex:1">{title}</h3>
        <div style="display:flex;align-items:center;justify-content:space-between;padding-top:14px;border-top:1px solid var(--color-fog);margin-top:4px">
          <span style="font-size:11px;color:var(--color-steel)">{pub}</span>
          <span style="font-size:9px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--color-steel);background:var(--color-mist);border:1px solid var(--color-fog);border-radius:4px;padding:3px 7px">Coming Soon</span>
        </div>
      </article>'''


# ── PWA cards ───────────────────────────────────────────────────────────────

def pwa_featured(p):
    title = esc(p["title"])
    cat = esc(p["category"].title())
    pub = fmt_datetime(p["publish_date"])
    ex = excerpt(p["body"], 200)
    return f'''        <!-- Featured post -->
        <article style="background:var(--color-obsidian);border:1px solid rgba(255,170,0,.18);border-radius:14px;overflow:hidden">
          <div style="padding:24px 20px 20px;position:relative">
            <div style="position:absolute;inset:0;background-image:linear-gradient(rgba(255,170,0,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(255,170,0,.05) 1px,transparent 1px);background-size:28px 28px"></div>
            <div style="position:relative">
              <div style="display:inline-flex;align-items:center;gap:4px;font-size:9px;font-weight:800;letter-spacing:1.2px;text-transform:uppercase;color:var(--color-amber);border:1px solid rgba(255,170,0,.3);border-radius:4px;padding:4px 8px;margin-bottom:14px">
                <span style="width:4px;height:4px;border-radius:50%;background:var(--color-amber);animation:blog-blink 1.8s ease-in-out infinite;display:inline-block"></span>
                {cat}
              </div>
              <h3 style="font-size:18px;font-weight:900;color:#fff;line-height:1.15;letter-spacing:-0.5px;text-wrap:balance">{title}</h3>
              <p style="font-size:12px;color:rgba(255,255,255,.5);line-height:1.65;margin-top:10px">{ex}</p>
            </div>
          </div>
          <div style="padding:14px 20px 18px;border-top:1px solid rgba(255,255,255,.06)">
            <div style="display:flex;align-items:center;gap:7px">
              <div style="width:26px;height:26px;border-radius:50%;background:linear-gradient(135deg,#1a1a22,#2a2a34);border:1.5px solid rgba(255,170,0,.4);display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:800;color:var(--color-amber)">SI</div>
              <div style="font-size:11px;font-weight:700;color:rgba(255,255,255,.6)">{pub}</div>
            </div>
          </div>
        </article>'''


def pwa_small(p):
    if p is None:
        return '''          <article style="background:#fff;border:1px solid #ececee;border-radius:12px;padding:18px 16px;display:flex;flex-direction:column;gap:8px;opacity:.55">
            <div style="font-size:9px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:var(--color-amber)">Coming Soon</div>
            <h3 style="font-size:13px;font-weight:700;color:#09090b;line-height:1.3;flex:1">More insights on the way</h3>
          </article>'''
    title = esc(p["title"])
    cat = esc(p["category"].title())
    pub = fmt_datetime(p["publish_date"])
    return f'''          <article style="background:#fff;border:1px solid #ececee;border-radius:12px;padding:18px 16px;display:flex;flex-direction:column;gap:8px;opacity:.55">
            <div style="font-size:9px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:var(--color-amber)">{cat}</div>
            <h3 style="font-size:13px;font-weight:700;color:#09090b;line-height:1.3;flex:1">{title}</h3>
            <div style="font-size:9px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:#71717a;background:#f5f4f0;border:1px solid #ececee;border-radius:3px;padding:2px 6px;width:fit-content">{pub}</div>
          </article>'''


# ── Main ─────────────────────────────────────────────────────────────────────

def replace_between(html, start_marker, end_marker, new_content):
    start_idx = html.find(start_marker)
    end_idx = html.find(end_marker)
    if start_idx == -1 or end_idx == -1:
        raise ValueError(f"Markers not found: {start_marker!r} / {end_marker!r}")
    after_start = html.index('\n', start_idx) + 1
    return html[:after_start] + new_content + '\n      ' + html[end_idx:]


def main():
    posts = json.loads(POSTS_FILE.read_text())
    week_idx = get_week_index()

    current = posts[week_idx]
    next1 = posts[week_idx + 1] if week_idx + 1 < TOTAL_POSTS else None
    next2 = posts[week_idx + 2] if week_idx + 2 < TOTAL_POSTS else None

    html = INDEX_FILE.read_text(encoding="utf-8")

    # Replace desktop bento cards
    desktop_cards = "\n".join([
        desktop_featured(current),
        desktop_small(next1, 3, 1),
        desktop_small(next2, 3, 2),
    ]) + "\n"
    html = replace_between(html, "<!-- BLOG_CARDS_START -->", "<!-- BLOG_CARDS_END -->", desktop_cards)

    # Replace PWA blog cards
    pwa_cards = "\n".join([
        pwa_featured(current),
        "        <!-- Upcoming posts -->",
        '        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">',
        pwa_small(next1),
        pwa_small(next2),
        "        </div>",
    ]) + "\n"
    html = replace_between(html, "<!-- PWA_BLOG_START -->", "<!-- PWA_BLOG_END -->", pwa_cards)

    INDEX_FILE.write_text(html, encoding="utf-8")
    print(f"Published post {week_idx + 1:02d}: {current['title']}")


if __name__ == "__main__":
    main()
