import interactions, asyncio, yt_dlp
from interactions.api.voice.audio import AudioVolume

class voice(interactions.Extension):
    def __init__(self, bot):
        self.bot = bot

        # private attributes
        self._voice_state = None
        self._in_voice = False
        self._recording = False
        self._output_recording = "recordings"
        self._ydl_opts = {
        'format': 'bestaudio/best',
        'audioformat': 'mp3',
        'extractaudio': True,
        'youtube_include_dash_manifest': False,
    }


        # public attributes
        self.music_queue = []

    @interactions.listen()
    async def on_ready(self):
        print("Voice extension loaded.")


    # Private methods
    async def _start_recording(self):
        await self._voice_state.start_recording(output_dir=self._output_recording)

    async def _stop_recording(self):
        await self._voice_state.stop_recording()

    async def _play_next_in_queue(self):
        while self.music_queue != []:
            print(self._get_youtube_direct_audio_link(self.music_queue[0]['id']))
            await self._voice_state.play(AudioVolume(self._get_youtube_direct_audio_link(self.music_queue[0]['id'])))
            self._voice_state.resume()
            self.music_queue.pop(0)

    def _search_youtube(self, name):
        with yt_dlp.YoutubeDL() as ydl:
            return ydl.extract_info(f'ytsearch:{name}', download=False)['entries'][0]
        
    def _get_youtube_direct_audio_link(self, url):
        with yt_dlp.YoutubeDL(self._ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            for i in info['formats']:
                if i['format_id'] == '258':
                    return i['url']
                elif i['format_id'] == '251':
                    return i['url']
                elif i['format_id'] == '22':
                    return i['url']
                elif i['format_id'] == '256':
                    return i['url']
                elif i['format_id'] == '140':
                    return i['url']
                elif i['format_id'] == '250':
                    return i['url']
                elif i['format_id'] == '18':
                    return i['url']
                elif i['format_id'] == '249':
                    return i['url']
                elif i['format_id'] == '139':
                    return i['url']
            raise Exception("No audio format found.")
            
    
    # Public methods
    
    @interactions.slash_command(name="play", description="Plays a song in the voice channel.", options=
                                [interactions.SlashCommandOption(name="title", description="The title of the song to play.", type=interactions.OptionType.STRING)])
    async def play(self, ctx: interactions.SlashContext, title: str):
        '''
        Plays a song in the voice channel or adds it to the queue if a song is already playing.
        '''
        if not self._in_voice:
            self._voice_state = await ctx.author.voice.channel.connect()
            self._in_voice = True

        og_message = await ctx.send("Searching for song...")

        top_result = self._search_youtube(title)

        if self.music_queue == []:
            await ctx.edit(og_message, content=f"Playing {top_result['title']}.")
            self.music_queue.append(top_result)
            await self._play_next_in_queue()
        else:
            self.music_queue.append(top_result)
            await ctx.edit(og_message, content=f"Added {top_result['title']} to the queue.")

    @interactions.slash_command(name="queue", description="Shows the current queue.", scopes=[810145273023823882])
    async def queue(self, ctx: interactions.SlashContext):
        '''
        Shows the current queue.
        '''
        message = ''
        for i in range(len(self.music_queue)):
            message += f"{i+1}. {self.music_queue[i]['title']}\n"
        await ctx.send(message)
    


        
