"""Игра в 21"""
import json
import os
from datetime import datetime

import discord
from discord import NotFound

from discord.ext import commands, tasks
from discord_components import Button, ButtonStyle, DiscordComponents
from path import Path

from black_jack_core.config import info_1, info_2, STATIC_PATH
from black_jack_core.game import Game


class BlackJack(commands.Cog, name='ОЧКО'):
    """Игра в 21"""

    def __init__(self, bot):
        self.max_players = 4
        self.bot = bot
        self.game_channel = None
        self.game_message = None

        self.start_time = ''
        self.timer = 120
        self.max_timer = 120

        self.game = False

        self.start_players_lst = []
        self.final_players_lst = []
        self.channels_lst = []
        self.players = {}

        self.res = None

        self.game_path = Path("databases/blackjack/game.json")

    @commands.Cog.listener()
    async def on_button_click(self, res):
        """Проверка нажатых кнопок"""

        # Кнопки мп игры
        if res.component.id == 'go':
            if res.author in self.start_players_lst:
                self.final_players_lst.append(res.author.name)
                await res.channel.send(f':white_check_mark: {res.author.mention}, Вы приняли вызов!',
                                       delete_after=5)

                guild = res.guild
                member = res.author
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True),
                    member: discord.PermissionOverwrite(read_messages=True)
                }

                self.channels_lst.append(await guild.create_text_channel(f'Рука {res.author.name}',
                                                                         overwrites=overwrites))

                # Если все приняли
                if len(self.final_players_lst) == len(self.start_players_lst)+1:
                    self.start_timer.stop()
                    for i, pl in enumerate(self.final_players_lst):
                        self.players[pl] = self.channels_lst[i]

                    game = Game(self.players, self.game_message, self.bot,
                                self.game_channel)
                    try:
                        await game.start_game()
                    except Exception as e:
                        print(f'game: {e}')

            elif res.author.name in self.final_players_lst:
                await res.channel.send(f':no_entry: {res.author.mention}, Вы уже подтвердили своё участие в игре!',
                                       delete_after=5)
            else:
                await res.channel.send(f':no_entry: {res.author.mention}, Вы не являетесь участником игры!',
                                       delete_after=5)

        elif res.component.id == 'no':
            if res.author in self.start_players_lst:
                await res.channel.send(f'{res.author.mention} отказался от игры :(', delete_after=5)
                self.start_players_lst.remove(res.author)
            elif res.author.name in self.final_players_lst:
                await res.channel.send(f':no_entry: {res.author.mention}, Вы уже подтвердили своё участие в игре! '
                                       f'В данный момент вы не можете отклонить приглашение',
                                       delete_after=5)
            else:
                await res.channel.send(f':no_entry: {res.author.mention}, Вы не являетесь участником игры!',
                                       delete_after=5)

    @commands.Cog.listener()
    async def on_ready(self):
        """При готовности бота"""
        DiscordComponents(self.bot)

    @commands.command(name='black_jack',
                      aliases=['очко', '21', 'блэкджек', 'двадцатьодно', 'bj'])
    async def black_jack(self, ctx, *args: discord.Member):
        """
        Команда запуска игры.
        Алиасы: очко, 21, блэкджек, двадцатьодно, bj
        Аргументы: список противников пингом через пробел (пример: .bj @testik @Ваня)
        Для соло игры отправьте команду без аргументов.
        Ограничение кол-ва игроков: 4
        """

        try:
            with open(self.game_path, 'r') as game_file:
                game_data = json.load(game_file)
                self.game = list(game_data.values())[0]
        except Exception as e:
            print(e)

        try:
            if self.game:
                # Если идёт игра
                await ctx.message.add_reaction('❌')
                await ctx.send(':no_entry: Игра уже идёт! Пожалуйста, дождитесь окончания', delete_after=5)
                await ctx.message.delete(delay=1)
                return

            if args:
                # Если есть противники-люди
                if len(args) > self.max_players:
                    # максимальное кол-во игроков 4
                    await ctx.message.add_reaction('❌')
                    await ctx.send(':no_entry: Максимальное количество игроков **4**!', delete_after=5)
                    await ctx.message.delete(delay=1)

                elif ctx.author in args:
                    # нельзя вызвать самого себя
                    await ctx.message.add_reaction('❌')
                    await ctx.send(':no_entry: Вы не можете вызвать на игру самого себя!', delete_after=5)
                    await ctx.message.delete(delay=1)

                else:
                    await ctx.message.add_reaction('✅')

                    # Обнуление списка игроков
                    self.final_players_lst = []

                    # данные игры
                    self.final_players_lst.append(ctx.author.name)

                    guild = ctx.guild
                    member = ctx.author
                    overwrites = {
                        guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        guild.me: discord.PermissionOverwrite(read_messages=True),
                        member: discord.PermissionOverwrite(read_messages=True)
                    }

                    self.channels_lst.append(await guild.create_text_channel(f'Рука {ctx.author.name}',
                                                                             overwrites=overwrites))

                    self.start_players_lst = [i for i in args]

                    # время запуска игры + канал игры
                    self.start_time = datetime.now().isoformat(),
                    self.game_channel = ctx.channel

                    # запись об игре
                    with open(self.game_path, 'w') as game:
                        game_data = {self.game_channel.id: True}
                        json.dump(game_data, game, indent=4)

                    # список игроков
                    players_lst = [f'<@{i.id}>' for i in args]

                    # уведомление об игре
                    file = discord.File(f'{STATIC_PATH}/source_img/blackjack.jpg', filename='blackjack.jpg')
                    embed = discord.Embed(
                        title='Начинается игра',
                        description=f'<@{str(ctx.author.id)}> предлагает сыграть пользователю(ям) '
                                    f'{str(players_lst).strip("[]")} в black_jack! \n'
                                    f'Вы можете принять игру или отказаться. '
                                    f'На это решение вам отводится одна минута.\n'
                                    f'Игровые позиции будут заполнены ботами до 4-х\n'
                                    f'Помните: главное не победа, главное -- участие! \nУдачи! :wink: \n',
                        color=discord.Colour.red()
                    )
                    embed.add_field(name='\u200b',
                                    value=f':stopwatch: До старта игры **{self.timer}** секунд.!')
                    embed.set_image(url='attachment://blackjack.jpg')
                    embed.set_footer(text='Разработал: 空っぽ leshiy#9472')

                    # кнопки
                    buttons = [
                        [
                            Button(style=ButtonStyle.gray, label='Играть', id='go'),
                            Button(style=ButtonStyle.gray, label='Пас', id='no'),
                        ]
                    ]
                    self.game_message = await ctx.send(embed=embed, file=file, components=buttons)

                    # запуск таймера
                    try:
                        self.start_timer.start()
                    except Exception as e:
                        print(f'timer_error: {e}')

            else:
                # Соло игра

                # данные игры
                self.game_channel = ctx.channel

                # запись об игре
                with open(self.game_path, 'w') as game:
                    game_data = {self.game_channel.id: True}
                    json.dump(game_data, game, indent=4)

                # кнопки
                buttons = [
                    [
                        Button(style=ButtonStyle.green, label='ДА', id='y'),
                        Button(style=ButtonStyle.red, label='НЕТ', id='n'),
                    ]
                ]

                # уведомление об игре
                file = discord.File(f'{STATIC_PATH}/source_img/blackjack.jpg', filename='blackjack.jpg')
                embed = discord.Embed(
                    title='Начинается игра',
                    description=f'<@{str(ctx.author.id)}> решил сыграть в black_jack в одиночку! \n'
                                f'По желанию игрока, игровые позиции будут заполнены ботами до 4-х\n'
                                f'Помни: главное не победа, главное -- участие! \nУдачи! :wink: \n',
                    color=discord.Colour.red()
                )
                embed.add_field(name='\u200b', value=f'Заполнить свободные слоты ботами?')
                embed.set_image(url='attachment://blackjack.jpg')
                embed.set_footer(text='Разработал: 空っぽ leshiy#9472')

                self.game_message = await ctx.send(embed=embed, file=file, components=buttons)

                # Ожидание игрока
                def check(res):
                    return res.user.name == ctx.author.name and res.channel == ctx.channel and \
                           (res.component.id == 'y' or res.component.id == 'n')

                try:
                    self.res = await self.bot.wait_for("button_click", check=check, timeout=30)
                    if self.res.component.id == 'y':
                        game = Game({ctx.author.name: ctx.channel}, self.game_message,
                                    self.bot, self.game_channel)
                        try:
                            await game.start_game()
                        except Exception as e:
                            print(f'game: {e}')

                    elif self.res.component.id == 'n':
                        game = Game({ctx.author.name: ctx.channel}, self.game_message, self.bot,
                                    self.game_channel, max_pl_count=1)
                        try:
                            await game.start_game()
                        except Exception as e:
                            print(f'game: {e}')

                except NotFound:
                    ...
                except Exception as e:
                    print(f'timeout: {repr(e)}')

                    await ctx.send(f'`Timeout` автоматический выбор: добавление ботв!', delete_after=15)
                    game = Game({ctx.author.name: ctx.channel}, self.game_message, self.bot,
                                self.game_channel)
                    try:
                        await game.start_game()
                    except Exception as e:
                        print(f'game: {e}')
        except Exception as e:
            print(e)

    @commands.command(aliases=['инфо'])
    async def info_bj(self, ctx):
        """
        Команда, выводящая информацию об игре.
        Алиасы: инфо
        """
        await ctx.message.add_reaction('✅')

        await ctx.send(info_1, delete_after=120)
        await ctx.send(info_2, delete_after=140)

        await ctx.message.delete(delay=1)

    @tasks.loop(seconds=5)
    async def start_timer(self):

        if self.start_time:
            try:
                cur_time = datetime.now()
                prev_time = datetime.strptime(
                    str(*self.start_time).replace('T', ' '), '%Y-%m-%d %H:%M:%S.%f')
                self.timer = self.max_timer - round((cur_time - prev_time).total_seconds())

                message = self.game_message

                if self.timer >= 0:

                    update_embed = discord.Embed(title=message.embeds[0].title,
                                                 description=message.embeds[0].description,
                                                 colour=discord.Colour.random())

                    update_embed.set_image(url='attachment://blackjack.jpg')
                    update_embed.add_field(name='\u200b', value=f':stopwatch: До старта игры '
                                                                f'**{self.timer}** секунд.!')
                    update_embed.set_footer(text='Разработал: 空っぽ leshiy#9472')

                    await message.edit(embed=update_embed)
                elif self.timer in (1, 0, -1, -2, -3, -4, -5):
                    update_embed = discord.Embed(title=message.embeds[0].title,
                                                 description=message.embeds[0].description,
                                                 colour=discord.Colour.random())

                    update_embed.set_image(url='attachment://blackjack.jpg')
                    update_embed.add_field(name='\u200b', value=f':stopwatch: **Игра началась**')
                    update_embed.set_footer(text='Разработал: 空っぽ leshiy#9472')

                    await message.edit(embed=update_embed, components=[])
                    self.start_timer.stop()

                    for i, pl in enumerate(self.final_players_lst):
                        self.players[pl] = self.channels_lst[i]

                    game = Game(self.players, self.game_message, self.bot,
                                self.game_channel)
                    try:
                        await game.start_game()
                    except Exception as e:
                        print(f'game: {e}')

            except discord.errors.NotFound:
                ...

    @black_jack.error
    async def black_jack_error(self, ctx, error):
        """Обработка ошибок команды"""
        if isinstance(error, commands.BadArgument):
            await ctx.message.add_reaction('✅')
            await ctx.send(
                f'Пожалуйста, укажите соперника(ов) с помощью пинга <@{str(ctx.author.id)}> '
                '(пример: <@747841276769992754>). Или отправьте только команду, для начала соло игры', delete_after=6)
            await ctx.message.delete(delay=1)

    @info_bj.error
    async def info_bj_error(self, ctx, error):
        """Обработка ошибок команды"""
        if isinstance(error, commands.BadArgument):
            await ctx.message.add_reaction('✅')
            await ctx.send(
                f'<@{str(ctx.author.id)}> Данная команда не имеет аргументов, отправляйте её пустой', delete_after=4)
            await ctx.message.delete(delay=1)


def setup(bot):
    """Настройка"""
    bot.add_cog(BlackJack(bot))

# TODO
#  Очистка папки с "руками" по завершению игры
#  Реализовать выдачу награды за 21 с первой комбинации
