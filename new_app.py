from pydoc import pager
import streamlit as st
import sqlite3
import json
import requests
from streamlit_lottie import st_lottie
import os
import threading
from flask import Flask, request as flask_request, jsonify
import pandas as pd
import matplotlib.pyplot as plt

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

# Render the chatbot HTML using components.html
import streamlit.components.v1 as components
components.html(html_content, height=800, width=None)

# Flask API for handling chat requests
def start_local_api_server():
    app = Flask(__name__)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST')
        return response

    @app.route('/api/research', methods=['POST'])
    def research_api():
        """Enhanced web search functionality similar to Google Gemini."""
        data = flask_request.get_json(force=True)
        q = (data or {}).get('query', '')
        if not q:
            return jsonify({'error': 'empty_query'}), 400

        results = {'query': q, 'sources': []}

        # DuckDuckGo Instant Answer API
        try:
            ddg = requests.get('https://api.duckduckgo.com/', params={
                'q': q,
                'format': 'json',
                'no_html': 1,
                'skip_disambig': 1
            }, timeout=8)
            if ddg.ok:
                jd = ddg.json()
                # Get main abstract
                abstract = jd.get('AbstractText', '')
                if abstract:
                    results['sources'].append({
                        'source': 'DuckDuckGo',
                        'type': 'main',
                        'text': abstract,
                        'url': jd.get('AbstractURL'),
                        'title': jd.get('Heading', '')
                    })
                # Get related topics
                if jd.get('RelatedTopics'):
                    for topic in jd.get('RelatedTopics')[:3]:
                        if isinstance(topic, dict) and topic.get('Text'):
                            results['sources'].append({
                                'source': 'DuckDuckGo',
                                'type': 'related',
                                'text': topic.get('Text'),
                                'url': topic.get('FirstURL'),
                                'title': 'Related Topic'
                            })
        except Exception as e:
            print(f"DuckDuckGo API error: {str(e)}")

        # Wikipedia API with enhanced search
        try:
            # Search Wikipedia
            s = requests.get('https://en.wikipedia.org/w/api.php', params={
                'action': 'query',
                'list': 'search',
                'srsearch': q,
                'format': 'json',
                'srlimit': 3
            }, timeout=6)
            
            if s.ok:
                search_data = s.json()
                search_results = search_data.get('query', {}).get('search', [])
                
                for result in search_results:
                    title = result.get('title')
                    if title:
                        # Get detailed page info
                        ps = requests.get(f'https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.requote_uri(title)}', timeout=6)
                        if ps.ok:
                            page_data = ps.json()
                            results['sources'].append({
                                'source': 'Wikipedia',
                                'type': 'article',
                                'text': page_data.get('extract', ''),
                                'url': page_data.get('content_urls', {}).get('desktop', {}).get('page'),
                                'title': title,
                                'thumbnail': page_data.get('thumbnail', {}).get('source')
                            })
        except Exception as e:
            print(f"Wikipedia API error: {str(e)}")

        # Build comprehensive response
        response = {
            'query': q,
            'sources': results['sources'],
            'summary': '',
            'suggestions': []
        }

        # Create main summary
        summary_parts = []
        main_sources = [s for s in results['sources'] if s['type'] == 'main']
        if main_sources:
            summary_parts.append(main_sources[0]['text'])
        
        article_sources = [s for s in results['sources'] if s['type'] == 'article']
        for source in article_sources[:2]:
            if source['text'] and source['text'] not in summary_parts:
                summary_parts.append(source['text'])

        response['summary'] = '\n\n'.join(summary_parts)

        # Add related topics as suggestions
        related_sources = [s for s in results['sources'] if s['type'] == 'related']
        response['suggestions'] = [{'text': s['text'], 'url': s['url']} for s in related_sources]

        if response['summary']:
            return jsonify(response), 200
        return jsonify({'error': 'no_results', 'suggestions': response['suggestions']}), 200

    def run():
        try:
            app.run(host='127.0.0.1', port=8502, debug=False, use_reloader=False)
        except Exception as e:
            print(f"Flask API Error: {str(e)}")

    t = threading.Thread(target=run, daemon=True)
    t.start()

# Start the local API server
try:
    start_local_api_server()
except Exception as e:
    print(f"Error starting API server: {str(e)}")