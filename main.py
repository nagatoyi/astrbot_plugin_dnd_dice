import random
import re
from astrbot.api.all import *

@register("astrbot_plugin_dnd_dice", "ishu", "DND专属纯净吐槽骰娘", "1.0.0")
class DndDicePlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    # 核心修改：直接重写原生底层的消息接收方法，不使用任何装饰器，去掉 event 类型声明以防导包失败
    async def on_message_received(self, event):
        # 获取用户纯文本输入，去掉前后空格
        msg = event.message_str.strip()
        
        # 正则匹配仅包含 1d20, 2d6, 1d20+5, 1D8-2 等纯指令格式（忽略大小写）
        match = re.match(r'^(\d+)[dD](\d+)(?:([+-])(\d+))?$', msg)
        if not match:
            return
            
        num = int(match.group(1))
        sides = int(match.group(2))
        
        # 限制骰子数量和面数，防止恶意刷屏或崩溃
        if num <= 0 or num > 50 or sides <= 1 or sides > 100:
            return
            
        mod_sign = match.group(3)
        mod_val = int(match.group(4)) if match.group(4) else 0
        
        # 投掷骰子
        rolls = [random.randint(1, sides) for _ in range(num)]
        dice_sum = sum(rolls)
        
        # 计算带调整值的总和
        total = dice_sum
        mod_str = ""
        if mod_sign == '+':
            total += mod_val
            mod_str = f" + {mod_val}"
        elif mod_sign == '-':
            total -= mod_val
            mod_str = f" - {mod_val}"
            
        # 🎭 DND专属吐槽逻辑生成
        roast = ""
        if sides == 20 and num == 1:
            # 针对 1D20 的属性/技能检定吐槽（根据自然骰点 Nat 进行判定）
            nat = rolls
            if nat == 20:
                roast = "大成功（Nat 20）！神明亲自为你指引了方向，去创造奇迹吧！"
            elif nat == 1:
                roast = "大失败（Nat 1）！众神发出了无情的嘲笑，这惨不忍睹的操作建议你换个脑子或换个骰子。"
            elif total >= 16:
                roast = "干得漂亮，看来幸运女神今晚就站在你这边。"
            elif total >= 10:
                roast = "平平无奇的骰运，刚好配得上你不加修饰的平庸表现。"
            else:
                roast = "就这？我强烈建议你下次行动前先去神殿捐点钱洗洗手。"
        else:
            # 针对其他多面骰（伤害骰/治疗骰等）的吐槽
            ratio = dice_sum / (num * sides)
            if ratio == 1.0:
                roast = "数值拉满！你今晚简直是一台无情的输出机器！"
            elif ratio >= 0.8:
                roast = "刀刀烈火，对手大概已经被你锤得找不到北了。"
            elif ratio <= 0.3:
                roast = "你是在给怪物刮痧吗？连街边的野狗都觉得你力气小。"
            else:
                roast = "中规中矩的效果，至少没把手里的武器脱手扔出去。"
                
        # 📝 组装最终的输出文本
        expr = f"{num}d{sides}{mod_sign}{mod_val}" if mod_sign else f"{num}d{sides}"
        
        if num == 1:
            result_text = f"你掷出了 {expr}，结果是：{rolls}{mod_str} = {total}\n【DM吐槽】：{roast}"
        else:
            result_text = f"你掷出了 {expr}，明细为 {rolls}{mod_str}，总计：{total}\n【DM吐槽】：{roast}"
            
        # 核心修改：使用最稳定的 plain_result 进行输出
        yield event.plain_result(result_text)
