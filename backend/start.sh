#!/bin/bash
cd backend
uvicorn api_sample:app --host 0.0.0.0 --port 10000
