import random
import asyncio
from typing import Union, Any, List

from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot import require, on_command
from nonebot.message import handle_event
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.params import Arg, ArgStr, Depends, CommandArg

require("nonebot_plugin_datastore")
from nonebot_plugin_datastore import get_session
from sqlalchemy.ext.asyncio.session import AsyncSession
from nonebot.adapters.onebot.v11 import (
    GROUP,
    Bot,
    Message,
    ActionFailed,
    MessageSegment,
    GroupMessageEvent,
    MessageEvent,
)

from .model import Bottle
from .config import (
    Config,
    maxrt,
    maxlen,
    rtrate,
    disable_comment_prompt,
    everyone_can_read,
    disable_forward
)
from .data_source import (
    ba,
    text_audit,
    bottle_manager,
    serialize_message,
    deserialize_message,
    get_content_preview,
    whether_collapse,
)

__plugin_meta__ = PluginMetadata(
    name="漂流瓶",
    description="群与群互通的漂流瓶插件",
    config=Config,
    usage=f"""
指令：
    扔漂流瓶 [文本/图片]
    寄漂流瓶 [文本/图片] （同扔漂流瓶，防止指令冲突用）
    捡漂流瓶
    查看漂流瓶 [漂流瓶编号]
    点赞漂流瓶 [漂流瓶编号]
    评论漂流瓶 [漂流瓶编号] [文本]
    举报漂流瓶 [漂流瓶编号]
    删除漂流瓶 [漂流瓶编号]
    我的漂流瓶
SUPERUSER指令：
    清空漂流瓶
    恢复漂流瓶 [漂流瓶编号]
    删除漂流瓶评论 [漂流瓶编号] [QQ号]
    漂流瓶白名单 [QQ / 群聊 / 举报] [QQ号 / 群号]
    漂流瓶黑名单 [QQ / 群聊] [QQ号 / 群号]
    漂流瓶详情 [漂流瓶编号]
""".strip(),
    type="application",
    homepage="https://github.com/Todysheep/nonebot_plugin_bottle",
    supported_adapters={"~onebot.v11"},
    extra={
        "unique_name": "nonebot_plugin_bottle",
        "example": "扔漂流瓶\n寄漂流瓶\n捡漂流瓶\n评论漂流瓶\n举报漂流瓶\n查看漂流瓶\n删除漂流瓶",
        "author": "Todysheep",
        "version": "2.0.1",
    },
)

throw = on_command(
    "扔漂流瓶",
    aliases=set(["寄漂流瓶", "丢漂流瓶"]),
    permission=GROUP,
    priority=100,
    block=True,
)
get = on_command("捡漂流瓶", priority=100, block=True)
report = on_command("举报漂流瓶", priority=100, block=True)
comment = on_command("评论漂流瓶", priority=100, block=True)
check_bottle = on_command("查看漂流瓶", priority=100, block=True)
remove = on_command("删除漂流瓶", priority=100, block=True)
listb = on_command("我的漂流瓶", priority=100, block=True)
like = on_command("点赞漂流瓶", priority=100, block=True)

resume = on_command("恢复漂流瓶", permission=SUPERUSER, priority=100, block=True)
clear = on_command("清空漂流瓶", permission=SUPERUSER, priority=100, block=True)
comrem = on_command("删除漂流瓶评论", permission=SUPERUSER, priority=100, block=True)
listqq = on_command("漂流瓶详情", permission=SUPERUSER, priority=100, block=True)
ban = on_command(
    "漂流瓶黑名单",
    aliases=set(["banbottle", "漂流瓶封禁"]),
    permission=SUPERUSER,
    priority=100,
    block=True,
)
white = on_command(
    "漂流瓶白名单",
    aliases=set(["whitebottle"]),
    permission=SUPERUSER,
    priority=100,
    block=True,
)


async def get_bottle(
    index: Union[str, int], matcher: Matcher, session: AsyncSession, include_del=False
) -> Bottle:
    if isinstance(index, str) and not index.isdigit():
        await matcher.finish("漂流瓶编号必须为正整数！")
    bottle = await bottle_manager.get_bottle(
        index=int(index), session=session, include_del=include_del
    )
    if not bottle:
        await matcher.finish("该漂流瓶不存在或已被删除！")
    return bottle


async def verify(matcher: Matcher, event: GroupMessageEvent) -> None:
    if not ba.verify(event.user_id, event.group_id):
        await matcher.finish(ba.bannedMessage if ba.bannedMessage.strip() else None)


