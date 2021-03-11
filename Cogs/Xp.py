import asyncio
import sys
from datetime import datetime, timedelta

import discord
from discord.ext import commands
from discord import Member, Guild, User, PermissionOverwrite, TextChannel
import os
import json

client = commands.Bot(command_prefix=commands.when_mentioned_or('='), help_command=None, intents=discord.Intents.all())

autoroles = {
    #814038818180825098: {'memberroles': [814038818193014803], 'botroles': [814038818193014802]}
    816634292372373524: {'memberroles': [], 'botroles': [818757502472159233]}
}

permissionroles = {
    816634292372373524: {'muteroles': [818542606039777352, 818604747249811476, 818603952580460564, 818604918109241415, 818606336136577045, 818606459742322718],
                         'unmuteroles': [818542606039777352, 818604747249811476, 818603952580460564, 818604918109241415]}
}

global prefix
prefix = "="

#guild = client.get_guild(814038818180825098)
#muterole = guild.get_role(814038818201272346)

def is_not_pinned(mess):
    return not mess.pinned

def mutetime(userid, time, guild, reason):
    with open('muted.json', 'r') as f:
        muted = json.load(f)

    finish = datetime.now() + timedelta(seconds=time)
    finish2 = str(finish)
    finish3 = finish2.split('.')
    finish4 = datetime.strptime(finish3[0], '%Y-%m-%d %H:%M:%S')
    print(finish4)

    guildid = guild.id

    muted[f'{guildid}'] = {}
    muted[f'{guildid}'][f'{userid}'] = {}
    muted[f'{guildid}'][f'{userid}']['time'] = str(finish4)
    muted[f'{guildid}'][f'{userid}']['reason'] = reason

    with open('muted.json', 'w') as f:
        json.dump(muted, f)

def bantime(userid, time, guild, reason):
    with open('banned.json', 'r') as f:
        banned = json.load(f)

    finish = datetime.now() + timedelta(seconds=time)
    finish2 = str(finish)
    finish3 = finish2.split('.')
    finish4 = datetime.strptime(finish3[0], '%Y-%m-%d %H:%M:%S')
    print(finish4)

    guildid = guild.id

    banned[f'{guildid}'] = {}
    banned[f'{guildid}'][f'{userid}'] = {}
    banned[f'{guildid}'][f'{userid}']['time'] = str(finish4)
    banned[f'{guildid}'][f'{userid}']['reason'] = reason

    with open('banned.json', 'w') as f:
        json.dump(banned, f)

def check_muterole(guildid):
    with open('settings.json', 'r') as f:
        role_settings = json.load(f)
    guild = client.get_guild(guildid)
    if str(guild.id) in role_settings:
        #print(f'id found for: {guild.name}')
        muterole = role_settings[str(guild.id)]['muterole']
        muterole = guild.get_role(int(muterole))
        if str(muterole) != str(None):
            #print(f'muterole for {guild.name} = {muterole}')
            return muterole.id
        else:
            #print(f'muterole for {guild.name} not found')
            return "NoneR"
    else:
        #print(f'id for: {guild.name} not found')
        return "NoneG"

def check_if_muted(member, guild):
    print('Checking if muted!')
    with open('muted.json', 'r') as f:
        muted_users = json.load(f)
    print(muted_users)
    if member.id in muted_users[guild.id]:
        print('mute')
        return "True"
    else:
        print('not mute')
        return "False"

@client.event
async def on_ready():
    print('Wir sind eingeloggt als User {}'.format(client.user.name))
    client.loop.create_task(check_muted())
    client.loop.create_task(check_banned())
    client.loop.create_task(status_task())
    
async def status_task():
    while True:
        await client.change_presence(activity=discord.Game('This is the LAC07 Bot by Ricci#4462!'), status=discord.Status.online)
        await asyncio.sleep(10)
        await client.change_presence(activity=discord.Game('If you need a discord Bot ask me! I can programm one for you!'), status=discord.Status.online)
        await asyncio.sleep(10)

