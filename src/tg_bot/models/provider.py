import datetime

from pydantic import BaseModel


class Provider(BaseModel):
    id: int
    url: str
    name: str
    date_add: datetime.datetime
    description: str | None
    city: str | None
    address: str | None
    contacts: str | None
    active: bool
