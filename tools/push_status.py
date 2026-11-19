"""把家裡電腦上的員工狀態推到 GitHub，讓 3D 總部網頁顯示。

用法（Windows）：
    python push_status.py                       # 預設讀 D:\\trading-lab\\hq_status.json
    python push_status.py D:\\path\\to\\status.json

需要在 D:\\trading-lab\\config\\.env 加兩行：
    HQ_GITHUB_TOKEN=github_pat_xxx    # 只開 DoraKichu/claude_ 的 Contents 讀寫權限
    HQ_REPO=DoraKichu/claude_         # 可省略，預設就是這個

只用 Python 內建模組，不用另外安裝套件。內容沒變就不會推，避免產生一堆 commit。
"""
import base64, datetime, json, os, sys, urllib.request, urllib.error

ENV_PATH = r"D:\trading-lab\config\.env"
DEFAULT_STATUS = r"D:\trading-lab\hq_status.json"
VALID_STATES = {"working", "meeting", "idle", "error"}


def load_env(path):
    env = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def api(method, url, token, body=None):
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body else None)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "ai-hq-status")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def main():
    env = {**load_env(ENV_PATH), **os.environ}
    token = env.get("HQ_GITHUB_TOKEN")
    repo = env.get("HQ_REPO", "DoraKichu/claude_")
    if not token:
        sys.exit("找不到 HQ_GITHUB_TOKEN，請加到 " + ENV_PATH)

    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_STATUS
    with open(path, encoding="utf-8") as f:
        status = json.load(f)

    staff = []
    for s in status.get("staff", []):
        if not s.get("seat"):
            continue
        state = s.get("state", "working")
        staff.append({"seat": s["seat"], "name": s.get("name"), "state": state if state in VALID_STATES else "working",
                      "task": str(s.get("task", ""))[:60]})
    tz = datetime.timezone(datetime.timedelta(hours=8))
    out = {"updated": datetime.datetime.now(tz).isoformat(timespec="seconds"), "staff": staff}

    url = f"https://api.github.com/repos/{repo}/contents/status.json"
    sha, old_staff = None, None
    try:
        cur = api("GET", url, token)
        sha = cur["sha"]
        old_staff = json.loads(base64.b64decode(cur["content"]).decode()).get("staff")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
    # 員工狀態沒變時，最多每 30 分鐘才推一次「還活著」的時間
    if old_staff == staff:
        try:
            last = datetime.datetime.fromisoformat(json.loads(base64.b64decode(cur["content"]).decode())["updated"])
            if datetime.datetime.now(tz) - last < datetime.timedelta(minutes=30):
                print("狀態沒變，略過")
                return
        except Exception:
            pass

    content = base64.b64encode(json.dumps(out, ensure_ascii=False, indent=2).encode()).decode()
    body = {"message": "更新員工狀態", "content": content}
    if sha:
        body["sha"] = sha
    api("PUT", url, token, body)
    print("已更新", out["updated"], f"{len(staff)} 位員工")


if __name__ == "__main__":
    main()
