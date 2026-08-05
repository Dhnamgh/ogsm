"""
OGSM Business Logic Service.
"""

import pandas as pd
from typing import Optional, Dict, Any, List
from excel_repository import ExcelOneDriveRepository
from analytics_service import OGSMAnalyticsService
from logger import get_logger

logger = get_logger()


class OGSMService:

    def __init__(self, repo: Optional[ExcelOneDriveRepository] = None):
        self.repo = repo or ExcelOneDriveRepository()

    def get_full_ogsm_data(self) -> pd.DataFrame:
        return self.repo.fetch_master_dataframe()

    def get_available_units(self) -> List[str]:
        df = self.get_full_ogsm_data()
        if "Unit_Code" in df.columns:
            return sorted(df["Unit_Code"].dropna().unique().tolist())
        return []

    def update_measure_actual(self, measure_id: str, new_actual: float, status: str) -> bool:
        df_master = self.repo.fetch_master_dataframe()

        mask = df_master["Measure_ID"] == measure_id
        if not mask.any():
            logger.error(f"Measure ID {measure_id} không tồn tại trong các file đơn vị.")
            return False

        source_file = df_master.loc[mask, "Source_File"].iloc[0]
        df_unit = df_master[df_master["Source_File"] == source_file].copy()

        unit_mask = df_unit["Measure_ID"] == measure_id
        df_unit.loc[unit_mask, "Actual"] = new_actual
        df_unit.loc[unit_mask, "Status"] = status

        return self.repo.save_unit_dataframe(source_file, df_unit)

    def get_dashboard_summary(self, unit_filter: Optional[str] = None) -> Dict[str, Any]:
        df = self.get_full_ogsm_data()
        if unit_filter and "Unit_Code" in df.columns:
            df = df[df["Unit_Code"] == unit_filter]
        return OGSMAnalyticsService.compute_summary_kpis(df)
