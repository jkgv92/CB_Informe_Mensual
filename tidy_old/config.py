# Base configuration ----------------------------------------------------------

lst_primary_pallete = ['#d5752d', '#59595b']
lst_secondary_palette = ['#13a2e1', '#00be91', '#fff65e', '#003fa2', '#ca0045']
USE_CELSIA_PALETTE = True
# Really it's Helvetica but one has to install it first.
# Arial does the trick and is officially endorsed.
CELSIA_FONT = 'Arial'
SCATTERGEO_MAX_MARKER_AREA = 1000

# Ubidots API
API_URL = 'https://industrial.api.ubidots.com/api/v1.6/devices/'
# _TOKEN: str = config["token"]
LST_VAR_FIELDS = ["value.value", "variable.id",
                  "device.label", "device.name", "timestamp"]
LST_HEADERS = ['value', 'variable', 'device', 'device_name', 'timestamp']

# Date and Time
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
LOCAL_TIMEZONE = 'America/Bogota'

# Plotting parameters
CONFIDENCE_INTERVAL = 95

# General parameters
ALLOWED_DATE_OVERLAP = 0
DAYS_PER_MONTH = 365.25/12

dct_dow = {
    0: 'lunes',
    1: 'martes',
    2: 'miércoles',
    3: 'jueves',
    4: 'viernes',
    5: 'sábado',
    6: 'domingo',
}

lst_nighttime_hours = [0, 1, 2, 3, 4, 5, 19, 20, 21, 22, 23]

# Client level configuration --------------------------------------------------

# Ubidots data parameters
DEVICE_GROUP_LABEL = 'bancolombia'
DATA_FREQUENCY = '2D'
HOUR_FREQUENCY = '1h'

USE_PICKLED_DATA = True


# Plotting parameters
# try 17.362, 24.579, 21.19 for widths
width = 17.362
height = width*5.5/12.5
WIDE_FIGURE_SIZE = (width, height)
SAVE_FIGURES = False
SHOW_OPTIONAL_FIGURES = False

# Cleaning parameters
CLEAN_DATA = False
VALIDATE_CLEANING = False

SHORT_WINDOW = '1h'
SHORT_CONFIDENCE_INTERVAL = 97.5

LONG_WINDOW = '5D'
LONG_CONFIDENCE_INTERVAL = 99

SMOOTHING_METHOD = 'mean'
SMOOTHING_WINDOW = '1h'

REFERENCE_POWER_PERCENTILE = 99

# General parameters
COP_PER_KWH = 692.29

ALL_VARIABLE_LABELS = (
    "ilu-consumo-activa",
    "consumo-domingo",
    "consumo-sabado",
    "consumo-semana",
    "potencia-diaria-promedio",
    "tipo-dia",
    "hora-def",
    "consumo-energia-reactiva-total",
    "aa-consumo-activa",
    "front-consumo-activa",
    "c2-energia-reactiva-capacitiva-acumulada",
    "c2-factor-de-potencia",
    "c2-corriente-total",
    "c2-corriente-l3",
    "c2-corriente-l2",
    "c2-corriente-l1",
    "c2-tension-fase---neutro-l3",
    "c2-tension-fase---neutro-l2",
    "c2-tension-fase---neutro-l1",
    "c2-frecuencia",
    "c2-potencia-reactiva-instantanea-total",
    "aa-potencia-activa",
    "c2-energia-reactiva-inductiva-acumulada",
    "c2-energia-activa-acumulada",
    "c1-factor-de-potencia",
    "c1-corriente-total",
    "c1-corriente-l3",
    "c1-corriente-l2",
    "c1-corriente-l1",
    "front-tension-3",
    "front-tension-2",
    "front-tension-1",
    "c1-frecuencia",
    "c1-potencia-reactiva-instantanea-total",
    "front-potencia-activa",
    "c1-energia-reactiva-capacitiva-acumulada",
    "c1-energia-reactiva-inductiva-acumulada",
    "c1-energia-activa-acumulada",
    "c1-tension-fase---neutro-l3",
    "c1-tension-fase---neutro-l2",
    "c1-tension-fase---neutro-l1",
    "otros-consumo-activa",
    "ilu-potencia-activa",
    "consumo-energia-reactiva-total-1",
    "consumo-sabados",
    "energia-reactiva-inductiva",
    "energia-activa",
    "factor-de-potencia",
    "corriente-total",
    "corriente-l3",
    "corriente-l2",
    "corriente-l1",
    "frecuencia",
    "potencia-reactiva-instantanea-total",
    "energia-reactiva-capacitiva-acumulada",
    "energia-reactiva-inductiva-acumulada",
    "energia-activa-acumulada",
    "c2-potencia-activa-instantanea-total",
    "c1-potencia-activa-instantanea-total",
    "consumo-promedio-diario",
    "potencia-diario-promedio",
    "c2-potencia-activa",
    "potencia-promedio-diaria",
    "potencia-promedio-diario",
    "consumo-promedio",
    "consumo-energia-reactiva-total-2",
    "c2-consumo-activa",
    "ilu-consumo-activa-1",
    "new-variable",
    "consumo-front-sintetica",
    "consumo-activa-total",
    "new-variable-7",
    "er-inductiva-acumulada",
    "new-variable-29",
    "new-variable-28",
    "new-variable-23",
    "new-variable-22",
    "new-variable-21",
    "new-variable-20",
    "new-variable-19",
    "new-variable-18",
    "new-variable-16",
    "new-variable-15",
    "new-variable-14",
    "new-variable-13",
    "new-variable-12",
    "new-variable-11",
    "new-variable-10",
    "new-variable-6",
    "front-tension-l2n",
    "front-tension-l1n",
    "new-variable-3",
    "er-capacitiva-acumulada"
)