async def check_muted():
    while True:
        await asyncio.sleep(1)
        with open('muted.json', 'r') as f:
            muted = json.load(f)
        for i2, value2 in enumerate(muted):
            guild = client.get_guild(int(value2))
            muterole_id = check_muterole(guild.id)
            if str(muterole_id) == str("NoneR"):
                return
            if str(muterole_id) == str("NoneG"):
                return
            muterole = guild.get_role(muterole_id)
            for i, value in enumerate(muted[value2]):
                now = datetime.now()
                now2 = str(now)
                now3 = now2.split('.')
                if datetime.strptime(muted[value2][value]['time'], '%Y-%m-%d %H:%M:%S') < datetime.strptime(now3[0], '%Y-%m-%d %H:%M:%S'):
                    with open('muted.json', 'r') as f:
                        muted = json.load(f)

                    member = guild.get_member(int(value))
                    print(member)

                    embed = discord.Embed(title="User UnMuted!",
                                              description="**{0}** was unmuted!".format(member),
                                              color=0xff00f6)
                    embed.add_field(name='Reason', value="Mute Time over!")

                    try:
                        if not member.dm_channel:
                            await member.create_dm()
                        await member.dm_channel.send(embed=embed)
                    except discord.errors.Forbidden:
                        print('Es konnte keine unmute benachrichtigung an {0} gesendet werden.'.format(member.name))

                    if muterole in member.roles:
                        await member.remove_roles(muterole, reason='Mute Time over')

                    muted.pop(value2)
                    with open('muted.json', 'w') as f:
                        json.dump(muted, f,)
                else:
                    member = guild.get_member(int(value))
                    if muterole not in member.roles:
                        await member.add_roles(muterole, reason='Mute Time not over')


async def check_banned():
    while True:
        await asyncio.sleep(1)
        with open('banned.json', 'r') as f:
            banned = json.load(f)
        for i2, value2 in enumerate(banned):
            guild = client.get_guild(int(value2))
            for i, value in enumerate(banned[value2]):
                print(i)
                now = datetime.now()
                now2 = str(now)
                now3 = now2.split('.')
                if datetime.strptime(banned[value2][value]['time'], '%Y-%m-%d %H:%M:%S') <= datetime.strptime(now3[0], '%Y-%m-%d %H:%M:%S'):
                    with open('banned.json', 'r') as f:
                        banned = json.load(f)

                    banned_users = await guild.bans()
                    for ban_entry in banned_users:
                        user = ban_entry.user
                        print(user.id)
                        print(value)
                        if str(value) == str(user.id):
                            await guild.unban(user)
                            embed = discord.Embed(title="User UnBanned!",
                                                  description="You were unbanned by the System!",
                                                  color=0xff00f6)
                            embed.add_field(name='Reason', value="Ban Time over!")
                            try:
                                if not user.dm_channel:
                                    await user.create_dm()
                                await user.dm_channel.send(embed=embed)
                            except discord.errors.Forbidden:
                                print('Es konnte keine DM an {0} gesendet werden.'.format(user.name))
                            await user.send(embed=embed)

                            banned.pop(value2)
                            with open('banned.json', 'w') as f:
                                json.dump(banned, f, )

                        else:
                            print("fail")

@client.event
async def on_raw_reaction_add(payload):
    guild = payload.guild_id
    check_in = ["818608854421078038"]
    if str(payload.guild_id) != "816634292372373524":
        return  # Reaction is on a private message
    guild = client.get_guild(payload.guild_id)
    role = guild.get_role(818606628307075142)
    member = guild.get_member(payload.user_id)
    if str(payload.channel_id) in check_in:
        if not member.bot:
            await member.add_roles(role, reason="verified")

@client.event
async def on_raw_reaction_remove(payload):
    guild = payload.guild_id
    check_in = ["818608854421078038"]
    if str(payload.guild_id) != "816634292372373524":
        return  # Reaction is on a private message
    guild = client.get_guild(payload.guild_id)
    role = guild.get_role(818606628307075142)
    member = guild.get_member(payload.user_id)
    if str(payload.channel_id) in check_in:
        if not member.bot:
            await member.remove_roles(role, reason="verified")

@client.event
async def on_member_join(member):
    print(member)
    guild = client.get_guild(816634292372373524)
    if str(member.id) == "685797014440771598":
        return
    if not member.bot:
        embed = discord.Embed(title=f'Welcome on {guild.name}, {member}!',
                              description='Welcome on this Server! Make sure to check out the rules!',
                              color=0x22a7f0)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f'This welcome message was made by Ricci#4462!')
        if guild:
            channel = guild.get_channel(818807853430210560)
            await channel.send(embed=embed)
        try:
            if not member.dm_channel:
                await member.create_dm()
            await member.dm_channel.send(embed=embed)
        except discord.errors.Forbidden:
            print('Es konnte keine Willkommensnachricht an {0} gesendet werden.'.format(member.name))
        autoguild = autoroles.get(guild.id)
        if autoguild and autoguild['memberroles']:
            for roleId in autoguild['memberroles']:
                role = guild.get_role(roleId)
                if role:
                    await member.add_roles(role, reason='AutoRoles', atomic=True)
    else:
        autoguild = autoroles.get(guild.id)
        if autoguild and autoguild['botroles']:
            for roleId in autoguild['botroles']:
                role = guild.get_role(roleId)
                if role:
                    await member.add_roles(role, reason='AutoRoles', atomic=True)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please pass in all requirements :rolling_eyes:.')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"{ctx.message.author.mention}, you don't have permissions to do this!")


