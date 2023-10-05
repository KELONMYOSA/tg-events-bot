from pydantic import BaseModel


class User(BaseModel):
    tg_id: int
    tg_username: str
    tg_action: str

    def build_extra(self) -> dict:
        return {"tags": self.model_dump(exclude_unset=True)}
