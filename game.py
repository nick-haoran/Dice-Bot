'''
file:game.py
author:nick-haoran
description:a simple dice game
'''
import asyncio
import json
import random
import re
import time
from khl import Bot, Message
from khl.card import Card, CardMessage, Element, Module, Types

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
account = {}
game_status = {}
channel = {}
bot = Bot(token='')
ban = {}

try:
    print('正在加载账号数据')
    with open('dice.data', 'r', encoding='utf-8') as f:
        json.load(f)
    print('加载成功')
except FileNotFoundError:
    print('加载失败')


async def get_dice() -> list:
    '''
    generate a 3-dice list
    '''
    random.seed(time.time())
    tmp = []
    for i in range(3):
        await asyncio.sleep(random.random())
        tmp.append(random.randint(1, 6))
    return tmp


def check_level(dice: list) -> dict:
    '''
    check the rate for the dice list
    '''
    dice_sum = dice[0] + dice[1] + dice[2]
    if dice[0] == dice[1] == dice[2]:
        return {'sum': dice_sum, 'level': 10}
    if dice[1] == dice[0] + 1 and dice[2] == dice[1] + 1:
        return {'sum': dice_sum, 'level': 5}
    if dice[1] == dice[0] or dice[2] == dice[1]:
        return {'sum': dice_sum, 'level': 2}
    return {'sum': dice_sum, 'level': 1}


def judge(dice1_result: dict, dice2_result: dict) -> bool:
    '''
    judge the game result
    '''
    if dice1_result['level'] != dice2_result['level']:
        return dice1_result['level'] > dice2_result['level']
    else:
        return dice1_result['sum'] > dice2_result['sum']


