import discord
from discord.ui import View

from modules.leveling.cards import generate_leaderboard


class LeaderboardView(View):
    def __init__(self, bot: discord.Bot, users, current_user_id=None, page=0, page_size=10):
        super().__init__(timeout=120)
        self.users = users
        self.bot = bot
        self.page = page
        self.page_size = page_size
        self.current_user_id = current_user_id
        self.update_buttons_state()

    def update_buttons_state(self):
        max_page = (len(self.users) - 1) // self.page_size
        for child in self.children:
            if child.label == "Previous":
                child.disabled = self.page == 0
            elif child.label == "Next":
                child.disabled = self.page >= max_page

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def prev(self, button, interaction):
        self.page = max(self.page - 1, 0)
        await self.update(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next(self, button, interaction):
        max_page = (len(self.users) - 1) // self.page_size
        self.page = min(self.page + 1, max_page)
        await self.update(interaction)

    async def update(self, interaction):
        self.update_buttons_state()
        start = self.page * self.page_size
        end = start + self.page_size
        slice_users = self.users[start:end]

        embed = await generate_leaderboard(self.bot, slice_users, start_index=start, current_user_id=self.current_user_id, page=self.page+1, total_pages=(len(self.users)-1)//self.page_size+1)
        await interaction.response.edit_message(embed=embed, view=self)
