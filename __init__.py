import re
from neobot_modloader import BasePlugin

PATTERN = re.compile(r"^\s*get(\s|$)", re.IGNORECASE)


class GetAvatarPlugin(BasePlugin):
    name = "get_avatar"
    version = "0.1.0"

    async def on_load(self, ctx):
        size = int(ctx.config.get("avatar_size", 640))
        allow_self = bool(ctx.config.get("allow_self", True))

        @ctx.on.message(
            group=True,
            regex=PATTERN,
            priority=10,
            block=True,            # 处理完不再让低优先 hook 处理
            block_ai_reply=True,   # 别让 AI 也回一遍
            timeout=10.0,
        )
        async def handle(event: dict):
            # 1) 收集消息里所有 @ 的 QQ
            targets: list[int] = []
            for seg in event.get("message", []):
                if not isinstance(seg, dict):
                    continue
                if seg.get("type") != "at":
                    continue
                qq = seg.get("data", {}).get("qq")
                if qq is None:
                    continue
                try:
                    targets.append(int(qq))
                except (TypeError, ValueError):
                    continue

            # 2) 没 @ 任何人时,回落到发送者自己
            if not targets:
                if allow_self and event.get("user_id") is not None:
                    targets = [int(event["user_id"])]
                else:
                    await ctx.reply(event, "用法: get @某人")
                    return

            # 3) 拼消息段返回
            segments: list[dict] = []
            for qq in targets:
                url = f"https://q1.qlogo.cn/g?b=qq&nk={qq}&s={size}"
                segments.append({"type": "text",  "data": {"text": f"QQ {qq}:\n"}})
                segments.append({"type": "image", "data": {"file": url}})

            ctx.logger.info(f"返回 {len(targets)} 个头像: {targets}")
            await ctx.reply(event, segments)


plugin = GetAvatarPlugin()