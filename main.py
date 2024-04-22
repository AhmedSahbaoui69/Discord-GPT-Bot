from nextcord.ext import commands
import nextcord
import os

token = os.environ["TOKEN"]

prefix='.'
bot = commands.Bot(intents=nextcord.Intents.all(), command_prefix=prefix)


@bot.event
async def on_ready():
  await bot.change_presence(status=nextcord.Status.do_not_disturb)
  print("Up.")


# command not found
@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandNotFound):
    await ctx.message.add_reaction('❓')
    await ctx.send(error)


# scan cogs
for cog in os.listdir('./cogs'):
  if cog.endswith('.py'):
    bot.load_extension('cogs.' + cog[:-3])

bot.run(token)
