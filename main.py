#!/usr/bin/python3

# =============================================================================
#                      EpicStore v1.0 www.github.com/wrrulos
#              Discord bot to keep up with free games from Epic Games
#                               Made by wRRulos
#                                  @wrrulos
# =============================================================================

# Any error report it to my discord please, thank you. 
# Programmed in Python 3.10.8

import requests
import discord
import asyncio
import shutil
import json
import sys
import os

from discord.ext import commands, tasks

try:
    with open('settings.json', 'r') as f:
        settings = json.loads(f.read())
        token = settings['token']
        prefix = settings['prefix']

except FileNotFoundError:
    data = { 'token': '', 'prefix': 'epicstore!' }
    with open('settings.json', 'w') as f:
        json.dump(data, f, indent=4)

if token == '' or prefix == '':
    print('\n [#] Invalid configuration!')
    sys.exit()

intents = discord.Intents.all()
client = commands.Bot(command_prefix=prefix, help_command=None, intents=intents)
api = 'https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions'

if not os.path.isdir('data'):
    os.mkdir('data')

if not os.path.isdir('data/servers'):
    os.mkdir('data/servers')
    

def save_server(server_id):
    """ Save the server folder and create the data.json file """
    server_folder = f'data/servers/{server_id}'
    server_file = f'{server_folder}/data.json'

    if os.path.exists(server_folder):
        shutil.rmtree(server_folder)

    os.mkdir(server_folder)

    with open(server_file, 'w') as f:
        data = {
            'channel_id': '',
            'send_role': True,
            'role_id': '@everyone',
            'games': [],
        }
        json.dump(data, f, indent=4)


def save_data(server_id, name, id):
    """ Save the configuration """
    file = f'data/servers/{server_id}/data.json'

    with open(file, 'r') as f:
        data = json.loads(f.read())

    data[name] = id

    with open(file, 'w') as f:
        json.dump(data, f, indent=4)


def get_games():
    """ Get current games from Epic Games API """
    games = {}
    r = requests.get(api)
    r_json = r.json()
    store_games = r_json['data']['Catalog']['searchStore']['elements']  # Games

    for num, game in enumerate(store_games):
        num = str(num)
        games[num] = [game['title'], game['description']]
        if game['keyImages'][0]['type'] == 'VaultClosed':
            games[num].append(game['keyImages'][1]['url'])

        else:
            games[num].append(game['keyImages'][0]['url'])

        games[num].append(game['price']['totalPrice']['fmtPrice']['discountPrice'])

    return games


async def send_announcement(server_id, games):
    """ Send a game announcement to the channel """
    try:
        with open(f'data/servers/{str(server_id)}/data.json', 'r') as f:
            data = json.loads(f.read())

        if data['channel_id'] == '':  # In the event that the user has not put a channel.
            return

        channel = client.get_channel(int(data['channel_id']))

        for num in range(len(games)):
            if games[str(num)][3] == '0':  # If the game costs 0 dollars
                embed = discord.Embed(title=f'FREE GAME! {games[str(num)][0]}', color=0x60f923, description=games[str(num)][1]).set_image(url=games[str(num)][2])
                await channel.send(embed=embed)

        if data['send_role'] == True:  # If the option to send a role is activated
            if data['role_id'] == '@everyone' or data['role_id'] == '@here':
                message = await channel.send(data['role_id'])

            else:
                message = await channel.send(f'<{data["role_id"]}>')

        await asyncio.sleep(2)
        await message.delete()

    except AttributeError:
        pass


@client.event
async def on_ready():
    """ When the bot starts """
    check_games.start()
    change_status.start()
    print(f"\nI'm currently at {len(client.guilds)} servers!\n")
        
    for guild in client.guilds:  # Check if a server does not have the configuration file
        if not os.path.exists(f'data/servers/{str(guild.id)}/data.json'):
            save_server(str(guild.id))


@client.event
async def on_guild_join(guild):
    """ When the bot joins the server """
    save_server(str(guild.id))


@client.event
async def on_message(message):
    """ Every time a message is sent """
    mention = f'<@{client.user.id}>'

    if mention in message.content:
        await message.channel.send(f'Hello user! Use `{prefix}help` to see the available commands.')

    await client.process_commands(message)


@tasks.loop(minutes=1)
async def change_status():
    """ Background task that changes the state of the bot """
    await client.change_presence(activity=discord.Game(name=f"I'm at {len(client.guilds)} servers! My prefix is {prefix}", type=0))


