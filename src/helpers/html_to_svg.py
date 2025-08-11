#!/usr/bin/env python3
"""
HTML to SVG Converter
Converts src/index.html to src/images/index.svg with embedded fonts for GitHub README display
"""

import re
import os
import base64
from pathlib import Path

def html_to_svg():
    """
    Convert src/index.html to src/images/index.svg with white text on transparent background.
    Embeds fonts directly in SVG for robust display in GitHub README.
    """
    # Get file paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    index_file = project_root / "src" / "index.html"
    output_file = project_root / "src" / "images" / "index.svg"
    
    # Create images directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Read index.html
    if not index_file.exists():
        print(f"Error: {index_file} not found!")
        return False
    
    with open(index_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Extract body content
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL)
    if body_match:
        body_content = body_match.group(1)
    else:
        body_content = html_content
    
    # Convert all text to white
    body_content = re.sub(r'color:\s*[^;]+;', 'color: white;', body_content)
    body_content = re.sub(r'(<div[^>]*style="[^"]*)(")', r'\1; color: white;\2', body_content)
    
    # Fix self-closing tags for XML compatibility
    body_content = re.sub(r'<br>', '<br/>', body_content)
    body_content = re.sub(r'<hr([^>]*)>', r'<hr\1/>', body_content)
    
    # Wrap in white text container
    modified_content = f'<div style="color: white; width: 100%; height: 100%;">{body_content}</div>'
    
    # Read styles.css content
    styles_file = project_root / "src" / "styles.css"
    css_content = ""
    if styles_file.exists():
        with open(styles_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
    
    # Create SVG with embedded CSS
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="300" viewBox="0 0 800 300">
    <defs>
        <style>
            {css_content}
        </style>
    </defs>
    <foreignObject width="100%" height="100%">
        <div xmlns="http://www.w3.org/1999/xhtml" style="width: 800px; height: 300px;">
            {modified_content}
        </div>
    </foreignObject>
</svg>"""
    
    # Process font files to embed them directly in the SVG
    fonts_dir = project_root / "src" / "fonts"
    embedded_fonts = ""
    
    if fonts_dir.exists() and fonts_dir.is_dir():
        for font_file in fonts_dir.glob("*.ttf"):
            print(f"Embedding font: {font_file.name}")
            try:
                # Read font file binary content
                with open(font_file, "rb") as f:
                    font_data = f.read()
                
                # Convert to base64
                font_b64 = base64.b64encode(font_data).decode("ascii")
                
                # Extract font name from the file name
                font_name = font_file.stem
                
                # Create embedded @font-face rule
                embedded_fonts += f"""
@font-face {{
                    font-family: '{font_name}';
                    src: url('data:font/truetype;base64,{font_b64}');
                    font-weight: normal;
                    font-style: normal;
                }}
                """
            except Exception as e:
                print(f"Error embedding font {font_file.name}: {e}")
    
    # Create SVG with embedded fonts directly (no external files needed)
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="300" viewBox="0 0 800 300">
    <defs>
        <style>
            {embedded_fonts}
            {css_content}
        </style>
    </defs>
    <foreignObject width="100%" height="100%">
        <div xmlns="http://www.w3.org/1999/xhtml" style="width: 800px; height: 300px;">
            {modified_content}
        </div>
    </foreignObject>
</svg>"""
    
    # Save SVG file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    print(f"Converted {index_file} to {output_file} with embedded fonts")
    return True

if __name__ == "__main__":
    html_to_svg()