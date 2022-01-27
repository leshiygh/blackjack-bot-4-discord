"""Файл с классами игроков"""

from asyncio import TimeoutError
from os import listdir
from random import randint

from abc import ABC, abstractmethod  # http://pythonicway.com/education/python-oop-themes/33-python-abstract-class
from PIL import Image, ImageDraw, ImageFont

from black_jack_core.config import coord, STATIC_PATH, bet_id


class AbstractPlayer(ABC):
    """Абстрактный класс игрока"""

    def __init__(self, name):
        self.name = name
        self.cards = []
        self.bet = 0
        self.full_points = 0
        self.money = 1000

    def change_point(self):
        """Метод изменения суммы очков игрока"""
        self.full_points = sum([card.points for card in self.cards])

    @abstractmethod
    def change_bet(self, *args):
        """Абстрактный метод выбора ставки (у каждого типа игрока свой)"""
        ...

    def take_card(self, card):
        """Метод получения карты"""
        self.cards.append(card)
        self.change_point()

    async def return_hand(self):
        """
        Метод возырата "руки"
        :return: cards_pict -- путь до картинки-руки игрока
        """
        cards_lst = [crd.picture for crd in self.cards]

        hand_name = ''
        for card in self.cards:
            hand_name += f'-{card.rank}_{card.suit}'

        if f'{hand_name}.png' not in listdir(f'{STATIC_PATH}/hands'):
            # Создание "руки"
            with Image.open(f'{STATIC_PATH}/source_img/bg.png').convert('RGBA') as background:

                for i, _ in enumerate(cards_lst):
                    card_pict = Image.open(cards_lst[i]).convert('RGBA').resize((411, 614))
                    background.paste(card_pict, coord.get(len(cards_lst))[i], card_pict)

                background.save(f'{STATIC_PATH}/hands/{hand_name}.png')

        # создание финального изображения "руки"
        cards_pict = f'{STATIC_PATH}/hands/{self.name}-{self.money}{hand_name}.png'
        if cards_pict not in listdir(f'{STATIC_PATH}/hands'):
            with Image.open(f'{STATIC_PATH}/hands/{hand_name}.png') as poster:
                # код ниже взят из примера библиотеки Pillow и изменён под нужды программы

                # make a blank image for the text, initialized to transparent text color
                txt = Image.new('RGBA', poster.size, (255, 255, 255, 0))

                # шрифт
                fnt = ImageFont.truetype(f'{STATIC_PATH}/fonts/MUTTER_.TTF', size=86)
                # get a drawing context
                d = ImageDraw.Draw(txt)

                # деньги
                d.text((121, 977), str(self.money), font=fnt, fill=(0, 0, 0, 230), align='center')
                # очки
                d.text((1502, 977), str(self.full_points), font=fnt, fill=(0, 0, 0, 230), align='center')

                out = Image.alpha_composite(poster, txt)
            out.save(f'{cards_pict}')

        return cards_pict


class Bot(AbstractPlayer, ABC):
    def __init__(self, name):
        super().__init__(name)
        self.max_points = randint(17, 20)

    async def change_bet(self, max_bet, min_bet):
        self.bet = randint(min_bet, max_bet if max_bet < self.money else self.money)
        self.money -= self.bet

    async def ask_card(self):
        if self.full_points < self.max_points:
            return True
        return False


class Dealer(AbstractPlayer, ABC):
    def __init__(self):
        super().__init__('Dealer')
        self.max_points = 17

    async def change_bet(self, max_bet, min_bet):
        """
        Ошибка типа -- диллер не может делать ставок
        """
        raise Exception('This type is dealer so it has no bets')

    async def ask_card(self):
        if self.full_points < self.max_points:
            return True
        return False


class Player(AbstractPlayer, ABC):
    def __init__(self, name, channel, game_channel, bot):
        """

        :param name:
        :param channel:
        :param game_channel:
        :param bot:
        """
        super(Player, self).__init__(name)
        self.game_channel = game_channel
        self.channel = channel
        self.msg = None
        self.bot = bot
        self.res = None

        self.hand_msg = None

    async def change_bet(self, max_bet, min_bet):
        if not self.msg:
            self.msg = await self.channel.send('Техническое сообщение')
        else:
            await self.msg.delete()
            self.msg = await self.channel.send('`Техническое сообщение`')

            def check(res):
                return self.name == res.user.name and self.game_channel == res.channel and res.component.id in bet_id

            try:
                try:
                    self.res = await self.bot.wait_for('button_click', check=check, timeout=30)
                    self.bet = int(self.res.component.lable)
                    await self.msg.edit(f'Вы сделали ставку в размере {self.bet}')

                except TimeoutError:
                    self.bet = randint(min_bet, max_bet if self.money > max_bet else self.money)
                    await self.msg.edit(f'`Timeout` Сделана автоматическая ставка в размере {self.bet}')
                finally:
                    self.money -= self.bet

            except Exception as e:
                print(f'bet: {e}')

    async def ask_card(self):
        if len(self.cards) < 4:
            def check(res):
                return self.name == res.user.name and res.channel == self.channel and \
                       (res.component.id == 'yep' or res.component.id == 'nop')

            try:
                try:
                    self.res = await self.bot.wait_for("button_click", check=check, timeout=30)
                except Exception as e:
                    print(e)
                return True if self.res.component.id == 'yep' else False

            except TimeoutError:
                return False

        await self.msg.edit('У вас 4 карты, что является максимально допустимым '
                            'числом в данной реализации игры. \n Ход передан следующему игроку')
        return False
