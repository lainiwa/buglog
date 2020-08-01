from pydantic import Field
from buglog.utils import Bug


#################################################
# EXCERCISES

class SideBridge(Bug):
    """Excercise: a side bridge"""
    reps: int = Field(1, title="Repetitions", gt=0)
    times: int = Field(..., gt=0)

class Squats(Bug):
    """Excercise: squats"""
    reps: int = Field(1, title="Repetitions", gt=0)
    times: int = Field(..., gt=0)

class PushUps(Bug):
    """Excercise: push ups"""
    reps: int = Field(1, title="Repetitions", gt=0)
    times: int = Field(..., gt=0)

class LegRaises(Bug):
    """Excercise: leg raises"""
    reps: int = Field(1, title="Repetitions", gt=0)
    time: int = Field(..., title="Time [s]", gt=0)

class PelvicLift(Bug):
    """Excercise: pelvic lift"""
    reps: int = Field(1, title="Repetitions", gt=0)
    times: int = Field(..., gt=0)


#################################################
# MEDS

class Escitalopram(Bug):
    """Meds: escitalopram antidepressant"""
    dose: int = Field(10, title="Dose [mg]", gt=0)
    num: int = Field(1, gt=0)

class Magnesium(Bug):
    """Meds: magnesium"""
    dose: int = Field(400, title="Dose [mg]", gt=0)
    num: int = Field(1, gt=0)

class VitaminD3K2(Bug):
    """Meds: vitamin D3+K2"""
    d3_dose: int = Field(100, title="Vitamin D3 dose [mcg]", gt=0)
    k2_dose: int = Field(10, title="Vitamin K2 dose [mcg]", gt=0)
    num: int = Field(1, gt=0)


#################################################
# FOOD

class Drink(Bug):
    liters: float = Field(..., title="Vol [L]", gt=0)
    name: str = Field(..., title="What was it")

class Drink_DietSoda2L(Bug):
    """Two liters of diet soda"""
    liters: float = Field(2, title="Vol [L]", gt=0)
    name: str = Field("diet soda", title="What was it")

class Crisps(Bug):
    mass: float = Field(..., title="Mass [g]", gt=0)


#################################################
# OTHER

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
