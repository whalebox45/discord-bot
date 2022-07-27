import os
from dotenv import load_dotenv

import interactions

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = interactions.Client(token=TOKEN,default_scope=False)


@bot.command(
    name="my_first_command",
    description="This is the first command I made!",
)
async def my_first_command(ctx: interactions.CommandContext):
    await ctx.send("Hi there!")


@bot.command(
    name="base_command",
    description="This description isn't seen in UI (yet?)",
    options=[
        interactions.Option(
            name="command_name",
            description="A descriptive description",
            type=interactions.OptionType.SUB_COMMAND,
            options=[
                interactions.Option(
                    name="option",
                    description="A descriptive description",
                    type=interactions.OptionType.INTEGER,
                    required=False,
                ),
            ],
        ),
        interactions.Option(
            name="second_command",
            description="A descriptive description",
            type=interactions.OptionType.SUB_COMMAND,
            options=[
                interactions.Option(
                    name="second_option",
                    description="A descriptive description",
                    type=interactions.OptionType.STRING,
                    required=True,
                ),
            ],
        ),
    ],
)
async def cmd(ctx: interactions.CommandContext, sub_command: str, second_option: str = "", option: int = None):
    if sub_command == "command_name":
      await ctx.send(f"You selected the command_name sub command and put in {option}")
    elif sub_command == "second_command":
      await ctx.send(f"You selected the second_command sub command and put in {second_option}")

try:
    bot.start()
except KeyboardInterrupt:
    exit(1)
