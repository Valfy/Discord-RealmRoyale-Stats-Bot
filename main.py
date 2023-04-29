# -- coding: utf-8 --

import discord
from discord.ext import commands
import environ
import pyrez
from pyrez.api import RealmRoyaleAPI

from allowed_dicts import allowed_classes, allowed_gamemode, dict_of_platforms, STATUS_MESSAGES, placement_medals
from vn_logger import VN_logger

env = environ.Env()
environ.Env.read_env()

if env('PRINT') == 'True':
   VN_logger.PRINT_MESSAGES = True
else:
   VN_logger.PRINT_MESSAGES = False
if env('LOGGING') == 'True':
   VN_logger.LOGGING = True
else:
   VN_logger.LOGGING = False
VN_logger.LOG_LEVEL_CEILING = 0
if VN_logger.LOGGING:
    VN_logger.logging('RUN', f'Запуск логгера с параметрами FILENAME={VN_logger._FILENAME}.txt,'
                             f' PRINT_MESSAGES={VN_logger.PRINT_MESSAGES},'
                             f' LOGGING={VN_logger.LOGGING},'
                             f' LOG_LEVEL_CEILING={VN_logger.LOG_LEVEL_CEILING}')

CHANNELS = set()
LOG_CHANNEL = -1

try:
    VN_logger.logging('INFO', 'Шаг 1 из 5 Попытка прочитать channels.txt')
    with open('channels.txt', 'r') as reader:
        line_number = 0
        for line in reader:
            line_number += 1
            if 'LOG' in line:
                try:
                    LOG_CHANNEL = int(line.replace('LOG', ''))
                except ValueError as error:
                    if line != '\n':
                        VN_logger.logging('INFO', f'Пропуск линии №{line_number}')
                        VN_logger.logging('ERROR', error)
                    LOG_CHANNEL = -1
            else:
                try:
                    channel_to_add = int(line)
                except ValueError as error:
                    if line != '\n':
                        VN_logger.logging('INFO', f'Пропуск линии №{line_number}')
                        VN_logger.logging('ERROR', error)
                else:
                    CHANNELS.add(channel_to_add)
except FileNotFoundError as error:
    VN_logger.logging('INFO', 'Шаг 2 из 5 Неудачная попытка прочитать channels.txt, создаю чистый')
    VN_logger.logging('ERROR', error)
    with open('channels.txt', 'w+') as create:
        create.write('')
else:
    VN_logger.logging('INFO', 'Шаг 2 из 5 Успешно прочитан channels.txt')

try:
    VN_logger.logging('INFO', 'Шаг 3 из 5 Попытка подключится к API')
    rrAPI = RealmRoyaleAPI(devId=env('DEV_ID'), authKey=env('AUTH_KEY'))
    pSession = rrAPI._createSession()
except (pyrez.exceptions.InvalidArgument, pyrez.exceptions.IdOrAuthEmpty) as error:
    VN_logger.logging('INFO', 'Шаг 4 из 5 Неудачная попытка подключится к API')
    VN_logger.logging('ERROR', error)
    exit(0)
else:
    VN_logger.logging('INFO', 'Шаг 4 из 5 Успешное подключение к API')
    VN_logger.BANWORDS.append(str(env('DEV_ID')))


bot = commands.Bot(command_prefix='hilda!', status=discord.Status.idle)


@bot.event
async def on_ready():
    VN_logger.logging('INFO', 'Шаг 5 из 5 Хильда готова к охоте')


