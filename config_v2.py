NIGHT_HOURS = [0, 1, 2, 3, 4, 5, 19, 20, 21, 22, 23]

# date format would be "YYYY-MM-DD"
# last baseline date must be the same
# date as start of study. Basically all
# dates must be mondays.
BASELINE = ['2023-05-01', '2023-07-31']
STUDY = ['2023-08-01', '2023-09-01']

MONTH_NAME = 'Agosto'

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