"""
OpenPyXL and Pandas Excel Repository querying OneDrive via secrets configuration.
"""

import io
import os
import pandas as pd
from typing import Optional, List
from core.graph_client import MicrosoftGraphClient
from repository.base_repository import BaseOGSMRepository
from core.logger import get_logger
from core.config import load_config

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
        """
        Scans all unit Excel files inside the DATA folder ID loaded from st.secrets.
        """
        # Đọc Folder ID của mục DATA trực tiếp từ secret
        data_folder_id = self.config.onedrive.data_folder_id
        logger.info(f"Đang quét danh sách file trong thư mục DATA (ID: {data_folder_id})...")

        files = self.graph_client.list_files_in_folder_id(data_folder_id)
        if not files:
            logger.warning(f"Không tìm thấy file Excel nào trong thư mục DATA ID: {data_folder_id}")
            return pd.DataFrame(columns=self.REQUIRED_COLUMNS + ["Unit_Code", "Source_File"])

        aggregated_dfs: List[pd.DataFrame] = []

        for f in files:
            file_name = f["name"]
            unit_code = os.path.splitext(file_name)[0]  # Ví dụ: P.HCTH.xlsx -> P.HCTH

            try:
                file_bytes = self.graph_client.download_file_by_folder_id(data_folder_id, file_name)
                buffer = io.BytesIO(file_bytes)
                df_unit = pd.read_excel(buffer, engine="openpyxl")

                # Kiểm tra và thêm các cột bắt buộc nếu thiếu
                for col in self.REQUIRED_COLUMNS:
                    if col not in df_unit.columns:
                        df_unit[col] = None

                df_unit["Unit_Code"] = unit_code
                df_unit["Source_File"] = file_name

                df_unit["Target"] = pd.to_numeric(df_unit["Target"], errors="coerce").fillna(0.0)
                df_unit["Actual"] = pd.to_numeric(df_unit["Actual"], errors="coerce").fillna(0.0)

                aggregated_dfs.append(df_unit)
                logger.info(f"Đã nạp dữ liệu đơn vị: {file_name} ({len(df_unit)} dòng)")

            except Exception as e:
                logger.error(f"Lỗi khi đọc file {file_name}: {e}")

        if not aggregated_dfs:
            return pd.DataFrame(columns=self.REQUIRED_COLUMNS + ["Unit_Code", "Source_File"])

        master_df = pd.concat(aggregated_dfs, ignore_index=True)
        return master_df

    def save_unit_dataframe(self, unit_file_name: str, df_unit: pd.DataFrame) -> bool:
        """
        Saves updated unit DataFrame back to its target folder ID in OneDrive.
        """
        data_folder_id = self.config.onedrive.data_folder_id
        logger.info(f"Đang ghi file đơn vị {unit_file_name} vào thư mục DATA ID: {data_folder_id}")

        clean_df = df_unit.drop(columns=["Unit_Code", "Source_File"], errors="ignore")

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            clean_df.to_excel(writer, index=False, sheet_name="OGSM_Unit")

        buffer.seek(0)
        content = buffer.read()

        self.graph_client.upload_file_by_folder_id(data_folder_id, unit_file_name, content)
        return True

    def save_master_dataframe(self, df: pd.DataFrame) -> bool:
        raise NotImplementedError("Sử dụng save_unit_dataframe để lưu file đơn vị cụ thể.")