# 信息初始化
proceed = set(["是", "对", "Y", "Yes", "y", "yes"])
cancel = set(["取消", "cancel"])


async def try_send_forward(event: MessageEvent, bot: Bot, messages: List[Any]):
    if disable_forward:
        if isinstance(event, GroupMessageEvent):
            for message in messages:
                await bot.send_group_msg(group_id=event.group_id, message=message)
                await asyncio.sleep(0.2)
        else:
            for message in messages:
                await bot.send_private_msg(group_id=event.user_id, message=message)
                await asyncio.sleep(0.2)
        return
    new_messages = []
    for message in messages:
        if isinstance(message, str):
            new_messages.append(Message(message))
        elif isinstance(message, MessageSegment):
            new_messages.append(Message(message))
        elif isinstance(message, Message):
            new_messages.append(message)
    forward_messages = [
        MessageSegment(
            type="node",
            data={
                "user_id": str(event.self_id),
                "nickname": "Bottle",
                "name": "Bottle",
                "uin": str(event.self_id),
                "content": message,
            },
        )
        for message in new_messages
    ]
    if isinstance(event, GroupMessageEvent):
        await bot.send_group_forward_msg(
            group_id=event.group_id,
            messages=forward_messages,
        )
    else:
        await bot.send_private_forward_msg(
            user_id=event.user_id,
            messages=forward_messages,
        )


@throw.handle()
async def _(
    matcher: Matcher,
    event: GroupMessageEvent,
    args: Message = CommandArg(),
):
    await verify(matcher=matcher, event=event)
    message = event.reply.message if event.reply else args
    if message:
        matcher.set_arg("content", message)
        matcher.set_arg("__has_content__", True)


@throw.got(
    "content", prompt="在漂流瓶中要写下什么呢？（输入“取消”来取消扔漂流瓶操作。）"
)
async def _(
    bot: Bot,
    state: T_State,
    event: GroupMessageEvent,
    args: Message = Arg("content"),
    session: AsyncSession = Depends(get_session),
):
    message_text = args.extract_plain_text().strip()

    message_id = event.message_id

    ba.add("cooldown", event.user_id)

    if "__has_content__" not in state and message_text in cancel:
        await throw.finish(MessageSegment.reply(message_id) + "已取消扔漂流瓶操作。")

    if maxlen != 0 and ((msg_len := len(message_text)) > maxlen):
        await throw.finish(
            MessageSegment.reply(message_id)
            + f"您漂流瓶中的字符数量超过了最大字符限制：{maxlen}。您可以尝试减少漂流瓶内容。\n当前字符数量：{msg_len}"
        )
    if maxrt != 0 and ((rt_cnt := message_text.count("\n")) > maxrt):
        await throw.finish(
            MessageSegment.reply(message_id)
            + f"您漂流瓶中的换行数量超过了最大换行限制：{maxrt}。您可尝试减少换行数量。\n当前换行数量：{rt_cnt}"
        )
    if rtrate != 0 and rt_cnt != 0 and (msg_len / rt_cnt) <= rtrate:
        await throw.finish(
            MessageSegment.reply(message_id)
            + "您漂流瓶中的字符换行比率超过了最大字符换行比率限制。\n字符换行比率，是您发送的漂流瓶总字符数量和换行的比值。为了防止刷屏，请您尝试减少漂流瓶的换行数量或增加有意义漂流瓶字符。"
        )
    audit = await text_audit(text=message_text)
    if not audit == "pass":
        if audit == "Error":
            await throw.finish(
                MessageSegment.reply(message_id)
                + "文字审核未通过！原因：调用审核API失败，请检查违禁词词表是否存在，或token是否正确设置！"
            )
        elif audit["conclusion"] == "不合规":
            await throw.finish(
                MessageSegment.reply(message_id)
                + "文字审核未通过！原因："
                + audit["data"][0]["msg"]
            )

    try:
        group_info = await bot.get_group_info(group_id=event.group_id)
        group_name = group_info["group_name"]
    except:
        group_name = "Unknown"
    user_info = await bot.get_group_member_info(
        group_id=event.group_id, user_id=event.user_id
    )
    user_name = user_info.get("card") or user_info.get("nickname")

    add_index = await bottle_manager.add_bottle(
        user_id=event.user_id,
        group_id=event.group_id,
        content=await serialize_message(message=args),
        user_name=user_name,
        group_name=group_name,
        session=session,
    )
    await session.commit()
    if add_index:
        # 添加个人冷却
        ba.add("cooldown", event.user_id)
        await asyncio.sleep(2)
        await throw.send(
            MessageSegment.reply(message_id)
            + f"你将编号No.{add_index}的漂流瓶以时速{random.randint(0,2**16)}km/h的速度扔出去，谁会捡到这个瓶子呢..."
        )
    else:
        await asyncio.sleep(2)
        await throw.send("你的瓶子以奇怪的方式消失掉了！")


