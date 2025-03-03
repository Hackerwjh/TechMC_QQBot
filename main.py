import asyncio
import tomllib
import time
from deepseek import DeepSeek

import botpy
from botpy.types.message import MarkdownPayload, MessageMarkdownParams
from botpy import logging, BotAPI
from botpy.ext.command_util import Commands
from botpy.message import Message


with open("keys.toml","rb") as tomlFile:
    keys = tomllib.load(tomlFile)
AI = DeepSeek(api_key=keys["DeepSeek"]["APIKey"])
BotLog = logging.get_logger()


@Commands("AI")
async def AIChat(api:BotAPI, message:Message, params="你好"):
    if params == "clear" or time.time() - AI.lastCallTime >= 1200:
        AI.clearMemery()
        await message.reply(content = "已清除全部记忆")
        if params == "clear":
            return

    BotLog.info(f"{message.author.username}: {message.content}")
    await message.reply(content = "正在回复中，请稍等......")
    
    # 回复
    ReplyMsg = await AI.AIChat(content = params)
    await message.reply(content = ReplyMsg)


class MyClient(botpy.Client):
    async def on_ready(self):
        BotLog.info(f"robot 「{self.robot.name}」 is ready!")
    
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
        public_guild_messages=True,
    )
    QQBot = MyClient(intents=intents)
    QQBot.run(
        appid=keys["QQBot"]["AppID"],
        secret = keys["QQBot"]["Secret"]
    )