@client.command()
#@commands.has_any_role([813339122869076019,813863874872344606,813863894212804720,813863818487660575,
                         #813863844941266944]) #Owner, Admin, Moderator, Supporter, T-Supporter
async def mute(ctx, member: discord.Member, time=None, *, reason = None):
    guild = ctx.guild
    muterole_id = check_muterole(guild.id)
    print(muterole_id)
    if str(muterole_id) == str("NoneR"):
        error = await ctx.send("No muterole setup for this server!")
        await asyncio.sleep(3)
        await error.delete()
        return
    if str(muterole_id) == str("NoneG"):
        error = await ctx.send("No muterole setup for this server!")
        await asyncio.sleep(3)
        await error.delete()
        return
    if str(member) == str(ctx.message.author):
        cant = await ctx.send("You can't mute Yourself!")
        await asyncio.sleep(3)
        await ctx.message.delete()
        await cant.delete()
        return
    autoguild = permissionroles.get(guild.id)
    if autoguild and autoguild['muteroles']:
        if not ctx.message.author.top_role.id in autoguild['muteroles']:
            cant = await ctx.send('Du hast nicht genug Rechte!')
            print("has no perm")
            await asyncio.sleep(3)
            await ctx.message.delete()
            await cant.delete()
            return
    if ctx.message.author.top_role <= member.top_role:
        print("has no perm")
        cant = await ctx.send('Du kannst diese Person nicht muten!')
        await asyncio.sleep(3)
        await ctx.message.delete()
        await cant.delete()
        return
    print("has perm")
    if str(time) == "None":
        reasons_embed = discord.Embed(title=f'Wähle einen Grund:',
                              description='**[1]** Spamming \n '
                                          '**[2]** NSFW  \n'
                                          '**[3]** Werbung \n'
                                          '**[4]** Beleidigung \n'
                                          '**[5]** Schwere Beleidigung \n'
                                          '**[6]** nerven \n'
                                          '**[7]** Ständiges nerven \n'
                                          '**[8]** perma \n'
                                          '**[9]** Just For Fun \n'
                                          '**[10]** Test',
                              color=0x22a7f0)
        reasons_embed.set_footer(text='To exit type: exit!')
        ask = await ctx.send(embed=reasons_embed)
        while str(time) == "None":
            msg = await client.wait_for('message', check=lambda message: message.author == ctx.author)
            answer = msg.content
            if answer == "1":
                await ask.delete()
                await msg.delete()
                reason = "Spamming!"
                time='2h'
            elif answer == "2":
                await ask.delete()
                await msg.delete()
                reason = "NSFW!"
                time='7d'
            elif answer == "3":
                await ask.delete()
                await msg.delete()
                reason = "Werbung!"
                time='7d'
            elif answer == "4":
                await ask.delete()
                await msg.delete()
                reason = "Beleidigung!"
                time='1h'
            elif answer == "5":
                await ask.delete()
                await msg.delete()
                reason = "Schwere Beleidigung!"
                time='1d'
            elif answer == "6":
                await ask.delete()
                await msg.delete()
                reason = "nerven!"
                time='1W'
            elif answer == "7":
                await ask.delete()
                await msg.delete()
                reason = "Ständiges nerven!"
                time='1M'
            elif answer == "8":
                await ask.delete()
                await msg.delete()
                reason = "perma!"
                time='perma'
            elif answer == "9":
                await ask.delete()
                await msg.delete()
                reason = "Just For Fun!"
                time='1d'
            elif answer == "10":
                await ask.delete()
                await msg.delete()
                reason = "Test!"
                time='30s'
            elif answer == "exit":
                exit = await ctx.channel.send('Exit!')
                await asyncio.sleep(3)
                await ctx.message.delete()
                await ask.delete()
                await msg.delete()
                await exit.delete()
                return
            else:
                invalid = await ctx.send("invalid")
                reason = None
    await ctx.message.delete()
    memberrole = guild.get_role(814038818193014801)
    #role_members = discord.utils.get(ctx.guild.roles, name='╚»『⛹️』Mitglied『⛹️』 «╝')
    #role_muted = discord.utils.get(ctx.guild.roles, name='╚»『🔇 』Muted『🔇 』«╝')
    #await member.remove_roles(memberrole)
    muterole = guild.get_role(muterole_id)
    await member.add_roles(muterole)
    embed = discord.Embed(title="User Muted!",
                          description="**{0}** was muted by **{1}**!".format(member, ctx.message.author),
                          color=0xff00f6)
    embed.add_field(name='Time', value=time)
    embed.add_field(name='Reason', value=reason, inline=True)
    try:
        if not member.dm_channel:
            await member.create_dm()
        await member.dm_channel.send(embed=embed)
    except discord.errors.Forbidden:
        print('Es konnte keine DM an {0} gesendet werden.'.format(member.name))
    await ctx.send(embed=embed)
    #await modlog.send(embed=embed)
    time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400, "W": 25200, "M": 2592000, "J": 31104000}
    tempmute = int(time[0]) * time_convert[time[-1]]
    mutetime(member.id, tempmute, guild, reason)
    #await modlog.send(embed=embed)

