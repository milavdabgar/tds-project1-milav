import os
import httpx
import subprocess
import sqlite3
from PIL import Image
import duckdb
import markdown
from bs4 import BeautifulSoup
import json
from pathlib import Path
from config import *

async def B3(url: str, save_path: str):
    """Fetch data from an API and save it."""
    ensure_data_path(save_path)
    real_path = get_real_path(save_path)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data from {url}")
            
        # Ensure directory exists
        os.makedirs(os.path.dirname(real_path), exist_ok=True)
        
        # Save response
        with open(real_path, 'wb') as f:
            f.write(response.content)

async def B5(db_path: str, query: str, output_path: str):
    """Run SQL query on SQLite/DuckDB database."""
    ensure_data_path(db_path)
    ensure_data_path(output_path)
    real_db = get_real_path(db_path)
    real_output = get_real_path(output_path)
    
    if db_path.endswith('.db'):
        # SQLite
        conn = sqlite3.connect(real_db)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
    else:
        # DuckDB
        conn = duckdb.connect(real_db)
        results = conn.execute(query).fetchall()
        conn.close()
        
    # Save results
    os.makedirs(os.path.dirname(real_output), exist_ok=True)
    with open(real_output, 'w') as f:
        json.dump(results, f, indent=2)

async def B6(url: str, output_path: str):
    """Scrape content from a website."""
    ensure_data_path(output_path)
    real_output = get_real_path(output_path)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch content from {url}")
            
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text content
        text = soup.get_text()
        
        # Save content
        os.makedirs(os.path.dirname(real_output), exist_ok=True)
        with open(real_output, 'w', encoding='utf-8') as f:
            f.write(text)

async def B7(image_path: str, output_path: str, width: str = None, height: str = None):
    """Process image (compress/resize)."""
    ensure_data_path(image_path)
    ensure_data_path(output_path)
    real_input = get_real_path(image_path)
    real_output = get_real_path(output_path)
    
    # Open image
    img = Image.open(real_input)
    
    # Resize if dimensions provided
    if width and height:
        img = img.resize((int(width), int(height)), Image.Resampling.LANCZOS)
    
    # Save with compression
    os.makedirs(os.path.dirname(real_output), exist_ok=True)
    img.save(real_output, optimize=True, quality=85)

async def B9(md_path: str, output_path: str):
    """Convert Markdown to HTML."""
    ensure_data_path(md_path)
    ensure_data_path(output_path)
    real_input = get_real_path(md_path)
    real_output = get_real_path(output_path)
    
    # Read markdown
    with open(real_input, 'r') as f:
        md_content = f.read()
        
    # Convert to HTML
    html = markdown.markdown(md_content)
    
    # Save HTML
    os.makedirs(os.path.dirname(real_output), exist_ok=True)
    with open(real_output, 'w') as f:
        f.write(html)

async def B10(csv_path: str, filter_column: str, filter_value: str, output_path: str):
    """Filter CSV and return as JSON."""
    ensure_data_path(csv_path)
    ensure_data_path(output_path)
    real_input = get_real_path(csv_path)
    real_output = get_real_path(output_path)
    
    # Use DuckDB to process CSV
    conn = duckdb.connect()
    conn.execute(f"""
        CREATE TABLE temp AS 
        SELECT * FROM read_csv_auto('{real_input}')
        WHERE "{filter_column}" = '{filter_value}'
    """)
    
    results = conn.execute("SELECT * FROM temp").fetchall()
    conn.close()
    
    # Save as JSON
    os.makedirs(os.path.dirname(real_output), exist_ok=True)
    with open(real_output, 'w') as f:
        json.dump(results, f, indent=2)
