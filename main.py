import random
import re
from astrbot.api.all import *

@register("astrbot_plugin_dnd_dice", "ishu", "极简纯净投掷插件", "1.0.1")
class SimpleDicePlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    # 直接使用最底层的消息接收，屏蔽所有兼容性报错
    async def on_message_received(self, event):
        msg = event.message_str.strip()
        
        # 仅正则匹配纯粹的投骰表达式，例如 1d20, 2d6, 1d20+3
        match = re.match(r'^(\d+)[dD](\d+)(?:([+-])(\d+))?$', msg)
        if not match:
            return
            
        num = int(match.group(1))
        sides = int(match.group(2))
        
        # 安全限制：防止骰子数量或面数过大导致崩溃
        if num <= 0 or num > 50 or sides <= 1 or sides > 100:
            return
            
        mod_sign = match.group(3)
        mod_val = int(match.group(4)) if match.group(4) else 0
        
        # 投掷并计算总和
        total = sum(random.randint(1, sides) for _ in range(num))
        
        if mod_sign == '+':
            total += mod_val
        elif mod_sign == '-':
            total -= mod_val
            
        # 拼装极简的投掷方式字符串
        expr = f"{num}d{sides}{mod_sign}{mod_val}" if mod_sign else f"{num}d{sides}"
        
        # 仅输出投掷方式和结果
        result_text = f"{expr} 结果是: {total}"
        
        yield event.plain_result(result_text)
