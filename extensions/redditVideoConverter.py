import discord
from discord.ext import commands
import asyncio
import aiohttp
import aiofiles
import json
import uuid
import os
from pathlib import Path

class RedditVideoConverter(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    class AsyncClientSession():
        # explicitly not inheriting from ClientSession as codebase is in flux
        # see https://github.com/aio-libs/aiohttp/issues/3185 and https://github.com/aio-libs/aiohttp/issues/2691
        # inheritance will be removed in v4.0 if I understand correctly

        def __init__(self, session):
            self.session = session

        async def stream(self, link, file):
            async with self.session.get(link) as response:
                assert response.status == 200
                async with aiofiles.open(file, mode="wb") as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        await file.write(chunk)

    def convertVideo(self,video, audio, output):
        os.system(
            "ffmpeg -i " + video + " -i " + audio + " -c copy " + output + " -y > /dev/null 2>&1")

    async def getCredentials(self):
        try:
            async with aiofiles.open(Path.cwd() / 'secrets/redditVideoConverter.secret', 'r') as secretFile:
                secrets = json.loads(await secretFile.read())
                # should not be a blocking issue for async but a larger file might be
                username = secrets['userName']
                password = secrets['passWord']
            return username, password
        except FileNotFoundError:
            raise Exception("Streamable credential file not found")

    def getLinks(self,json_array):
        try:
            link = json_array[0]['data']['children'][0]['data']['secure_media']['reddit_video'][
                'fallback_url']
            video = link.split("?")[0]
            audio = link.split("/DASH")[0] + "/DASH_audio.mp4"
            return video, audio
        except:
            raise Exception(
                "Unable to find video file, are you sure it's a post with a video hosted "
                "on reddit?")

    async def convertRedditLink(self,link):

        username, password = await self.getCredentials()

        videotitle = str(uuid.uuid4())
        json_link = link.split("?")[0] + ".json"

        custom_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) "
                                       "Gecko/20100101 Firefox/70.0"}

        async with aiohttp.ClientSession(headers=custom_headers) as session:
            try:
                async with session.get(json_link) as response:
                    assert response.status == 200
                    reddit_json = await response.json()
            except aiohttp.client_exceptions.InvalidURL:
                raise Exception(
                    "Not a valid link - make sure to include the protocol (https://)")
            except:
                raise Exception("Could not retrieve the link given, is it a link to a valid "
                                "reddit post?")

            video_link, audio_link = self.getLinks(reddit_json)

            async_session = self.AsyncClientSession(session)

            await async_session.stream(video_link, f"{videotitle}_video.mp4")

            try:
                await async_session.stream(audio_link, f"{videotitle}_audio.mp4")
                self.convertVideo(f"{videotitle}_video.mp4", f"{videotitle}_audio.mp4",
                             f'{videotitle}.mp4')
            except AssertionError:
                os.system(f"mv {videotitle}_video.mp4 {videotitle}.mp4")

            async with aiofiles.open(f"{videotitle}.mp4", 'rb') as file:
                files = {f"{videotitle}.mp4": await file.read()}
                async with session.post("https://api.streamable.com/upload",
                                        auth=aiohttp.BasicAuth(username, password),
                                        data=files) as streamable_response:
                    details = await streamable_response.json()

            convertedLink = "https://streamable.com/" + details['shortcode']
            return (convertedLink)

def setup(bot):
    bot.add_cog(RedditVideoConverter(bot))



