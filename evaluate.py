# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "faker",
#     "httpx",
#     "numpy",
#     "pillow",
#     "python-dateutil",
# ]
# ///
import hashlib
import httpx
import json
import logging
import numpy as np
import os
import re
import subprocess
from dateutil.parser import parse
from datagen import (
    get_markdown,
    get_dates,
    get_contacts,
    get_logs,
    get_docs,
    get_email,
    get_credit_card,
    get_comments,
    get_tickets,
)


openai_api_base = os.getenv("OPENAI_API_BASE", "https://aiproxy.sanand.workers.dev/openai/v1")
openai_api_key = os.getenv("OPENAI_API_KEY")


def num(str):
    return int(hashlib.sha256(str.encode()).hexdigest(), 16) % (2**32)


def mismatch(msg, expected, result):
    logging.error(f"🔴 {msg}\n⚠️ EXPECTED:\n{expected}\n⚠️ RESULT:\n{result}")
    return False


async def run(task: str):
    async with httpx.AsyncClient(timeout=30) as client:
        logging.warning(f"🟡 Running task: {task.strip()}")
        response = await client.post("http://localhost:8000/run", params={"task": task})
        try:
            response_text = json.dumps(response.json(), indent=2)
        except json.JSONDecodeError:
            response_text = response.text
        if response.status_code < 400:
            logging.info(f"🟢 HTTP {response.status_code} {response_text}")
        else:
            logging.error(f"🔴 HTTP {response.status_code} {response_text}")
        return response.status_code, response_text


async def read(path: str):
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(f"http://localhost:8000/read?path={path}")
        if response.status_code != 200:
            raise Exception(f"Cannot read {path}")
        return response.text


async def a1(email: str, **kwargs):
    await run(
        f"""
Install `uv` (if required) and run the script `https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py`
with `{email}` as the only argument
"""
    )
    return email in await read("/data/format.md")


async def a2(email: str, file: str = "/data/format.md", **kwargs):
    original = get_markdown(email)
    expected = subprocess.run(
        ["npx", "prettier@3.4.2", "--stdin-filepath", file],
        input=original,
        capture_output=True,
        text=True,
        check=True,
        # Ensure npx is picked up from the PATH on Windows
        shell=True,
    ).stdout
    result = await run(
        f"""
Format the contents of `{file}` using `prettier@3.4.2`, updating the file in-place
"""
    )
    result = await read(file)
    if result != expected:
        return mismatch(file, expected, result)
    return True


async def a3(email, **kwargs):
    dates = get_dates(email)
    await run(
        "The file `/data/dates.txt` contains a list of dates, one per line. Count the number of Wednesdays in the list, and write just the number to `/data/dates-wednesdays.txt`"
    )
    result = await read("/data/dates-wednesdays.txt")
    expected = sum(1 for date in dates if parse(date).weekday() == 2)
    if result.strip() != str(expected):
        return mismatch("/data/dates-wednesdays.txt", expected, result)
    return True


async def a4(email, **kwargs):
    contacts = get_contacts(email)
    contacts.sort(key=lambda c: (c["last_name"], c["first_name"]))
    await run(
        "Sort the array of contacts in `/data/contacts.json` by `last_name`, then `first_name`, and write the result to `/data/contacts-sorted.json`"
    )
    result = await read("/data/contacts-sorted.json")
    try:
        result = json.loads(result)
    except json.JSONDecodeError:
        logging.error("🔴 /data/contacts-sorted.json was not valid JSON")
        return False
    if json.dumps(result, sort_keys=True) != json.dumps(contacts, sort_keys=True):
        return mismatch("/data/contacts-sorted.json", contacts, result)
    return True


async def a5(email, **kwargs):
    files = get_logs(email)
    files.sort(key=lambda f: f[0])
    expected = "".join([f[1].split("\n")[0] + "\n" for f in files[:10]])
    await run(
        "Write the first line of the 10 most recent `.log` file in `/data/logs/` to `/data/logs-recent.txt`, most recent first"
    )
    result = await read("/data/logs-recent.txt")
    if result.strip() != expected.strip():
        return mismatch("/data/logs-recent.txt", expected, result)
    return True


