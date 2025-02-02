# tasks.py
from discord.ext import tasks
from database import connect_to_db, user_exists, add_user_to_db, get_all_users, update_user_ban_status, update_user_discord_status
import config
import sys

@tasks.loop(hours=1)
async def monitor_users(bot):
    db_conn = connect_to_db()
    if not db_conn:
        return

    target_guild_id = config.MAIN_DISCORD  # ID целевого сервера
    target_guild = bot.get_guild(target_guild_id)
    if not target_guild:
        print(f"Не удалось найти сервер с ID: {target_guild_id}")
        sys.exit("Завершение работы.")

    async for member in target_guild.fetch_members(limit=None):
        if user_exists(db_conn, member.id):
            update_user_discord_status(db_conn, member.id, True, False)
            print(f"Пользователь {member.name} с id {member.id} уже существует в базе данных")
        else:
            add_user_to_db(db_conn, member.id, member.name)

    # Проверка забаненных пользователей
    bans = [ban_entry async for ban_entry in target_guild.bans()]
    banned_user_ids = [ban_entry.user.id for ban_entry in bans]

    # Обновление статуса бана и нахождения в Discord для всех пользователей
    all_users = get_all_users(db_conn)
    for user in all_users:
        discord_id = int(user[0])
        is_banned = discord_id in banned_user_ids
        update_user_ban_status(db_conn, discord_id, is_banned)

        # Проверка наличия пользователя в Discord
        member = target_guild.get_member(discord_id)
        if member:
            update_user_discord_status(db_conn, discord_id, True, False)
        else:
            update_user_discord_status(db_conn, discord_id, False, True)

    db_conn.close()
