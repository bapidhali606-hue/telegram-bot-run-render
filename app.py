import os, subprocess, signal, time
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string

app=Flask(__name__)
BASE=Path(os.getenv("BOT_DATA_DIR","./bot_data")); BASE.mkdir(parents=True,exist_ok=True)
KEY=os.getenv("RUNTIME_API_KEY","ZX")
PROCS={}

def auth(): return request.headers.get("Authorization","")==f"Bearer {KEY}"
def safe_id(x):
    x="".join(c for c in x if c.isalnum() or c in "-_")
    if not x: raise ValueError("Invalid bot ID")
    return x
def folder(x):
    p=BASE/safe_id(x); p.mkdir(parents=True,exist_ok=True); return p
def state(x):
    p=PROCS.get(x)
    return "running" if p and p.poll() is None else "stopped"

@app.get("/")
def home():
    return render_template_string("""<!doctype html><meta name=viewport content="width=device-width,initial-scale=1">
<title>ZX OM FF BOT HOSTING</title><style>
body{margin:0;background:#050706;color:#eee;font:15px Arial}.w{max-width:950px;margin:auto;padding:20px}
.c{background:#0c100d;border:1px solid #26352b;border-radius:18px;padding:20px;margin:15px 0}
h1{color:#39ff88}input,button{width:100%;box-sizing:border-box;padding:13px;margin:6px 0;border-radius:10px}
input{background:#050605;color:white;border:1px solid #344238}button{border:0;background:#39ff88;font-weight:bold}
pre{background:#000;padding:15px;min-height:180px;white-space:pre-wrap;overflow:auto}.row{display:grid;grid-template-columns:repeat(4,1fr);gap:7px}
</style><div class=w><h1>ZX OM FF BOT HOSTING</h1>
<div class=c><input id=k type=password placeholder="Runtime API Key"><input id=i placeholder="Bot ID">
<input id=p type=file accept=.py><input id=r type=file accept=.txt>
<button onclick=upload()>UPLOAD BOT</button><div class=row>
<button onclick=act('start')>START</button><button onclick=act('stop')>STOP</button>
<button onclick=act('restart')>RESTART</button><button onclick=stat()>STATUS</button></div></div>
<div class=c><b id=s>Status: -</b><h3>Logs</h3><pre id=l>No logs yet.</pre><button onclick=logs()>REFRESH LOGS</button></div>
<p style="text-align:center;color:#69756d">Created by ZX OM FF</p></div>
<script>
const H=()=>({Authorization:"Bearer "+k.value}),I=()=>encodeURIComponent(i.value.trim());
async function upload(){if(!p.files[0])return alert("Select bot.py");let f=new FormData();f.append("bot.py",p.files[0]);if(r.files[0])f.append("requirements.txt",r.files[0]);let x=await fetch("/bots/"+I()+"/files",{method:"POST",headers:H(),body:f});alert(await x.text())}
async function act(a){let x=await (await fetch("/bots/"+I()+"/"+a,{method:"POST",headers:H()})).json();s.textContent="Status: "+(x.status||x.error);logs()}
async function stat(){let x=await (await fetch("/bots/"+I()+"/status",{headers:H()})).json();s.textContent="Status: "+(x.status||x.error)}
async function logs(){let x=await (await fetch("/bots/"+I()+"/logs",{headers:H()})).json();l.textContent=x.logs||x.error||""}
</script>""")

@app.get("/health")
def health(): return jsonify(status="online",service="ZX OM FF BOT HOSTING")

@app.post("/bots/<bid>/files")
def upload(bid):
    if not auth(): return jsonify(error="Unauthorized"),401
    d=folder(bid); saved=[]
    for n in ("bot.py","requirements.txt"):
        f=request.files.get(n)
        if f: f.save(d/n); saved.append(n)
    return jsonify(ok=True,saved=saved)

@app.post("/bots/<bid>/<action>")
def action(bid,action):
    if not auth(): return jsonify(error="Unauthorized"),401
    if action not in ("start","stop","restart"): return jsonify(error="Invalid action"),400
    d=folder(bid); p=PROCS.get(bid)
    if action in ("stop","restart") and p and p.poll() is None:
        try: os.killpg(os.getpgid(p.pid),signal.SIGTERM)
        except: pass
        PROCS.pop(bid,None)
    if action in ("start","restart"):
        py=d/"bot.py"
        if not py.exists(): return jsonify(error="Upload bot.py first"),400
        log=open(d/"runtime.log","a",encoding="utf8")
        log.write("\\n["+time.ctime()+"] Starting bot\\n");log.flush()
        PROCS[bid]=subprocess.Popen(["python",str(py)],cwd=d,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    return jsonify(ok=True,status=state(bid))

@app.get("/bots/<bid>/status")
def status(bid):
    if not auth(): return jsonify(error="Unauthorized"),401
    return jsonify(status=state(bid))

@app.get("/bots/<bid>/logs")
def logs(bid):
    if not auth(): return jsonify(error="Unauthorized"),401
    p=folder(bid)/"runtime.log"
    return jsonify(logs=p.read_text(errors="replace")[-20000:] if p.exists() else "")

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.getenv("PORT","8000")))