likes = set(["+", "点赞", "赞"])


@get.handle()
async def _(
    bot: Bot,
    matcher: Matcher,
    event: GroupMessageEvent,
    state: T_State,
    session: AsyncSession = Depends(get_session),
):
    await verify(matcher=matcher, event=event)

    bottle = await bottle_manager.select(session=session)
    if not bottle:
        await get.finish("好像一个瓶子也没有呢..要不要扔一个？")
    try:
        user_info = await bot.get_group_member_info(
            group_id=bottle.group_id, user_id=bottle.user_id
        )
        user_name = user_info.get("card") or user_info.get("nickname")
    except ActionFailed:
        user_name = bottle.user_name
    try:
        group_info = await bot.get_group_info(group_id=bottle.group_id)
        group_name = group_info["group_name"]
    except ActionFailed:
        group_name = bottle.group_name

    comments = await bottle_manager.get_comment(bottle=bottle, session=session)
    comment_str = "\n".join(
        [f"{comment.user_name}：{comment.content}" for comment in comments]
    )
    ba.add("cooldown", event.user_id)
    bottle_content = (await deserialize_message(bottle.content)).extract_plain_text().strip()
    bottle_message = (
        f"【漂流瓶No.{bottle.id}】【+{bottle.like}/{bottle.picked}】\n来自【{group_name}】的“{user_name}”！\n"
        + f"时间：{bottle.time.strftime('%Y-%m-%d')}\n"
        + f"内容：\n"
        + await deserialize_message(bottle.content)
        + (f"\n★前 {len(comments)} 条评论★\n{comment_str}" if comment_str else "")
    )

    if whether_collapse(bottle, bottle_content):
        await try_send_forward(event, bot, [bottle_message])
    else:
        message_id = event.message_id
        await get.send(MessageSegment.reply(message_id) + bottle_message)
    state["bottle_id"] = bottle.id
    await session.commit()


@get.got("prompt")
async def _(
    bot: Bot,
    matcher: Matcher,
    event: GroupMessageEvent,
    like: str = ArgStr("prompt"),
    bottle_id: int = Arg("bottle_id"),
    session: AsyncSession = Depends(get_session),
):
    if like in likes:
        bottle = await get_bottle(index=bottle_id, matcher=matcher, session=session)
        result = await bottle_manager.like_bottle(
            bottle=bottle, user_id=event.user_id, session=session
        )
        if result == 0:
            await get.send("你已经点过赞了。")
        elif result == 1:
            ba.add("cooldown", event.user_id)
            await get.send(f"点赞成功～该漂流瓶已有 {bottle.like} 次点赞！")
            await session.commit()
    else:
        asyncio.create_task(handle_event(bot=bot, event=event))


@like.handle()
async def _(
    matcher: Matcher,
    event: GroupMessageEvent,
    args: Message = CommandArg(),
    session: AsyncSession = Depends(get_session),
):
    index = args.extract_plain_text().strip()
    bottle = await get_bottle(index=index, matcher=matcher, session=session)
    result = await bottle_manager.like_bottle(
        bottle=bottle, user_id=event.user_id, session=session
    )
    if result == 0:
        await like.send("你已经点过赞了。")
    elif result == 1:
        ba.add("cooldown", event.user_id)
        await like.send(f"点赞成功～该漂流瓶已有 {bottle.like} 次点赞！")
        await session.commit()


