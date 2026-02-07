import discord
from discord import app_commands
from discord.ext import commands
import json
import random
import os
import asyncio

# --- CẤU HÌNH ---
# ĐẠI CA NHỚ THAY TOKEN VÀO DÒNG DƯỚI NÀY Ạ !!!
TOKEN = 'YOUR_BOT_TOKEN_HERE' 
CONFIG_FILE = 'role_config.json'

intents = discord.Intents.default()
intents.members = True
intents.message_content = True 

class AuthBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("Đã đồng bộ Slash Commands!")

bot = AuthBot()
verification_cache = {}

def load_config():
    if not os.path.exists(CONFIG_FILE): return {}
    with open(CONFIG_FILE, 'r') as f: return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, 'w') as f: json.dump(config, f)

@bot.event
async def on_ready():
    print(f'{bot.user} đã online phục vụ đại ca TrueHieu!')

@bot.tree.command(name="setverifiedrole", description="Admin: Chọn Role cho thành viên đã xác minh")
@app_commands.describe(role="Chọn Role")
@app_commands.checks.has_permissions(administrator=True)
async def set_verified_role(interaction: discord.Interaction, role: discord.Role):
    if role.position >= interaction.guild.me.top_role.position:
        await interaction.response.send_message("❌ Role này cao hơn Role của em, em không phát được ạ!", ephemeral=True)
        return
    config = load_config()
    config[str(interaction.guild_id)] = role.id
    save_config(config)
    await interaction.response.send_message(f"✅ Đã lưu! Role xác thực là: {role.mention}", ephemeral=True)

@bot.tree.command(name="verify", description="Lấy mã xác thực qua DM")
async def verify(interaction: discord.Interaction):
    role_id = load_config().get(str(interaction.guild_id))
    if not role_id:
        await interaction.response.send_message("❌ Admin chưa set role ạ.", ephemeral=True)
        return
    
    auth_code = str(random.randint(100000, 999999))
    verification_cache[interaction.user.id] = {"code": auth_code, "guild_id": interaction.guild_id}
    
    try:
        await interaction.user.send(f"Mã xác thực của bạn cho **{interaction.guild.name}** là: `{auth_code}`\nDùng lệnh `/submit {auth_code}` tại server để xác nhận.")
        await interaction.response.send_message("📩 Em đã gửi mã vào DM nhé đại ca.", ephemeral=True)
    except:
        await interaction.response.send_message("❌ Em không nhắn tin cho đại ca được, vui lòng mở DM.", ephemeral=True)

@bot.tree.command(name="submit", description="Nhập mã xác thực")
async def submit(interaction: discord.Interaction, code: str):
    data = verification_cache.get(interaction.user.id)
    if not data or data["guild_id"] != interaction.guild_id:
        await interaction.response.send_message("❌ Sai mã hoặc chưa yêu cầu mã.", ephemeral=True)
        return

    if code.strip() == data["code"]:
        role_id = load_config().get(str(interaction.guild_id))
        role = interaction.guild.get_role(role_id)
        if role:
            await interaction.user.add_roles(role)
            del verification_cache[interaction.user.id]
            await interaction.response.send_message(f"🎉 Xác thực thành công! Đã cấp role {role.mention}.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Role không tồn tại.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Mã sai rồi ạ.", ephemeral=True)

bot.run(TOKEN)
