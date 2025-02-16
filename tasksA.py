import os
import json
import httpx
import base64
from datetime import datetime
import sqlite3
import subprocess
from dateutil import parser
import numpy as np
from scipy.spatial.distance import cdist
from config import *
from PIL import Image

async def A1(email: str):
    """Install uv and run datagen.py with email as argument."""
    try:
        # Run datagen.py with email
        result = subprocess.run(f"python datagen.py {email}", shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Error running datagen.py: {result.stderr}")
        return result.stdout
    except Exception as e:
        raise Exception(f"Failed to run datagen.py: {str(e)}")

async def A2(prettier_version: str = "prettier@3.4.2", filename: str = "/data/format.md"):
    """Format markdown file using prettier."""
    ensure_data_path(filename)
    real_path = get_real_path(filename)
    
    try:
        # Format the file in place
        with open(real_path, 'r') as f:
            content = f.read()
            
        # Create a temporary directory for node_modules
        temp_dir = "/tmp/prettier_temp"
        os.makedirs(temp_dir, exist_ok=True)
        os.chdir(temp_dir)
        
        # Install prettier locally
        install_result = subprocess.run(["npm", "install", prettier_version], capture_output=True, text=True)
        if install_result.returncode != 0:
            raise Exception(f"Error installing prettier: {install_result.stderr}")
            
        # Run prettier using node directly
        prettier_path = os.path.join(temp_dir, "node_modules", ".bin", "prettier")
        result = subprocess.run([prettier_path, "--stdin-filepath", real_path], 
                               input=content, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Error formatting file: {result.stderr}")
            
        # Write the formatted content back to the file
        with open(real_path, 'w') as f:
            f.write(result.stdout)
            
        # Clean up
        subprocess.run(["rm", "-rf", temp_dir])
        return "File formatted successfully"
    except Exception as e:
        # Clean up in case of error
        subprocess.run(["rm", "-rf", temp_dir])
        raise Exception(f"Failed to format file: {str(e)}")

async def A3(filename: str = '/data/dates.txt', targetfile: str = '/data/dates-wednesdays.txt'):
    """Count Wednesdays in a list of dates."""
    ensure_data_path(filename)
    ensure_data_path(targetfile)
    real_input = get_real_path(filename)
    real_output = get_real_path(targetfile)
    
    try:
        # Read dates from file
        with open(real_input, 'r') as f:
            dates = f.readlines()
        
        # Count Wednesdays
        wednesday_count = 0
        for date_str in dates:
            date_str = date_str.strip()
            if not date_str:
                continue
            try:
                date = parser.parse(date_str)
                if date.weekday() == 2:  # Wednesday is 2 (0 is Monday)
                    wednesday_count += 1
            except:
                continue
        
        # Write result to output file
        with open(real_output, 'w') as f:
            f.write(str(wednesday_count))
            
        return f"Found {wednesday_count} Wednesdays"
    except Exception as e:
        raise Exception(f"Failed to process dates: {str(e)}")

async def A4(filename: str = "/data/contacts.json", targetfile: str = "/data/contacts-sorted.json"):
    """Sort contacts by last_name, then first_name."""
    ensure_data_path(filename)
    ensure_data_path(targetfile)
    real_input = get_real_path(filename)
    real_output = get_real_path(targetfile)
    
    with open(real_input, 'r') as f:
        contacts = json.load(f)
        
    sorted_contacts = sorted(contacts, key=lambda x: (x['last_name'], x['first_name']))
    
    with open(real_output, 'w') as f:
        json.dump(sorted_contacts, f, indent=2)

async def A5(log_dir: str = '/data/logs', output_file: str = '/data/logs-recent.txt', num_files: int = 10):
    """Extract first lines from recent log files."""
    ensure_data_path(log_dir)
    ensure_data_path(output_file)
    real_log_dir = get_real_path(log_dir)
    real_output = get_real_path(output_file)
    
    # Get all .log files with their modification times
    log_files = []
    for file in Path(real_log_dir).glob("*.log"):
        log_files.append((file, os.path.getmtime(file)))
        
    # Sort by modification time (newest first) and take top 10
    recent_files = sorted(log_files, key=lambda x: x[1], reverse=True)[:num_files]
    
    # Extract first line from each file
    first_lines = []
    for file, _ in recent_files:
        with open(file, 'r') as f:
            first_lines.append(f.readline().strip())
            
    # Write results
    with open(real_output, 'w') as f:
        f.write('\n'.join(first_lines))

async def A6(doc_dir: str = '/data/docs', output_file: str = '/data/docs/index.json'):
    """Create index of markdown file titles."""
    ensure_data_path(doc_dir)
    ensure_data_path(output_file)
    real_doc_dir = get_real_path(doc_dir)
    real_output = get_real_path(output_file)
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(real_output), exist_ok=True)
    
    # Process markdown files
    index = {}
    for root, _, files in sorted(os.walk(real_doc_dir)):
        for file in sorted(files):
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, real_doc_dir)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('# '):  # First H1 found
                            index[relative_path] = line[2:].strip()
                            break
    
    # Sort the index by keys
    sorted_index = dict(sorted(index.items()))
    
    # Write index to file
    with open(real_output, 'w', encoding='utf-8') as f:
        json.dump(sorted_index, f, indent=4)