@report.handle()
async def _(
    bot: Bot,
    matcher: Matcher,
    event: GroupMessageEvent,
    args: Message = CommandArg(),
    session: AsyncSession = Depends(get_session),
):
    await verify(matcher=matcher, event=event)
    if not ba.verifyReport(event.user_id):
        await report.finish(ba.bannedMessage)

    index = args.extract_plain_text().strip()
    bottle = await get_bottle(index=index, matcher=matcher, session=session)
    result = await bottle_manager.report(
        bottle=bottle, user_id=event.user_id, session=session
    )
    if result == 0:
        await report.send("举报失败！")
    elif result == 1:
        ba.add("cooldown", event.user_id)
        await report.send(f"举报成功！关于此漂流瓶已经有 {bottle.report} 次举报")
        await session.commit()
    elif result == 2:
        mes = f"有一漂流瓶遭到封禁！\n编号：{bottle.id}\n用户QQ：{bottle.user_id}\n来源群组：{bottle.group_id}\n"
        mes += await deserialize_message(bottle.content)
        comments = await bottle_manager.get_comment(
            bottle=bottle, session=session, limit=None
        )
        comment_str = "\n".join(
            [
                f"【{comment.user_id}】{comment.user_name}：{comment.content}"
                for comment in comments
            ]
        )
        await session.commit()

        # 私聊发送被删除的漂流瓶详情
        for i in list(bot.config.superusers):
            await bot.send_private_msg(user_id=i, message=mes)
            await bot.send_private_msg(user_id=i, message=comment_str)
            await asyncio.sleep(0.5)
        await report.send("举报成功！该漂流瓶已沉底。")
    elif result == 3:
        await report.send("该漂流瓶已经被删除。")


@comment.handle()
async def _(
    bot: Bot,
    matcher: Matcher,
    event: GroupMessageEvent,
    args: Message = CommandArg(),
    session: AsyncSession = Depends(get_session),
):
    await verify(matcher=matcher, event=event)

    command = args.extract_plain_text().strip().split()
    message_id = event.message_id
    if not command:
        await comment.finish(
            MessageSegment.reply(message_id) + f"请在指令后接 漂流瓶id 评论"
        )
    if len(command) == 1:
        await comment.finish(
            MessageSegment.reply(message_id) + "想评论什么呀，在后边写上吧！"
        )
    bottle = await get_bottle(index=command[0], matcher=matcher, session=session)
    user_info = await bot.get_group_member_info(
        group_id=event.group_id, user_id=event.user_id
    )
    user_name = user_info.get("card") or user_info["nickname"]
    command[1] = command[1].strip()

    # 进行文字审核
    audit = await text_audit(text=command[1])
    if not audit == "pass":
        if audit == "Error":
            await comment.finish(
                MessageSegment.reply(message_id)
                + "文字审核未通过！原因：调用审核API失败，请检查违禁词词表格式是否正确，或token是否正确设置！"
            )
        elif audit["conclusion"] == "不合规":
            await comment.finish(
                MessageSegment.reply(message_id)
                + "文字审核未通过！原因："
                + audit["data"][0]["msg"]
            )

    # 审核通过
    bottle_manager.comment(
        bottle=bottle,
        user_id=event.user_id,
        user_name=user_name,
        content=command[1],
        session=session,
    )
    try:
        if not disable_comment_prompt:
            await bot.send_group_msg(
                group_id=bottle.group_id,
                message=Message(
                    MessageSegment.at(bottle.user_id)
                    + f" 你的{bottle.id}号漂流瓶被评论啦！\n{command[1]}"
                ),
            )
            await asyncio.sleep(2)
    finally:
        ba.add("cooldown", event.user_id)
        await comment.send("回复成功！")
    await session.commit()


