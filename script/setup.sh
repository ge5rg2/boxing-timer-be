#!/bin/bash

echo "📦 Installing virtualenv..."
python3 -m venv venv
source venv/bin/activate

echo "⬇️ Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

echo "📁 Initializing alembic..."
alembic upgrade head

echo "🚀 Running FastAPI server..."
uvicorn app.main:app --reload
