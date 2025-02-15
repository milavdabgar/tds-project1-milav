from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import httpx
from tasksA import *
from tasksB import *
from config import *

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.post("/run")
async def run_task(task: str = Query(..., description="Task description")):
    """Execute a task based on the provided description."""
    try:
        # Extract task type and parameters using LLM
        task_info = await get_task_info(task)
        
        # Execute the appropriate task
        if task_info["task_type"].startswith("A"):
            result = await execute_task_a(task_info)
        else:
            result = await execute_task_b(task_info)
            
        return {"status": "success", "message": "Task completed successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/read")
async def read_file(path: str = Query(..., description="File path to read")):
    """Read and return the contents of a file."""
    try:
        # Ensure path is within data directory
        ensure_data_path(path)
        real_path = get_real_path(path)
        
        if not os.path.exists(real_path):
            raise HTTPException(status_code=404, detail=f"File not found: {path}")
            
        with open(real_path, "r") as f:
            content = f.read()
            
        return PlainTextResponse(content)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

async def get_task_info(task_description: str):
    """Use LLM to parse task description and identify the task type and parameters."""
    system_prompt = """You are a task parser. Given a task description, identify the task type (A1-A10, B1-B10) and extract relevant parameters.
    For Task A1: Return {"task_type": "A1", "parameters": {"email": "<email>"}}
    For Task A2: Return {"task_type": "A2", "parameters": {"prettier_version": "prettier@3.4.2", "filename": "/data/format.md"}}
    For Task A3: Return {"task_type": "A3", "parameters": {"filename": "/data/dates.txt", "targetfile": "/data/dates-wednesdays.txt"}}
    For Task A4: Return {"task_type": "A4", "parameters": {"filename": "/data/contacts.json", "targetfile": "/data/contacts-sorted.json"}}
    For Task A5: Return {"task_type": "A5", "parameters": {"log_dir": "/data/logs", "output_file": "/data/logs-recent.txt", "num_files": 10}}
    For Task A6: Return {"task_type": "A6", "parameters": {"doc_dir": "/data/docs", "output_file": "/data/docs/index.json"}}
    For Task A7: Return {"task_type": "A7", "parameters": {"filename": "/data/email.txt", "output_file": "/data/email-sender.txt"}}
    For Task A8: Return {"task_type": "A8", "parameters": {"image_path": "/data/credit-card.png", "output_file": "/data/credit-card.txt"}}
    For Task A9: Return {"task_type": "A9", "parameters": {"filename": "/data/comments.txt", "output_file": "/data/comments-similar.txt"}}
    For Task A10: Return {"task_type": "A10", "parameters": {"db_path": "/data/ticket-sales.db", "output_file": "/data/ticket-sales-gold.txt"}}
    For Task B3: Return {"task_type": "B3", "parameters": {"url": "<api_url>", "save_path": "/data/<output_file>"}}
    For Task B5: Return {"task_type": "B5", "parameters": {"db_path": "<db_path>", "query": "<sql_query>", "output_path": "/data/<output_file>"}}
    For Task B6: Return {"task_type": "B6", "parameters": {"url": "<website_url>", "output_path": "/data/<output_file>"}}
    For Task B7: Return {"task_type": "B7", "parameters": {"image_path": "<input_image>", "output_path": "/data/<output_file>", "width": "<width>", "height": "<height>"}}
    For Task B9: Return {"task_type": "B9", "parameters": {"md_path": "<markdown_file>", "output_path": "/data/<output_file>"}}
    For Task B10: Return {"task_type": "B10", "parameters": {"csv_path": "<csv_file>", "filter_column": "<column>", "filter_value": "<value>", "output_path": "/data/<output_file>"}}
    Return ONLY the JSON object."""
    
    print(f"Task description: {task_description}")  # Debug log
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {AIPROXY_TOKEN}"}
            response = await client.post(
                OPENAI_CHAT_URL,
                headers=headers,
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": task_description}
                    ]
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=f"Failed to parse task using LLM: {response.text}")
                
            result = response.json()
            task_info = json.loads(result["choices"][0]["message"]["content"])
            print(f"Parsed task info: {task_info}")  # Debug log
            return task_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse task using LLM: {str(e)}")

async def execute_task_a(task_info):
    """Execute Phase A tasks."""
    task_type = task_info["task_type"]
    params = task_info["parameters"]
    
    if task_type == "A1":
        return await A1(params["email"])
    elif task_type == "A2":
        return await A2(params.get("prettier_version", "prettier@3.4.2"), params.get("filename", "/data/format.md"))
    elif task_type == "A3":
        return await A3(params.get("filename", "/data/dates.txt"), params.get("targetfile", "/data/dates-wednesdays.txt"))
    elif task_type == "A4":
        return await A4(params.get("filename", "/data/contacts.json"), params.get("targetfile", "/data/contacts-sorted.json"))
    elif task_type == "A5":
        return await A5(params.get("log_dir", "/data/logs"), params.get("output_file", "/data/logs-recent.txt"), params.get("num_files", 10))
    elif task_type == "A6":
        return await A6(params.get("doc_dir", "/data/docs"), params.get("output_file", "/data/docs/index.json"))
    elif task_type == "A7":
        return await A7(params.get("filename", "/data/email.txt"), params.get("output_file", "/data/email-sender.txt"))
    elif task_type == "A8":
        return await A8(params.get("image_path", "/data/credit-card.png"), params.get("output_file", "/data/credit-card.txt"))
    elif task_type == "A9":
        return await A9(params.get("filename", "/data/comments.txt"), params.get("output_file", "/data/comments-similar.txt"))
    elif task_type == "A10":
        return await A10(params.get("db_path", "/data/ticket-sales.db"), params.get("output_file", "/data/ticket-sales-gold.txt"))
    else:
        raise ValueError(f"Unknown task type: {task_type}")

async def execute_task_b(task_info):
    """Execute Phase B tasks."""
    task_type = task_info["task_type"]
    params = task_info["parameters"]
    
    if task_type == "B3":
        return await B3(params.get("url"), params.get("save_path", "/data/api_response.json"))
    elif task_type == "B5":
        return await B5(params.get("db_path"), params.get("query"), params.get("output_path", "/data/query_results.json"))
    elif task_type == "B6":
        return await B6(params.get("url"), params.get("output_path", "/data/scraped_content.txt"))
    elif task_type == "B7":
        return await B7(
            params.get("image_path"), 
            params.get("output_path", "/data/processed_image.jpg"),
            params.get("width"),
            params.get("height")
        )
    elif task_type == "B9":
        return await B9(params.get("md_path"), params.get("output_path", "/data/converted.html"))
    elif task_type == "B10":
        return await B10(
            params.get("csv_path"),
            params.get("filter_column"),
            params.get("filter_value"),
            params.get("output_path", "/data/filtered.json")
        )
    else:
        raise ValueError(f"Unknown task type: {task_type}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
