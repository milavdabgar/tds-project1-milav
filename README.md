# TDS Project 1

This project implements various data science tasks using Python. It provides a FastAPI-based web service that can handle tasks like file manipulation, git operations, audio transcription, and more.

## Running with Docker

The project is available as a Docker image on Docker Hub:
[milavdabgar/tds-project1](https://hub.docker.com/r/milavdabgar/tds-project1)

To run the project:

```bash
docker run -p 8000:8000 -e AIPROXY_TOKEN=$AIPROXY_TOKEN milavdabgar/tds-project1:latest
```

The service will be available at http://localhost:8000

Note: The AIPROXY_TOKEN environment variable must be set to a valid token for AI operations to work.

## Environment Variables

- `EMAIL`: Your email address (required)
- `AIPROXY_TOKEN`: Token for AI proxy (optional)

## Project Structure

- `app.py`: FastAPI application and task router
- `tasksA.py`: Implementation of Phase A tasks
- `tasksB.py`: Implementation of Phase B tasks
- `config.py`: Configuration and utility functions
- `evaluate.py`: Test script to evaluate task implementations

## Current Status

Current Test Status (13/18):

Phase A (7/10):
- ✅ A1: Run datagen.py script
- ❌ A2: Format markdown with prettier
- ✅ A3: Count Wednesdays in dates
- ✅ A4: Sort contacts by name
- ✅ A5: Extract recent log lines
- ✅ A6: Create markdown index
- ✅ A7: Extract email sender
- ❌ A8: Extract credit card number
- ❌ A9: Find similar comments
- ✅ A10: Calculate ticket sales

Phase B (6/8):
- ✅ B3: Fetch API data
- ❌ B4: Git repository operations
- ✅ B5: Run SQL query
- ✅ B6: Extract webpage heading
- ✅ B7: Resize image
- ❌ B8: Audio transcription
- ✅ B9: Convert markdown to HTML
- ✅ B10: Filter CSV data

## Dependencies

All dependencies are handled by the Docker container. If you want to run locally, see `requirements.txt`.