@client.command()
#@commands.has_any_role([813339122869076019, 813863874872344606, 813863894212804720, #Owner, Admin, Moderator,
                        #813863818487660575]) #Supporter
async def unmute(ctx, member: discord.Member, *, reason = None):
    guild = ctx.guild
    muterole_id = check_muterole(guild.id)
    print(muterole_id)
    if str(muterole_id) == str("NoneR"):
        error = await ctx.send("No muterole setup for this server!")
        await asyncio.sleep(3)
        error.delete()
        return
    if str(muterole_id) == str("NoneG"):
        error = await ctx.send("No muterole setup for this server!")
        await asyncio.sleep(3)
        error.delete()
        return
    muterole = guild.get_role(muterole_id)
    autoguild = permissionroles.get(guild.id)
    if autoguild and autoguild['unmuteroles']:
        if not ctx.message.author.top_role.id in autoguild['unmuteroles']:
            print("has no perm")
            cant = await ctx.send('Du hast keine Rechte dafür!')
            await asyncio.sleep(3)
            await ctx.message.delete()
            await cant.delete()
            return
    if ctx.message.author.top_role <= member.top_role:
        print("has no perm")
        cant = await ctx.send('Du kannst diese Person nicht muten!')
        await asyncio.sleep(3)
        await ctx.message.delete()
        await cant.delete()
        return

    print("has perm")

    await ctx.message.delete()
    #role_members = discord.utils.get(ctx.guild.roles, name='Members')
    #role_muted = discord.utils.get(ctx.guild.roles, name='Muted')
    await member.remove_roles(muterole)
    #await member.add_roles(memberrole)
    mutetime(member.id, 0, guild, reason)
    embed = discord.Embed(title="User UnMuted!",
                          description="**{0}** was unmuted by **{1}**!".format(member, ctx.message.author),
                          color=0xff00f6)
    embed.add_field(name='Reason', value=reason)
    try:
        if not member.dm_channel:
            await member.create_dm()
        await member.dm_channel.send(embed=embed)
    except discord.errors.Forbidden:
        print('Es konnte keine DM an {0} gesendet werden.'.format(member.name))
    await ctx.send(embed=embed)
    #await modlog.send(embed=embed)

