import json
from typing import List, Optional
from enum import Enum
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, EmailStr, Field
from geojson_pydantic import Point
from beanie import Document, Indexed, Link


class Status(Enum):
    NEW = 0
    PENDING = 1
    ACCEPTED = 2
    REJECTED = 3


class TitlePrefix(BaseModel):
    value: str

    class Settings:
        name = 'title_prefix'

    def __repr__(self):
        return f'<TitlePrefix {self.value}>'

    def __str__(self):
        return self.value


class GeoDataOut(BaseModel):
    data: Point
    altitude: int


class GeoData(Document):
    data: Point
    altitude: Indexed(int)

    class Settings:
        name = 'geo_data'

    def __repr__(self):
        return f'<GeoData {self.data.coordinates}|{self.altitude}>'

    def __str__(self):
        return str(self.data.coordinates)


class PhotoData(Document):

    id: UUID = Field(default_factory=uuid4)
    title: str

    class Settings:
        name = 'photo_data'

    def __repr__(self):
        return f'<PhotoData {self.id.hex}>'

    def __str__(self):
        return self.title


class PersonOut(BaseModel):

    email: EmailStr
    username: str
    first_name: str


class Person(Document):

    email: Indexed(EmailStr, unique=True)
    username: str
    first_name: str
    last_name: str = None
    phone: str = None

    class Settings:
        name = 'person'

    def __repr__(self):
        return f'<Person {self.username}>'

    def __str__(self):
        return self.username

    @classmethod
    async def get_by_email(cls, email):
        return await cls.find_one(cls.email == email)


class MountainPassOut(BaseModel):
    title: str
    title_prefix: TitlePrefix
    alt_titles: Optional[List[str]]
    timestamp: datetime
    person: PersonOut
    geodata: GeoDataOut
    photos: List[PhotoData]
    connects: Optional[str]
    status: Status


class MountainPass(Document):
    title: str
    title_prefix: TitlePrefix
    alt_titles: Optional[List[str]] = None
    timestamp: datetime = datetime.now()
    person: Link[Person]
    geodata: Link[GeoData]
    photos: List[Link[PhotoData]]
    connects: Optional[str] = None
    status: Status = Status.NEW

    class Config:
        schema_extra = {
            'example':
                {
                    'title': 'Dyatlov',
                    'title_prefix': {
                        'value': 'per.'
                    },
                    'alt_titles': [
                        'Schmyatlov'
                    ],
                    'timestamp': '2022-09-02T02:42:04.340Z',
                    'person': {
                        'email': 'john_doe_1969@example.com',
                        'username': 'johndoe1969',
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'phone': '+19991234567'
                    },
                    'geodata': {
                        'data': {
                            'coordinates': [
                                '1.33',
                                '-2.66'
                            ],
                            'type': 'Point'
                        },
                        'altitude': 2789
                    },
                    'photos': [
                        {
                            'title': 'Overlook'
                        }
                    ]
                }
        }

    class Settings:
        name = 'mountain_pass'

    def __repr__(self):
        return f'<MountainPass {self.title}>'

    def __str__(self):
        return self.title

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


__beanie_models__ = [MountainPass, Person, PhotoData, GeoData]
