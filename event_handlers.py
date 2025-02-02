from discord.ext import commands
from database import connect_to_db, get_user_id, add_user_to_db, user_exists, add_user_call_to_db, update_user_call_in_db, get_discord_id, add_discord_to_db, add_message_to_db, update_user_msg_count, create_user_msg_record, get_user_msg_record, update_user_msg_count_pvp, create_user_msg_record_pvp, get_user_msg_record_pvp, update_user_msg_count_pve, create_user_msg_record_pve, get_user_msg_record_pve
from datetime import datetime
import config

def register_event_handlers(bot: commands.Bot):
    @bot.event
    async def on_voice_state_update(member, before, after):
        db_conn = connect_to_db()
        if not db_conn:
            return

        if before.channel is None and after.channel is not None:
            add_user_call_to_db(db_conn, member.id)
        elif before.channel is not None and after.channel is None:
            update_user_call_in_db(db_conn, member.id)

        db_conn.close()

    @bot.event
    async def on_message(message):
        if message.author.bot:
            return

        db_conn = connect_to_db()
        if not db_conn:
            return

        user_id = get_user_id(db_conn, message.author.id)
        if not user_id:
            add_user_to_db(db_conn, message.author.id, message.author.name)
            user_id = get_user_id(db_conn, message.author.id)

        discord_id = get_discord_id(db_conn, message.guild.id)
        if not discord_id:
            add_discord_to_db(db_conn, message.guild.id, message.guild.name)
            discord_id = get_discord_id(db_conn, message.guild.id)

        add_message_to_db(db_conn, user_id, discord_id, message.content, message.created_at)

        current_month = datetime.now().strftime('%Y-%m-01')

        user_msg_record = get_user_msg_record(db_conn, user_id, current_month)
        if not user_msg_record:
            create_user_msg_record(db_conn, user_id, current_month)
            user_msg_record = get_user_msg_record(db_conn, user_id, current_month)
        update_user_msg_count(db_conn, user_msg_record[0])

        if (message.channel.id == config.MAIN_CHANNEL_ID_PVP or
                (hasattr(message.channel, 'parent_id') and message.channel.parent_id == config.MAIN_CHANNEL_ID_PVP)):
            user_msg_record_pvp = get_user_msg_record_pvp(db_conn, user_id, current_month)
            if not user_msg_record_pvp:
                create_user_msg_record_pvp(db_conn, user_id, current_month)
                user_msg_record_pvp = get_user_msg_record_pvp(db_conn, user_id, current_month)
            update_user_msg_count_pvp(db_conn, user_msg_record_pvp[0])

        if (message.channel.id == config.MAIN_CHANNEL_ID_PVE or
                (hasattr(message.channel, 'parent_id') and message.channel.parent_id == config.MAIN_CHANNEL_ID_PVE)):
            user_msg_record_pve = get_user_msg_record_pve(db_conn, user_id, current_month)
            if not user_msg_record_pve:
                create_user_msg_record_pve(db_conn, user_id, current_month)
                user_msg_record_pve = get_user_msg_record_pve(db_conn, user_id, current_month)
            update_user_msg_count_pve(db_conn, user_msg_record_pve[0])

        db_conn.close()

    @bot.event
    async def on_member_join(member):
        db_conn = connect_to_db()
        if not db_conn:
            return
        if user_exists(db_conn, member.id):
            print(f"Пользователь {member.name} с id {member.id} уже существует в базе данных")
        else:
            add_user_to_db(db_conn, member.id, member.name)
        db_conn.close()
