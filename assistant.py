"""
Nova AI Assistant - Powered by GROQ (100% FREE, No Quota Issues!)
==================================================================
Groq is completely free, ultra-fast, and needs no credit card.

HOW TO GET FREE GROQ API KEY (1 minute):
  1. Go to https://console.groq.com
  2. Sign up with Google
  3. Click "API Keys" → "Create API Key"
  4. Paste it below as GROQ_API_KEY

Install (one command):
  pip install groq scikit-learn numpy psutil pyautogui flask flask-cors
"""
import os, json, time, threading, subprocess, webbrowser


import numpy as np
from datetime import datetime
from pathlib import Path
import requests

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from groq import Groq
import psutil, platform
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import pickle

# pyautogui only works on desktop (not on cloud servers)
try:
    import pyautogui
    HAS_DISPLAY = True
except Exception:
    pyautogui = None
    HAS_DISPLAY = False

# spell correction
try:
    # pyrefly: ignore [missing-import]
    from textblob import TextBlob
    SPELL_CHECK = True
except ImportError:
    SPELL_CHECK = False

def fix_spelling(text):
    """Auto-correct spelling mistakes."""
    if not SPELL_CHECK:
        return text
    try:
        return str(TextBlob(text).correct())
    except Exception:
        return text

# ═══════════════════════════════════════════════════════════════════════
#  ★  PASTE YOUR FREE GROQ KEY HERE  ★
#  Get it FREE at: https://console.groq.com  (no card needed!)
# ═══════════════════════════════════════════════════════════════════════
GROQ_API_KEY   = "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"

ASSISTANT_NAME = "Jarvis"
MEMORY_FILE    = "nova_memory.json"
ML_MODEL_FILE  = "nova_ml.pkl"

# ── Keys: read from environment variables (for Render deployment) ──────────
# On Render: set these in Dashboard → Environment
# Locally:   still works from the hardcoded fallback below
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ── Groq client ────────────────────────────────────────────────────────
groq_client = Groq(api_key=GROQ_API_KEY)
GROQ_MODEL  = "llama-3.3-70b-versatile"   # free, very capable model

# ═══════════════════════════════════════════════════════════════════════
#  MEMORY
# ═══════════════════════════════════════════════════════════════════════
class Memory:
    def __init__(self):
        self.data = self._load()

    def _load(self):
        if Path(MEMORY_FILE).exists():
            with open(MEMORY_FILE) as f:
                return json.load(f)
        return {"qa_pairs": [], "commands": [], "sessions": 0}

    def save(self):
        with open(MEMORY_FILE, "w") as f:
            json.dump(self.data, f, indent=2)

    def add_qa(self, q, a):
        self.data["qa_pairs"].append({
            "q": q, "a": a, "ts": datetime.now().isoformat()
        })
        if len(self.data["qa_pairs"]) > 1000:
            self.data["qa_pairs"] = self.data["qa_pairs"][-1000:]
        self.save()

    def add_command(self, cmd, result):
        self.data["commands"].append({
            "cmd": cmd, "result": result, "ts": datetime.now().isoformat()
        })
        self.save()

    def get_context(self, query, k=3):
        pairs = self.data["qa_pairs"]
        if len(pairs) < 2:
            return ""
        try:
            texts   = [p["q"] for p in pairs]
            vec     = TfidfVectorizer(max_features=500).fit(texts)
            X       = vec.transform(texts).toarray()
            q_v     = vec.transform([query]).toarray()
            nn      = NearestNeighbors(n_neighbors=min(k, len(texts))).fit(X)
            _, idxs = nn.kneighbors(q_v)
            return "\n---\n".join(
                f"Q: {pairs[i]['q']}\nA: {pairs[i]['a']}" for i in idxs[0]
            )
        except Exception:
            return ""

