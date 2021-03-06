#modules
import discord
import json
import os
import re
import threading
os.system("pip install dnspython")
import matplotlib.pyplot as plt 

#files
import database 
import methods
import commands
from config import config
from server import start_server
import embeds

#server.keep_alive()
#log = logging.getLogger('werkzeug')
#log.setLevel(logging.ERROR)



class MyClient(discord.Client):
    async def on_ready(self):
        start_server(self)
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        await self.change_presence(activity=discord.Game(name=f'type $help for all commands|Currently in {len(self.guilds)} guilds'))

        

        for guild in self.guilds:
            print(guild)
            time_trigger_msg =  methods.set_interval( database.trigger_time,config["day_length"], guild, client)
    #async def on_error(self,error, thing):
     #   print("there was an error")
    async def on_message(self, message):
        if message.guild is None:
            await message.author.send("I can only respond to messages in guilds")
            return
        message.content = message.content.replace("  "," ")
        person_roles= list(map(lambda role: role.id , message.author.roles))
        server_members = list(map(lambda member:member.id, message.guild.members))
        server_roles = list(map(lambda role: role.id, message.guild.roles))
        person_id = message.author.id
        if(message.author.bot):
            return
        ##(guild, message,  person_roles,server_members,server_roles,person_id)
        trigger_msg = database.trigger_messages(message.guild, message, person_roles, server_members, server_roles, message.author.id)
        #print(trigger_msg)
        if trigger_msg is not None:
            for i in trigger_msg:
                if(i[1]):
                    if(not i[0]):
                        await message.channel.send(embed=embeds.simple_embed(False,
                            f'<@!{i[2]}> your smart contract was annuled: {i[1]}'
                        ))
                    else:
                        await message.channel.send(embed=embeds.simple_embed(True,f'a smart contract said: {i[1]}'))
        answer = database.answer_question(message.author, message.content, message.guild)
        if answer is not None:
            await message.channel.send(embed=embeds.simple_embed(answer[0],answer[1]))
        if(message.content.startswith("$")):
            if(message.content.startswith("$smart-contract")):
                if(message.content.count("```") == 2):
                    if(message.content.split("```")[0].count(" ") == 2):
                        await message.channel.send(embed=embeds.simple_embed(True,database.write_contract(message.guild,message.author,message.content.split("```")[1],message.content.split(" ")[1],client, person_roles,server_members,server_roles,person_id  )[1]))
                        return
            if(commands.is_valid_command(message)):
                message_array = message.content.split(" ")
                message_command = message_array[0]
                if(message_command == "$help"):
                    await message.channel.send(embed=embeds.simple_embed("info",'''
- $help - shows all commands
- $send (from wallet) (to wallet) (amount) - sends an amount to a person from that wallet
- $print (wallet name) (amount) - creates an amount of money in that wallet if you have the role "printer"
- $balance (wallet name) - returns the amount of money in the wallet
- $links - show some links related to this bot
- $smart-contract (trigger) (code block) - code a smart contract
- $clear-contracts - delete all your smart contracts.
- $create (ping wallet) - create an account
- $whois (condition) - figure out who is a condition
- $send-each (from wallet) (ammount) (condition) - send each person who meets a condition
- $set-balance (ping wallet) - set the balance of a wallet for admins only
- $set-balance-each (amount) (condition) - set the balance of each person who meets a condition
- $wallet-settings (target person) (ping wallet) (setting name) (boolean) - change the setting, such as view or access, to allow certain people to do more with wallets
- $trade (wallet) (wanted currency) (giving up currency) (optional limitations) - create a trade
- $accept (message id of trade) (wallet) - accept a trade
- $quiz - start a quiz based on a subject
- $shop (item name) (price) - same as trade but only for admins and you can also offer roles as trades
- $work - get an amount of money no strings attached
- $work-conditional (level name) (work reward) (conditional) - allows admins to add levels to working and give different people different work rewards
                    '''
                    ))
                if(message_command == "$send"):
                    #send(person_roles, server_members, server_roles, person_id, guild_id, from_wallet, to_wallet, amount)
                    person_roles= list(map(lambda role: role.id , message.author.roles))
                    server_members = list(map(lambda member:member.id, message.guild.members))
                    server_roles = list(map(lambda role: role.id, message.guild.roles))

                    send_result = database.send(message.author.id, message.guild, message_array[1], message_array[2], message_array[3])
                    await message.channel.send(embed=embeds.simple_embed(send_result[0],send_result[1]))
                    #if  send_result[0]:
                     #   await message.channel.send(send_result[1])
                    #else:
                    #    await message.channel.send(f'an error occured {send_result[1]}')
                if(message_command == "$create"):
                    result = database.create(message.guild, message_array[1])
                    await message.channel.send(embed=embeds.simple_embed(result[0],result[1]))

                if(message_command == "$balance"):
                    ##guild,wallet,server_members, server_roles
                    if len(message_array)==1:
                        message_array.append(message.author.mention)
                    bal = database.get_balance(message.author,message.guild, message_array[1])
                    if(bal[0]):
                        res = ""
                        for key,value in bal[1].items():
                            if("balance" in key):
                                res = res+ f'{key}: {value}\n'
                        await message.channel.send(embed=embeds.simple_embed(True,f'the balance is:\n {res}'))
                    else:
                        await message.channel.send(embed=embeds.simple_embed(False,f'there was an error: {bal[1]}'))
                if(message_command == "$print"):
                    ##(discord_client, guild_id, wallet, amount)
                    result = database.print_money(message.author, message.guild, message_array[1], message_array[2])
                    await message.channel.send(embed=embeds.simple_embed(result[0],result[1]))
                if(message_command == "$clear-contracts"):
                    database.clear_contracts(message.guild, message.author.id)
                    await message.channel.send(embed=embeds.simple_embed("info","your contracts were all deleted"))
                if(message_command == "$links"):
                    await message.channel.send(embed=embeds.simple_embed("info","Github - https://github.com/eulerthedestroyer/EU-Economy-Bot \n Discord link -  https://discord.gg/ghFs7ZM \n Bot link - https://discord.com/api/oauth2/authorize?client_id=716434826151854111&permissions=268503104m&scope=bot \n Web interface - https://economy-bot.atticuskuhn.repl.co"))
                if(message_command == "$config"):
                    if message.author.guild_permissions.administrator:
                        await message.channel.send(embed=embeds.simple_embed(*database.set_config(message.guild ,message_array[1], message_array[2])))
                    else:
                        await message.channel.send(embed=embeds.simple_embed(False,"you must be an administrator to access the config"))
                if message_command.startswith("$stats"):
                    result = methods.get_wallet(server_members,server_roles, message.guild.id, message_array[1])
                    if(result[0]):
                        print(result)
                        found_wallet = database.wallet_by_id(message.guild, result[1])
                        if "record" in found_wallet:
                            fig = plt.figure(figsize=(10,5))
                            X1 = list(found_wallet["record"].keys())
                            Y1 = list(found_wallet["record"].values())

                            plt.plot(X1, Y1, label = "plot 1")
                            fig.savefig('fig.jpg', bbox_inches='tight', dpi=150)
                            await message.channel.send(file=discord.File('fig.jpg'))
                            os.remove("fig.jpg")
                            #await message.channel.send(found_wallet["record"])
                        else:
                             await message.channel.send(embed=embeds.simple_embed(False,"can't find any stats"))
                    else:
                        await message.channel.send("error")
                if message_command =="$whois":
                    people = methods.whois(message_array[1:], message.guild)
                    return_statement = ""
                    symbol = "\n"
                    if len(people)> 7:
                        symbol = ","
                    for index,person in enumerate(people):
                        if len(return_statement) > 700:
                            return_statement += f' and {len(people)-index} others'
                            break
                        return_statement = return_statement + f'<@{person}>{symbol}'
                    if return_statement == "":
                        return_statement = "(no people found)"
                    embedVar = discord.Embed(title="Result", description=f'Found {len(people)} People', color=0x00ff00)
                    embedVar.add_field(name="People", value=return_statement, inline=False)
                    await message.channel.send(embed=embedVar)
                if message_command == "$send-each":
                    people = methods.whois(message_array[3:], message.guild)
                    return_statement = ""
                    successful_transfer = True
                    for person in people:
                        send_result = database.send(message.author.id, message.guild, message_array[1], f'<@{person}>',  message_array[2])
                        if  send_result[0]:
                            return_statement = return_statement + f'<@{person}> - success\n'
                        else:
                            return_statement = return_statement + f'<@{person}> - error: {send_result[1]}\n'
                            successful_transfer = False
                    if return_statement == "":
                        return_statement = "(no people found)"
                    if successful_transfer :
                        embedVar = discord.Embed(title="Result", color=0x00ff00)
                    else:
                        embedVar = discord.Embed(title="Result", color=0xff0000)

                    embedVar.add_field(name="People", value=return_statement, inline=False)
                    await message.channel.send(embed=embedVar)
                if message_command == "$set-balance":
                    if(not message.author.guild_permissions.administrator):
                        await message.channel.send("you do not have administrator permissions")
                        return                    
                    result = database.set_money(message.guild, message_array[2],message_array[1])
                    await message.channel.send(embed=embeds.simple_embed(result[0],f'{result[0]}{result[1]}'))
                if message_command == "$set-balance-each":
                    if(not message.author.guild_permissions.administrator):
                        await message.channel.send("you do not have administrator permissions")
                        return 
                    people = methods.whois(message_array[2:], message.guild)
                    return_statement = ""
                    successful_transfer = True
                    for person in people:
                        send_result = database.set_money(message.guild, message_array[1],f'<@{person}>')
                        if  send_result[0]:
                            return_statement = return_statement + f'<@{person}> - success\n'
                        else:
                            return_statement = return_statement + f'<@{person}> - error: {send_result[1]}\n'
                            successful_transfer = False
                    if return_statement == "":
                        return_statement = "(no people found)"
                    if successful_transfer :
                        embedVar = discord.Embed(title="Result", color=0x00ff00)
                    else:
                        embedVar = discord.Embed(title="Result", color=0xff0000)

                    embedVar.add_field(name="People", value=return_statement, inline=False)
                    await message.channel.send(embed=embedVar)
                if message_command == "$wallet-settings":
                    res= database.set_settings(message.guild, message.author, message_array[1], message_array[2], message_array[3], message_array[4])
                    await message.channel.send(embed=embeds.simple_embed(res[0],res[1]))
                if message_command == "$trade":
                    res = database.insert_trade(message, message.author,message.guild,message_array[1], message_array[2],message_array[3], message_array[4:])
                    await message.channel.send(embed=embeds.simple_embed(res[0],res[1]))
                    if res[0]:
                        await message.add_reaction("✅")
                if message_command == "$accept":
                    res= database.fulfill_trade(message_array[1], message_array[2], message.author, message.guild)
                    await message.channel.send(embed=embeds.simple_embed(res[0],res[1]))
                if message_command=="$quiz":
                    res=database.get_question(message.author, message.guild)
                    await message.channel.send(embed=embeds.simple_embed(res[0],res[1]))
                if message_command == "$shop":
                    if not message.author.guild_permissions.administrator:
                       await message.channel.send(embed=embeds.simple_embed(False,"you must be an administrator to configure the shop"))
                       return
                    res = database.insert_trade(message, message.author, message.guild,"admins", message_array[1],message_array[2], message_array[3:])
                    await message.channel.send(embed=embeds.simple_embed(res[0],res[1]))
                    if res[0]:
                        await message.add_reaction("✅")
                if message_command == "$work":
                    res = database.work(message.author, message.guild)
                    await message.channel.send(embed=embeds.simple_embed(*res))
                if message_command == "$work-conditional":
                    if not message.author.guild_permissions.administrator:
                       await message.channel.send(embed=embeds.simple_embed(False,"you must be an administrator to configure conditional work rewards"))
                       return
                    res = database.work_conditions(message.guild,message_array[1], message_array[2], message_array[3:])
                    await message.channel.send(embed=embeds.simple_embed(*res))
            else:
                await message.channel.send(embed=embeds.simple_embed(False,"not valid command. If you want a list of all commands, type '$help' "))
            
    async def on_reaction_add(self,reaction, user):
        if reaction.emoji != "✅":
            return
        if user.bot:
            return
        res= database.fulfill_trade(reaction.message.id, user.mention,  user, reaction.message.guild)
        await reaction.message.channel.send(str(res[1]))


client = MyClient()
token = os.environ.get("DISCORD_BOT_SECRET")
client.run(token)