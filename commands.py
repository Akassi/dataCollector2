from discord.ext import commands

def register_commands(bot: commands.Bot):
    @bot.command(name='ping')
    async def ping(ctx):
        await ctx.send('pong')
