import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd


class OrderAnalyzer:
    def __init__(self, config: Any) -> None:
        self.config = config
        self.results: List[Dict[str, Any]] = []
        self.processed_files = 0
        self.error_files = 0
        self._setup_logging()


    def _setup_logging(self) -> None:
        self.config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("OrderAnalyzer")
        self.logger.setLevel(logging.ERROR)
        if not self.logger.handlers:
            handler = logging.FileHandler(
                self.config.LOG_FILE, mode="a", encoding="utf-8"
            )
            handler.setFormatter(
                logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            )
            self.logger.addHandler(handler)

    # ---------- чтение и валидация ----------
    def load_file(self, file_path: Path) -> Optional[pd.DataFrame]:

        try:
            df = pd.read_csv(file_path)
        except Exception as exc:
            self.logger.error(f"[{file_path.name}] ошибка чтения: {exc}")
            return None

        if df.empty:
            self.logger.error(f"[{file_path.name}] файл пустой")
            return None

        missing = [c for c in self.config.REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            self.logger.error(
                f"[{file_path.name}] отсутствуют колонки: {missing}"
            )
            return None

        try:
            df[self.config.AMOUNT_COLUMN] = pd.to_numeric(
                df[self.config.AMOUNT_COLUMN], errors="raise"
            )
        except Exception as exc:
            self.logger.error(
                f"[{file_path.name}] нечисловые значения в "
                f"'{self.config.AMOUNT_COLUMN}': {exc}"
            )
            return None

        return df

  
    def filter_delivered(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[df[self.config.STATUS_COLUMN] == self.config.DELIVERED_STATUS]

    def calculate_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        count = int(len(df))
        revenue = float(df[self.config.AMOUNT_COLUMN].sum()) if count else 0.0
        avg = float(df[self.config.AMOUNT_COLUMN].mean()) if count else 0.0
        return {
            "total_revenue": round(revenue, 2),
            "avg_order_value": round(avg, 2),
            "orders_count": count,
        }

    def process_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        df = self.load_file(file_path)
        if df is None:
            self.error_files += 1
            return None

        delivered = self.filter_delivered(df)
        metrics = self.calculate_metrics(delivered)
        metrics["file_name"] = file_path.name

        self.processed_files += 1
        return metrics

    def process_all(self) -> pd.DataFrame:
        self.config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        self.config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        self.config.DATA_DIR.mkdir(parents=True, exist_ok=True)

        files = sorted(self.config.DATA_DIR.glob("*.csv"))
        if not files:
            print(f"В папке {self.config.DATA_DIR} не найдено CSV-файлов.")

        for file_path in files:
            metrics = self.process_file(file_path)
            if metrics is not None:
                self.results.append(metrics)

        report_df = pd.DataFrame(
            self.results,
            columns=[
                "file_name",
                "total_revenue",
                "avg_order_value",
                "orders_count",
            ],
        )
        report_df.to_csv(self.config.REPORT_FILE, index=False, encoding="utf-8")
        return report_df


    def summary(self) -> None:
        print(f"Обработано файлов: {self.processed_files}")
        print(f"Файлов с ошибками: {self.error_files}")
        if self.results:
            print(f"Отчёт сохранён: {self.config.REPORT_FILE}")