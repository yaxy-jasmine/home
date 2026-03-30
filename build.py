#!/usr/bin/env python3
"""Build blog posts from Markdown files in blog/posts/ into blog/*.html.

Usage:  python3 build.py            # build all .md files
        python3 build.py my-post    # build only blog/posts/my-post.md

No external dependencies required (stdlib only).
"""

import os, re, sys, html

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(SCRIPT_DIR, "blog", "posts")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "blog")
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, "blog", "template.html")

# ---------------------------------------------------------------------------
# Minimal Markdown -> HTML converter (covers blog-post needs)
# ---------------------------------------------------------------------------

def md_to_html(text):
    """Convert a subset of Markdown to HTML (paragraphs, headings, bold,
    italic, links, images, unordered/ordered lists, blockquotes, <hr>,
    and raw HTML passthrough)."""
    lines = text.split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Blank line – skip
        if line.strip() == "":
            i += 1
            continue

        # Raw HTML block (starts with <)
        if re.match(r"^\s*<(?!a |img |strong|em )", line):
            block = [line]
            i += 1
            # Collect until blank line or end
            while i < len(lines) and lines[i].strip() != "":
                block.append(lines[i])
                i += 1
            out.append("\n".join(block))
            continue

        # Heading
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{_inline(m.group(2))}</h{level}>")
            i += 1
            continue

        # Horizontal rule
        if re.match(r"^(\*{3,}|-{3,}|_{3,})\s*$", line):
            out.append("<hr>")
            i += 1
            continue

        # Blockquote
        if line.startswith(">"):
            bq_lines = []
            while i < len(lines) and (lines[i].startswith(">") or (lines[i].strip() != "" and bq_lines)):
                bq_lines.append(re.sub(r"^>\s?", "", lines[i]))
                i += 1
            out.append(f"<blockquote><p>{_inline(' '.join(bq_lines))}</p></blockquote>")
            continue

        # Unordered list
        if re.match(r"^\s*[-*+]\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\s*[-*+]\s+", lines[i]):
                items.append(re.sub(r"^\s*[-*+]\s+", "", lines[i]))
                i += 1
            out.append("<ul>" + "".join(f"<li>{_inline(it)}</li>" for it in items) + "</ul>")
            continue

        # Ordered list
        if re.match(r"^\s*\d+\.\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append(re.sub(r"^\s*\d+\.\s+", "", lines[i]))
                i += 1
            out.append("<ol>" + "".join(f"<li>{_inline(it)}</li>" for it in items) + "</ol>")
            continue

        # Paragraph – collect consecutive non-blank lines
        para = []
        while i < len(lines) and lines[i].strip() != "" and not re.match(r"^(#{1,6}\s|>\s|[-*+]\s|\d+\.\s|\s*<)", lines[i]):
            para.append(lines[i])
            i += 1
        out.append(f"<p>{_inline(' '.join(para))}</p>")

    return "\n\n        ".join(out)


def _inline(text):
    """Handle inline Markdown: images, links, bold, italic."""
    # Images  ![alt](src)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1" class="card-image">', text)
    # Links  [text](url)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    # Bold  **text**
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic  *text*
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text


# ---------------------------------------------------------------------------
# Front-matter parser
# ---------------------------------------------------------------------------

def parse_post(filepath):
    """Return (meta_dict, markdown_body) from a .md file with --- front matter."""
    with open(filepath, encoding="utf-8") as f:
        raw = f.read()
    if not raw.startswith("---"):
        return {}, raw
    _, fm, body = raw.split("---", 2)
    meta = {}
    for line in fm.strip().splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            meta[key.strip()] = val.strip()
    return meta, body.strip()


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build_post(md_path, template):
    meta, body = parse_post(md_path)
    title = meta.get("title", "Untitled")
    date = meta.get("date", "")
    tags = meta.get("tags", "")
    subtitle = " &middot; ".join(part for part in [date, tags] if part)
    content_html = md_to_html(body)

    result = template.replace("{{title}}", title)
    result = result.replace("{{subtitle}}", subtitle)
    result = result.replace("{{content}}", content_html)

    slug = os.path.splitext(os.path.basename(md_path))[0]
    out_path = os.path.join(OUTPUT_DIR, f"{slug}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(result)
    return slug, title, date, tags, meta.get("excerpt", "")


def main():
    if not os.path.isfile(TEMPLATE_PATH):
        sys.exit(f"Error: template not found at {TEMPLATE_PATH}")
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        template = f.read()

    # Determine which posts to build
    if len(sys.argv) > 1:
        md_files = [os.path.join(POSTS_DIR, f"{sys.argv[1]}.md")]
    else:
        if not os.path.isdir(POSTS_DIR):
            sys.exit(f"Error: posts directory not found at {POSTS_DIR}")
        md_files = sorted(
            os.path.join(POSTS_DIR, f)
            for f in os.listdir(POSTS_DIR)
            if f.endswith(".md")
        )

    if not md_files:
        print("No .md files found in blog/posts/")
        return

    for md_path in md_files:
        slug, title, date, tags, excerpt = build_post(md_path, template)
        print(f"  built: blog/{slug}.html  ({title})")

    print(f"\nDone – {len(md_files)} post(s) built.")


if __name__ == "__main__":
    main()
