# 我的 AI 3D 總部

打開網頁：https://dorakichu.github.io/claude_/

一間等角視角的 3D 微縮辦公室，裡面有四間工作室：交易作戰室、投資人辦公室、製程班表工坊、遊戲休息區。中間是 Claude 核心。員工頭上的對話框會顯示他們現在在做什麼，網頁每分鐘自動更新一次。

## 員工狀態怎麼來

網頁會讀這個 repo 裡的 `status.json`。家裡電腦的交易系統把狀態寫進 `D:\trading-lab\hq_status.json`，再由 `tools/push_status.py` 推上來。

`hq_status.json` 的格式：

```json
{
  "staff": [
    { "seat": "ceo",      "state": "meeting", "task": "主持會議：檢討今天的策略" },
    { "seat": "whisper",  "state": "working", "task": "轉錄直播音檔" },
    { "seat": "trader",   "state": "idle",    "task": "等待進場訊號" }
  ]
}
```

- `seat`（座位）：`ceo` `analyst` `risk` `strategy` `tech` `gemini` `whisper` `trader` `diaochan` `robot`
- `state`（狀態）：`working` 工作中、`meeting` 開會中、`idle` 待命、`error` 出狀況
- `task`：正在做的事，最多 60 個字
- `name`：可省略，想讓員工換名字時才填

狀態超過 2 小時沒更新，網頁左上角會顯示「最後更新 X 小時前」。

注意：這個 repo 是公開的，`status.json` 任何人都看得到，`task` 裡不要寫金額、帳號或 API key。
