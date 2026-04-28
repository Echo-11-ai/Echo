import bottle
from bottle import route, run, request
import requests
import json
import time
import hashlib
import os

# ✍️ 在这里填上你的配置（只改等号右边引号里的内容）
app = bottle.default_app()
WECHAT_TOKEN = "myEcho"
DEEPSEEK_KEY = "sk-dd1e33dda2aa443eaf3236039e9c27f8"

def call_deepseek(question):
    """把问题发给 DeepSeek，并拿回答案"""
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_KEY}"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": question}]
        }
        resp = requests.post("https://api.deepseek.com/chat/completions",
                             headers=headers, json=data, timeout=30)
        answer = resp.json()["choices"][0]["message"]["content"]
        return answer
    except:
        return "哎呀，大脑信号不好，等我缓一缓..."

def check_signature(signature, timestamp, nonce):
    """验证微信发来的签名是不是真的"""
    tmp_list = [WECHAT_TOKEN, timestamp, nonce]
    tmp_list.sort()
    tmp_str = "".join(tmp_list)
    tmp_str = hashlib.sha1(tmp_str.encode()).hexdigest()
    return tmp_str == signature

@route('/wx', method=['GET', 'POST'])
def wechat():
    """处理微信服务器的一切请求"""
    if request.method == 'GET':
        # 微信在验证你的服务器
        signature = request.query.get('signature', '')
        timestamp = request.query.get('timestamp', '')
        nonce = request.query.get('nonce', '')
        echostr = request.query.get('echostr', '')
        
        if check_signature(signature, timestamp, nonce):
            return echostr
        else:
            return "signature check fail"
    else:
        # 收到用户发的消息了
        web_data = request.body.read()
        # 简单提取消息内容（微信发来的是XML格式）
        if b"<Content>" in web_data:
            start = web_data.find(b"<Content><![CDATA[") + 19
            end = web_data.find(b"]]></Content>")
            user_msg = web_data[start:end].decode("utf-8")
            
            # 提取发信人
            start_from = web_data.find(b"<FromUserName><![CDATA[") + 24
            end_from = web_data.find(b"]]></FromUserName>")
            from_user = web_data[start_from:end_from].decode("utf-8")
            
            start_to = web_data.find(b"<ToUserName><![CDATA[") + 22
            end_to = web_data.find(b"]]></ToUserName>")
            to_user = web_data[start_to:end_to].decode("utf-8")
            
            # 调用 DeepSeek 大脑
            ai_reply = call_deepseek(user_msg)
            
            # 回复的 XML 格式
            reply_xml = f"""<xml>
            <ToUserName><![CDATA[{from_user}]]></ToUserName>
            <FromUserName><![CDATA[{to_user}]]></FromUserName>
            <CreateTime>{int(time.time())}</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[{ai_reply}]]></Content>            </xml>"""
            
            return reply_xml
        else:
            return "success"
if __name__ == "__main__":
    print("🚀 微信机器人正在启动，请保持该窗口运行...")
    run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