@client.command()
@commands.has_permissions(ban_members = True)
async def ban(ctx, member : discord.Member, time=None, *, reason = None):
    if str(member) == str(ctx.message.author):
        cant = await ctx.send("You can't ban Yourself!")
        await asyncio.sleep(3)
        await ctx.message.delete()
        await cant.delete()
        return
    if str(time) == "None":
        reasons_embed = discord.Embed(title=f'Wähle einen Grund:',
                              description='**[1]** Spamming \n '
                                          '**[2]** Belästigung  \n'
                                          '**[3]** Hacking \n'
                                          '**[4]** Werbung \n'
                                          '**[5]** NSFW \n'
                                          '**[6]** Bug using \n'
                                          '**[7]** Beleidigung \n'
                                          '**[8]** Schwere Beleidigung \n'
                                          '**[9]** nerven \n'
                                          '**[10]** Ständiges nerven'
                                          '**[11]** Nutzloser Bot \n'
                                          '**[12]** Just For Fun \n'
                                          '**[13]** Test \n'
                                          '**[14]** perma',
                              color=0x22a7f0)
        reasons_embed.set_footer(text='To exit type: exit!')
        ask = await ctx.send(embed=reasons_embed)
        while str(time) == "None":
            msg = await client.wait_for('message', check=lambda message: message.author == ctx.author)
            answer = msg.content
            if answer == "1":
                await ask.delete()
                await msg.delete()
                reason = "Spamming!"
                time = '1W'
            elif answer == "2":
                await ask.delete()
                await msg.delete()
                reason = "Belästigung!"
                time = '2W'
            elif answer == "3":
                await ask.delete()
                await msg.delete()
                reason = "Hacking!"
                time = '2J'
            elif answer == "4":
                await ask.delete()
                await msg.delete()
                reason = "Werbung!"
                time = '1M'
            elif answer == "5":
                await ask.delete()
                await msg.delete()
                reason = "NSFW!"
                time = '1M'
            elif answer == "6":
                await ask.delete()
                await msg.delete()
                reason = "Bug using!"
                time = '1W'
            elif answer == "7":
                await ask.delete()
                await msg.delete()
                reason = "Beleidigung!"
                time = '1W'
            elif answer == "8":
                await ask.delete()
                await msg.delete()
                reason = "Schwere Beleidigung!"
                time = '1M'
            elif answer == "9":
                await ask.delete()
                await msg.delete()
                reason = "nerven!"
                time = '3d'
            elif answer == "10":
                await ask.delete()
                await msg.delete()
                reason = "Ständiges nerver!"
                time = '1W'
            elif answer == "11":
                await ask.delete()
                await msg.delete()
                reason = "Nutzloser Bot!"
                time = '1m'
            elif answer == "12":
                await ask.delete()
                await msg.delete()
                reason = "Just For Fun!"
                time = '1d'
            elif answer == "13":
                await ask.delete()
                await msg.delete()
                reason = "Test!"
                time = '1m'
            elif answer == "14":
                await ask.delete()
                await msg.delete()
                reason = "perma!"
                time = 'perma'
            elif answer == "exit":
                exit = await ctx.channel.send('Exit!')
                await asyncio.sleep(3)
                await ctx.message.delete()
                await ask.delete()
                await msg.delete()
                await exit.delete()
                return
            else:
                invalid = await ctx.send("invalid")
                reason = None
    await ctx.message.delete()
    embed = discord.Embed(title="User Banned!",
                          description="**{0}** was banned by **{1}**!".format(member, ctx.message.author),
                          color=0xff00f6)
    embed.add_field(name='Reason', value=reason)
    try:
        if not member.dm_channel:
            await member.create_dm()
        await member.dm_channel.send(embed=embed)
    except discord.errors.Forbidden:
        print('Es konnte keine DM an {0} gesendet werden.'.format(member.name))
    await ctx.send(embed=embed)
    print(member)
    time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400, "W": 25200, "M": 2592000, "J": 31104000}
    tempban = int(time[0]) * time_convert[time[-1]]
    guild = ctx.guild
    bantime(member.id, tempban, guild, reason)
    await member.ban(reason = reason)

@client.command()
@commands.has_permissions(kick_members = True)
async def kick(ctx, member : discord.Member, *, reason = None):
    if str(member) == str(ctx.message.author):
        cant = await ctx.send("You can't kick Yourself!")
        await asyncio.sleep(3)
        await ctx.message.delete()
        await cant.delete()
        return
    if str(reason) == "None":
        reasons_embed = discord.Embed(title=f'Wähle einen Grund:',
                              description='**[1]** Spamming \n '
                                          '**[2]** NSFW  \n'
                                          '**[3]** Werbung \n'
                                          '**[4]** Beleidigung \n'
                                          '**[5]** Schwere Beleidigung \n'
                                          '**[6]** Ständiges nerven \n'
                                          '**[7]** nerven \n'
                                          '**[8]** Just For Fun',
                              color=0x22a7f0)
        reasons_embed.set_footer(text='To exit type: exit!')
        ask = await ctx.send(embed=reasons_embed)
        while str(reason) == "None":
            msg = await client.wait_for('message', check=lambda message: message.author == ctx.author)
            answer = msg.content
            if answer == "1":
                await ask.delete()
                await msg.delete()
                reason = "Spamming!"
            elif answer == "exit":
                exit = await ctx.channel.send('Exit!')
                await asyncio.sleep(3)
                await ctx.message.delete()
                await ask.delete()
                await msg.delete()
                await exit.delete()
                return
            else:
                invalid = await ctx.send("invalid")
                reason = None
    await ctx.message.delete()
    embed = discord.Embed(title="User Kicked!",
                          description="**{0}** was kicket by **{1}**!".format(member, ctx.message.author),
                          color=0xff00f6)
    embed.add_field(name='Reason', value=reason)
    try:
        if not member.dm_channel:
            await member.create_dm()
        await member.dm_channel.send(embed=embed)
    except discord.errors.Forbidden:
        print('Es konnte keine DM an {0} gesendet werden.'.format(member.name))
    await ctx.send(embed=embed)
    print(member)
    await member.kick(reason = reason)
    #await modlog.send(embed=embed)

