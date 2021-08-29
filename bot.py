import discord
import valorantStats

client = discord.Client()

logins = {}

@client.event
async def on_ready():
    print("Le bot est prêt !")


@client.event
async def on_message(message:discord.message.Message):
    if message.author == client.user:
        return
    if message.content == "Ping":
        await message.channel.send("Pong")
    if message.content == "!stats":
        if not message.author.id in logins:
            await message.channel.send("Please use !login before using this command (message the bot for privacy)")
        else :
            await message.channel.send(valorantStats.main(logins[message.author.id]["usr"], logins[message.author.id]["pass"]))
    if message.content.startswith("!login"):
        if len(message.content.split()) == 3:
            username = message.content.split()[1]
            password = message.content.split()[2]
            logins[message.author.id] = {"usr":username,"pass":password}
            await message.channel.send("Logged in")
        else:
            await message.channel.send("Usage : !login username password (message the bot for privacy)")
    if message.content == "!logoff":
        logins.pop(message.author.id)
        await message.channel.send("Logged off")


client.run(tokenhere)
