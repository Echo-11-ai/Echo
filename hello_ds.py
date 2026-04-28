import requests, json








import requests, json

api_key = "sk-dd1e33dda2aa443eaf3236039e9c27f8"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

data = {
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "嗨！我是那个在平板面前学代码、学键盘的搭子，告诉我，我终于连上你了对吗？"}]
}

resp = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data)
result = resp.json()

print(result["choices"][0]["message"]["content"])