@client.command()
@commands.has_permissions(administrator = True)
async def unban(ctx, member):
    print("test1")
    banned_users = await ctx.guild.bans()
    print("test2")
    for ban_entry in banned_users:
        print("test3")
        user = ban_entry.user
        print("test4")
        print(user)
        print("test5")
        print(member)
        if str(member) == str(user):
            print("succes")
            await ctx.guild.unban(user)
            await ctx.message.delete()
            embed = discord.Embed(title="User UnBanned!",
                                    description="**{0}** was unbanned by **{1}**!".format(member, ctx.message.author),
                                    color=0xff00f6)
            try:
                if not member.dm_channel:
                    await member.create_dm()
                await member.dm_channel.send(embed=embed)
            except discord.errors.Forbidden:
                print('Es konnte keine DM an {0} gesendet werden.'.format(member.name))
            await ctx.send(embed=embed)
        else:
            print("fail")

@client.command()
async def userinfo(ctx, member: discord.Member):
    if member:
        embed = discord.Embed(title='Userinfo for {}'.format(member.name),
                              description='This is a userinfo for the user {}'.format(member.mention),
                              color=0x22a7f0)
        embed.add_field(name='Server joined at: ', value=member.joined_at.strftime('%d/%m/%Y, %H:%M:%S'),
                        inline=True)
        embed.add_field(name='Discord joined at: ', value=member.created_at.strftime('%d/%m/%Y, %H:%M:%S'),
                        inline=True)
        rollen = ''
        for role in member.roles:
            if not role.is_default():
                rollen += '{} \r\n'.format(role.mention)
        if rollen:
            embed.add_field(name='Roles', value=rollen, inline=True)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f'Userinfo requestet by {ctx.message.author}.')
        await ctx.message.delete()
        mess = await ctx.channel.send(embed=embed)
        #await modlog.send(embed=embed)

@client.command()
@commands.has_permissions(manage_messages = True)
async def clear(ctx):
    args = ctx.message.content.split(' ')
    if len(args) == 2:
        if args[1].isdigit():
            count = int(args[1]) + 1
            deleted = await ctx.channel.purge(limit=count, check=is_not_pinned)
            answer = await ctx.channel.send(''
                                            '{} Messages deleted.\n'
                                            ''.format(len(deleted) - 1))
            await asyncio.sleep(3)
            await answer.delete()
            #await modlog.send(f"Clear command used by {ctx.message.author}!")
    elif len(args) == 1:
        await ctx.channel.purge()
        answer = await ctx.channel.send('```Channel cleared!```')
        await asyncio.sleep(3)
        await answer.delete()

@client.command()
async def help(ctx):
    await ctx.message.delete()
    embed = discord.Embed(title=f'Help:', description=f'**{prefix}ban**         ban a player!             \n'
                                                      f'**{prefix}unban**       unban a player!           \n'
                                                      f'**{prefix}mute**        mute a player!            \n'
                                                      f'**{prefix}unmute**      unmute a player!          \n'
                                                      f'**{prefix}kick**        kick a player!            \n'
                                                      f'**{prefix}help**        shows help!               \n'
                                                      f'**{prefix}userinfo**    shows a userinfo!         \n'
                                                      f'**{prefix}clear**       clears some messages!', color=0x2ecc71)
    embed.set_footer(text=f'If you have ideas for the Bot or if you want to report bugs ask Ricci#4462!')
    await ctx.channel.send(embed=embed)

