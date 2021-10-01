#!/usr/bin/env python3

import json
import sys
from datetime import datetime
from io import StringIO

import discord
from discord.ext import commands, tasks
from pytz import timezone

from main import main, output_student_info


class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout


bot = commands.Bot(command_prefix="s!", intents=discord.Intents.all())

with open("config.json", "r") as f:
    config = json.load(f)

settings = {
    "timezone": "Europe/Amsterdam",
    "hour": 7,
    "minute": 0,
    "channels": [885153461790974032, 855139201505820746],
}


@bot.event
async def on_ready():
    print("Ready")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)


@tasks.loop(minutes=1)
async def send_schedule():
    tz = timezone(settings["timezone"])

    hour = datetime.now(tz).hour
    minute = datetime.now(tz).minute

    weekday = datetime.now(tz).weekday

    if weekday == 5 or weekday == 6:
        return

    if hour == settings["hour"] and minute == settings["minute"]:
        channels = [bot.get_channel(ch) for ch in settings["channels"]]

        with Capturing() as output:
            await main()

        for channel in channels:
            try:
                msg = "@everyone schedule for today!"
                msg += f"\nlogged in as: <{output[0]}>"

                output.pop(0)

                counter = 0

                for line in output:
                    msg += f"\n`{line}`"

                    counter += 1
                    if counter == 2:
                        msg += "\n"
                        counter = 0

                await channel.send(msg)
            except AttributeError:
                pass


send_schedule.start()
bot.run(config["discord_token"])
