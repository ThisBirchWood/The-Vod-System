import interactions, media_editor

class clip_discord(interactions.Extension):
    def __init__(self, bot, obs_instance):
        self.obs = obs_instance
        self.bot = bot

    @interactions.listen()
    async def on_ready(self):
        print("Discord Clip Extension loaded.")

    async def send_media(self, ctx, media):
        await ctx.send(file=media.path)

    @interactions.slash_command(name="clip", description="Returns a clip of the specified length.", 
                                options=[interactions.SlashCommandOption(name="seconds", description="The length of the clip in seconds.", type=interactions.OptionType.INTEGER,
                                                                         required=False),
                                         interactions.SlashCommandOption(name="desktop_audio", description="Include desktop audio.", type=interactions.OptionType.BOOLEAN,
                                                                        required=False),
                                         interactions.SlashCommandOption(name="resolution", description="The resolution of the clip.", type=interactions.OptionType.STRING, 
                                                                         required=False, 
                                                                         choices=[interactions.SlashCommandChoice(name="720p", value="1280x720"), 
                                                                                  interactions.SlashCommandChoice(name="1080p", value="1920x1080"),
                                                                                  interactions.SlashCommandChoice(name="1440p", value="2560x1440"),]),
                                        interactions.SlashCommandOption(name="fps", description="The FPS of the clip.", type=interactions.OptionType.INTEGER,
                                                                         required=False,
                                                                         choices=[interactions.SlashCommandChoice(name="15", value=15),
                                                                                  interactions.SlashCommandChoice(name="30", value=30),
                                                                                  interactions.SlashCommandChoice(name="60", value=60)]),
                                        interactions.SlashCommandOption(name="file_size", description="File size of the clip in MB. (WARNING: Above 25MB will not work unless server is boosted)", 
                                                                        type=interactions.OptionType.INTEGER,
                                                                        required=False)])
    async def clip(self, ctx: interactions.SlashContext, seconds: int = 30, desktop_audio: bool = True, resolution: int = "1280x720", fps: int = 30, file_size: int = 25):
        if seconds < 0 or seconds > 120:
            await ctx.send("Seconds must be between 0 and 120.")
            return
        
        original_message = await ctx.send("Bellin' OBS...")
        full_replay_buffer_file = self.obs.save_replay_buffer()
        
        await ctx.edit(original_message, content="Rendering clip...")

        resolution = [int(i) for i in resolution.split("x")]
        end_point = full_replay_buffer_file.duration - 3
        start_point = end_point - seconds

        editor = media_editor.MediaEditor(full_replay_buffer_file)
        editor.start_point = start_point
        editor.end_point = end_point
        editor.change_resolution(resolution[0], resolution[1])
        editor.change_fps(fps)
        if desktop_audio:
            editor.flatten()
        else:
            editor.disable_audio_stream(0)
            editor.enable_audio_stream(2)
            editor.enable_audio_stream(3)
        editor.compress_to_filesize_mb(file_size)
        clip = editor.export("raera.mp4")

        await ctx.edit(original_message, content="Uploading clip...")
        await ctx.edit(original_message, file=clip.path, content="")
