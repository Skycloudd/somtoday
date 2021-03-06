#!/usr/bin/env python3

import asyncio
import datetime
import json
from datetime import datetime, timedelta

import aiohttp
from dateutil import parser


def pretty_datetime(dt: datetime):
    year = dt.year
    month = dt.month
    day = dt.day
    hour = dt.hour
    minute = dt.minute

    return f"{day}/{month}/{year} at {hour}:{minute}"


def pretty_timedelta(td: timedelta):
    minutes = (td.seconds % 3600) // 60
    hours = td.seconds // 3600

    if hours > 0:
        output = f"{hours}h {minutes}m"
    else:
        output = f"{minutes}m"

    return output


async def authenticate(session: aiohttp.ClientSession, config):
    endpoint = "https://somtoday.nl"
    params = {
        "grant_type": "password",
        "username": config["school_uuid"] + "\\" + config["username"],
        "password": config["password"],
        "scope": "openid",
        "client_id": config["client_id"],
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    async with session.post(
        f"{endpoint}/oauth2/token", params=params, headers=headers
    ) as res:
        return json.loads(await res.text())


async def output_student_info(session: aiohttp.ClientSession, auth):
    endpoint = auth["somtoday_api_url"]

    headers = {"Authorization": "Bearer " + auth["access_token"]}

    async with session.get(f"{endpoint}/rest/v1/leerlingen", headers=headers) as res:
        data = json.loads(await res.text())

    for i, student in enumerate(data["items"]):
        # first_name = student.get("roepnaam", "unknown")
        # surname = student.get("achternaam", "unknown")
        # email = student.get("email", "unknown")
        student_id = student.get("leerlingnummer", "unknown")
        # date_of_birth = student.get("geboortedatum", "unknown")
        # phone_number = student.get("mobielNummer", "unknown")
        # gender = student.get("geslacht", "unknown")

        print(f"Student ID: {student_id}")


async def output_schedule(
    session: aiohttp.ClientSession,
    auth,
    days: int,
):
    start_date = datetime.now() + timedelta(days=days)
    end_date = datetime.now() + timedelta(days=days + 1)

    endpoint = auth["somtoday_api_url"]

    headers = {"Authorization": "Bearer " + auth["access_token"]}

    params = {
        "sort": "asc-id",
        # "additional": "vak",
        # "additional": "docentAfkortingen",
        # "additional": "leerlingen"
        "begindatum": "2021-09-06",
        "einddatum": "2021-09-07",
        "begindatum": f"{start_date.year}-{start_date.month}-{start_date.day}",
        "einddatum": f"{end_date.year}-{end_date.month}-{end_date.day}",
    }

    lower = 0
    upper = 99

    all_items = []

    while True:
        params["Range"] = f"items={lower}-{upper}"

        async with session.get(
            f"{endpoint}/rest/v1/afspraken", headers=headers, params=params
        ) as res:
            data = json.loads(await res.text())

        all_items.extend(data["items"])

        if len(data["items"]) < 99:
            break

        lower = upper + 1
        upper = lower + 99

    all_items.sort(key=lambda x: x["beginDatumTijd"])

    for appointment in all_items:
        title = appointment.get("titel", "unknown")
        start = parser.parse(appointment.get("beginDatumTijd", None))
        end = parser.parse(appointment.get("eindDatumTijd", None))

        p_start = pretty_datetime(start)
        p_dur = pretty_timedelta(end - start)

        print(title)
        print(f"\tStart: {p_start}, for {p_dur}")


async def main():
    with open("config.json", "r") as f:
        config = json.load(f)

    default_headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    """
    i should add documentation for this,
    or even a cli interface

    but here are your docs for now:
    days = 0 | today
    days = 1 | tomorrow
    days = 2 | day after tomorrow
    etc...
    negative numbers work aswell!
    days = -1 | yesterday
    etc...
    """

    days = -1

    async with aiohttp.ClientSession(headers=default_headers) as session:
        auth = await authenticate(session, config)
        await output_student_info(session, auth)
        await output_schedule(session, auth, days)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