@bot.command(pass_context=True)
async def add_channel(ctx, channelID, status='commands'):
    VN_logger.logging('COMMAND', f'Вызов команды add_channel, с параметрами {channelID}, {status}, от пользователя {ctx.author}')
    global CHANNELS, LOG_CHANNEL
    if ctx.message.author.guild_permissions.administrator:
        try:
            channel_to_add = int(channelID)
        except Exception as error:
            VN_logger.logging('ERROR', error)
            VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Нужно число!')
            await ctx.send('Нужно число!')
        else:
            if status.upper() == 'LOG':
                if channel_to_add == LOG_CHANNEL:
                    VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: В этот канал уже отправляются ошибки!')
                    await ctx.send('В этот канал уже отправляются ошибки!')
                else:
                    LOG_CHANNEL = channel_to_add
                    with open('channels.txt', 'a') as writer:
                        writer.write(f'LOG{channel_to_add}\n')
                    VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Понятно!')
                    await ctx.send('Понятно!')
            else:
                if channel_to_add in CHANNELS:
                    VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Такой канал уже в списках!')
                    await ctx.send('Такой канал уже в списках!')
                else:
                    CHANNELS.add(channel_to_add)
                    with open('channels.txt', 'a') as writer:
                        writer.write(f'{channel_to_add}\n')
                    VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Понятно!')
                    await ctx.send('Понятно!')
    else:
        VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: У тебя нет прав!')
        await ctx.send('У тебя нет прав!')


@bot.command(pass_context=True)
async def delete_channel(ctx, channelID):
    VN_logger.logging('COMMAND', f'Вызов команды delete_channel, с параметрами {channelID}, от пользователя {ctx.author}')
    global CHANNELS, LOG_CHANNEL
    if ctx.message.author.guild_permissions.administrator:
        try:
            channel_to_add = int(channelID)
        except Exception as error:
            VN_logger.logging('ERROR', error)
            VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Нужно число!')
            await ctx.send('Нужно число!')
        else:
            if channel_to_add in CHANNELS:
                CHANNELS.remove(channel_to_add)
                with open('channels.txt', 'w') as writer:
                    for channel in CHANNELS:
                        writer.write(f'{channel}\n')
                    if LOG_CHANNEL != -1:
                        writer.write(f'LOG{LOG_CHANNEL}\n')
                VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Канал успешно удалён!')
                await ctx.send('Канал успешно удалён!')
            else:
                VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Такого канала нет в списках!')
                await ctx.send('Такого канала нет в списках!')
    else:
        VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: У тебя нет прав!')
        await ctx.send('У тебя нет прав!')


@bot.command(pass_context=True)
async def return_channels(ctx):
    VN_logger.logging('COMMAND', f'Вызов команды return_channel, от пользователя {ctx.author}')
    global CHANNELS, LOG_CHANNEL
    if ctx.message.author.guild_permissions.administrator:
        VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Список каналов: {list(CHANNELS)}')
        await ctx.send(f'Список каналов: {list(CHANNELS)}\nКанал логгер: {LOG_CHANNEL}')
    else:
        VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: У тебя нет прав!')
        await ctx.send('У тебя нет прав!')


