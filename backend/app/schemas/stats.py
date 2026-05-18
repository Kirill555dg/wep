import pydantic


class CalendarDay(pydantic.BaseModel):
    date: str
    count: int


class CalendarResponse(pydantic.BaseModel):
    year: int
    month: int
    days: dict[str, int]
