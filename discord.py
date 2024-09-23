import interactions, media_editor
from obs import OBS
from config_reader import config


if __name__ == "__main__":
    c = config("config.env")
    obs = OBS(c.get_obs_ip(), c.get_obs_port(), c.get_obs_password())

    bot = interactions.Client(intents=interactions.Intents.GUILDS | interactions.Intents.GUILD_VOICE_STATES)
    bot.load_extension("discord_exts.clipper", obs_instance=obs)
    bot.load_extension("discord_exts.voice")
    bot.start(c.get_discord_token())