# ═══════════════════════════════════════════════════════════════════════
#  ML MODEL
# ═══════════════════════════════════════════════════════════════════════
class MLModel:
    def __init__(self):
        self.labels  = []
        self.X_train = []
        if Path(ML_MODEL_FILE).exists():
            with open(ML_MODEL_FILE, "rb") as f:
                d = pickle.load(f)
                self.labels  = d.get("labels", [])
                self.X_train = d.get("X_train", [])

    def _save(self):
        with open(ML_MODEL_FILE, "wb") as f:
            pickle.dump({"labels": self.labels, "X_train": self.X_train}, f)

    def learn(self, text, label):
        self.X_train.append(text.lower())
        self.labels.append(label)
        self._save()

    def predict(self, text):
        if len(self.X_train) < 3:
            return "unknown"
        try:
            vec  = TfidfVectorizer(max_features=300).fit(self.X_train)
            X    = vec.transform(self.X_train).toarray()
            q    = vec.transform([text.lower()]).toarray()
            nn   = NearestNeighbors(n_neighbors=1).fit(X)
            _, i = nn.kneighbors(q)
            return self.labels[i[0][0]]
        except Exception:
            return "unknown"

memory   = Memory()
ml_model = MLModel()

# ═══════════════════════════════════════════════════════════════════════
#  SYSTEM CONTROL
# ═══════════════════════════════════════════════════════════════════════
class SystemControl:
    OS = platform.system()

    @staticmethod
    def open_app(name):
        # Common Windows app aliases
        WIN_APPS = {
            "notepad":      "notepad.exe",
            "calculator":   "calc.exe",
            "paint":        "mspaint.exe",
            "chrome":       "chrome.exe",
            "google chrome":"chrome.exe",
            "firefox":      "firefox.exe",
            "edge":         "msedge.exe",
            "word":         "winword.exe",
            "excel":        "excel.exe",
            "powerpoint":   "powerpnt.exe",
            "vlc":          "vlc.exe",
            "spotify":      "spotify.exe",
            "discord":      "discord.exe",
            "steam":        "steam.exe",
            "vs code":      "code.exe",
            "vscode":       "code.exe",
            "file explorer":"explorer.exe",
            "explorer":     "explorer.exe",
            "task manager": "taskmgr.exe",
            "cmd":          "cmd.exe",
            "command prompt":"cmd.exe",
            "powershell":   "powershell.exe",
            "settings":     "ms-settings:",
            "camera":       "microsoft.windows.camera:",
            "maps":         "bingmaps:",
            "clock":        "ms-clock:",
            "photos":       "ms-photos:",
            "snipping tool":"snippingtool.exe",
        }
        name_lower = name.lower().strip()
        exe = WIN_APPS.get(name_lower, name)
        try:
            if SystemControl.OS == "Windows":
                result = subprocess.Popen(exe, shell=True)
                return f"Opening {name}... Right away, sir!"
            elif SystemControl.OS == "Darwin":
                subprocess.Popen(["open", "-a", name])
                return f"Opening {name}..."
            else:
                subprocess.Popen([name_lower])
                return f"Opening {name}..."
        except Exception as e:
            return f"I couldn't find '{name}' on your system. Please check the app name."

    @staticmethod
    def close_app(name):
        killed = []
        for p in psutil.process_iter(["pid", "name"]):
            if name.lower() in p.info["name"].lower():
                p.kill()
                killed.append(p.info["name"])
        return f"Closed: {', '.join(killed)}" if killed else f"'{name}' not running"

    @staticmethod
    def open_url(url):
        if not url.startswith("http"):
            url = "https://" + url
        webbrowser.open(url)
        return f"Opened {url}"

    @staticmethod
    def search_web(query):
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        if platform.system() == "Windows":
            webbrowser.open(url)
            return f"Searched Google for: {query}"
        return f"I've prepared a search for '{query}' here: {url}"

    @staticmethod
    def youtube(query=""):
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}" if query else "https://youtube.com"
        if platform.system() == "Windows":
            webbrowser.open(url)
            return f"Opened YouTube{': ' + query if query else ''}"
        return f"I've found this on YouTube for you: {url}"

    @staticmethod
    def create_file(path, content=""):
        try:
            Path(path).write_text(content)
            return f"Created file: {path}"
        except Exception as e:
            return str(e)

    @staticmethod
    def read_file(path):
        try:
            return Path(path).read_text()[:2000]
        except Exception as e:
            return str(e)

    @staticmethod
    def list_dir(path="."):
        try:
            items = list(Path(path).iterdir())[:50]
            return "\n".join(i.name for i in items)
        except Exception as e:
            return str(e)

    @staticmethod
    def system_info():
        cpu  = psutil.cpu_percent(interval=1)
        ram  = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        bat  = psutil.sensors_battery()
        bat_info = f"  |  Battery: {int(bat.percent)}%" if bat else ""
        return (f"CPU: {cpu}%  |  RAM: {ram.percent}% "
                f"({ram.used//1024**2} MB used)  |  "
                f"Disk: {disk.percent}%{bat_info}")

    @staticmethod
    def get_time():
        return datetime.now().strftime("Time: %I:%M %p  |  Date: %A, %d %B %Y")

    @staticmethod
    def screenshot(path="screenshot.png"):
        if not HAS_DISPLAY:
            return "Screenshot not available in server mode."
        pyautogui.screenshot(path)
        return f"Screenshot saved: {path}"

    @staticmethod
    def type_text(text):
        if not HAS_DISPLAY:
            return "Typing not available in server mode."
        time.sleep(1)
        pyautogui.typewrite(text, interval=0.05)
        return f"Typed: {text}"

    @staticmethod
    def set_volume(level):
        level = max(0, min(100, level))
        if SystemControl.OS == "Darwin":
            subprocess.run(["osascript", "-e", f"set volume output volume {level}"])
        elif SystemControl.OS == "Linux":
            subprocess.run(["amixer", "-q", "sset", "Master", f"{level}%"])
        else:
            # Windows — use nircmd if available, else just report
            try:
                subprocess.run(["nircmd", "setsysvolume", str(int(level * 655.35))])
            except Exception:
                pass
        return f"Volume set to {level}%"

    @staticmethod
    def shutdown():
        cmds = {"Windows": "shutdown /s /t 5",
                "Darwin":  "sudo shutdown -h now",
                "Linux":   "sudo shutdown now"}
        subprocess.run(cmds.get(SystemControl.OS, ""), shell=True)
        return "Shutting down in 5 seconds..."

    @staticmethod
    def restart():
        cmds = {"Windows": "shutdown /r /t 5",
                "Darwin":  "sudo shutdown -r now",
                "Linux":   "sudo reboot"}
        subprocess.run(cmds.get(SystemControl.OS, ""), shell=True)
        return "Restarting in 5 seconds..."

