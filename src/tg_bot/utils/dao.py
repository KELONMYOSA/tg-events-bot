import psycopg2

from src.config.config import settings
from src.tg_bot.models.event import Event
from src.tg_bot.models.provider import Provider


class PostgreDB:
    # Устанавливаем соединение с базой данных
    def __init__(self):
        self.connection = psycopg2.connect(
            database=settings.DATABASE_NAME,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD,
            host=settings.DATABASE_HOST,
            port=settings.DATABASE_PORT
        )
        self.cursor = self.connection.cursor()

    def __enter__(self):
        return self

    # Сохраняем изменения и закрываем соединение
    def __exit__(self, ext_type, exc_value, traceback):
        self.cursor.close()
        if isinstance(exc_value, Exception):
            print(exc_value)
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()

    def db_select(self, query: str):
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except (Exception, psycopg2.Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
            return None

    def db_insert(self, query: str):
        try:
            self.cursor.execute(query)
        except (Exception, psycopg2.Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
            return None

    def get_event_ids_by_domain_name(self, domain_name: str) -> list[int]:
        domain_id = self.db_select(f"SELECT id FROM domain WHERE name = '{domain_name}'")[0][0]
        event_ids = self.db_select(f"SELECT e_id FROM event_domain WHERE d_id = {domain_id}")
        result = []
        for event_id in event_ids:
            result.extend(event_id)
        return result

    def get_events_by_ids(self, event_ids: list[int]) -> list[Event]:
        events_result = self.db_select(f"SELECT * FROM event "
                                       f"WHERE id IN ({str(event_ids)[1:-1]}) AND date >= CURRENT_DATE "
                                       f"ORDER BY date")
        events = []
        for event in events_result:
            events.append(Event(
                id=event[0],
                m_id=event[1],
                p_id=event[2],
                original_text=event[3],
                title=event[4],
                long_desc=event[5],
                short_desc=event[6],
                date=event[7],
                time_b=event[8],
                time_e=event[9],
                place=event[10],
                geo_id=event[11],
                url=event[12],
                is_online=event[13],
                date_add=event[14],
                active=event[15]
            ))
        return events

    def get_providers(self) -> list[Provider]:
        provider_result = self.db_select("SELECT * FROM provider")
        providers = []
        for provider in provider_result:
            providers.append(Provider(
                id=provider[0],
                url=provider[1],
                name=provider[2],
                description=provider[3],
                city=provider[4],
                address=provider[5],
                contacts=provider[6],
                date_add=provider[7],
                active=provider[8]
            ))
        return providers