# 查看漂流瓶
@check_bottle.handle()
async def _(
    bot: Bot,
    event: GroupMessageEvent,
    matcher: Matcher,
    args: Message = CommandArg(),
    session: AsyncSession = Depends(get_session),
):
    index = args.extract_plain_text().strip()
    bottle = await get_bottle(index=index, matcher=matcher, session=session)

    try:
        user_info = await bot.get_group_member_info(
            group_id=bottle.group_id, user_id=bottle.user_id
        )
        user_name = user_info.get("card") or user_info.get("nickname")
    except ActionFailed:
        user_name = bottle.user_name
    try:
        group_info = await bot.get_group_info(group_id=bottle.group_id)
        group_name = group_info["group_name"]
    except ActionFailed:
        group_name = bottle.group_name
    comments = await bottle_manager.get_comment(bottle=bottle, session=session)
    message_id = event.message_id
    if not everyone_can_read and (
        not comments
        and event.user_id != bottle.user_id
        and str(event.user_id) not in bot.config.superusers
    ):
        await check_bottle.finish(
            MessageSegment.reply(message_id)
            + f"这个漂流瓶还没有评论，或你不是此漂流瓶的主人，因此不能给你看里面的东西！\n【该漂流瓶(+{bottle.like})来自【{group_name}】的 {user_name}，被捡到{bottle.picked}次，于{bottle.time.strftime('%Y-%m-%d %H:%M:%S')}扔出】"
        )

    comment_str = "\n".join(
        [f"{comment.user_name}：{comment.content}" for comment in comments]
    )
    comment_all = f"★前 {len(comments)} 条评论★\n{comment_str}\n" if comments else ""
    ba.add("cooldown", event.user_id)
    check_msg = (
        MessageSegment.reply(message_id)
        + f"#{bottle.id}(+{bottle.like})：来自【{group_name}】的 {user_name}\n"
        + await deserialize_message(bottle.content)
        + f"\n\n"
        + comment_all
        + f"【被捡到{bottle.picked}次，于{bottle.time.strftime('%Y-%m-%d %H:%M:%S')}扔出】"
    )

    if whether_collapse(bottle, check_msg):
        await try_send_forward(event, bot, [check_msg])
    else:
        message_id = event.message_id
        await check_bottle.finish(MessageSegment.reply(message_id) + check_msg)


@remove.handle()
async def _(
    bot: Bot,
    matcher: Matcher,
    event: GroupMessageEvent,
    arg: Message = CommandArg(),
    session: AsyncSession = Depends(get_session),
):
    index = arg.extract_plain_text().strip()
    bottle = await get_bottle(index=index, matcher=matcher, session=session)
    message_id = event.message_id
    if str(event.user_id) in bot.config.superusers or bottle.user_id == event.user_id:
        content_preview = await get_content_preview(bottle)
        matcher.set_arg("index", int(index))
        await remove.send(
            MessageSegment.reply(message_id)
            + f"真的要删除{index}(+{bottle.like})号漂流瓶（Y/N）？漂流瓶将会永久失去。（真的很久！）\n漂流瓶内容：{content_preview}"
        )
    else:
        await remove.finish(MessageSegment.reply(message_id) + "你没有相关权限。")


@remove.got("prompt")
async def _(
    event: GroupMessageEvent,
    conf: str = ArgStr("prompt"),
    index: int = Arg("index"),
    session: AsyncSession = Depends(get_session),
):
    message_id = event.message_id
    if conf in proceed:
        (await bottle_manager.get_bottle(index=index, session=session)).is_del = True
        await session.commit()
        await remove.send(
            MessageSegment.reply(message_id) + f"成功删除 {index} 号漂流瓶！"
        )
    else:
        await remove.finish(MessageSegment.reply(message_id) + "取消删除操作。")


@listb.handle()
async def _(
    bot: Bot, event: GroupMessageEvent, session: AsyncSession = Depends(get_session)
):
    bottles = await bottle_manager.list_bottles(
        user_id=event.user_id, session=session, include_del=False
    )
    if not bottles:
        await listb.finish("你还没有扔过漂流瓶哦～")

    # 获取漂流瓶预览内容
    bottles_info = []
    for bottle in bottles:
        content_preview = await get_content_preview(bottle)
        bottles_info.append(f"#{bottle.id}【+{bottle.like}】：{content_preview}")

    # 整理消息
    messages = []
    total_bottles_info = f"您总共扔了{len(bottles_info)}个漂流瓶～\n"
    if len(bottles_info) > 10:
        i = 1
        while len(bottles_info) > 10:
            messages.append(
                total_bottles_info + "\n".join(bottles_info[:10]) + f"\n【第{i}页】"
            )
            bottles_info = bottles_info[10:]
            i = i + 1
        messages.append(
            total_bottles_info + "\n".join(bottles_info[:10]) + f"\n【第{i}页-完】"
        )

        # 发送合并转发消息
        await try_send_forward(event, bot, messages)
    else:
        await listb.finish(total_bottles_info + "\n".join(bottles_info[:10]))
    ba.add("cooldown", event.user_id)


###### SUPERUSER命令 ######


@resume.handle()
async def _(
    matcher: Matcher,
    arg: Message = CommandArg(),
    session: AsyncSession = Depends(get_session),
):
    index = arg.extract_plain_text().strip()
    bottle = await get_bottle(
        index=index, matcher=matcher, session=session, include_del=True
    )
    bottle.is_del = False
    await session.commit()
    await resume.finish(f"成功恢复 {index} 号漂流瓶！")