BLACKLISTED_VARIABLE_LABELS = (
    # "ilu-consumo-activa",
    "consumo-domingo",
    "consumo-sabado",
    "consumo-semana",
    "potencia-diaria-promedio",
    "tipo-dia",
    "hora-def",
    # "consumo-energia-reactiva-total",
    # "aa-consumo-activa",
    # "front-consumo-activa",
    "c2-energia-reactiva-capacitiva-acumulada",
    "c2-factor-de-potencia",
    "c2-corriente-total",
    "c2-corriente-l3",
    "c2-corriente-l2",
    "c2-corriente-l1",
    "c2-tension-fase---neutro-l3",
    "c2-tension-fase---neutro-l2",
    "c2-tension-fase---neutro-l1",
    "c2-frecuencia",
    "c2-potencia-reactiva-instantanea-total",
    # "aa-potencia-activa",
    "c2-energia-reactiva-inductiva-acumulada",
    "c2-energia-activa-acumulada",
    "c1-factor-de-potencia",
    "c1-corriente-total",
    "c1-corriente-l3",
    "c1-corriente-l2",
    "c1-corriente-l1",
    # "front-tension-3",
    # "front-tension-2",
    # "front-tension-1",
    "c1-frecuencia",
    "c1-potencia-reactiva-instantanea-total",
    # "front-potencia-activa",
    "c1-energia-reactiva-capacitiva-acumulada",
    "c1-energia-reactiva-inductiva-acumulada",
    "c1-energia-activa-acumulada",
    "c1-tension-fase---neutro-l3",
    "c1-tension-fase---neutro-l2",
    "c1-tension-fase---neutro-l1",
    "otros-consumo-activa",
    # "ilu-potencia-activa",
    "consumo-energia-reactiva-total-1",
    "consumo-sabados",
    "energia-reactiva-inductiva",
    "energia-activa",
    "factor-de-potencia",
    "corriente-total",
    "corriente-l3",
    "corriente-l2",
    "corriente-l1",
    "frecuencia",
    "potencia-reactiva-instantanea-total",
    "energia-reactiva-capacitiva-acumulada",
    "energia-reactiva-inductiva-acumulada",
    "energia-activa-acumulada",
    "c2-potencia-activa-instantanea-total",
    "c1-potencia-activa-instantanea-total",
    "consumo-promedio-diario",
    "potencia-diario-promedio",
    "c2-potencia-activa",
    "potencia-promedio-diaria",
    "potencia-promedio-diario",
    "consumo-promedio",
    "consumo-energia-reactiva-total-2",
    "c2-consumo-activa",
    "ilu-consumo-activa-1",
    "new-variable",
    "consumo-front-sintetica",
    "consumo-activa-total",
    "new-variable-7",
    "er-inductiva-acumulada",
    "new-variable-29",
    "new-variable-28",
    "new-variable-23",
    "new-variable-22",
    "new-variable-21",
    "new-variable-20",
    "new-variable-19",
    "new-variable-18",
    "new-variable-16",
    "new-variable-15",
    "new-variable-14",
    "new-variable-13",
    "new-variable-12",
    "new-variable-11",
    "new-variable-10",
    "new-variable-6",
    "front-tension-l2n",
    "front-tension-l1n",
    "new-variable-3",
    "er-capacitiva-acumulada"
)

# This can be front active energy label
# for setups with a single site
# and a device-per-circuit arrangement.
# Lux has cummulative energy data, which
# is the prefered format. But this changes
# things slightly due to the code being
# written for incremental and not cummulative
# data. So we have to invent a synthetic
# variable called consumo-activa.
ACTIVE_ENERGY_LABELS = (
    "consumo-activa",
)
ACTIVE_POWER_LABELS = (
    "potencia-activa",
)

CUMMULATIVE_ENERGY_LABELS = (
    'energia-activa-imp'
)

ACTIVE_ENERGY_LUMP_LABEL = 'consumo-activa-otros'
ACTIVE_POWER_LUMP_LABEL = 'potencia-activa-otros'
TOTAL_ACTIVE_ENERGY_LABEL = None
TOTAL_ACTIVE_POWER_LABEL = None
TOTAL_REACTIVE_ENERGY_LABEL = None
SUB_STR = ()

DATE_INTERVALS_TO_DISCARD = {
}

BASELINE_DATE_INTERVAL = {
    'start':"2022-01-01",
    'end':"2022-08-31"
}

STUDY_DATE_INTERVAL = {
    'start':"2022-09-01",
    'end':"2022-09-30"
}