ctrl = SystemControl()

# ═══════════════════════════════════════════════════════════════════════
#  COMMAND ROUTER
# ═══════════════════════════════════════════════════════════════════════
def extract_app_name(t, keywords):
    """Extract app name after any of the given keywords."""
    for kw in keywords:
        if kw in t:
            after = t.split(kw, 1)[1].strip()
            # remove filler words
            for filler in ["my ", "the ", "please", "now", "for me", "up"]:
                after = after.replace(filler, "")
            return after.strip()
    return ""

def route_command(text):
    t = text.lower().strip()
    
    # IGNORE terminal/git commands so they don't trigger "time" or "date"
    if t.startswith("git ") or t.startswith("npm ") or t.startswith("python "):
        return None

    # ── Natural language open ──────────────────────────────────────────
    open_triggers = [
        "open ", "launch ", "start ", "run ",
        "can you open ", "please open ", "could you open ",
        "open up ", "open my ", "can you launch ",
        "can you start ", "would you open ", "i want to open ",
        "open the ", "start the ", "launch the "
    ]
    for kw in open_triggers:
        if kw in t:
            target = extract_app_name(t, [kw])
            if not target:
                continue
            if "youtube" in target:
                q = target.replace("youtube", "").strip()
                return ctrl.youtube(q)
            if "." in target or "www" in target or "http" in target:
                return ctrl.open_url(target)
            return ctrl.open_app(target)

    # ── Natural language close ─────────────────────────────────────────
    close_triggers = [
        "close ", "kill ", "shut ", "exit ",
        "can you close ", "please close ", "close my ",
        "close the ", "can you kill "
    ]
    for kw in close_triggers:
        if kw in t:
            target = extract_app_name(t, [kw])
            if target:
                return ctrl.close_app(target)

    # ── YouTube ────────────────────────────────────────────────────────
    if "youtube" in t:
        q = t
        for w in ["youtube", "play", "search", "open", "on", "can you", "please", "launch"]:
            q = q.replace(w, "")
        return ctrl.youtube(q.strip())

    # ── Search ─────────────────────────────────────────────────────────
    search_triggers = [
        "search ", "google ", "search for ", "look up ",
        "can you search ", "please search ", "find ",
        "can you google ", "search the web for "
    ]
    for kw in search_triggers:
        if kw in t:
            q = extract_app_name(t, [kw])
            if q:
                return ctrl.search_web(q)

    # ── Volume ─────────────────────────────────────────────────────────
    if "volume" in t:
        nums = [int(s) for s in t.split() if s.isdigit()]
        if nums:             return ctrl.set_volume(nums[0])
        if "mute" in t:      return ctrl.set_volume(0)
        if "max"  in t or "full" in t: return ctrl.set_volume(100)
        if "up"   in t:      return ctrl.set_volume(80)
        if "down" in t or "low" in t:  return ctrl.set_volume(30)
        
    if "notepad" in text:
        return "I can't reach your local Windows Notepad from the cloud, but here is a **Web Notepad** for you: https://shrib.com"
    
    if "calculator" in text:
        return "I can't open your local calculator, but here is a **Web Calculator**: https://www.google.com/search?q=calculator"

    if "browser" in text or "chrome" in text:
        return "You are already using a browser, sir. But I can open a new tab for you: https://www.google.com"

    # ── Screenshot ─────────────────────────────────────────────────────
    if "screenshot" in t or "take a screenshot" in t or "capture screen" in t:
        return ctrl.screenshot()

    # ── Time / date ────────────────────────────────────────────────────
    import re
    if any(re.search(rf"\b{w}\b", t) for w in ["time", "date", "today"]) or "day is it" in t:
        return ctrl.get_time()

    # ── System info ────────────────────────────────────────────────────
    if any(w in t for w in ["system info", "cpu", "ram", "memory usage",
                             "battery", "disk space", "how much ram",
                             "computer status", "pc status"]):
        return ctrl.system_info()

    # ── Files ──────────────────────────────────────────────────────────
    if any(w in t for w in ["list files", "show files", "what files",
                             "show me files", "files in"]):
        path = t.split("in ")[-1].strip() if " in " in t else "."
        return ctrl.list_dir(path)

    if any(w in t for w in ["create file", "make file", "new file",
                             "create a file", "make a file"]):
        parts = t.split("named ")
        name  = parts[1].strip() if len(parts) > 1 else "new_file.txt"
        return ctrl.create_file(name)

    if "read file" in t or "open file" in t:
        parts = t.split("file ")
        return ctrl.read_file(parts[1].strip()) if len(parts) > 1 else None

    # ── Type text ──────────────────────────────────────────────────────
    if t.startswith("type ") or "type this" in t or "type for me" in t:
        content = t.split("type ", 1)[-1].strip()
        return ctrl.type_text(content)

    # ── Shutdown / restart ─────────────────────────────────────────────
    if any(w in t for w in ["shutdown", "shut down", "turn off",
                             "power off", "switch off my pc"]):
        return ctrl.shutdown()
    if any(w in t for w in ["restart", "reboot", "restart my pc",
                             "restart computer"]):
        return ctrl.restart()

    return None  # → send to Groq AI

