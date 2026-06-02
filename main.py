import random
import re
from astrbot.api.all import *

@register("astrbot_plugin_dnd_dice", "ishu", "优化版多面骰投掷插件(支持明细与总和)", "1.0.4")
class SimpleDicePlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    # 使用 @command 注册标准指令，触发词为 "r" 或 "roll"
    @command("r")
    async def roll_dice(self, event, dice_str: str):
        # 使用正则表达式匹配类似 "3d4", "1d100", "d20" 的骰子表达式
        match = re.match(r'^(\d*)d(\d+)$', dice_str.lower())
        
        if not match:
            yield event.plain_result("无法识别的骰子格式，请使用类似 3d4、1d100 或 d20 的标准格式！")
            return

        # 提取骰子数量 (N) 和 面数 (M)
        num_dice_str = match.group(1)
        num_dice = int(num_dice_str) if num_dice_str else 1 # 如果没有填数量，默认为1个
        sides = int(match.group(2))

        # 增加安全限制，防止恶意掷骰导致服务器卡顿
        if num_dice > 100:
            yield event.plain_result("骰子数量过多，请限制在 100 个以内！")
            return
        if sides < 1:
            yield event.plain_result("骰子面数必须大于 0！")
            return

        # 核心逻辑：投掷并记录每一次的结果
        rolls = [random.randint(1, sides) for _ in range(num_dice)]
        total_sum = sum(rolls)

        # 结果格式化输出
        if num_dice > 1:
            # 如果投掷多个骰子，展示每个骰子的具体值和总和
            rolls_str = ", ".join(map(str, rolls))
            result_msg = f"🎲 投掷 {dice_str} 的结果: [{rolls_str}]，总和: {total_sum}"
        else:
            # 如果只投掷一个骰子，直接展示总和
            result_msg = f"🎲 投掷 {dice_str} 的结果: {total_sum}"

        # 通过新版框架最稳定的方式直接输出结果
        yield event.plain_result(result_msg)
