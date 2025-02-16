# TDS Project 1

This project implements various data science tasks using Python. It provides a FastAPI-based web service that can handle tasks like file manipulation, git operations, audio transcription, and more.

## Running with Docker

The easiest way to run this project is using Docker:

```bash
docker run -p 8000:8000 -v $(pwd)/data:/data -e EMAIL=your@email.com milavdabgar/tds-project1:latest
```

The service will be available at http://localhost:8000

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

Successfully implemented tasks:
- A1, A3, A4, A5
- B5, B6, B7, B9, B10

## Dependencies

All dependencies are handled by the Docker container. If you want to run locally, see `requirements.txt`.
