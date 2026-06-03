import os
import re

def parse_markdown(md_text):
    """Simple regex-based markdown parser to avoid external dependencies."""
    html = md_text
    
    # Escape HTML tags first
    html = html.replace("<", "&lt;").replace(">", "&gt;")
    
    # Headings
    html = re.sub(r'^#\s+(.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^##\s+(.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^###\s+(.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    
    # Images (MUST be matched before links)
    html = re.sub(r'!\[(.*?)\]\((.*?)\)', 
                  r'<div class="img-container"><img src="\2" alt="\1" /><div class="img-caption">\1</div></div>', 
                  html)
    
    # Bold
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    
    # Links
    html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" target="_blank">\1</a>', html)
    
    # Unordered Lists
    lines = html.split('\n')
    in_list = False
    new_lines = []
    for line in lines:
        if line.strip().startswith('* ') or line.strip().startswith('- '):
            content = line.strip()[2:]
            if not in_list:
                new_lines.append('<ul>')
                in_list = True
            new_lines.append(f'  <li>{content}</li>')
        else:
            if in_list:
                new_lines.append('</ul>')
                in_list = False
            new_lines.append(line)
    if in_list:
        new_lines.append('</ul>')
    html = '\n'.join(new_lines)
    
    # Paragraphs
    blocks = html.split('\n\n')
    new_blocks = []
    for block in blocks:
        block_stripped = block.strip()
        if not block_stripped:
            continue
        if block_stripped == '---':
            new_blocks.append('<hr>')
        elif (block_stripped.startswith('<h') or 
              block_stripped.startswith('<ul') or 
              block_stripped.startswith('<li') or
              block_stripped.startswith('<div')):
            new_blocks.append(block_stripped)
        else:
            p_content = block_stripped.replace('\n', ' ')
            new_blocks.append(f'<p>{p_content}</p>')
            
    html = '\n\n'.join(new_blocks)
    html = html.replace('\n\n<hr>\n\n', '\n<hr>\n')
    return html

def compile_to_html(md_path, html_path, title, theme_color_h=210):
    if not os.path.exists(md_path):
        print(f"File not found: {md_path}")
        return

    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    body_html = parse_markdown(md_content)

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Plus+Jakarta+Sans:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary-hue: {theme_color_h};
            --primary: hsl(var(--primary-hue), 85%, 55%);
            --primary-dark: hsl(var(--primary-hue), 85%, 40%);
            --primary-light: hsl(var(--primary-hue), 85%, 95%);
            --bg: #0f172a;
            --card-bg: rgba(30, 41, 59, 0.7);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border: rgba(255, 255, 255, 0.08);
            --gradient: linear-gradient(135deg, hsl(var(--primary-hue), 85%, 60%) 0%, hsl(calc(var(--primary-hue) + 40), 90%, 55%) 100%);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            line-height: 1.7;
            padding: 4rem 2rem;
            min-height: 100vh;
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(var(--primary-hue), 85%, 55%, 0.15) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(calc(var(--primary-hue) + 40), 90%, 55%, 0.1) 0%, transparent 40%);
            background-attachment: fixed;
        }}

        .container {{
            max-width: 850px;
            margin: 0 auto;
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            padding: 3.5rem;
            border-radius: 24px;
            border: 1px solid var(--border);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }}

        h1 {{
            font-family: 'Outfit', sans-serif;
            font-size: 2.8rem;
            font-weight: 800;
            background: var(--gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 2rem;
            line-height: 1.2;
            letter-spacing: -0.02em;
        }}

        h2 {{
            font-family: 'Outfit', sans-serif;
            font-size: 1.8rem;
            font-weight: 600;
            color: var(--text-main);
            margin-top: 2.5rem;
            margin-bottom: 1rem;
            position: relative;
            padding-bottom: 0.5rem;
        }}

        h2::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 40px;
            height: 4px;
            background: var(--gradient);
            border-radius: 2px;
        }}

        h3 {{
            font-family: 'Outfit', sans-serif;
            font-size: 1.3rem;
            font-weight: 600;
            color: hsl(var(--primary-hue), 90%, 75%);
            margin-top: 1.8rem;
            margin-bottom: 0.8rem;
        }}

        p {{
            margin-bottom: 1.5rem;
            color: #cbd5e1;
            font-size: 1.05rem;
        }}

        ul {{
            margin-bottom: 1.5rem;
            padding-left: 1.5rem;
        }}

        li {{
            margin-bottom: 0.5rem;
            color: #cbd5e1;
        }}

        a {{
            color: hsl(var(--primary-hue), 90%, 65%);
            text-decoration: none;
            font-weight: 600;
            transition: all 0.2s ease;
            border-bottom: 1px dashed rgba(255, 255, 255, 0.2);
            padding-bottom: 1px;
        }}

        a:hover {{
            color: hsl(calc(var(--primary-hue) + 20), 90%, 70%);
            border-bottom-color: var(--primary);
        }}

        hr {{
            border: 0;
            height: 1px;
            background: linear-gradient(90deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.12) 50%, rgba(255, 255, 255, 0.03) 100%);
            margin: 2.5rem 0;
        }}

        .img-container {{
            text-align: center;
            margin: 2.5rem 0;
        }}

        .img-container img {{
            max-width: 100%;
            border-radius: 12px;
            border: 1px solid var(--border);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.45);
        }}

        .img-caption {{
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-top: 0.75rem;
            font-style: italic;
        }}

        /* Subtle micro-animations */
        .container {{
            animation: fadeIn 0.8s cubic-bezier(0.16, 1, 0.3, 1);
        }}

        @keyframes fadeIn {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @media (max-width: 640px) {{
            body {{
                padding: 1.5rem 1rem;
            }}
            .container {{
                padding: 1.8rem;
                border-radius: 16px;
            }}
            h1 {{
                font-size: 2rem;
            }}
            h2 {{
                font-size: 1.4rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {body_html}
    </div>
</body>
</html>
"""

    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    print(f"Compiled: '{md_path}' -> '{html_path}' successfully.")

if __name__ == "__main__":
    # Base paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(os.path.dirname(base_dir), "output", "kb_html")
    
    # 1. Golf Swing KB (Theme H = 142: nice green color for golf)
    compile_to_html(
        os.path.join(base_dir, "kb_golf.md"),
        os.path.join(output_dir, "kb_golf.html"),
        "SwingPro AI - Golf Swing Guide",
        theme_color_h=142
    )

    # 2. NPC KB (Theme H = 220: professional blue color)
    compile_to_html(
        os.path.join(base_dir, "kb_npc.md"),
        os.path.join(output_dir, "kb_npc.html"),
        "College Financial Aid & Net Price Guide",
        theme_color_h=220
    )

    # 3. Dev Journey Reddit Replier (Theme H = 265: premium purple for AI development)
    compile_to_html(
        os.path.join(base_dir, "dev_journey_reddit_replier.md"),
        os.path.join(output_dir, "dev_journey_reddit_replier.html"),
        "Building a KB-Driven Reddit Outreach Dashboard",
        theme_color_h=265
    )
