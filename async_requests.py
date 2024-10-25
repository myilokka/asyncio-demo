import asyncio
import datetime

import aiohttp
import more_itertools

from models import SessionDB, SwapiPeople, init_orm
from schema import Person

MAX_REQUESTS = 5


async def get_http_response(url: str, session_http, params: dict = None) -> dict:
    if not params:
        params = {}
    response = await session_http.get(url, params=params)
    res_json = await response.json()
    return res_json


async def insert_people(people_list: list[Person]):
    async with SessionDB() as session:
        orm_model_list = []
        for person in people_list:
            orm_model_list.append(
                SwapiPeople(**person.model_dump(exclude_none=True))
            )
        session.add_all(orm_model_list)
        await session.commit()


async def get_people_raw_data(session_http, params: dict = None) -> dict:
    people_url = f"https://swapi.py4e.com/api/people/"
    people = await get_http_response(people_url, session_http, params)
    return people


async def main():
    await init_orm()
    async with aiohttp.ClientSession() as session_http:
        people_count = (await get_people_raw_data(session_http))['count']
        page = 1
        while people_count:
            req_param = {'page': page}
            people_raw_data = (await get_people_raw_data(session_http, req_param)).get('results')
            if not people_raw_data:
                break
            for people_chunk in more_itertools.chunked(people_raw_data, 5):
                people_to_insert = []
                for person_raw_data in people_chunk:
                    person = Person(
                        birth_year=person_raw_data['birth_year'],
                        eye_color=person_raw_data['eye_color'],
                        hair_color=person_raw_data['hair_color'],
                        height=person_raw_data['height'],
                        gender=person_raw_data['gender'],
                        mass=person_raw_data['mass'],
                        name=person_raw_data['name'],
                        skin_color=person_raw_data['skin_color']
                    )
                    people_to_insert.append(person)

                    nested_data_coros = []

                    nested_data_url_list = (person_raw_data.get('films', []) + person_raw_data.get('species', []) +
                                            person_raw_data.get('starships', []) + person_raw_data.get('vehicles', []) +
                                            [person_raw_data.get('homeworld')] or [])

                    for url in nested_data_url_list:
                        nested_data_coros.append(get_http_response(url, session_http))
                    for coros_chunk in more_itertools.chunked(nested_data_coros, 5):
                        nested_data_list = await asyncio.gather(*coros_chunk)
                        for nested_data in nested_data_list:
                            for key_word in ['films', 'species', 'starships', 'vehicles', 'planets']:
                                if key_word in nested_data['url']:
                                    if key_word == 'planets':
                                        key_word = 'homeworld'
                                    attr_data = getattr(person, key_word)
                                    value = nested_data['title'] if nested_data.get('title') else nested_data.get(
                                        'name')
                                    if attr_data:
                                        attr_data = attr_data.split(',')
                                        attr_data.append(value)
                                        attr_data = ','.join(attr_data)
                                    else:
                                        attr_data = value
                                    setattr(person, key_word, attr_data)
                                    break

            asyncio.create_task(insert_people(people_to_insert))

        page += 1

    tasks = asyncio.all_tasks()
    main_task = asyncio.current_task()
    tasks.remove(main_task)
    await asyncio.gather(*tasks)


start = datetime.datetime.now()
asyncio.run(main())
print(datetime.datetime.now() - start)
