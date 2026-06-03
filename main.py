import random
import re
from astrbot.api.all import *
from astrbot.api.event import filter

@register("astrbot_plugin_dnd_dice", "ishu", "无前缀直读多面骰插件(支持明细与总和)", "1.0.5")
class SimpleDicePlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    # 核心改动 1：废弃 @command，改用 @filter.regex 直接进行全局正则表达式拦截
    # (?i) 代表忽略大小写，允许直读匹配 "3d4" 或 "1D20" 这样占据整行的指令
    @filter.regex(r"(?i)^(\d*)d(\d+)$")
    async def roll_dice(self, event):
        # 稳妥起见，直接从 event 对象中提取纯文本进行二次解析，防止框架升级导致传参变化
        message_text = event.message_str.strip().lower()
        match = re.match(r'^(\d*)d(\d+)$', message_text)
        
        if not match:
            return

        # 提取骰子数量 (N) 和 面数 (M)
        num_dice_str = match.group(1)
        num_dice = int(num_dice_str) if num_dice_str else 1 # 如果直接发 d20，没有填数量则默认为 1
        sides = int(match.group(2))

        # 安全限制，防止恶意投掷导致服务器卡死
        if num_dice > 100:
            yield event.plain_result("骰子数量过多，请限制在 100 个以内！")
            return
        if sides < 1:
            yield event.plain_result("骰子面数必须大于 0！")
            return

        # 核心改动 2：后台模拟 N 次独立掷骰，并将每次结果记录进列表中
        rolls = [random.randint(1, sides) for _ in range(num_dice)]
        total_sum = sum(rolls)

        # 核心改动 3：输出格式化，满足输出明细和总和的需求
        if num_dice > 1:
            # 如果投掷 3d4，将输出类似：🎲 投掷 3d4 的结果: [2-4]，总和: 7
            rolls_str = ", ".join(map(str, rolls))
            result_msg = f"🎲 投掷 {message_text} 的结果: [{rolls_str}]，总和: {total_sum}"
        else:
            # 如果只投掷单骰子 1d20，则保持极简只输出总和
            result_msg = f"🎲 投掷 {message_text} 的结果: {total_sum}"

        # 截获并输出结果，自然替代大模型的回复
        yield event.plain_result(result_msg)