async def game_handler(player1_id: dict, player2_id: dict):
    '''
    1v1 game handler
    '''
    player1 = await bot.client.fetch_user(player1_id['id'])
    player2 = await bot.client.fetch_user(player2_id['id'])
    print(f'{player1.username}-{player2.username}')
    if player1_id['mode'] == '普通' and player2_id['mode'] == '普通':

        while True:
            dice1 = await get_dice()
            dice2 = await get_dice()
            sorted_dice1 = sorted(dice1)
            sorted_dice2 = sorted(dice2)
            if sorted_dice1 != sorted_dice2:
                break
        dice1_result = check_level(sorted_dice1)
        dice2_result = check_level(sorted_dice2)
        if judge(dice1_result, dice2_result):
            winner = {'account': player1, 'dice_result': dice1_result}
            loser = {'account': player2, 'dice_result': dice2_result}
        else:
            winner = {'account': player2, 'dice_result': dice2_result}
            loser = {'account': player1, 'dice_result': dice1_result}
        if channel[player1_id['id']].id != channel[player2_id['id']].id:
            content_str = f'(met){player1_id["id"]}(met) 您的三个骰子:{dice1},对手的三个骰子:{dice2}'
            await bot.client.send(channel[player1_id['id']],
                                  content=content_str)
            content_str = f'(met){player2_id["id"]}(met) 您的三个骰子:{dice2},对手的三个骰子:{dice1}'
            await bot.client.send(channel[player2_id['id']],
                                  content=content_str)
            content_str = f'您赢了,积分变化:{account[winner["account"].id]}->{account[winner["account"].id]+winner["dice_result"]["level"]}'
            account[winner["account"].id] = account[
                winner["account"].id] + winner["dice_result"]["level"]
            await bot.client.send(channel[winner["account"].id],
                                  content=content_str)
            content_str = f'您输了,积分变化:{account[loser["account"].id]}->{account[loser["account"].id]-winner["dice_result"]["level"]}'
            account[loser["account"].id] = account[
                loser["account"].id] - winner["dice_result"]["level"]
            await bot.client.send(channel[loser["account"].id],
                                  content=content_str)
        else:
            content_str = f'(met){player1_id["id"]}(met) 您的三个骰子:{dice1}\n(met){player2_id["id"]}(met) 您的三个骰子:{dice2}'
            await bot.client.send(channel[player1_id['id']],
                                  content=content_str)
            content_str = f'{winner["account"].username}赢了,积分变化:{account[winner["account"].id]}->{account[winner["account"].id]+winner["dice_result"]["level"]}'
            account[winner["account"].id] = account[
                winner["account"].id] + winner["dice_result"]["level"]
            await bot.client.send(channel[player1_id['id']],
                                  content=content_str)
            content_str = f'{loser["account"].username}输了,积分变化:{account[loser["account"].id]}->{account[loser["account"].id]-winner["dice_result"]["level"]}'
            account[loser["account"].id] = account[
                loser["account"].id] - winner["dice_result"]["level"]
            await bot.client.send(channel[player1_id['id']],
                                  content=content_str)
    else:
        if account[player1_id['id']] > account[player2_id['id']]:
            player1_id, player2_id = player2_id, player1_id
            player1, player2 = player2, player1
        while True:
            dice1 = await get_dice()
            dice2 = await get_dice()
            sorted_dice1 = sorted(dice1)
            sorted_dice2 = sorted(dice2)
            if sorted_dice1 != sorted_dice2:
                break
        dice1_result = check_level(sorted_dice1)
        dice2_result = check_level(sorted_dice2)

        if judge(dice1_result, dice2_result):
            winner = 1
        else:
            winner = 2
        if channel[player1_id['id']].id != channel[player2_id['id']].id:
            content_str = f'(met){player1_id["id"]}(met) 您的三个骰子:{dice1},对手的三个骰子:{dice2}'
            await bot.client.send(channel[player1_id['id']],
                                  content=content_str)
            content_str = f'(met){player2_id["id"]}(met) 您的三个骰子:{dice2},对手的三个骰子:{dice1}'
            await bot.client.send(channel[player2_id['id']],
                                  content=content_str)
            if winner == 1:
                content_str = f'您赢了,积分变化:{account[player1_id["id"]]}->{account[player1_id["id"]]+round(account[player2_id["id"]] * 0.9)}'
                account[player1_id["id"]] = account[player1_id["id"]] + round(
                    account[player2_id["id"]] * 0.9)
                await bot.client.send(channel[player1_id["id"]],
                                      content=content_str)
                content_str = f'您输了,积分变化:{account[player2_id["id"]]}->{account[player2_id["id"]]-round(account[player2_id["id"]] * 0.9)}'
                account[player2_id["id"]] = account[player2_id["id"]] - round(
                    account[player2_id["id"]] * 0.9)
                await bot.client.send(channel[player2_id["id"]],
                                      content=content_str)
            else:
                content_str = '您赢了,积分不变'
                await bot.client.send(channel[player2_id["id"]],
                                      content=content_str)
                content_str = '您输了,禁赛1小时'
                ban[player1_id["id"]] = time.time()
                await bot.client.send(channel[player1_id["id"]],
                                      content=content_str)
        else:
            content_str = f'(met){player1_id["id"]}(met) 您的三个骰子:{dice1}\n(met){player2_id["id"]}(met) 您的三个骰子:{dice2}'
            await bot.client.send(channel[player1_id['id']],
                                  content=content_str)
            if winner == 1:
                content_str = f'{player1.username}赢了,积分变化:{account[player1_id["id"]]}->{account[player1_id["id"]]+round(account[player2_id["id"]] * 0.9)}'
                account[player1_id["id"]] = account[player1_id["id"]] + round(
                    account[player2_id["id"]] * 0.9)
                await bot.client.send(channel[player1_id['id']],
                                      content=content_str)
                content_str = f'{player2.username}输了,积分变化:{account[player2_id["id"]]}->{account[player2_id["id"]]-round(account[player2_id["id"]] * 0.9)}'
                account[player2_id["id"]] = account[player2_id["id"]] - round(
                    account[player2_id["id"]] * 0.9)
                await bot.client.send(channel[player1_id['id']],
                                      content=content_str)
            else:
                content_str = f'{player2.username}赢了,积分不变'
                await bot.client.send(channel[player1_id['id']],
                                      content=content_str)
                content_str = f'{player1.username}输了,禁赛1小时'
                ban[player1_id["id"]] = time.time()
                await bot.client.send(channel[player1_id['id']],
                                      content=content_str)
    if account[player1_id['id']] < 0:
        content_str = f'(met){player1_id["id"]}(met) 您破产了,积分重置,禁赛1小时'
        await bot.client.send(channel[player1_id['id']], content=content_str)
        account[player1_id['id']] = 100
        ban[player1_id["id"]] = time.time()
    if account[player2_id['id']] < 0:
        content_str = f'(met){player2_id["id"]}(met) 您破产了,积分重置,禁赛1小时'
        await bot.client.send(channel[player2_id['id']], content=content_str)
        account[player2_id['id']] = 100
        ban[player2_id["id"]] = time.time()
    game_status[player1_id['id']] = 'FINISH'
    game_status[player2_id['id']] = 'FINISH'


