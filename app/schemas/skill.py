from pydantic import BaseModel


class SkillCreate(BaseModel):
    name: str
    level: str = "intermediate"


class SkillRead(SkillCreate):
    id: int

    class Config:
        from_attributes = True