@clear.got(
    "prompt",
    prompt="你确定要清空所有漂流瓶吗？（Y/N）所有的漂流瓶都将会永久失去。（真的很久！）",
)
async def _(conf: str = ArgStr("prompt"), session: AsyncSession = Depends(get_session)):
    if conf in proceed:
        await bottle_manager.clear(session)
        await session.commit()
        await clear.finish("所有漂流瓶清空成功！")
    else:
        await clear.finish("取消清空操作。")


@listqq.handle()
async def _(
    bot: Bot,
    event: MessageEvent,
    matcher: Matcher,
    args: Message = CommandArg(),
    session: AsyncSession = Depends(get_session),
):
    index = args.extract_plain_text().strip()
    bottle = await get_bottle(
        index=index, matcher=matcher, session=session, include_del=True
    )

    msg_list = []

    mes = (
        ("【已删除】" if bottle.is_del else "")
        + f"漂流瓶编号：{index}【+{bottle.like}】\n用户QQ：{bottle.user_id}\n来源群组：{bottle.group_id}\n发送时间：{bottle.time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    )
    msg_list.append(mes + await deserialize_message(bottle.content))

    report_info = await bottle_manager.get_report_info(bottle=bottle, session=session)

    if report_info:
        msg_list.append(
            f"被举报 {len(report_info)} 次\n举报人：\n"
            + "\n".join([str(report.user_id) for report in report_info])
        )
    else:
        msg_list.append("漂流瓶暂未被举报")

    comments = await bottle_manager.get_comment(
        bottle=bottle, session=session, limit=None
    )
    comment_str = "\n".join(
        [
            f"【{comment.user_id}】{comment.user_name}：{comment.content}"
            for comment in comments
        ]
    )
    if comment_str:
        msg_list.append(comment_str)
    else:
        msg_list.append("漂流瓶暂无回复")
    await try_send_forward(event, bot, msg_list)


@ban.handle()
async def _(
    args: Message = CommandArg(),
):
    command = args.extract_plain_text().strip().split(" ")
    if command[0] in ["group", "群聊", "群号"]:
        if ba.add("group", command[1]):
            await ban.finish(f"成功封禁{command[0]}：{command[1]}")
        else:
            ba.remove("group", command[1])
            await ban.finish(f"成功解封{command[0]}：{command[1]}")

    if command[0] in ["qq", "QQ", "user", "用户", "qq号", "QQ号"]:
        if ba.add("user", command[1]):
            await ban.finish(f"成功封禁{command[0]}：{command[1]}")
        else:
            ba.remove("user", command[1])
            await ban.finish(f"成功解封{command[0]}：{command[1]}")

    if command[0] in ["report", "举报"]:
        result = ba.banreport(command[1])
        if result == 1:
            await ban.finish(f"成功取消{command[0]}权限：{command[1]}")
        elif result == 0:
            await ban.finish(f"成功赋予{command[0]}权限：{command[1]}")
        else:
            await ban.finish(result)


@white.handle()
async def _(
    args: Message = CommandArg(),
):
    command = args.extract_plain_text().strip().split(" ")
    if command[0] in ["group", "群聊", "群号"]:
        if ba.add("whiteGroup", command[1]):
            await ban.finish(f"成功设置白名单{command[0]}：{command[1]}")
        else:
            ba.remove("whiteGroup", command[1])
            await ban.finish(f"成功移除白名单{command[0]}：{command[1]}")

    if command[0] in ["qq", "QQ", "user", "用户", "qq号", "QQ号"]:
        if ba.add("whiteUser", command[1]):
            await ban.finish(f"成功设置白名单{command[0]}：{command[1]}")
        else:
            ba.remove("whiteUser", command[1])
            await ban.finish(f"成功移除白名单{command[0]}：{command[1]}")


@comrem.handle()
async def _(
    matcher: Matcher,
    args: Message = CommandArg(),
    session: AsyncSession = Depends(get_session),
):
    command = args.extract_plain_text().strip().split()
    if len(command) != 2:
        await comrem.finish("请检查参数")
    bottle = await get_bottle(
        index=command[0], matcher=matcher, session=session, include_del=True
    )
    command[1] = command[1].strip()
    if not command[1].isdigit():
        await comrem.finish("用户id必须为数字！")
    await bottle_manager.del_comment(
        bottle=bottle, user_id=int(command[1]), session=session
    )
    await session.commit()
    await comrem.finish("删除成功！")
