from pydantic import Field, BaseModel


class Bug(BaseModel):
    pass


class SideBridge(Bug):
    """Excercise: a side bridge"""

    reps: int = Field(1, title="Repetitions", gt=0)
    times: int = Field(..., gt=0)


class Squats(Bug):
    """Excercise: squats"""

    reps: int = Field(1, title="Repetitions", gt=0)
    times: int = Field(..., gt=0)


class Drink(Bug):
    liters: float = Field(..., title="Vol [L]", gt=0)
    name: str = Field(..., title="What was it")


class DietSoda(Bug):
    """Two liters of Pepsi"""

    liters: float = Field(2, title="Vol [L]", gt=0)
    name: str = Field("diet coke", title="What was it")


class Mood(Bug):
    """Current mood & feel"""

    mood: int = Field(
        ..., title="How do you feel? (1=bad ... 5=great)", ge=1, le=5
    )


class Weight(Bug):
    kg: float = Field(..., ge=0)


class Learned(Bug):
    """Learned stuff"""

    summary: str = Field(
        "nothing", title="Description of a thing you learned lately"
    )


# class Drug(Bug):