@bot.command(pass_context=True)
async def profile(ctx, name_or_id, platform='5'):
    VN_logger.logging('COMMAND', f'Вызов команды profile, с параметрами {name_or_id}, {platform}, от пользователя {ctx.author}')
    BREAK = False
    if ctx.channel.id in CHANNELS:
        try:
            type_test = int(name_or_id)
        except ValueError:
            player_name = name_or_id
            try:
                rr_pid = rrAPI.getPlayerId(playerName=player_name,
                                           portalId=dict_of_platforms[platform.upper()] if platform.upper() in dict_of_platforms else 5)
                playerid = rr_pid[0]["id"]
            except:
                MSG = VN_logger.collect_traceback()
                VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Ошибочка!')
                await ctx.send('Ошибочка!')
                if LOG_CHANNEL != -1:
                    channel_to_send_traceback = bot.get_channel(LOG_CHANNEL)
                    await channel_to_send_traceback.send(MSG)
                BREAK = True
        else:
            try:
                playerid = type_test
                rr_player = rrAPI.getPlayer(playerid, 5)
                player_name = rr_player['name']
            except:
                MSG = VN_logger.collect_traceback()
                VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Ошибочка!')
                await ctx.send('Ошибочка!')
                if LOG_CHANNEL != -1:
                    channel_to_send_traceback = bot.get_channel(LOG_CHANNEL)
                    await channel_to_send_traceback.send(MSG)
                BREAK = True
        finally:
            try:
                rr_pstats = rrAPI.getPlayerStats(playerId=playerid)
                rr_status = rrAPI.getPlayerStatus(playerId=playerid)
            except:
                if not BREAK:
                    MSG = VN_logger.collect_traceback()
                    VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Ошибочка!')
                    await ctx.send('Ошибочка!')
                    if LOG_CHANNEL != -1:
                        channel_to_send_traceback = bot.get_channel(LOG_CHANNEL)
                        await channel_to_send_traceback.send(MSG)
            else:
                try:
                    player_matches_class = {
                        'total': 0
                    }
                    player_wins_class = {
                        'total': 0
                    }
                    player_wins_mode = {}
                    for x in rr_pstats['queue_class_stats']:
                        if x['class_name'] in player_matches_class:
                            player_matches_class[x['class_name']] += x['stats']['games_played']
                        else:
                            player_matches_class[x['class_name']] = x['stats']['games_played']
                        player_matches_class['total'] += x['stats']['games_played']

                        if x['class_name'] in player_wins_class:
                            player_wins_class[x['class_name']] += x['stats']['wins']
                        else:
                            player_wins_class[x['class_name']] = x['stats']['wins']
                        player_wins_class['total'] += x['stats']['wins']

                        if x['match_queue_name'] in player_wins_mode:
                            player_wins_mode[x['match_queue_name']] += x['stats']['wins']
                        else:
                            player_wins_mode[x['match_queue_name']] = x['stats']['wins']

                    embed = discord.Embed(title=f'Профиль игрока {player_name} (ID:{playerid})\n',
                                          description=f'Всего матчей сыграно **{player_matches_class["total"]}**,'
                                                      f' из них выйграно **{player_wins_class["total"]}** \n',
                                          color=0xff9955)
                    embed.set_thumbnail(url="https://raw.githubusercontent.com/luissilva1044894/hirez-api-docs/master/.assets/realm-royale/icons/{}.png"
                          .format(str(sorted(player_matches_class.items(), key=lambda i: i[1], reverse=True)[1][0]).lower()))
                    embed.add_field(name='Статус',
                                    value=STATUS_MESSAGES[rr_status["status_id"]],
                                    inline=False)

                    value_to_send = ""
                    for x in player_matches_class:
                        if x != 'total':
                            if x in allowed_classes:
                                value_to_send += f'**{allowed_classes[x]}**: Сыграно {player_matches_class[x]}, ' \
                                                 f'из них выйграно {player_wins_class[x]}\n'
                            else:
                                value_to_send += f'**Неизвестный класс**: Сыграно {player_matches_class[x]}, ' \
                                                 f'из них выйграно {player_wins_class[x]}\n'
                    embed.add_field(name='Матчей по классам:',
                                    value=value_to_send,
                                    inline=False)

                    value_to_send = ""
                    for y in player_wins_mode:
                        value_to_send += f'{allowed_gamemode[y] if y in allowed_gamemode else y}: **{player_wins_mode[y]}**\n'
                    embed.add_field(name='Побед в режимах:',
                                    value=value_to_send,
                                    inline=False)

                    VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: embed*')
                    await ctx.send(embed=embed)
                except:
                    if not BREAK:
                        MSG = VN_logger.collect_traceback()
                        VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Ошибочка!')
                        await ctx.send('Ошибочка!')
                        if LOG_CHANNEL != -1:
                            channel_to_send_traceback = bot.get_channel(LOG_CHANNEL)
                            await channel_to_send_traceback.send(MSG)
    else:
        VN_logger.logging('INFO', f'Недопустимый канал для команды, пользователю {ctx.author} не отвечаем')


