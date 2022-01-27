"""Файл с классом игры"""
import json

import discord
from discord_components import Button, ButtonStyle
from path import Path

import black_jack_core.player as bj_player
from black_jack_core.config import STATIC_PATH

from black_jack_core.deck import Deck


class Game:
    def __init__(self, players: dict, game_msg, bot, channel, max_pl_count=4):
        """
        Основной класс игры
        :param players:
        :param game_msg:
        :param bot:
        :param channel:
        :param max_pl_count:
        """
        self.game_path = Path("databases/black_jack/game.json")

        self.game_msg = game_msg
        self.dealer_msg = None  # Сообщение с рукой диллера в основном чате
        self.game_channel = channel

        self.max_pl_count = max_pl_count
        self.players = players  # Игроки, принявшие игру
        self.final_players = []  # Финальный список игроков (с ботами, если людей не хватает)
        self.round_players = []  # Игроки в текушем раунде
        self.copy_round_players = []  # Игроки в текушем раунде (копия, нужная для работы в цикле запроса карт)

        self.bot = bot  # Передача основного дискорд-бота

        self.dealer = bj_player.Dealer()
        self.deck = Deck()
        self.max_bet, self.min_bet = 30, 10

        self.res = None

    def _launching(self):
        """Функция загрузки игры (создание игроков)"""
        if len(self.players) < self.max_pl_count:
            for i in range(self.max_pl_count - len(self.players)):
                b = bj_player.Bot(f'bot{i + 1}')
                self.final_players.append(b)

        for i in range(len(self.players)):
            # players - {name: msg, ...}
            h_player = bj_player.Player(*[*self.players.items()][i], self.game_channel, self.bot)
            self.final_players.append(h_player)

    async def ask_bet(self):

        """Функция запроса ставок у игроков"""
        bet_buttons = [
            [
                Button(style=ButtonStyle.green, label='10', id='bet_10'),
                Button(style=ButtonStyle.red, label='20', id='bet_20'),
                Button(style=ButtonStyle.green, label='30', id='bet_30'),
                Button(style=ButtonStyle.red, label='40', id='bet_40'),
                Button(style=ButtonStyle.green, label='50', id='bet_50'),
            ],
            [
                Button(style=ButtonStyle.red, label='100', id='bet_100'),
                Button(style=ButtonStyle.green, label='200', id='bet_200'),
                Button(style=ButtonStyle.red, label='300', id='bet_300'),
                Button(style=ButtonStyle.green, label='500', id='bet_500'),
                Button(style=ButtonStyle.red, label='1000', id='bet_1000')
            ]
        ]

        for pl in self.round_players:
            if isinstance(pl, bj_player.Player):
                file = discord.File(f'{STATIC_PATH}/source_img/blackjack.jpg', filename='blackjack.jpg')
                update_embed = discord.Embed(title=self.game_msg.embeds[0].title,
                                             description=self.game_msg.embeds[0].description,
                                             colour=discord.Colour.random())

                update_embed.set_image(url='attachment://blackjack.jpg')
                update_embed.add_field(name='Время ставок', value=f'Ставка {pl.name}')
                update_embed.set_footer(text='Разработал: 空っぽ leshiy#9472')
                await self.game_msg.delete()
                self.game_msg = await self.game_channel.send(file=file, embed=update_embed, components=bet_buttons)
            await pl.change_bet(self.max_bet, self.min_bet)

        update_embed = discord.Embed(title=self.game_msg.embeds[0].title,
                                     description=self.game_msg.embeds[0].description,
                                     colour=discord.Colour.random())

        update_embed.set_image(url='attachment://blackjack.jpg')
        update_embed.add_field(name='Ставки сделаны', value='Ставок больше нет')
        update_embed.set_footer(text='Разработал: 空っぽ leshiy#9472')
        await self.game_msg.edit(embed=update_embed, components=[])

    async def first_distribution(self):
        """Функция для первой раздачи карт"""
        for plr in self.round_players:
            for _ in range(2):
                card = self.deck.get_card()
                plr.take_card(card)

        card = self.deck.get_card()
        self.dealer.take_card(card)

        file = discord.File(await self.dealer.return_hand())
        self.dealer_msg = await self.game_channel.send('*Карты дилера*', file=file)

    @staticmethod
    def check_stop(plr):
        """Функция, проверяющая колв-во очков (для принудительной остановки набора карт игроками)"""
        if plr.full_points >= 21:
            return True
        else:
            return False

    async def remove_player(self, plr):
        """Функция, удаляющая игрока из раунда при переборе"""

        file = discord.File(await plr.return_hand())
        msg = None
        if isinstance(plr, bj_player.Player):
            await plr.hand_msg.delete()
            await plr.msg.edit('`У вас перебор!`')
            msg = f'Игрок {plr.name} набрал больше 21!\n' \
                  f'`{plr.name} выбывает!`'
        elif isinstance(plr, bj_player.Bot):
            msg = f'{plr.name} набрал больше 21!\n' \
                  f'`{plr.name} выбывает!`'
        await self.game_channel.send(msg, file=file)
        self.copy_round_players.remove(plr)

    async def ask_cards(self):
        """Функция, обрабатывающая запрос карт игроками"""
        buttons = [
            [
                Button(style=ButtonStyle.green, label='Ещё', id='yep'),
                Button(style=ButtonStyle.red, label='Пас', id='nop'),
            ]
        ]
        for plr in self.round_players:
            # Отрисовка стартовых "рук" игроков
            if isinstance(plr, bj_player.Player):
                file = discord.File(await plr.return_hand())
                plr.hand_msg = await plr.channel.send('*Ваши карты*', file=file, components=buttons)

            while await plr.ask_card():
                card = self.deck.get_card()
                plr.take_card(card)

                if isinstance(plr, bj_player.Player):
                    # Перерисовка "рук" игроков
                    file = discord.File(await plr.return_hand())
                    await plr.hand_msg.delete()
                    plr.hand_msg = await plr.channel.send('*Ваши карты*', file=file, components=buttons)

                is_stop = self.check_stop(plr)
                if is_stop:
                    if plr.full_points > 21:
                        await self.remove_player(plr)
                    break

            if isinstance(plr, bj_player.Player):
                await plr.msg.edit('`Ход передан следующему игроку`')

        self.round_players = self.copy_round_players

    async def check_winner(self):
        """Функция, проверяющая победителя(ей) и проигравшего(их)"""
        if self.round_players:
            if self.dealer.full_points > 21:
                await self.game_channel.send('У дилера перебор, победили все не выбывшие игроки!', delete_after=10)
                for winner in self.round_players:
                    winner.money += winner.bet * 2

            else:
                for plr in self.round_players:
                    if plr.full_points == self.dealer.full_points:
                        plr.money += plr.bet
                        await self.game_channel.send(f'{plr.name} набрал {plr.full_points}, '
                                                     f'что эквивалентно очкам дилера. \n'
                                                     f'`Ставка игрока возвращена!`', delete_after=10)
                        if isinstance(plr, bj_player.Player):
                            await plr.msg.edit('`Очки совпадают с дилером!`')
                    elif plr.full_points > self.dealer.full_points:
                        plr.money += plr.bet * 2
                        await self.game_channel.send(f'{plr.name} набрал {plr.full_points}, '
                                                     f'что больше чем у дилера. \n'
                                                     f'`{plr.name} победил -- ставка удвоена!`', delete_after=10)
                        if isinstance(plr, bj_player.Player):
                            await plr.msg.edit('`Вы победили!`')

                    elif plr.full_points < self.dealer.full_points:
                        await self.game_channel.send(f'{plr.name} набрал {plr.full_points}, '
                                                     f'что меньше чем у дилера. \n'
                                                     f'`{plr.name} проиграл -- ставка потеряна!`', delete_after=10)
                        if isinstance(plr, bj_player.Player):
                            await plr.msg.edit('`Вы проиграли!`')
        else:
            await self.game_channel.send(':hot_face: `Все игроки выбыли`', delete_after=10)

    async def play_with_dealer(self):
        """Ход дилера"""
        while await self.dealer.ask_card():
            card = self.deck.get_card()
            self.dealer.take_card(card)
        file = discord.File(await self.dealer.return_hand())
        await self.dealer_msg.delete()
        self.dealer_msg = await self.game_channel.send('*Карты дилера*', file=file)

    async def rerun(self):
        """Перезапуск игры"""
        buttons = [
            [
                Button(style=ButtonStyle.green, label='Да', id='y'),
                Button(style=ButtonStyle.red, label='Нет', id='n'),
            ]
        ]
        rerun_msg = await self.game_channel.send('Хотите сыграть ещё раунд в данном составе?', components=buttons)

        yep_players = []

        for i in range(len(self.players)):
            def check(res):
                return res.user.name in [name for name in self.players.keys()] and \
                       res.channel == self.game_channel and (res.component.id == 'y' or res.component.id == 'n')

            try:
                try:
                    self.res = await self.bot.wait_for("button_click", check=check, timeout=30)
                    if self.res.component.id == 'y':
                        yep_players.append(self.res.user.name)

                except Exception as e:
                    print(e)

            except TimeoutError:
                pass
        await rerun_msg.edit('`Игра перезапущена!`' if len(yep_players) == len(self.players) else
                             'К сожалению, не все игроки захотели сыграть ещё раунд в том же составе =('
                             '\n `Игра завершена!`',
                             components=[])
        return True if len(yep_players) == len(self.players) else False

    async def start_game(self):
        """Запуск игры"""

        # загркза игры
        self._launching()

        while True:
            # Основной цикл игры
            self.deck = Deck()

            # Обнуление карт и очков диллера
            self.dealer.cards = []
            self.dealer.full_points = 0

            # Запись игроков раунда (чтоб не упустить выбывших и избежать эффекта перебора очков)
            self.round_players = self.final_players.copy()

            for pl in self.round_players:
                # Удаление игрока из игры в случае отсутствия денег
                if pl.money < self.min_bet:
                    if isinstance(pl, bj_player.Player):
                        await pl.msg.edit(embed=discord.Embed(description='`У вас закончились деньги, '
                                                                          'вы больше не можете играть!`',
                                                              color=discord.Color.red()))
                        if pl.channel.id != self.game_channel.id:
                            await pl.channel.delete()
                        self.final_players.remove(pl)

                # Обнуление списков карт, ставок и очков игроков
                pl.cards = []
                pl.full_points = pl.bet = 0

            if not [pl for pl in self.final_players if isinstance(pl, bj_player.Player)]:
                await self.game_channel.send(':dizzy_face: ```У всех игроков-людей закончились денги, '
                                             'игра завершена!``` :dizzy_face:')
                # запись об игре
                with open(self.game_path, 'w', encoding='utf-8') as game:
                    game_data = {self.game_channel.id: False}
                    json.dump(game_data, game, indent=4)
                break

            # Создание копии игроков раунда для правильной отработки циклов
            self.round_players = self.final_players.copy()
            self.copy_round_players = self.round_players.copy()

            # Запрос ставок
            await self.ask_bet()

            # Первая раздача
            await self.first_distribution()

            # запрс на получение карт
            await self.ask_cards()

            # ход дилера
            await self.play_with_dealer()

            # проверка победителя
            await self.check_winner()

            if not await self.rerun():
                # удаление игровых чатов
                for pl in [pl for pl in self.round_players if isinstance(pl, bj_player.Player)]:
                    if pl.channel.id != self.game_channel.id:
                        await pl.channel.delete()

                # запись об игре
                with open(self.game_path, 'w') as game:
                    game_data = {self.game_channel.id: False}
                    json.dump(game_data, game, indent=4)

                break
