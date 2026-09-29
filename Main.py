import os
import time
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv("Bot.env")

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ============================================================
# CONFIGURATION
# ============================================================

# Server A - Voice Channel where the bot must stay
VOICE_CHANNEL_ID = int(os.getenv("VOICE_CHANNEL_ID", "0"))

# Server B - Text Channel where notifications are sent
NOTIFICATION_TEXT_CHANNEL_ID = int(
    os.getenv("NOTIFICATION_TEXT_CHANNEL_ID", "0")
)

# ============================================================
# BOT SETUP
# ============================================================

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# ============================================================
# VARIABLES
# ============================================================

is_initial_startup = True

last_reconnect_message_time = 0

COOLDOWN_24_HOURS = 86400

vc_task = None


# ============================================================
# 24 HOUR RECONNECT MESSAGE COOLDOWN
# ============================================================

def can_send_reconnect_message():
    global last_reconnect_message_time

    current_time = time.time()

    if current_time - last_reconnect_message_time >= COOLDOWN_24_HOURS:
        last_reconnect_message_time = current_time
        return True

    return False


# ============================================================
# GET CHANNELS
# ============================================================

def get_voice_channel():
    channel = bot.get_channel(VOICE_CHANNEL_ID)

    if channel is None:
        return None

    if not isinstance(channel, (discord.VoiceChannel, discord.StageChannel)):
        print(
            f"❌ ID {VOICE_CHANNEL_ID} is not a voice/stage channel."
        )
        return None

    return channel


def get_notification_channel():
    channel = bot.get_channel(NOTIFICATION_TEXT_CHANNEL_ID)

    if channel is None:
        return None

    if not isinstance(channel, discord.TextChannel):
        print(
            f"❌ ID {NOTIFICATION_TEXT_CHANNEL_ID} is not a text channel."
        )
        return None

    return channel


# ============================================================
# SEND NOTIFICATION SAFELY
# ============================================================

async def send_notification(message):
    try:
        channel = get_notification_channel()

        if channel is None:
            return

        await channel.send(message)

    except discord.Forbidden:
        print("❌ Missing permission to send messages in notification channel.")

    except discord.HTTPException as e:
        print(f"❌ Failed to send notification: {e}")

    except Exception as e:
        print(f"❌ Notification error: {type(e).__name__}: {e}")


# ============================================================
# CONNECT TO VOICE
# ============================================================

async def connect_to_voice():
    global is_initial_startup

    await bot.wait_until_ready()

    while not bot.is_closed():

        try:
            vc_channel = get_voice_channel()

            if vc_channel is None:
                print(
                    f"❌ Voice channel not found: {VOICE_CHANNEL_ID}"
                )

                await asyncio.sleep(30)
                continue

            # ------------------------------------------------
            # Find voice client for this guild
            # ------------------------------------------------

            voice_client = discord.utils.get(
                bot.voice_clients,
                guild=vc_channel.guild
            )

            # ------------------------------------------------
            # Bot is not connected
            # ------------------------------------------------

            if voice_client is None:

                print(
                    f"🔊 Joining {vc_channel.name} "
                    f"(Guild: {vc_channel.guild.name})..."
                )

                try:
                    voice_client = await vc_channel.connect(
                        reconnect=False,
                        self_deaf=True
                    )

                    print(
                        f"✅ Connected to VC: {vc_channel.name}"
                    )

                    if is_initial_startup:

                        await send_notification(
                            f"Bot has connected to the Voice Channel "
                            f"in **{vc_channel.guild.name}** from startup!"
                        )

                        is_initial_startup = False

                    elif can_send_reconnect_message():

                        await send_notification(
                            f"Bot has reconnected back to the Voice Channel "
                            f"in **{vc_channel.guild.name}**!"
                        )

                except asyncio.TimeoutError:

                    print(
                        "❌ Voice connection timed out."
                    )

                    print(
                        "⚠️ Discord voice handshake did not complete."
                    )

                except discord.ClientException as e:

                    print(
                        f"❌ Discord voice client error: "
                        f"{type(e).__name__}: {e}"
                    )

                except discord.DiscordException as e:

                    print(
                        f"❌ Discord voice error: "
                        f"{type(e).__name__}: {e}"
                    )

                except Exception as e:

                    print(
                        f"❌ Voice connection error: "
                        f"{type(e).__name__}: {e}"
                    )

            # ------------------------------------------------
            # Bot is connected somewhere
            # ------------------------------------------------

            else:

                if not voice_client.is_connected():

                    print(
                        "🔄 Voice client exists but is disconnected."
                    )

                    try:
                        await voice_client.disconnect(force=True)
                    except Exception:
                        pass

                else:

                    # ------------------------------------------------
                    # Bot is in the wrong channel
                    # ------------------------------------------------

                    if voice_client.channel.id != VOICE_CHANNEL_ID:

                        print(
                            f"⚠️ Bot is in "
                            f"'{voice_client.channel.name}'. "
                            f"Moving back to '{vc_channel.name}'."
                        )

                        try:
                            await voice_client.move_to(vc_channel)

                            print(
                                f"✅ Moved back to {vc_channel.name}"
                            )

                        except Exception as e:

                            print(
                                f"❌ Failed to move bot: "
                                f"{type(e).__name__}: {e}"
                            )

        except Exception as e:

            print(
                f"⚠️ VC loop error: "
                f"{type(e).__name__}: {e}"
            )

        # Check every 10 seconds
        await asyncio.sleep(10)


