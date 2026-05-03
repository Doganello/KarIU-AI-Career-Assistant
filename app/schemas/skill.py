from pydantic import BaseModel


class SkillCreate(BaseModel):
    name:  str
    level: str = "beginner"


class SkillRead(SkillCreate):
    id: int

    class Config:
        from_attributes = True