import discord
from discord import commands, Embed, ButtonStyle


class Info(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    def calculate_oauth(self):
        perms = discord.Permissions.advanced()
        return discord.utils.oauth_url(
            self.bot.user.id,
            permissions=perms,
            scopes=("bot", "applications.commands")
        )

    @commands.command()
    async def info(self, ctx):
        info_embed = Embed(
            title=f"About {self.bot.user.name}",
            description=f"""
        {self.bot.user.name} is a multifunctional Discord bot designed to enhance your server experience with a variety of features including leveling, join logs and more.
        We are constantly working to add new features and improve existing ones. Want to know more or add the bot to your own server? Use the buttons below!
        """
        )
        info_embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        # Buttons
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Invite", url=self.calculate_oauth()))
        view.add_item(discord.ui.Button(label="Support Server", url="https://discord.gg/mamono"))
        view.add_item(discord.ui.Button(label="GitHub", url="https://github.com/Revyena/mamono-world"))

        await ctx.respond(embed=info_embed, view=view)


def setup(bot: discord.Bot):
    bot.add_cog(Info(bot))