# ============================================================
# BOT READY
# ============================================================

@bot.event
async def on_ready():

    global vc_task

    print("=" * 50)

    print(
        f"✅ Bot is online as {bot.user}"
    )

    print(
        f"🆔 Bot ID: {bot.user.id}"
    )

    print(
        f"🎤 Voice Channel ID: {VOICE_CHANNEL_ID}"
    )

    print(
        f"💬 Notification Channel ID: "
        f"{NOTIFICATION_TEXT_CHANNEL_ID}"
    )

    print("=" * 50)

    # Prevent duplicate VC tasks after reconnects
    if vc_task is None or vc_task.done():

        vc_task = asyncio.create_task(
            connect_to_voice()
        )

        print(
            "♾️ 24/7 VC system started!"
        )

    else:

        print(
            "♾️ 24/7 VC system is already running."
        )


# ============================================================
# VOICE STATE UPDATE
# ============================================================

@bot.event
async def on_voice_state_update(member, before, after):

    global is_initial_startup

    vc_channel = get_voice_channel()

    if vc_channel is None:
        return

    notification_channel = get_notification_channel()

    # ========================================================
    # BOT'S OWN VOICE STATE
    # ========================================================

    if bot.user and member.id == bot.user.id:

        # ----------------------------------------------------
        # BOT WAS DISCONNECTED
        # ----------------------------------------------------

        if after.channel is None:

            mover = "a user"

            # Try to determine who disconnected the bot
            try:

                await asyncio.sleep(0.5)

                async for entry in vc_channel.guild.audit_logs(
                    limit=5,
                    action=discord.AuditLogAction.member_disconnect
                ):

                    if entry.target and entry.target.id == bot.user.id:

                        mover = (
                            f"{entry.user.name} "
                            f"({entry.user.id})"
                        )

                        break

            except Exception:
                pass

            print(
                f"🚨 Bot was disconnected from VC by {mover}."
            )

            # Send notification
            if notification_channel:

                try:

                    await notification_channel.send(
                        "# 🚨 Bot was disconnected from VC by a user."
                    )

                except Exception as e:

                    print(
                        f"❌ Disconnect notification error: "
                        f"{type(e).__name__}: {e}"
                    )

            # Try to reconnect
            try:

                await asyncio.sleep(2)

                # Make sure there isn't already a connection
                existing_vc = discord.utils.get(
                    bot.voice_clients,
                    guild=vc_channel.guild
                )

                if existing_vc is None:

                    print(
                        "🔄 Attempting instant VC reconnect..."
                    )

                    await vc_channel.connect(
                        reconnect=False,
                        self_deaf=True
                    )

                    print(
                        "✅ Instantly reconnected to VC!"
                    )

                    if (
                        not is_initial_startup
                        and can_send_reconnect_message()
                    ):

                        await send_notification(
                            f"Bot has reconnected back to the Voice Channel "
                            f"in **{vc_channel.guild.name}**!"
                        )

            except asyncio.TimeoutError:

                print(
                    "❌ Instant reconnect timed out."
                )

            except Exception as e:

                print(
                    f"❌ Instant reconnect error: "
                    f"{type(e).__name__}: {e}"
                )

        # ----------------------------------------------------
        # BOT WAS MOVED TO ANOTHER VC
        # ----------------------------------------------------

        elif after.channel and after.channel.id != VOICE_CHANNEL_ID:

            mover = "a user"

            try:

                await asyncio.sleep(0.5)

                async for entry in vc_channel.guild.audit_logs(
                    limit=5,
                    action=discord.AuditLogAction.member_move
                ):

                    if entry.target and entry.target.id == bot.user.id:

                        mover = (
                            f"{entry.user.name} "
                            f"({entry.user.id})"
                        )

                        break

            except Exception:
                pass

            print(
                f"⚠️ Bot was moved to "
                f"'{after.channel.name}' by {mover}."
            )

            print(
                f"🔄 Moving bot back to '{vc_channel.name}'..."
            )

            await send_notification(
                "# ⚠️ The bot was moved to another voice channel."
            )

            try:

                voice_client = discord.utils.get(
                    bot.voice_clients,
                    guild=vc_channel.guild
                )

                if voice_client:

                    await voice_client.move_to(
                        vc_channel
                    )

                    print(
                        f"✅ Bot moved back to {vc_channel.name}."
                    )

            except Exception as e:

                print(
                    f"❌ Failed to move bot back: "
                    f"{type(e).__name__}: {e}"
                )

        return

    # ========================================================
    # OTHER USERS' VOICE ACTIVITY
    # ========================================================

    if notification_channel is None:
        return

    try:

        # ----------------------------------------------------
        # USER JOINED MAIN VC
        # ----------------------------------------------------

        if (
            (before.channel is None
             or before.channel.id != VOICE_CHANNEL_ID)
            and
            after.channel is not None
            and after.channel.id == VOICE_CHANNEL_ID
        ):

            await notification_channel.send(
                f"**{member.display_name}** has joined the "
                f"Voice Channel in **{vc_channel.guild.name}**."
            )

        # ----------------------------------------------------
        # USER DISCONNECTED FROM MAIN VC
        # ----------------------------------------------------

        elif (
            before.channel is not None
            and before.channel.id == VOICE_CHANNEL_ID
            and after.channel is None
        ):

            await notification_channel.send(
                f"**{member.display_name}** has disconnected from "
                f"the Voice Channel in **{vc_channel.guild.name}**."
            )

        # ----------------------------------------------------
        # USER MOVED FROM MAIN VC
        # ----------------------------------------------------

        elif (
            before.channel is not None
            and before.channel.id == VOICE_CHANNEL_ID
            and after.channel is not None
            and after.channel.id != VOICE_CHANNEL_ID
        ):

            await notification_channel.send(
                f"**{member.display_name}** was moved to "
                f"**{after.channel.name}** in "
                f"**{vc_channel.guild.name}**."
            )

    except discord.Forbidden:

        print(
            "❌ Missing permission to send notification messages."
        )

    except discord.HTTPException as e:

        print(
            f"❌ Discord notification error: {e}"
        )

    except Exception as e:

        print(
            f"❌ Voice state notification error: "
            f"{type(e).__name__}: {e}"
        )


# ============================================================
# START BOT
# ============================================================

if __name__ == "__main__":

    if not BOT_TOKEN:

        print(
            "❌ ERROR: BOT_TOKEN is missing from Bot.env"
        )

    elif VOICE_CHANNEL_ID == 0:

        print(
            "❌ ERROR: VOICE_CHANNEL_ID is missing from Bot.env"
        )

    elif NOTIFICATION_TEXT_CHANNEL_ID == 0:

        print(
            "❌ ERROR: NOTIFICATION_TEXT_CHANNEL_ID "
            "is missing from Bot.env"
        )

    else:

        print("🚀 Starting bot...")

        bot.run(BOT_TOKEN)