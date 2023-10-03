import datetime


class Provider:
    def __init__(self, id: int, url: str, name: str, date_add: datetime.datetime, description: str, city: str,
                 address: str, contacts: str, active: bool):
        self.id = id
        self.url = url
        self.name = name
        self.date_add = date_add
        self.description = description
        self.city = city
        self.address = address
        self.contacts = contacts
        self.active = active