@bot.command(pass_context=True)
async def mh(ctx, id, matches=None):
    VN_logger.logging('COMMAND', f'Вызов команды mh, с параметрами {id}, {matches}, от пользователя {ctx.author}')
    if ctx.channel.id in CHANNELS:
        if matches is None:
            matches = 5
        try:
            matches = int(matches)
        except ValueError:
            VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Нужно указать количество матчей в виде цифр от 1 до 12')
            await ctx.send('Нужно указать количество матчей в виде цифр от 1 до 12')
        else:
            if matches > 12:
                matches = 12
            if matches < 1:
                matches = 5
            try:
                rr_history = rrAPI.getMatchHistory(playerId=id)
            except:
                MSG = VN_logger.collect_traceback()
                VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Ошибочка!')
                await ctx.send('Ошибочка!')
                if LOG_CHANNEL != -1:
                    channel_to_send_traceback = bot.get_channel(LOG_CHANNEL)
                    await channel_to_send_traceback.send(MSG)
            else:
                playername = rr_history["name"]
                embed = discord.Embed(title=f'Последние матчи игрока {playername}:',
                                      color=0xff9955)
                try:
                    rr_matches = rr_history["matches"][:matches]
                except TypeError:
                    embed.add_field(name="Матчи не найдены", value="Проверьте точно ли вы указали айди.", inline=False)
                else:
                    for match in rr_matches:
                        title_to_send, value_to_send = "", ""
                        if match["placement"] <= 3:
                            title_to_send += f'🟧 {placement_medals[match["placement"]]}'
                        else:
                            title_to_send += f'🟨'
                        title_to_send += f' (Топ {match["placement"]}) ID: {match["match_id"]}'
                        value_to_send += f'Класс: {allowed_classes[match["class_name"]]} 🔸 ' \
                            if match["class_name"] in allowed_classes else 'Неизвестный класс 🔸 '
                        value_to_send += f'Режим: {allowed_gamemode[match["match_queue_name"]]} \n' \
                            if match["match_queue_name"] in allowed_gamemode else f'{match["match_queue_name"]} \n'
                        embed.add_field(name=title_to_send, value=value_to_send, inline=False)
                finally:
                    VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: embed*')
                    await ctx.send(embed=embed)
    else:
        VN_logger.logging('INFO', f'Недопустимый канал для команды, пользователю {ctx.author} не отвечаем')


@bot.command(pass_context=True)
async def mi(ctx, match_id, theme='standart'):
    VN_logger.logging('COMMAND', f'Вызов команды mi, с параметрами {match_id}, {theme}, от пользователя {ctx.author}')
    BREAK = False
    if ctx.channel.id in CHANNELS:
        if 'last' in match_id:
            try:
                rr_history = rrAPI.getMatchHistory(playerId=match_id.replace('last', '').replace(' ', ''))
            except:
                MSG = VN_logger.collect_traceback()
                VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Ошибочка!')
                await ctx.send('Ошибочка!')
                if LOG_CHANNEL != -1:
                    channel_to_send_traceback = bot.get_channel(LOG_CHANNEL)
                    await channel_to_send_traceback.send(MSG)
                BREAK = True
            else:
                match_id = str(rr_history["matches"][0]["match_id"])

        try:
            rr_mi = rrAPI.getMatch(matchId=[match_id])
        except:
            if not BREAK:
                MSG = VN_logger.collect_traceback()
                VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Ошибочка!')
                await ctx.send('Ошибочка!')
                if LOG_CHANNEL != -1:
                    channel_to_send_traceback = bot.get_channel(LOG_CHANNEL)
                    await channel_to_send_traceback.send(MSG)
        else:
            gamemode_not_live = rr_mi[0]["match_queue_name"].replace('LIVE ', '')
            gamemode_right = allowed_gamemode[gamemode_not_live] if gamemode_not_live in allowed_gamemode else gamemode_not_live
            total_players, total_teams = 0, 0
            for team in rr_mi[0]["teams"]:
                total_teams += 1
                for _ in team["players"]:
                    total_players += 1
            if gamemode_not_live == 'Wars':
                total_teams = 2
                teams_info = [{"id": 1,
                               "placement": 1,
                               "players": []},
                              {"id": 2,
                               "placement": 999,
                               "players": []}]
                for team in rr_mi[0]["teams"]:
                    for player in team["players"]:
                        teams_info[0 if team["placement"] == 1 else 1]["players"].append(player)
            else:
                teams_info = rr_mi[0]["teams"][:10 if 'Соло' in gamemode_right else 5]
            embed = discord.Embed(title=f'Матч {match_id} в режиме {gamemode_right}:',
                                  description=f'{total_players} живых игроков, {total_teams} команд',
                                  color=0xff9955)
            for team in teams_info:
                title_to_send, value_to_send = "", ""
                if team["placement"] <= 3:
                    title_to_send += f'🟠 {placement_medals[team["placement"]]} топ {team["placement"]}'
                else:
                    title_to_send += f'🟡 🏅 топ {team["placement"]}'
                for player in team["players"]:
                    value_to_send += f'**{player["name"]}** (ID:{player["id"]}) на '
                    value_to_send += f'{allowed_classes[player["class_name"]]} \n' \
                        if player["class_name"] in allowed_classes else 'Неизвестный класс \n'
                    if theme == 'iconic':
                        value_to_send += f'{player["kills_player"]} ☠ 🔸' \
                                         f'{player["damage_player"]} ⚔ 🔸' \
                                         f'{player["damage_taken"]} 🛡 \n'
                    else:
                        value_to_send += f'Киллы: {player["kills_player"]} 🔸' \
                                         f'Урон: {player["damage_player"]} 🔸' \
                                         f'Полученный: {player["damage_taken"]} \n'
                embed.add_field(name=title_to_send, value=value_to_send, inline=False)
            VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: embed*')
            await ctx.send(embed=embed)
    else:
        VN_logger.logging('INFO', f'Недопустимый канал для команды, пользователю {ctx.author} не отвечаем')


