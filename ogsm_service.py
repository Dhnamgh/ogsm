"""
High level business service for querying and updating OGSM records.
"""

import pandas as pd
from typing import Optional, Dict, Any
from repository.excel_repository import ExcelOneDriveRepository
from services.analytics_service import OGSMAnalyticsService
from core.logger import get_logger

logger = get_logger()


class OGSMService:

    def __init__(self, repo: Optional[ExcelOneDriveRepository] = None):
        self.repo = repo or ExcelOneDriveRepository()

    def get_full_ogsm_data(self) -> pd.DataFrame:
        """Retrieves master dataframe."""
        return self.repo.fetch_master_dataframe()

    def update_measure_actual(self, measure_id: str, new_actual: float, status: str) -> bool:
        """
        Updates actual metrics and status for a specific measure item and persists to cloud.
        """
        df = self.repo.fetch_master_dataframe()
        
        mask = df["Measure_ID"] == measure_id
        if not mask.any():
            logger.error(f"Measure ID {measure_id} not found for update.")
            return False

        df.loc[mask, "Actual"] = new_actual
        df.loc[mask, "Status"] = status

        return self.repo.save_master_dataframe(df)

    def get_dashboard_summary(self) -> Dict[str, Any]:
        df = self.get_full_ogsm_data()
        return OGSMAnalyticsService.compute_summary_kpis(df)
