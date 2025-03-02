import asyncio
import tomllib
import requests
import time
from copy import deepcopy
from rich import print
from openai import OpenAI

import botpy
from botpy.types.message import MarkdownPayload, MessageMarkdownParams
from botpy import logging, BotAPI
from botpy.ext.command_util import Commands
from botpy.message import Message



with open("/storage/emulated/0/Fx/keys.toml","rb") as tomlFile:
    keys = tomllib.load(tomlFile)
PreSetMemery = [
    {"role": "system", "content": "\
        1. 无论何时请使用中文交流\
        2. 所有回复中严格禁止包含任何形式的URL链接（包括完整网址、缩短链接、域名等）\
        3. 若需引用网络资源，请直接说明信息来源名称而非链接\
        4. 避免使用包含顶级域名后缀的词汇组合（如.com/.cn/.net等）\
    "}
]
AIMemery = deepcopy(PreSetMemery)
AILastCall = time.time()
DeepSeek = OpenAI(api_key=keys["DeepSeek"]["APIKey"], base_url="https://api.deepseek.com")
_log = logging.get_logger()



@Commands("AI")
async def AIChat(api:BotAPI, message:Message, params=None):
    global AIMemery, AILastCall
    
    if params == "clear" or time.time() - AILastCall >= 1200:
        AIMemery = PreSetMemery
        AILastCall = time.time()
        await message.reply(content = "已清除全部记忆")
        if params == "clear":
            return

    _log.info(f"{message.author.username}: {message.content}")
    await message.reply(content = "正在回复中，请稍等......")
    
    # 回复
    AIMemery.append({"role": "user", "content": params})
    AIReply = DeepSeek.chat.completions.create(
        model="deepseek-chat",
        messages=AIMemery,
        stream=False
        )
    ReplyMsg = AIReply.choices[0].message.content
    AIMemery.append({"role": "assistant", "content": ReplyMsg})
    AILastCall = time.time()
    await message.reply(content = ReplyMsg)
    
    # 统计输出
    balanceAPIUrl = "https://api.deepseek.com/user/balance"
    payload={}
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {keys['DeepSeek']['APIKey']}"
    }
    balance = requests.request("GET", balanceAPIUrl, headers=headers, data=payload)
    replyCount=f"回复完成\n输入Token：{AIReply.usage.prompt_tokens}\n输出Token：{AIReply.usage.completion_tokens}\n命中缓存：{AIReply.usage.prompt_cache_hit_tokens}\n未命中缓存：{AIReply.usage.prompt_cache_miss_tokens}\n账户余额：{balance.json()['balance_infos'][0]['total_balance']}"
    await message.reply(content = replyCount)


class MyClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 is ready!")
        self.messageSet = set()
    
    async def on_at_message_create(self, message: Message):
        # 注册指令handler
        handlers = [
            AIChat,
        ]
        for handler in handlers:
            if await handler(api = self.api, message = message):
                return

if __name__ == "__main__":
    # 监听事件设置
    intents = botpy.Intents(
        public_guild_messages=True
    )
    QQBot = MyClient(intents=intents)
    QQBot.run(
        appid=keys["QQBot"]["AppID"],
        secret = keys["QQBot"]["Secret"]
    )