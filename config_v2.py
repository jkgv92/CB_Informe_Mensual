NIGHT_HOURS = [0, 1, 2, 3, 4, 5, 19, 20, 21, 22, 23]

# date format would be "YYYY-MM-DD"
# last baseline date must be the same
# date as start of study. Basically all
# dates must be mondays.
BASELINE = ['2022-08-01', '2022-10-31']
STUDY = ['2022-11-01', '2022-11-30']

MONTH_NAME = 'Noviembre'

DATE_INTERVALS_TO_DISCARD = {
}

# variables that make up totalizer measurement
ENERGY_VAR_LABELS = ('aa-consumo-activa', 'ilu-consumo-activa')
POWER_VAR_LABELS = ('aa-potencia-activa', 'ilu-potencia-activa')


WHITELISTED_VAR_LABELS = (
    "ilu-consumo-activa",
    "consumo-energia-reactiva-total",
    "aa-consumo-activa",
    "front-consumo-activa",
    "aa-potencia-activa",
    # "front-tension-3",
    # "front-tension-2",
    # "front-tension-1",
    "front-potencia-activa",
    "ilu-potencia-activa",
)