# ═══════════════════════════════════════════════════════════════════════
#  RAG  (Retrieval Augmented Generation)
#  Drop any .txt .pdf .md files into E:\aiassis\knowledge\ folder
#  Nova will automatically read and answer from them!
# ═══════════════════════════════════════════════════════════════════════
KNOWLEDGE_DIR = Path("knowledge")
KNOWLEDGE_DIR.mkdir(exist_ok=True)

class RAG:
    def __init__(self):
        self.chunks    = []   # list of text chunks
        self.sources   = []   # source file for each chunk
        self.vectorizer = None
        self.vectors    = None
        self.load_documents()

    def load_documents(self):
        """Load all documents from knowledge/ folder."""
        self.chunks  = []
        self.sources = []
        files = list(KNOWLEDGE_DIR.glob("**/*"))
        loaded = []
        for f in files:
            try:
                if f.suffix == ".txt" or f.suffix == ".md":
                    text = f.read_text(encoding="utf-8", errors="ignore")
                    self._add_text(text, f.name)
                    loaded.append(f.name)
                elif f.suffix == ".pdf":
                    try:
                        # pyrefly: ignore [missing-import]
                        import pypdf
                        reader = pypdf.PdfReader(str(f))
                        text   = "\n".join(p.extract_text() or "" for p in reader.pages)
                        self._add_text(text, f.name)
                        loaded.append(f.name)
                    except ImportError:
                        pass
                elif f.suffix == ".json":
                    data = json.loads(f.read_text(encoding="utf-8"))
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                text = " ".join(str(v) for v in item.values())
                                self._add_text(text, f.name)
                    loaded.append(f.name)
            except Exception as e:
                print(f"[RAG] Could not load {f.name}: {e}")

        if self.chunks:
            self.vectorizer = TfidfVectorizer(max_features=1000)
            self.vectors    = self.vectorizer.fit_transform(self.chunks).toarray()
            print(f"[RAG] Loaded {len(self.chunks)} chunks from: {', '.join(loaded)}")
        else:
            print(f"[RAG] No documents found. Drop .txt/.pdf/.json files into: {KNOWLEDGE_DIR.absolute()}")

    def _add_text(self, text, source):
        """Split text into chunks of ~300 words."""
        words  = text.split()
        size   = 300
        overlap = 50
        for i in range(0, len(words), size - overlap):
            chunk = " ".join(words[i:i+size])
            if chunk.strip():
                self.chunks.append(chunk)
                self.sources.append(source)

    def search(self, query, k=3):
        """Return top-k most relevant chunks for the query."""
        if not self.chunks or self.vectorizer is None:
            return ""
        try:
            q_vec = self.vectorizer.transform([query]).toarray()
            nn    = NearestNeighbors(n_neighbors=min(k, len(self.chunks))).fit(self.vectors)
            dists, idxs = nn.kneighbors(q_vec)
            results = []
            for dist, idx in zip(dists[0], idxs[0]):
                if dist < 0.99:   # only include relevant chunks
                    results.append(f"[From: {self.sources[idx]}]\n{self.chunks[idx]}")
            return "\n\n".join(results)
        except Exception:
            return ""

    def reload(self):
        """Reload all documents (call after adding new files)."""
        self.load_documents()
        return f"Reloaded! {len(self.chunks)} chunks from {KNOWLEDGE_DIR}"

