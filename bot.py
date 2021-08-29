import discord
import valorantStats

client = discord.Client()



@client.event
async def on_ready():
    print("Le bot est prêt !")

@client.event
async def on_message(message):
    if message.content == "Ping":
        await message.channel.send("Pong")
    if message.content.startswith("!stats"):
        name = message.content[7:]
        print("Loading data")
        await message.channel.send(valorantStats.main(name))

client.run("Njk1NTQ5MTc0ODQxODY4MzM5.XobypQ.7gk1mZFUJYv9Woqbr7oqL709yEA")
