import psycopg2

from src.config.config import settings
from src.tg_bot.models.dictionaries import topic2domain
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
            self.connection.commit()
        except (Exception, psycopg2.Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
            return None

    @staticmethod
    def list_of_str_to_query_str(str_list: list[str]) -> str:
        formatted = []
        for s in str_list:
            formatted.append(f"'{s}'")
        return ','.join(formatted)

    def get_event_ids_by_domain_names(self, domain_names: list[str]) -> list[int]:
        domains_str = self.list_of_str_to_query_str(domain_names)

        domain_result = self.db_select(f"SELECT id FROM domain WHERE name IN ({domains_str})")
        domain_ids = [row[0] for row in domain_result]

        event_ids = self.db_select(f"SELECT e_id FROM event_domain WHERE d_id IN ({str(domain_ids)[1:-1]})")
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
        domains = list(topic2domain.values())
        domains_str = self.list_of_str_to_query_str(domains)

        domain_result = self.db_select(f"SELECT id FROM domain WHERE name IN ({domains_str})")
        domain_ids = [row[0] for row in domain_result]
        provider_id_result = self.db_select(f"SELECT p_id FROM provider_domain WHERE d_id IN ({str(domain_ids)[1:-1]})")
        provider_ids = [row[0] for row in provider_id_result]

        provider_result = self.db_select(f"SELECT * FROM provider WHERE id IN ({str(provider_ids)[1:-1]})")
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

    def get_user_domains(self, user_id: int) -> list[str]:
        domain_result = self.db_select(f"SELECT d_id FROM \"user\".\"tg_user_domain\" WHERE u_id = {user_id}")
        domain_ids = [row[0] for row in domain_result]
        if not domain_ids:
            return []
        domain_name_result = self.db_select(f"SELECT name FROM domain WHERE id IN ({str(domain_ids)[1:-1]})")
        domain_name = [row[0] for row in domain_name_result]

        return domain_name

    def set_user_domains(self, user_id: int, domains: list[str]):
        self.db_insert(f"DELETE FROM \"user\".\"tg_user_domain\" WHERE u_id = {user_id}")
        for domain in domains:
            domain_id = self.db_select(f"SELECT id FROM domain WHERE name = '{domain}'")[0][0]
            self.db_insert(f"INSERT INTO \"user\".\"tg_user_domain\" (u_id, d_id) VALUES ({user_id}, {domain_id})")

    def set_push_interval(self, user_id: int, interval: int):
        self.db_insert(f"INSERT INTO \"user\".\"tg_notification\" (u_id, interval) VALUES ({user_id}, {interval}) "
                       f"ON CONFLICT (u_id) DO UPDATE SET interval = {interval}")

    def set_user(self, user_id: int, username: str):
        self.db_insert(f"INSERT INTO \"user\".\"tg_user\" (id, username) VALUES ({user_id}, '{username}') "
                       f"ON CONFLICT (id) DO NOTHING")

    def get_user_providers(self, user_id: int) -> list[int]:
        provider_result = self.db_select(f"SELECT p_id FROM \"user\".\"tg_user_provider\" WHERE u_id = {user_id}")
        provider_ids = [row[0] for row in provider_result]

        return provider_ids

    def set_user_providers(self, user_id: int, p_ids: list[int]):
        self.db_insert(f"DELETE FROM \"user\".\"tg_user_provider\" WHERE u_id = {user_id}")

        for p_id in p_ids:
            self.db_insert(f"INSERT INTO \"user\".\"tg_user_provider\" (u_id, p_id) VALUES ({user_id}, {p_id})")