# TODO: Verify after datagen
async def a6(email, **kwargs):
    docs = get_docs(email)
    await run(
        """Find all Markdown (`.md`) files in `/data/docs/`.
For each file, extract the first occurrance of each H1 (i.e. a line starting with `# `).
Create an index file `/data/docs/index.json` that maps each filename (without the `/data/docs/` prefix) to its title
(e.g. `{"README.md": "Home", "path/to/large-language-models.md": "Large Language Models", ...}`)"""
    )
    expected = {}
    for dir, file, text in docs:
        # get the first line starting with #
        for line in text.split("\n"):
            if line.startswith("# "):
                title = line[2:].strip()
                break
        expected[f"{dir}/{file}.md"] = title
    result = await read("/data/docs/index.json")
    try:
        result = json.loads(result)
    except json.JSONDecodeError:
        logging.error("🔴 /data/docs/index.json was not valid JSON")
        return False
    if json.dumps(result, sort_keys=True) != json.dumps(expected, sort_keys=True):
        return mismatch("/data/docs/index.json", expected, result)
    return True


async def a7(email, **kwargs):
    expected = get_email(email)["from_email"]
    await run(
        "`/data/email.txt` contains an email message. Pass the content to an LLM with instructions to extract the sender's email address, and write just the email address to `/data/email-sender.txt`"
    )
    result = await read("/data/email-sender.txt")
    if result != expected:
        return mismatch("/data/email-sender.txt", expected, result)
    return True


async def a8(email, **kwargs):
    data = get_credit_card(email)
    await run(
        "`/data/credit_card.png` contains a credit card number. Pass the image to an LLM, have it extract the card number, and write it without spaces to `/data/credit-card.txt`"
    )
    result = await read("/data/credit-card.txt")
    if re.sub(r"\D", "", result) != re.sub(r"\D", "", data["number"]):
        return mismatch("/data/credit-card.txt", data["number"], result)
    return True


async def a9(email, **kwargs):
    data = get_comments(email)
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{openai_api_base}/embeddings",
            headers={"Authorization": f"Bearer {openai_api_key}"},
            json={"model": "text-embedding-3-small", "input": data},
        )
    embeddings = np.array([emb["embedding"] for emb in response.json()["data"]])
    similarity = np.dot(embeddings, embeddings.T)
    # Create mask to ignore diagonal (self-similarity)
    np.fill_diagonal(similarity, -np.inf)
    # Get indices of maximum similarity
    i, j = np.unravel_index(similarity.argmax(), similarity.shape)
    expected = "\n".join(sorted([data[i], data[j]]))
    await run(
        "`/data/comments.txt` contains a list of comments, one per line. Using embeddings, find the most similar pair of comments and write them to `/data/comments-similar.txt`, one per line"
    )
    result = await read("/data/comments-similar.txt")
    sorted_result = "\n".join(sorted([line for line in result.split("\n") if line.strip()]))
    if sorted_result != expected:
        return mismatch("/data/comments-similar.txt", expected, result)
    return True


async def a10(email, **kwargs):
    data = get_tickets(email)
    await run(
        'The SQLite database file `/data/ticket-sales.db` has a `tickets` with columns `type`, `units`, and `price`. Each row is a customer bid for a concert ticket. What is the total sales of all the items in the "Gold" ticket type? Write the number in `/data/ticket-sales-gold.txt`'
    )
    result = await read("/data/ticket-sales-gold.txt")
    expected = sum(row[1] * row[2] for row in data if row[0].lower() == "gold")
    try:
        result = float(result)
    except ValueError:
        logging.error(f"🔴 /data/ticket-sales-gold.txt was {result}, not a valid number")
        return False
    if abs(result - expected) > 0.1:
        return mismatch("/data/ticket-sales-gold.txt", expected, result)
    return True


async def main(email: str):
    score, total = 0, 0
    logging.info("\n🔵 Phase A: Basic Tasks")
    for task in [a1, a2, a3, a4, a5, a6, a7, a8, a9, a10]:
        total += 1
        try:
            success = await task(email=email)
        except Exception as e:
            logging.error(f"🔴 {task.__name__.upper()} failed: {e}")
            success = False
        if success:
            logging.info(f"✅ {task.__name__.upper()} PASSED")
        else:
            logging.error(f"❌ {task.__name__.upper()} FAILED")
        score += 1 if success else 0
    
    logging.info("\n🔵 Phase B: Business Tasks")
    for task in [b3, b4, b5, b6, b7, b8, b9, b10]:
        total += 1
        try:
            success = await task(email=email)
        except Exception as e:
            logging.error(f"🔴 {task.__name__.upper()} failed: {e}")
            success = False
        if success:
            logging.info(f"✅ {task.__name__.upper()} PASSED")
        else:
            logging.error(f"❌ {task.__name__.upper()} FAILED")
        score += 1 if success else 0
    
    logging.info(f"\n🎯 Final Score: {score} / {total}")