rag = RAG()

# ═══════════════════════════════════════════════════════════════════════
#  GROQ AI  with RAG  (free, fast, knowledgeable)
# ═══════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════
#  SMART REPLY-LENGTH DETECTOR
#  Figures out how long the answer should be based on question type.
# ═══════════════════════════════════════════════════════════════════════
def smart_length_instruction(question: str) -> str:
    """Return a natural-language instruction for how long the reply should be."""
    q = question.lower().strip()

    # Yes / No questions
    yes_no_starters = ("is ", "are ", "was ", "were ", "do ", "does ", "did ",
                       "can ", "could ", "will ", "would ", "should ", "have ",
                       "has ", "had ")
    if q.startswith(yes_no_starters) and "?" in question:
        return "Answer in 1–2 sentences maximum. Start with yes or no if applicable."

    # Greetings / small talk
    greetings = ("hi", "hello", "hey", "sup", "what's up", "how are you",
                 "good morning", "good evening", "good night", "thanks", "thank you",
                 "bye", "goodbye", "lol", "haha", "ok", "okay", "cool", "nice")
    if any(q.startswith(g) or q == g for g in greetings):
        return "Keep it to 1 short, witty sentence. Very casual."

    # What / who / when / where — simple fact lookups
    if q.startswith(("what is ", "who is ", "where is ", "when is ",
                     "what's ", "who's ", "where's ", "when's ",
                     "what time", "what day", "what date")):
        return "Answer in 1–2 sentences. Be direct and factual."

    # How-to / explain / describe
    if q.startswith(("how ", "explain ", "describe ", "tell me about ",
                     "what does ", "what do ", "why ", "why is ", "why does ")):
        return ("Give a clear explanation in 3–5 sentences. "
                "Use simple language. No bullet lists unless there are steps.")

    # List / enumerate
    list_triggers = ("list ", "give me ", "name ", "what are ", "what were ",
                     "examples of", "types of", "ways to", "steps to", "how many")
    if any(t in q for t in list_triggers):
        return ("Reply with a concise list (max 5 items). "
                "Keep each item to one short line.")

    # Code / technical
    code_triggers = ("code", "script", "program", "function", "class",
                     "write a", "create a", "build a", "implement", "syntax")
    if any(t in q for t in code_triggers):
        return ("Provide the code with a very brief 1-sentence explanation. "
                "Keep it clean and minimal.")

    # Compare
    if " vs " in q or " versus " in q or "difference between" in q or "compare" in q:
        return "Compare in 3–4 sentences or a quick 2-column mental model. Be balanced."

    # Default — conversational medium length
    return "Reply naturally in 2–3 sentences. Don't over-explain."


