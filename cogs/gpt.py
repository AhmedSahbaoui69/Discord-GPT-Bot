import nextcord
from nextcord.ext import commands
from gpt4all import GPT4All
import asyncio
import os
from gtts import gTTS

# Choose and define the model
model_name = "gpt4all-falcon-newbpe-q4_0.gguf"
model_path = "model/"
model = GPT4All(model_name=model_name, model_path=model_path)

class GPT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Stop current generation.")
    async def stop(self, ctx):
        if os.path.exists('.generating'):
            os.remove('.generating')
        else:
            await ctx.message.add_reaction('❓')

    @commands.command(description="Chat with the GPT model.")
    async def gpt(self, ctx, *args):
        # Check if the user included the '-tts' argument
        if args and args[0] == "-tts":
            # Pop the '-tts' argument from the args list
            args = args[1:]
            tts = True
        else:
            tts = False

        # Join the remaining args to form the prompt
        prompt = ' '.join(args)

        # Notify the user that the response is being generated
        await ctx.message.add_reaction("⚙️")
        
        custom_prompt = f"""[INST]As an AI Assistant, your role is to perform users' instructions. Also, never roleplay anyone else but you.
                            Respond to the following instruction:
                            {prompt}
                            [/INST]
                            """
        if not os.path.exists(".generating"):
            try:
                # This file is temporarily created to prevent multiple requests at the same time
                with open(f'.generating', 'w') as f:
                    f.write('THIS FILE IS TEMPORARILY CREATED TO AVOID THE BOT CRASHING ON MULTIPLE REQUESTS (DO NOT DELETE).')

                # Adjust parameters to your liking
                response_generator = model.generate(
                    prompt=custom_prompt,  # Input prompt
                    temp=0.75,  # Temperature to control the randomness of the response
                    streaming=True,  # Streaming mode to increment the discord message one token at a time
                    max_tokens=500,  # Maximum number of tokens to generate in the response
                    n_batch=128  # Batch size (adjust based on resource usage)
                )

                message = await ctx.reply('https://i.ibb.co/DWx6qJh/loading.gif')
                
                # Increment each token to the response message string
                for i, token in enumerate(response_generator):
                    # Check if the user sent a stop command
                    if not os.path.exists('.generating'):
                        await ctx.message.add_reaction("❌")
                        await ctx.reply("Generation stopped.")
                        os.remove(".generating")
                        return

                    if i == 0:
                        response = token
                    else:
                        response += token

                    try:
                        await asyncio.wait_for(message.edit(content=response.strip()), timeout=0.2)
                    except asyncio.TimeoutError:
                        pass

                
                # Add an emoji to the end of the string
                response_final = response.strip() + " 🤖."
                await message.edit(content=response_final)
                # Notify the user that the task is finished
                await ctx.message.add_reaction("✅")
                # Delete the temporary file
                try:
                    os.remove(".generating")
                except:
                    pass
                
                # If TTS is enabled, play the response as audio
                if tts:
                    # Generate TTS audio file of the response
                    sound = gTTS(text=str(response), lang="en", slow=False)
                    sound.save("tts.mp3")
                    
                    user = ctx.message.author
                    # Play the audio if the user is inside a voice channel
                    if user.voice != None:
                        try:
                            vc = await user.voice.channel.connect()
                        except:
                            try:
                                vc = ctx.voice_client
                                if vc.is_playing():
                                    vc.stop()
                                source = await nextcord.FFmpegOpusAudio.from_probe("tts.mp3", method="fallback")
                                vc.play(source)
                            except:
                                pass

                    # Send the audio file
                    await ctx.reply(file=nextcord.File('tts.mp3'))

            except Exception as e:
                os.remove(".generating")
                await ctx.message.add_reaction("❌")
                await ctx.reply(f"Error generating response: {e}")
        else:
            await ctx.reply(f"Due to limited resources multiple prompts can't be processed at the same time.\nWait for the current one to finish or simply type `.stop` to cancel the current one.")

    async def check_stop(self, ctx):
        try:
            # Check if the latest message from the user is 'stop'
            last_message = await ctx.channel.history(limit=1).get(author=ctx.author)
            return last_message.content.lower() == 'stop'
        except:
            return False

def setup(bot):
    bot.add_cog(GPT(bot))
