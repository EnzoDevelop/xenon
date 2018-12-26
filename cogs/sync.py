from discord.ext import commands as cmd
import discord

from utils import helpers


class Sync:
    def __init__(self, bot):
        self.bot = bot

    @cmd.group(invoke_without_command=True, aliases=["unsync"])
    async def sync(self, ctx):
        """
        Sync messages, channel & bans from one to another server
        The sync command works only in one direction, but you can run the command in both guilds / channel to sync it in both directions.
        """
        await ctx.invoke(self.bot.get_command("chelp"), "sync")

    @sync.command()
    @cmd.guild_only()
    @cmd.has_permissions(administrator=True)
    @cmd.bot_has_permissions(administrator=True)
    async def bans(self, ctx, guild_id: int):
        """
        Copy all bans from another guild to this guild and keep them up to date
        guild_id ::     The id of the guild
        """
        guild = self.bot.get_guild(guild_id)
        if guild is None:
            raise cmd.CommandError(f"There is **no guild with the id** `{guild_id}`.")

        if guild.get_member(ctx.author.id) is None or not guild.get_member(ctx.author.id).guild_permissions.administrator:
            raise cmd.MissingPermissions([f"administrator` on the guild `{guild.name}"])

        if not guild.me.guild_permissions.administrator:
            raise cmd.BotMissingPermissions([f"administrator` on the guild `{guild.name}"])

        current = await ctx.db.table("syncs").get(f"{guild.id}{ctx.guild.id}").run(ctx.db.con)
        types = []
        if current is not None:
            types = current.get("types", [])

        if "bans" not in types:
            types.append("bans")
            await ctx.send(**ctx.em(f"Successfully **enabled ban sync** from **{guild.name}** to **{ctx.guild.name}**.", type="success"))
            for reason, user in await guild.bans():
                try:
                    await ctx.guild.ban(user, reason=reason)
                except:
                    pass

        else:
            types.remove("bans")
            await ctx.send(**ctx.em(f"Successfully **disabled ban sync** from **{guild.name}** to **{ctx.guild.name}**.", type="success"))

        await ctx.db.table("syncs").insert({
            "id": f"{guild.id}{ctx.guild.id}",
            "types": types,
            "origin": str(guild.id),
            "target": str(ctx.guild.id)
        }, conflict="update").run(ctx.db.con)

    async def on_member_ban(self, guild, user):
        syncs = await self.bot.db.table("syncs").get_all(str(guild.id), index="origin").filter(lambda s: s["types"].contains("bans")).run(self.bot.db.con)
        while await syncs.fetch_next():
            sync = await syncs.next()
            target = self.bot.get_guild(int(sync["target"]))
            if target is None:
                continue

            try:
                await target.ban(user, reason=f"Banned on `{guild.name}`")

            except:
                pass

    async def on_member_unban(self, guild, user):
        syncs = await self.bot.db.table("syncs").get_all(str(guild.id), index="origin").filter(lambda s: s["types"].contains("bans")).run(self.bot.db.con)
        while await syncs.fetch_next():
            sync = await syncs.next()
            target = self.bot.get_guild(int(sync["target"]))
            if target is None:
                continue

            try:
                await target.unban(user, reason=f"Unbanned on `{guild.name}`")

            except:
                pass

    @sync.command(aliases=["channel"])
    @cmd.guild_only()
    @cmd.has_permissions(administrator=True)
    @cmd.bot_has_permissions(administrator=True)
    async def messages(self, ctx, channel_id: int):
        """
        Synchronize all new messages from another channel to this channel
        channel_id ::     The id of the channel
        """
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            raise cmd.CommandError(f"There is **no channel with the id** `{channel_id}`.")

        if channel.id == ctx.channel.id:
            raise cmd.CommandError(f"**No lol.**")

        if channel.guild.get_member(ctx.author.id) is None or not channel.permissions_for(channel.guild.get_member(ctx.author.id)).administrator:
            raise cmd.MissingPermissions([f"administrator` in the channel `{channel.name}"])

        if not channel.guild.me.guild_permissions.administrator:
            raise cmd.BotMissingPermissions([f"administrator` in the channel `{channel.name}"])

        current = await ctx.db.table("syncs").get(f"{channel.id}{ctx.channel.id}").run(ctx.db.con)
        types = []
        if current is not None:
            types = current.get("types", [])

        if "messages" not in types:
            types.append("messages")
            await ctx.send(**ctx.em(f"Successfully **enabled message sync** from **<#{channel.id}> to <#{ctx.channel.id}>**.", type="success"))

        else:
            types.remove("messages")
            await ctx.send(**ctx.em(f"Successfully **disabled message sync** from **<#{channel.id}> to <#{ctx.channel.id}>**.", type="success"))

        await ctx.db.table("syncs").insert({
            "id": f"{channel.id}{ctx.channel.id}",
            "types": types,
            "origin": str(channel.id),
            "target": str(ctx.channel.id)
        }, conflict="update").run(ctx.db.con)

    async def on_message(self, msg):
        if msg.author.discriminator == "0000":
            return

        wait_for = []
        syncs = await self.bot.db.table("syncs").get_all(str(msg.channel.id), index="origin").filter(lambda s: s["types"].contains("messages")).run(self.bot.db.con)
        while await syncs.fetch_next():
            sync = await syncs.next()
            target = self.bot.get_channel(int(sync["target"]))
            if target is None:
                continue

            try:
                webhooks = await target.webhooks()
                if len(webhooks) == 0:
                    webhook = await target.create_webhook(name="message sync")

                else:
                    webhook = webhooks[0]

                embeds = msg.embeds
                for attachment in msg.attachments:
                    embed = discord.Embed()
                    embed.set_image(url=attachment.url)
                    embeds.append(embed)

                wait_for.append(await webhook.send(username=msg.author.name, avatar_url=msg.author.avatar_url, content=helpers.clean_content(msg.content), embeds=embeds))
            except:
                pass


def setup(bot):
    bot.add_cog(Sync(bot))
