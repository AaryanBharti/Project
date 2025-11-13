# Embed AI chatbot widget
import streamlit.components.v1 as components
import os

# Get the directory containing app.py
current_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(current_dir, "assets")

# Load HTML template, CSS and JS content
with open(os.path.join(assets_dir, "template.html"), "r", encoding="utf-8") as f:
    html_content = f.read()
with open(os.path.join(assets_dir, "style.css"), "r", encoding="utf-8") as f:
    css_content = f.read()
with open(os.path.join(assets_dir, "script.js"), "r", encoding="utf-8") as f:
    js_content = f.read()

# Replace placeholders in the template
html_content = html_content.replace("<!-- CSS will be injected here -->", f"<style>{css_content}</style>")
html_content = html_content.replace("<!-- Scripts will be injected here -->", 
    f'''<script>
        window.addEventListener("error", function(e) {{ 
            console.error("Error:", e.message);
        }});
    </script>
    <script>{js_content}</script>''')