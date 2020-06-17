#modules
import discord
import json
import os
#files
import database 
import methods
import commands

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
    async def on_message(self, message):
        if(message.content.startswith("$")):
            if(commands.is_valid_command(message)):
                message_array = message.content.split(" ")
                message_command = message_array[0]
                if(message_command == "$help"):
                    await message.channel.send('''
- $help - shows all commands
- $send (ping person) (wallet name) (amount) - sends an amount to a person from that wallet
- $request (ping person) (amount) - requests some money from a person which her or she can accept or deny
- $tax (ping person) (amount) (wallet name) - if you have the role "taxation" take that amount of money from the person and put it in the wallet
- $print (wallet name) (amount) - creates an amount of money in that wallet if you have the role "printer"
- $burn (wallet name) (amount) - deletes that much money from a wallet
- $balance (wallet name) - returns the amount of money in the wallet
                    '''
                    )
                if(message_command == "$send"):
                    send_result = database.send(client, message.guild.id, message_array[1], message_array[2], message_array[3], message.author)
                    if  send_result[0]:
                        await message.channel.send("success")
                    else:
                        await message.channel.send(f'an error occured {send_result[1]}')
                if(message_command == "$create"):
                    result = database.create(message.guild.id, message_array[1], client)
                    if(result[0]):
                        await message.channel.send("created")
                    else:
                        await message.channel.send(f'error {result[1]}')
                if(message_command == "$balance"):
                    if(database.get_balance(message.guild.id, message_array[1], client)):
                        await message.channel.send(f'the balane is {database.get_balance(message.guild.id, message_array[1], client)[1]}')
                    else:
                        await message.channel.send("there was an error")
                if(message_command == "$print"):
                    roles = map(lambda role: role.name, message.author.roles)
                    if("printer" not in roles):
                        await message.channel.send("you do not have the role printer")
                        return
                    result = database.print_money(client, message.guild.id, message_array[1], message_array[2])
                    if(result[0]):
                        await message.channel.send("the printing was successful")
                    else:
                        await message.channel.send(f' there was an error {result[1]}')

            else:
                await message.channel.send("not valid command ")


client = MyClient()
token = os.environ.get("DISCORD_BOT_SECRET")
client.run(token)