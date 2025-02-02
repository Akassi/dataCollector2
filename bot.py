
import discord
from discord.ext import commands
import logging
import config
from event_handlers import register_event_handlers
from tasks import monitor_users
from commands import register_commands


logging.basicConfig(filename='users.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Бот {bot.user} подключился и готов к работе!')
    monitor_users.start(bot)  # Запускаем фоновую задачу и передаем экземпляр бота

register_event_handlers(bot)
register_commands(bot)


bot.run(config.DISCORD_TOKEN)
