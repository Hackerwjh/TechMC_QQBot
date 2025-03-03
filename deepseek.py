import time
import aiohttp
from copy import deepcopy
from openai import AsyncOpenAI

class DeepSeek(AsyncOpenAI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url="https://api.deepseek.com"
        self.presetMemery = [
            {"role": "system", "content": "\
                1. 无论何时请使用中文交流\
                2. 所有回复中严格禁止包含任何形式的URL链接（包括完整网址、缩短链接、域名等）\
                3. 若需引用网络资源，请直接说明信息来源名称而非链接\
                4. 避免使用包含顶级域名后缀的词汇组合（如.com/.cn/.net等）\
            "}]
        self.memery = deepcopy(self.presetMemery)
        self.lastCallTime = time.time()
        
    
    async def AIChat(self, content:str):
        # AIchat 是因为与父类方法冲突
        # 使用临时记忆来防止多个对话同时调用而可能发生的记忆顺序错误
        tempMemery = [{"role": "user", "content": content}]
        AIReply = await self.chat.completions.create(
                model="deepseek-chat",
                messages=self.memery + tempMemery,
                stream=False
            )
        tempMemery.append({"role": "assistant", "content": AIReply.choices[0].message.content})
        self.memery.extend(tempMemery)
        self.lastCallTime = time.time()
        print(tempMemery)
        return AIReply.choices[0].message.content
        
    async def balance(self):
        balanceAPIUrl = "https://api.deepseek.com/user/balance"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        async with aiohttp.ClientSession as session:
            async with session.get(balanceAPIUrl, headers=headers) as response:
                balanceInfo = await response.json()
        return balanceInfo
    
    def clearMemery(self):
        self.memery = self.presetMemery