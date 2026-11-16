from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

REPORT_FILE = REPORTS_DIR / "summary_report.csv"
LOG_FILE = LOGS_DIR / "errors.log"

# Названия колонок
STATUS_COLUMN = "status"
AMOUNT_COLUMN = "total_amount"

# Значение статуса для фильтрации
DELIVERED_STATUS = "Delivered"

# Обязательные колонки в каждом файле
REQUIRED_COLUMNS = [
    "order_id",
    "person_id",
    "order_date",
    "status",
    "total_amount",
    "currency",
    "payment_method",
    "shipping_method",
]