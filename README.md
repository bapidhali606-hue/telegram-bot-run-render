# ZX OM FF BOT HOSTING — ALL IN ONE

## One deployment
Upload this repository to GitHub and connect it to Render as a Web Service.

Build:
pip install -r requirements.txt

Start:
gunicorn --bind 0.0.0.0:$PORT app:app

Environment:
RUNTIME_API_KEY=ZX

After deployment, your Render URL is the BOT_RUNTIME_URL.
Example:
https://your-service.onrender.com

Health:
https://your-service.onrender.com/health

## Important
This service executes uploaded Python code. Use it only for trusted bots. Public multi-user hosting needs sandboxing, quotas, authentication and process isolation.
