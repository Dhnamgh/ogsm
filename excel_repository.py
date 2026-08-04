"""
OpenPyXL and Pandas Excel Repository handling Multi-file Unit datasets in OneDrive DATA folder.
"""

import io
import os
import pandas as pd
from typing import Optional, List
from graph_client import MicrosoftGraphClient
from base_repository import BaseOGSMRepository
from logger import get_logger
from config import load_config

logger = get_logger()


class ExcelOneDriveRepository(BaseOGSMRepository):

    REQUIRED_COLUMNS = [
        "Objective_ID", "Objective_Title", "Goal_ID", "Goal_Desc",
        "Strategy_ID", "Strategy_Desc", "Measure_ID", "Measure_Desc",
        "Unit", "Target", "Actual", "Owner", "Status"
    ]

    def __init__(self, graph_client: Optional[MicrosoftGraphClient] = None):
        self.graph_client = graph_client or MicrosoftGraphClient()
        self.config = load_config()

    def fetch_master_dataframe(self) -> pd.DataFrame:
        data_folder_id = self.config.onedrive.data_folder_id
        logger.info(f"Scanning and loading all unit files inside DATA folder ({data_folder_id})")

        files = self.graph_client.list_files_in_folder_id(data_folder_id)
        if not files:
            logger.warning(f"No Excel files found in DATA folder ID: {data_folder_id}")
            return pd.DataFrame(columns=self.REQUIRED_COLUMNS + ["Unit_Code", "Source_File"])

        aggregated_dfs: List[pd.DataFrame] = []

        for f in files:
            file_name = f["name"]
            unit_code = os.path.splitext(file_name)[0]

            try:
                file_bytes = self.graph_client.download_file_by_folder_id(data_folder_id, file_name)
                buffer = io.BytesIO(file_bytes)
                df_unit = pd.read_excel(buffer, engine="openpyxl")

                for col in self.REQUIRED_COLUMNS:
                    if col not in df_unit.columns:
                        df_unit[col] = None

                df_unit["Unit_Code"] = unit_code
                df_unit["Source_File"] = file_name

                df_unit["Target"] = pd.to_numeric(df_unit["Target"], errors="coerce").fillna(0.0)
                df_unit["Actual"] = pd.to_numeric(df_unit["Actual"], errors="coerce").fillna(0.0)

                aggregated_dfs.append(df_unit)
                logger.info(f"Successfully loaded unit dataset: {file_name} ({len(df_unit)} rows)")

            except Exception as e:
                logger.error(f"Error reading file {file_name}: {e}")

        if not aggregated_dfs:
            return pd.DataFrame(columns=self.REQUIRED_COLUMNS + ["Unit_Code", "Source_File"])

        master_df = pd.concat(aggregated_dfs, ignore_index=True)
        return master_df

    def save_unit_dataframe(self, unit_file_name: str, df_unit: pd.DataFrame) -> bool:
        data_folder_id = self.config.onedrive.data_folder_id
        logger.info(f"Saving updated unit dataset: {unit_file_name} to DATA folder ({data_folder_id})")

        clean_df = df_unit.drop(columns=["Unit_Code", "Source_File"], errors="ignore")

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            clean_df.to_excel(writer, index=False, sheet_name="OGSM_Unit")

        buffer.seek(0)
        content = buffer.read()

        self.graph_client.upload_file_by_folder_id(data_folder_id, unit_file_name, content)
        return True

    def save_master_dataframe(self, df: pd.DataFrame) -> bool:
        raise NotImplementedError("Use save_unit_dataframe to update specific unit file.")
