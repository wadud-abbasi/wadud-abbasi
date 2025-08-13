#!/usr/bin/env python3
import re
import base64
from pathlib import Path
from html2image import Html2Image

def base64_encode_font(font_path):
    """Encode font file to base64 string"""
    with open(font_path, 'rb') as f:
        font_data = f.read()
        base64_data = base64.b64encode(font_data).decode('ascii')
        return f'data:font/{font_path.suffix[1:].lower()};base64,{base64_data}'

def html_to_png():
    """
    Converts HTML content to PNG using html2image library.
    Reads HTML from index.html, applies CSS from styles.css,
    and saves the output as a PNG in the images folder.
    Embeds fonts directly as base64 to ensure proper rendering.
    """
    root = Path(__file__).resolve().parents[2]
    index_file = root/"src"/"index.html"
    styles_file = root/"src"/"styles.css"
    fonts_dir = root/"src"/"fonts"
    out = root/"src"/"images"/"index.png"
    out.parent.mkdir(parents=True, exist_ok=True)

    html = index_file.read_text(encoding="utf-8")
    m = re.search(r"<body[^>]*>(.*)</body>", html, re.DOTALL)
    body = m.group(1) if m else html

    # force white text and XML-friendly tags
    body = re.sub(r'color:\s*[^;]+;', 'color: white;', body)
    body = re.sub(r'(<div[^>]*style="[^"]*)(")', r'\1; color: white;\2', body)

    # Read CSS and replace relative font URLs with base64-encoded data URLs
    css = styles_file.read_text(encoding="utf-8") if styles_file.exists() else ""
    
    # Find and encode fonts
    font_files = {}
    if fonts_dir.exists():
        for font_file in fonts_dir.glob('*.ttf'):
            font_files[font_file.name] = base64_encode_font(font_file)
    
    # Replace relative font URLs with base64 data URLs
    for font_name, data_url in font_files.items():
        css = css.replace(f"url('../fonts/{font_name}')", f"url('{data_url}')")
    
    # Set up HTML2Image with desired output size
    hti = Html2Image(output_path=str(out.parent), size=(1600, 800))
    
    # Create combined HTML with CSS
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            {css}
            body, html {{
                background-color: transparent;
                margin: 0;
                padding: 0;
                width: 1600px;
                height: 800px;
                overflow: hidden;
            }}
            .content {{
                color: white;
                width: 100%;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }}
            /* Use styles from CSS file */
        </style>
    </head>
    <body>
        <div class="content">
            {body}
        </div>
    </body>
    </html>
    """
    
    # Save to PNG
    hti.screenshot(html_str=full_html, save_as=out.name, size=(1600, 800))
    
    print(f"HTML converted to PNG and saved at: {out}")

if __name__ == "__main__":
    html_to_png()
    print("HTML has been converted directly to PNG")
