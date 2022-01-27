import os
from fnmatch import fnmatch

import discord

from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path


class MainBot(commands.Bot):
    def __init__(self):
        # Cogs
        self._cogs = [p.stem for p in Path(".").glob("commands/*.py")]
        super().__init__(command_prefix=self.prefix, intents=self.intents(),
                         case_insensitive=True)

    async def on_ready(self):
        """При готовности бота"""
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name='.help'))
        print('ГОТОВ')

    @staticmethod
    async def prefix(bot, msg):
        return commands.when_mentioned_or('.')(bot, msg)

    def startup(self):
        """Запуск"""
        # настройка
        try:
            for cog in self._cogs:
                self.load_extension(f'commands.{cog}')
                print(f'[загрузка] {cog}')
        except Exception as e:
            print(e)

        # загрузка .enf
        load_dotenv()
        token = os.getenv('TOKEN')

        self.run(token)

    def intents(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.presences = True

        return intents


if __name__ == '__main__':
    MainBot().startup()