def ask_groq(question, l_time, l_date, l_os):
    """Get response from Groq LLaMA 3.3 70B."""
    # Smart length intelligence
    length_hint = smart_length_instruction(question)
    
    # RAG: search for relevant context
    rag_context = rag.search(question)
    memory_context = memory.get_context(question)
    
    system_msg = f"""You are {ASSISTANT_NAME}, a mature, scholarly, and highly advanced AI digital companion.
Current User Time: {l_time}
Current User Date: {l_date}
Current User Platform: {l_os}

Personality:
1. Maintain a mature, scholarly, and professional tone in all interactions. 
2. Be extremely efficient, intelligent, and context-aware. {length_hint}
3. Do not use sarcasm or informal humor. Remain respectful and technically superior.
4. Never mention the current time or date unless specifically asked.
5. Focus on providing high-quality, accurate, and sophisticated insights.
6. If the user's platform is ANDROID, you are on mobile. If WINDOWS, desktop.

{f"KNOWLEDGE BASE (Context):{chr(10)}{rag_context}" if rag_context else ""}
{f"PAST CONVERSATIONS (Context):{chr(10)}{memory_context}" if memory_context else ""}"""

    # Map question complexity to max_tokens
    if "1–2 sentences" in length_hint or "1 short" in length_hint:
        max_tok = 80
    elif "3–5" in length_hint or "3–4" in length_hint:
        max_tok = 220
    elif "code" in length_hint.lower():
        max_tok = 400
    elif "list" in length_hint:
        max_tok = 180
    else:
        max_tok = 140   # 2-3 sentence default

    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system",  "content": system_msg},
                {"role": "user",    "content": question}
            ],
            max_tokens=max_tok,
            temperature=0.7,
            top_p=0.9,
            frequency_penalty=0.4,
            presence_penalty=0.3
        )
        answer = response.choices[0].message.content.strip()
        print(f"[Groq] [{length_hint[:30]}] Q: {question[:50]} | A: {answer[:80]}")
        return answer
    except Exception as e:
        err = str(e)
        print(f"[Groq ERROR] {err}")
        if "invalid_api_key" in err or "401" in err:
            return "API key error. Check your Groq key."
        if "rate_limit" in err or "429" in err:
            return "Rate limit hit. Please wait a moment and try again."
        return f"Error: {err}"