@client.command()
async def roleguide(ctx):
    if str(ctx.guild.id) == "816634292372373524":
        owner_role = ctx.guild.get_role(818604747249811476)
        admin_role = ctx.guild.get_role(818603952580460564)
        mod_role = ctx.guild.get_role(818604918109241415)
        supp_role = ctx.guild.get_role(818606336136577045)
        tsupp_role = ctx.guild.get_role(818606459742322718)
        staff_role = ctx.guild.get_role(818608077821444096)

        youtuber_role = ctx.guild.get_role(818607876053663816)
        serverbooster_role = ctx.guild.get_role(818636152009523250)
        friends_role = ctx.guild.get_role(818608075191091251)
        premium_role = ctx.guild.get_role(818607209872228394)
        member_role = ctx.guild.get_role(818606628307075142)
        
        LAC07Bot_role = ctx.guild.get_role(818899535601467462)
        Bots_role = ctx.guild.get_role(818757502472159233)

        muted_role = ctx.guild.get_role(818551265545158783)

        ricci_role = ctx.guild.get_role(818542606039777352)
        if owner_role in ctx.message.author.roles or ricci_role in ctx.message.author.roles:
            await ctx.message.delete()
            embed = discord.Embed(title=f'Role Guide:', description='', color=0x2ecc71)
            embed.add_field(name="Staff Roles", value=f"{owner_role.mention}: This role is only for the Owner! \n"
                                                      f"{admin_role.mention}: This role you can get after enough trust! \n"
                                                      f"{mod_role.mention}: This role you can get after enough trust! \n"
                                                      f"{supp_role.mention}: This role you can after the test time as T-Supporter! \n"
                                                      f"{tsupp_role.mention}: This role is for new staff members in the test time! \n"
                                                      f"{staff_role.mention}: This role is for the staff members!", inline=False)

            embed.add_field(name="Other Roles", value=f"{youtuber_role.mention}: This is for Youtubers with 250+ subscribers! \n"
                                                      f"{serverbooster_role.mention}: This role is for server booster! \n"
                                                      f"{friends_role.mention}: This role is for friends! \n"
                                                      f"{premium_role.mention}: This role can do nothing at the moment! \n"
                                                      f"{member_role.mention}: This role is the role for all verified members! \n"
                                                      f"{LAC07Bot_role.mention}: This role is for the LAC07 Bot! \n"
                                                      f"{Bots_role.mention}: This role is for the Bots! \n"
                                                      f"{muted_role.mention}: This role is for muted users! ", inline=False)

            LAC07 = ctx.guild.get_role(818753671851409429)
            MEE6 = ctx.guild.get_role(818524567458938981)
            carl = ctx.guild.get_role(818521416407973948)
            censor = ctx.guild.get_role(818543560483536967)
            yagpd = ctx.guild.get_role(818548353813053533)

            dyno = ctx.guild.get_role(818458115967025174)
            Groovy = ctx.guild.get_role(818543867146010625)
            Rythm = ctx.guild.get_role(818544073270100070)
            Statsify = ctx.guild.get_role(818553888486850571)

            embed.add_field(name="Bot Roles",
                            value=f"{LAC07.mention}: This role is for the LAC07 Bot! \n"
                                  f"{MEE6.mention}: This role is for the MEE6 Bot! \n"
                                  f"{carl.mention}: This role is for the Carl-Bot! \n"
                                  f"{censor.mention}: This role is for the Censor Bot! \n"
                                  f"{yagpd.mention}: This role is for the YAGPD Bot! \n"
                                  f"{dyno.mention}: This role is for the Dyno Bot! \n"
                                  f"{Groovy.mention}: This role is for the Groovy Bot! \n"
                                  f"{Rythm.mention}: This role is for the Rythm Bot! \n"
                                  f"{Statsify.mention}: This role is for the Statsify Bot! \n", inline=False)

            embed.set_footer(text=f'This is the roleguid of {ctx.guild.name}, by Ricci#4462!')
            role_guide_ch = ctx.guild.get_channel(818637178313506886)
            ctx.message.delete()
            await role_guide_ch.purge()
            await role_guide_ch.send(embed=embed)

@client.command()
async def channelportal(ctx):
    if str(ctx.guild.id) == "816634292372373524":
        owner_role = ctx.guild.get_role(818604747249811476)
        ricci_role = ctx.guild.get_role(818542606039777352)
        if owner_role in ctx.message.author.roles or ricci_role in ctx.message.author.roles:
            channel_portal_ch = ctx.guild.get_channel(818609074635276329)
            embed = discord.Embed(title=f'Role Guide:', description='', color=0x2ecc71)
            guild = client.get_guild(816634292372373524)

            rules_channel = guild.get_channel(818608854421078038)
            general_channel = guild.get_channel(818620765280665650)
            mates_channel = guild.get_channel(816634930477924362)
            images_channel = guild.get_channel(818528283247378492)
            imagesreact_channel = guild.get_channel(818544874663837746)
            videos_channel = guild.get_channel(818530025753149440)
            bothelp_channel = guild.get_channel(818606725585436682)
            botcmds_channel = guild.get_channel(818606796050530344)
            stats_channel = guild.get_channel(818605660681404416)
            birthday_channel = guild.get_channel(818536107196153907)

            embed.add_field(name="Channel Portal",
                            value=f"{rules_channel.mention}: Before getting startet make sure to check out the rules! \n"
                                  f"{general_channel.mention}: If you want to chat make sure to check out the general channel! \n"
                                  f"{mates_channel.mention}: If you want to find mates for a game ask in this channel and maybe u find someone! \n"
                                  f"{images_channel.mention}: If you want to post images then go to this channel! \n"
                                  f"{imagesreact_channel.mention}: To ract to images check out this channel! \n"
                                  f"{videos_channel.mention}: To post videos go to this channel! \n"
                                  f"{bothelp_channel.mention}: If you don't know the bot prefixes go to this channel! \n"
                                  f"{botcmds_channel.mention}: To use Bot Commands go to this channel! \n"
                                  f"{stats_channel.mention}: To see the Hypixel stats of someone go to this channel! \n"
                                  f"{birthday_channel.mention}: In this channels are the birthdays shown! You can set yours with **!birthday**!", inline=False)
            embed.set_footer(text='This is the Channel Portal by Ricci#4462!')
            await channel_portal_ch.purge()
            await channel_portal_ch.send(embed=embed)