@tasks.loop(hours=1)
async def check_games():
    """ 
    Background task that checks current games 
    against previously obtained ones 
    """
    games = get_games()
    game_names = [games[str(num)][0] for num in range(len(games))]
    
    for guild in client.guilds:
        with open(f'data/servers/{guild.id}/data.json', 'r') as f:
            data = json.loads(f.read())

        if data['games'] != game_names:
            with open(f'data/servers/{guild.id}/data.json', 'w') as f:
                data['games'] = game_names
                json.dump(data, f, indent=4)

            await send_announcement(guild.id, games)


@client.command(name='help')
async def help_command(ctx):
    """ Command to see available commands """
    embed = discord.Embed(title='💸 EpicStore | Command List', color=0x014EFF, description=None)
    embed.add_field(name=f'**{prefix}help**', value='`📄 Show this help menu.`', inline=False)
    embed.add_field(name=f'**{prefix}channel [channel]**', value='`🧾 Sets the selected channel for the bot to send game ads.`', inline=False)
    embed.add_field(name=f'**{prefix}role [role]**', value='`📍 Sets the role that the bot will tag when sending the message. If you want to enable or disable this option, just send the command without a role.`', inline=False)
    embed.add_field(name=f'**{prefix}settings**', value='`⚙ This command shows the current settings of the bot.`', inline=False)
    embed.set_footer(text='🔗 Made By @wrrulos')
    await ctx.send(embed=embed)


@client.command(name='channel')
@commands.has_permissions(administrator=True)
async def set_channel(ctx, channel):
    """ Command to save the channel id """
    channel_id = channel.replace('<', '').replace('>', '').replace('#', '')
    server_id = str(ctx.guild.id)

    for i in ctx.guild.channels:  # i = channel
        if str(i.id) in channel:
            save_data(server_id, 'games', '[]')
            save_data(server_id, 'channel_id', channel_id)
            await ctx.send(f'Announcement channel is now {channel}')
            return

    await ctx.send('Enter a valid channel!')


@set_channel.error
async def set_channel_error(ctx, error):
    """ Catch command errors. In this case, the lack of arguments """
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You need to specify a channel!')

    if isinstance(error, commands.MissingPermissions):
        await ctx.send('You do not have permissions to use this command.')


@client.command(name='role')
@commands.has_permissions(administrator=True)
async def set_role(ctx, role=None):
    """ Command to save the role id """
    server_id = str(ctx.guild.id)

    if role is not None:
        if role in ['@everyone', '@here']:
            save_data(server_id, 'role_id', role)
            await ctx.send(f'The role that the bot will use now is: {role}')
            return

        for i in ctx.guild.roles:  # i = role
            if str(i.id) in role:
                save_data(server_id, 'role_id', role)
                await ctx.send(f'The role that the bot will use now is: {role}')
                return

        await ctx.send('Enter a valid role!')

    else:
        with open(f'data/servers/{server_id}/data.json') as f:
            data = json.loads(f.read())

        if data['send_role'] == True:
            save_data(server_id, 'send_role', False)
            await ctx.send('The bot will now not mention a role when sending game ads')

        else:
            save_data(server_id, 'send_role', True)
            await ctx.send('The bot will now mention a role when sending game ads')


@set_role.error
async def set_role_error(ctx, error):
    """ Catch command errors """
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('You do not have permissions to use this command.')


@client.command(name='settings')
@commands.has_permissions(administrator=True)
async def view_settings(ctx):
    """ This command show server settings """
    server_id = str(ctx.guild.id)

    with open(f'data/servers/{server_id}/data.json') as f:
        data = json.loads(f.read())

    channel = 'None' if data['channel_id'] == '' else f'<#{data["channel_id"]}>'
    
    embed = discord.Embed(title='💸 EpicStore | Server Settings', color=0x014EFF, description=None)
    embed.add_field(name='**Channel**', value=channel, inline=False)
    embed.add_field(name='**Mention a Role**', value=data["send_role"], inline=False)
    embed.add_field(name='**Role**', value=data["role_id"], inline=False)
    embed.set_footer(text='🔗 Made By @wrrulos')
    await ctx.send(embed=embed)


@view_settings.error
async def view_settings_error(ctx, error):
    """ Catch command errors """
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('You do not have permissions to use this command.')


client.run(token)