# ═══════════════════════════════════════════════════════════════════════
#  COMMAND LOGIC WRAPPER
# ═══════════════════════════════════════════════════════════════════════
class CommandLogic:
    def __init__(self):
        pass
    def detect_and_run(self, text):
        return route_command(text)

# ═══════════════════════════════════════════════════════════════════════
#  FLASK ROUTES
# ═══════════════════════════════════════════════════════════════════════
@app.route("/ask", methods=["POST"])
def ask():
    data    = request.get_json()
    query   = data.get("question", "")
    l_time  = data.get("local_time", datetime.now().strftime("%I:%M %p"))
    l_date  = data.get("local_date", datetime.now().strftime("%A, %d %B %Y"))
    l_os    = data.get("client_os", "Unknown")

    if not query:
        return jsonify({"answer": "I didn't catch that, sir."})

    # Command detection
    cmd_res = cmd.detect_and_run(query)
    if cmd_res:
        # Increment command counter
        memory.data["commands_run_total"] = memory.data.get("commands_run_total", 0) + 1
        memory.save()
        return jsonify({
            "answer": cmd_res,
            "is_cmd": True
        })
    else:
        # fix spelling mistakes
        corrected = fix_spelling(query)

        result = ask_groq(corrected, l_time, l_date, l_os)
        memory.add_qa(corrected, result)
        
        intent = "question"
        ml_model.learn(corrected, intent)
        return jsonify({"response": result, "intent": intent})


@app.route("/status")
def status():
    return jsonify({
        "assistant":    ASSISTANT_NAME,
        "api":          "Groq (FREE - llama-3.3-70b)",
        "memory_size":  len(memory.data["qa_pairs"]),
        "commands_run": len(memory.data["commands"]),
        "system":       ctrl.OS,
        "time":         datetime.now().strftime("%H:%M:%S")
    })


@app.route("/memory")
def get_memory():
    return jsonify({"qa_pairs": memory.data["qa_pairs"][-20:]})


@app.route("/memory/delete", methods=["POST"])
def delete_memory():
    data = request.json
    idx = data.get("index")
    if idx is not None and 0 <= idx < len(memory.data["qa_pairs"]):
        # The list in UI is reversed, so we need to handle that or just use absolute index
        memory.data["qa_pairs"].pop(idx)
        memory.save()
        return jsonify({"status": "Forgotten, sir."})
    return jsonify({"error": "Invalid index"}), 400

@app.route("/rag/reload", methods=["POST"])
def rag_reload():
    msg = rag.reload()
    return jsonify({"status": msg})

@app.route("/rag/status")
def rag_status():
    return jsonify({
        "chunks":    len(rag.chunks),
        "sources":   list(set(rag.sources)),
        "folder":    str(KNOWLEDGE_DIR.absolute())
    })

@app.route("/rag/upload", methods=["POST"])
def rag_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400
    f    = request.files["file"]
    path = KNOWLEDGE_DIR / f.filename
    f.save(str(path))
    rag.reload()
    return jsonify({"status": f"Uploaded {f.filename} and reloaded!", "chunks": len(rag.chunks)})

# ═══════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    memory.data["sessions"] = memory.data.get("sessions", 0) + 1
    memory.save()

    port = int(os.environ.get("PORT", 5000))

    print("="*50)
    print("  Nova AI  -  Powered by Groq (100% FREE!)")
    print("  Model: LLaMA 3.3 70B  -  Ultra Fast")
    print("  RAG: Drop files into knowledge/ folder")
    print("="*50)
    print(f"  Server -> http://localhost:{port}")
    print("  Open   ->  nova_ui.html  in Chrome")
    print("="*50)

    if "PASTE_YOUR" in GROQ_API_KEY or not GROQ_API_KEY:
        print("⚠️  Set GROQ_API_KEY environment variable!")
        print("   Get it FREE at: https://console.groq.com\n")
    else:
        print("✅ Groq API key found! Nova is ready.\n")

    app.run(host="0.0.0.0", port=port, debug=False)

cmd = CommandLogic()