@client.command()
async def bothelp(ctx):
    if str(ctx.guild.id) == "816634292372373524":
        owner_role = ctx.guild.get_role(818604747249811476)
        ricci_role = ctx.guild.get_role(818542606039777352)
        if owner_role in ctx.message.author.roles or ricci_role in ctx.message.author.roles:
            embed = discord.Embed(title=f'', description='', color=0x2ecc71)
            embed.add_field(name="Bot Prefix",
                            value=f'LAC07: **{prefix}** \n'
                                  'Rythm: **.** \n'
                                  'Groovy: **%** \n'
                                  'Mee6: **!** \n'
                                  'Yagpdb: **-** \n'
                                  'statisfy: **s!p (mode) (name)** / **s!d (name)** \n'
                                  'carl-bot: **_** \n'
                                  'Censor Bot: **+** \n'
                                  'Dyno: **?**')
            embed.set_footer(text='This are all Bot prefix by Ricci#4462!')
            guild = client.get_guild(816634292372373524)
            bothelp_channel = guild.get_channel(818606725585436682)
            await ctx.message.delete()
            await bothelp_channel.purge()
            await bothelp_channel.send(embed=embed)

@client.command()
async def rules(ctx):
    if str(ctx.guild.id) == "816634292372373524":
        owner_role = ctx.guild.get_role(818604747249811476)
        ricci_role = ctx.guild.get_role(818542606039777352)
        if owner_role in ctx.message.author.roles or ricci_role in ctx.message.author.roles:
            embed = discord.Embed(title='Rules', description='**More Rules are coming soon!**', color=0x2ecc71)
            embed.add_field(name="§1: Text Channels",
                            value=f'**§1.1**: Don\'t use bad words! \n'
                                  f'**§1.2**: Don\'t insult anyone! \n'
                                  f'**§1.3**: No racist or NSFW stuff! \n'
                                  f'**§1.4**: Keep chat clear and use the channels for what they are made for! \n'
                                  f'**§1.5**: Don\'t spam! \n'
                                  f'**§1.6**: Pinging only for a reason!')
            embed.add_field(name="§2: Voice Channels",
                            value=f'**§2.1**: Don\'t use bad words! \n'
                                  f'**§2.2**: No racist or NSFW stuff! \n'
                                  f'**§2.3**: Don\'t ubuse ur microphone! \n'
                                  f'**§2.4**: You can only record in a voice channel if all members in the channel allows it! \n'
                                  f'**§2.5**: Don\' make loud sounds!', inline=False)
            #emed.
            embed.set_footer(text='This are the rules made by Ricci#4462!')
            guild = client.get_guild(816634292372373524)
            rules_channel = guild.get_channel(818608854421078038)
            await ctx.message.delete()
            await rules_channel.purge()
            mess = await rules_channel.send(embed=embed)
            await mess.add_reaction('✅')
             
@client.command()
async def s_updates(ctx, *, update=None):
    await ctx.message.delete()
    if str(update) == "None":
        error = await ctx.channel.send('Du musst angeben was du da reinschreiben möchtest!')
        await asyncio.sleep(3)
        error.delete()
        return
    owner_role = ctx.guild.get_role(818604747249811476)
    ricci_role = ctx.guild.get_role(818542606039777352)
    if owner_role in ctx.message.author.roles or ricci_role in ctx.message.author.roles:
        s_update_ch = ctx.guild.get_channel(818852811348508682)
        embed = discord.Embed(title='Server Updates!', description='', color=0x2ecc71)
        embed.add_field(name="Updates:", value=str(update))
        embed.set_footer(text=f'This update was sent by {ctx.message.author}!')
        anouncement = await s_update_ch.send(embed=embed)
        await anouncement.publish()

@client.command()
async def karma(ctx, member: discord.Member, count):
    with open('karma.json', 'r') as f:
        karmadata = json.load(f)

    if karmadata[f'{member.id}']:
        leftkarma = karmadata[f'{member.id}']['karma']
    else:
        karmadata[f'{member.id}'] = {}
        karmadata[f'{member.id}']['karma'] = 100
        ctx.channel.send(karmadata)

        with open('karma.json', 'w') as f:
            json.dump(karmadata, f)

@client.command()
async def showkarma(ctx):
    with open('karma.json', 'r') as f:
        karmadata = json.load(f)
    ctx.channel.send(karmadata)

client.run(os.environ['token'])