@bot.command(name='匹配')
async def match_game(msg: Message, *args):
    '''
    match 1v1
    '''
    if time.time() - ban.get(msg.author.id, 0) < 3600:
        await msg.ctx.channel.send(
            f'您已被禁赛,剩余时间:{round(3600-time.time()+ban[msg.author.id])}秒')
        return
    args = list(args)
    if msg.author.id not in account:
        print(f"create account for {msg.author.username}-{msg.author.id}")
        account[msg.author.id] = 100
        ban[msg.author.id] = 0
        await msg.ctx.channel.send('账号创建成功')

    if msg.author.id in game_status:
        await msg.ctx.channel.send('您已在匹配或游戏中')
        return
    mode = '普通'
    target = '0'
    for s in args:
        if '特殊' in s:
            mode = '特殊'
        if '(met)' in s:
            try:
                pattern = r'(?<=\(met\))[0-9]+'
                tmp = re.search(pattern, s)
                assert tmp is not None
                target = tmp.group()
            except AssertionError:
                target = '0'
    game_status[msg.author.id] = f"MATCHING:{mode}:{target}"
    channel[msg.author.id] = msg.ctx.channel
    await msg.ctx.channel.send(f"正在匹配:{mode}")
    while 'MATCHING' in game_status[msg.author.id]:
        await asyncio.sleep(0.1)

    await msg.ctx.channel.send(
        f'(met){msg.author.id}(met) 匹配成功: {msg.author.username} vs {(await bot.client.fetch_user(game_status[msg.author.id])).username}'
    )


@bot.command(name='查询积分')
async def points_check(msg: Message):
    '''
    points query
    '''
    i = 0
    cm = CardMessage()
    ca = Card(color="#6AC629")
    ca.append(Module.Header('积分榜'))
    flag = False
    for player_id, points in sorted(account.items(),
                                    key=lambda kv: (kv[1], kv[0])):
        i += 1
        ca.append(
            Module.Section(
                f'#{i}: {(await bot.client.fetch_user(player_id)).username} {points}pp'
            ))
        if player_id == msg.author.id:
            flag = True
        if i == 10 and flag:
            break
    cm.append(ca)
    await msg.ctx.channel.send(cm)
    if msg.author.id not in account:
        await msg.ctx.channel.send('您还没有进行过游戏')
        return
    await msg.ctx.channel.send(f'您的积分: {account[msg.author.id]}pp 排名: #{i}')


@bot.command(name='帮助')
async def help_card(msg: Message):
    '''
    send help document
    '''
    helpcm = CardMessage(
        Card(
            Module.Header('帮助文档'),
            Module.Section(
                '1.匹配\n若没有游玩过则自动创建账号,初始积分100pp\n若已有账号且没有被禁赛则开始匹配\n在"匹配"后@可以指定你想要匹配的人\n在"匹配"后输入"特殊"可进行特殊挑战\n详细规则请看下图\n'),
            Module.Container(Element.Image(src='https://img.kookapp.cn/assets/2022-09/s8DgPILVyK0uh08i.png')),
            Module.Section('2.查询积分\n调出积分榜')))
    await msg.ctx.channel.send(helpcm)


@bot.task.add_interval(seconds=1)
async def auto_match_player():
    '''
    maintain matching queue
    '''
    game_status_iter = list(game_status.keys())
    random.shuffle(game_status_iter)
    waiting_player = []
    delete_list = []
    for player_id in game_status_iter:
        status = game_status[player_id]
        if status == 'FINISH':
            delete_list.append(player_id)
        if 'MATCHING' in status:
            status_split = status.split(':')
            waiting_player.append({
                'id': player_id,
                'mode': status_split[1],
                'target': status_split[2]
            })
        if len(waiting_player) == 2:
            if (waiting_player[0]['id'] == waiting_player[1]['target']
                    and waiting_player[1]['id'] == waiting_player[0]['target']
                ) or (waiting_player[0]['target'] == '0'
                      and waiting_player[1]['target']
                      == '0') or (waiting_player[0]['mode'] == '特殊'
                                  and account[waiting_player[0]['id']] <
                                  account[waiting_player[1]['id']]) or (
                                      waiting_player[1]['mode'] == '特殊'
                                      and account[waiting_player[1]['id']] <
                                      account[waiting_player[0]['id']]):
                game_status[waiting_player[0]['id']] = waiting_player[1]['id']
                game_status[waiting_player[1]['id']] = waiting_player[0]['id']
                asyncio.ensure_future(
                    game_handler(waiting_player[0], waiting_player[1]))
            waiting_player.clear()
    for player_id in delete_list:
        del game_status[player_id]


bot.command.update_prefixes("", ".", "/")
asyncio.ensure_future(bot.start(), loop=loop)
try:
    loop.run_forever()
except BaseException:
    print('正在保存账号数据')
    with open('dice.data', 'w', encoding='utf-8') as f:
        f.write(json.dumps(account))
    print('保存成功')