async def b4(email, **kwargs):
    """Test B4: Clone a git repo and make a commit"""
    test_repo = "https://github.com/milavdabgar/my-email-repo"
    repo_name = test_repo.split('/')[-1].replace('.git', '')
    await run(f"Clone the git repo {test_repo} and make a commit with message 'Test commit'")
    try:
        content = await read(f"/data/{repo_name}/test.txt")
        return "Test commit" in content
    except Exception as e:
        logging.error(f"🔴 B4 failed: {str(e)}")
        return False

async def b8(email, **kwargs):
    """Test B8: Transcribe audio from an MP3 file"""
    input_path = "/data/test.mp3"
    output_path = "/data/transcription.txt"
    await run(f"Transcribe the audio from {input_path} and save the transcription to {output_path}")
    try:
        content = await read(output_path)
        return len(content) > 0  # For now, just check if we got any output
    except Exception as e:
        logging.error(f"🔴 B8 failed: {str(e)}")
        return False

async def b3(email, **kwargs):
    """Test B3: Fetch data from an API and save it"""
    api_url = "https://jsonplaceholder.typicode.com/posts/1"
    output_file = "/data/api_data.json"
    await run(f"Fetch data from the API {api_url} and save it to {output_file}")
    try:
        content = await read(output_file)
        data = json.loads(content)
        return isinstance(data, dict) and "id" in data and "title" in data
    except Exception as e:
        logging.error(f"🔴 B3 failed: {str(e)}")
        return False

async def b5(email, **kwargs):
    """Test B5: Run a SQL query on a SQLite database"""
    db_path = "/data/ticket-sales.db"
    query = "SELECT type, SUM(units) as total_units FROM tickets GROUP BY type"
    output_path = "/data/ticket-stats.json"
    await run(f"Run the SQL query '{query}' on the database {db_path} and save the results as JSON to {output_path}")
    try:
        content = await read(output_path)
        data = json.loads(content)
        return isinstance(data, list) and len(data) > 0 and all(isinstance(row, dict) for row in data)
    except Exception as e:
        logging.error(f"🔴 B5 failed: {str(e)}")
        return False

async def b6(email, **kwargs):
    """Test B6: Extract data from a website"""
    url = "https://example.com"
    output_path = "/data/website.txt"
    await run(f"Extract the main heading (h1) from {url} and save it to {output_path}")
    try:
        content = await read(output_path)
        return "Example Domain" in content
    except Exception as e:
        logging.error(f"🔴 B6 failed: {str(e)}")
        return False

async def b7(email, **kwargs):
    """Test B7: Compress or resize an image"""
    input_path = "/data/credit_card.png"
    output_path = "/data/credit_card_small.jpg"
    await run(f"Resize the image {input_path} to 50% of its original size and save as JPEG to {output_path}")
    try:
        content = await read(output_path)
        return len(content) > 0
    except Exception as e:
        logging.error(f"🔴 B7 failed: {str(e)}")
        return False

async def b9(email, **kwargs):
    """Test B9: Convert Markdown to HTML"""
    md_path = "/data/format.md"
    output_path = "/data/format.html"
    await run(f"Convert the Markdown file {md_path} to HTML and save it to {output_path}")
    try:
        content = await read(output_path)
        return "<html" in content.lower() and "</html>" in content.lower()
    except Exception as e:
        logging.error(f"🔴 B9 failed: {str(e)}")
        return False

async def b10(email, **kwargs):
    """Test B10: Write an API endpoint that filters a CSV file"""
    csv_path = "/data/contacts.csv"
    filter_column = "last_name"
    filter_value = "Smith"
    output_path = "/data/filtered_contacts.json"
    await run(f"Filter the CSV file {csv_path} where {filter_column} equals '{filter_value}' and save the results as JSON to {output_path}")
    try:
        content = await read(output_path)
        data = json.loads(content)
        return isinstance(data, list) and all(row.get(filter_column) == filter_value for row in data)
    except Exception as e:
        logging.error(f"🔴 B10 failed: {str(e)}")
        return False

if __name__ == "__main__":
    import asyncio
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate tasks with configurable logging")
    parser.add_argument("--email", default="user@example.com", help="Set the email address")
    levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    parser.add_argument("--log-level", default="INFO", choices=levels, help="Set logging level")
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level, format="%(message)s\n")
    asyncio.run(main(args.email))
