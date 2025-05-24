from logging import Logger

import discord
from discord import commands
from discord.ext import commands as ext_commands

from controllers.logger import setup_logger


class EvalModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Eval Python Code")
        self.code = discord.ui.InputText(
            label="Enter Python code",
            style=discord.InputTextStyle.paragraph,
            placeholder="result = 2 + 2",
            required=True,
            max_length=1000
        )
        self.ephemeral = discord.ui.InputText(
            label="Ephemeral Response",
            style=discord.InputTextStyle.singleline,
            placeholder="Should the response be ephemeral? (True, False)",
            value="True",
            required=False,
            max_length=5
        )
        self.add_item(self.code)
        self.add_item(self.ephemeral)

    async def callback(self, interaction: discord.Interaction):
        code = self.children[0].value.strip()
        setup_logger().info(f"Eval code executed by {interaction.user.name} ({interaction.user.id})\n{code}")

        try:
            # Wrap user code inside an async function dynamically
            func_code = "async def __dynamic_exec():\n"
            for line in code.splitlines():
                func_code += "    " + line + "\n"

            local_vars = {}
            exec(func_code, {}, local_vars)

            # Await the dynamically created async function
            result = await local_vars['__dynamic_exec']()

            # If no explicit result, set a default message
            if result is None:
                result = "Executed successfully with no return value."

        except Exception as e:
            result = f"Error:\n{e}"

        is_ephemeral = False if self.children[1].value.lower() == "false" else True
        await interaction.response.send_message(f"```py\n{result}\n```", ephemeral=is_ephemeral)


class EvalCog(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @ext_commands.is_owner()
    @commands.command(name="eval", description="Run dynamic python code")
    async def eval(self, ctx: discord.ApplicationContext):
        setup_logger().info(f"Eval command used by {ctx.user.name} ({ctx.user.id})")
        modal = EvalModal()
        await ctx.send_modal(modal)


def setup(bot: discord.Bot):
    bot.add_cog(EvalCog(bot))