@bot.command(pass_context=True)
async def status(ctx, name_or_id, platform='5'):
    VN_logger.logging('COMMAND', f'Вызов команды status, с параметрами {name_or_id}, {platform}, от пользователя {ctx.author}')
    BREAK = False
    if ctx.channel.id in CHANNELS:
        try:
            type_test = int(name_or_id)
        except ValueError:
            player_name = name_or_id
            try:
                rr_pid = rrAPI.getPlayerId(playerName=player_name,
                                           portalId=dict_of_platforms[platform.upper()] if platform.upper() in dict_of_platforms else 5)
                playerid = rr_pid[0]["id"]
            except:
                MSG = VN_logger.collect_traceback()
                VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Ошибочка!')
                await ctx.send('Ошибочка!')
                if LOG_CHANNEL != -1:
                    channel_to_send_traceback = bot.get_channel(LOG_CHANNEL)
                    await channel_to_send_traceback.send(MSG)
                BREAK = True
        else:
            try:
                playerid = type_test
                rr_player = rrAPI.getPlayer(playerid, 5)
                player_name = rr_player['name']
            except:
                MSG = VN_logger.collect_traceback()
                VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Ошибочка!')
                await ctx.send('Ошибочка!')
                if LOG_CHANNEL != -1:
                    channel_to_send_traceback = bot.get_channel(LOG_CHANNEL)
                    await channel_to_send_traceback.send(MSG)
                BREAK = True
        finally:
            try:
                rr_status = rrAPI.getPlayerStatus(playerId=playerid)
            except:
                if not BREAK:
                    MSG = VN_logger.collect_traceback()
                    VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Ошибочка!')
                    await ctx.send('Ошибочка!')
                    if LOG_CHANNEL != -1:
                        channel_to_send_traceback = bot.get_channel(LOG_CHANNEL)
                        await channel_to_send_traceback.send(MSG)
            else:
                try:
                    VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Статус игрока {player_name}: {STATUS_MESSAGES[rr_status["status_id"]]}')
                    await ctx.send(f'Статус игрока {player_name}: {STATUS_MESSAGES[rr_status["status_id"]]}')
                except:
                    if not BREAK:
                        MSG = VN_logger.collect_traceback()
                        VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Ошибочка!')
                        await ctx.send('Ошибочка!')
                        if LOG_CHANNEL != -1:
                            channel_to_send_traceback = bot.get_channel(LOG_CHANNEL)
                            await channel_to_send_traceback.send(MSG)
    else:
        VN_logger.logging('INFO', f'Недопустимый канал для команды, пользователю {ctx.author} не отвечаем')


TOKEN = env('HILDA_TOKEN')
bot.run(TOKEN)