async def A7(filename: str = '/data/email.txt', output_file: str = '/data/email-sender.txt'):
    """Extract sender's email using LLM."""
    ensure_data_path(filename)
    ensure_data_path(output_file)
    real_input = get_real_path(filename)
    real_output = get_real_path(output_file)
    
    with open(real_input, 'r') as f:
        email_content = f.read()
        
    async with httpx.AsyncClient() as client:
        response = await client.post(
            OPENAI_CHAT_URL,
            headers={"Authorization": f"Bearer {AIPROXY_TOKEN}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": "Extract the sender's email address from this email message. Return only the email address, nothing else."
                    },
                    {
                        "role": "user",
                        "content": email_content
                    }
                ]
            }
        )
        
        if response.status_code != 200:
            raise Exception("Failed to extract email using LLM")
            
        result = response.json()
        email_address = result["choices"][0]["message"]["content"].strip()
        
        with open(real_output, 'w') as f:
            f.write(email_address)

async def A8(image_path: str = '/data/credit_card.png', output_file: str = '/data/credit-card.txt'):
    """Extract credit card number from image."""
    ensure_data_path(image_path)
    ensure_data_path(output_file)
    real_input = get_real_path(image_path)
    real_output = get_real_path(output_file)
    
    try:
        # Validate and preprocess image
        img = Image.open(real_input)
        img = img.convert('RGB')  # Convert to RGB to ensure compatibility
        
        # Save as temporary PNG for consistent format
        temp_path = os.path.join(os.path.dirname(real_input), 'temp.png')
        img.save(temp_path, format='PNG')
        
        # Read and encode image
        with open(temp_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
            
        # Clean up temp file
        os.remove(temp_path)
            
        # Make API call
        headers = {"Authorization": f"Bearer {AIPROXY_TOKEN}", "Content-Type": "application/json"}
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user", 
                    "content": [
                        {
                            "type": "text",
                            "text": "This image contains a credit card number. Extract ONLY the sequence of digits that represents the credit card number. Return ONLY the digits with no spaces or formatting. The number should be between 13-19 digits long."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_data}"
                            }
                        }
                    ]
                }
            ]
        }
        
        base_url = os.getenv("OPENAI_API_BASE_URL", "http://aiproxy.sanand.workers.dev/openai/v1")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.text}")
                
            result = response.json()
            card_number = ''.join(c for c in result["choices"][0]["message"]["content"] if c.isdigit())
            
            # Validate card number length
            if not card_number.isdigit() or len(card_number) < 13 or len(card_number) > 19:
                raise Exception(f"Invalid card number format: {card_number}")
            
            with open(real_output, 'w') as f:
                f.write(card_number)
            return f"Successfully extracted card number: {card_number}"
            
    except Exception as e:
        raise Exception(f"Failed to extract card number: {str(e)}")

async def A9(filename: str = '/data/comments.txt', output_file: str = '/data/comments-similar.txt'):
    """Find most similar comments using embeddings."""
    ensure_data_path(filename)
    ensure_data_path(output_file)
    real_input = get_real_path(filename)
    real_output = get_real_path(output_file)
    
    try:
        # Read comments
        with open(real_input, 'r') as f:
            comments = [line.strip() for line in f if line.strip()]
            
        if len(comments) < 2:
            raise Exception("Need at least 2 comments to find similarities")
            
        # Get embeddings for all comments at once
        async with httpx.AsyncClient() as client:
            response = await client.post(
                OPENAI_EMBEDDINGS_URL,
                headers={"Authorization": f"Bearer {AIPROXY_TOKEN}"},
                json={
                    "model": "text-embedding-3-small",
                    "input": comments
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get embeddings: {response.text}")
                
            result = response.json()
            embeddings = [item["embedding"] for item in result["data"]]
                
        # Convert to numpy array for efficient computation
        embeddings_array = np.array(embeddings)
        
        # Calculate cosine similarities between all pairs
        similarities = 1 - cdist(embeddings_array, embeddings_array, metric='cosine')
        
        # Find most similar pair
        np.fill_diagonal(similarities, -1)  # Exclude self-similarity
        max_sim_idx = np.unravel_index(np.argmax(similarities), similarities.shape)
        
        # Write result to file
        with open(real_output, 'w') as f:
            f.write(f"{comments[max_sim_idx[0]]}\n{comments[max_sim_idx[1]]}")
            
        return "Successfully found most similar comments"
        
    except Exception as e:
        raise Exception(f"Failed to find similar comments: {str(e)}")

async def A10(db_path: str = '/data/ticket-sales.db', output_file: str = '/data/ticket-sales-gold.txt'):
    """Calculate total sales for Gold tickets."""
    ensure_data_path(db_path)
    ensure_data_path(output_file)
    real_db = get_real_path(db_path)
    real_output = get_real_path(output_file)
    
    conn = sqlite3.connect(real_db)
    cursor = conn.cursor()
    
    cursor.execute("SELECT CAST(COALESCE(SUM(units * price), 0) AS FLOAT) as total FROM tickets WHERE LOWER(type) = 'gold'")
    total = cursor.fetchone()[0]
    
    conn.close()
    
    with open(real_output, 'w') as f:
        f.write(f"{total:.2f}")
