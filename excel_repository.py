"""
Repository layer to load OGSM files directly from OneDrive DATA folder.
Khôi phục cơ chế đọc ổn định 100% cho 29 Đơn vị chính thức.
"""

import io
import os
import re
import unicodedata
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

    def _clean_unit_code(self, file_name: str) -> str:
        """Chuẩn hóa tên file thành đúng Mã đơn vị / Bộ môn chuẩn."""
        file_name_nfc = unicodedata.normalize('NFC', str(file_name))
        base_name = os.path.splitext(file_name_nfc)[0].strip()
        base_clean = re.sub(r'\s+', ' ', base_name)
        return base_clean

    def _normalize_status(self, raw_status: str) -> str:
        """Dịch tất cả nhãn tiếng Anh về đúng 4 nhãn Tiếng Việt"""
        st = str(raw_status).strip().lower()
        if any(k in st for k in ["hoàn thành", "completed", "done", "100%"]):
            return "Hoàn thành"
        if any(k in st for k in ["không đạt", "not achieved", "failed"]):
            return "Không đạt"
        if any(k in st for k in ["chưa đến hạn", "not due", "pending"]):
            return "Chưa đến hạn"
        return "Đang thực hiện"

    def fetch_master_dataframe(self) -> pd.DataFrame:
        data_folder_id = self.config.onedrive.data_folder_id
        files = self.graph_client.list_files_in_folder_id(data_folder_id)
        if not files:
            return pd.DataFrame(columns=self.REQUIRED_COLUMNS + ["Unit_Code", "Source_File", "Target_Year"])

        aggregated_dfs: List[pd.DataFrame] = []

        for f in files:
            file_name = f["name"]
            if file_name.startswith("~$") or not file_name.lower().endswith(('.xlsx', '.xls')):
                continue

            unit_code = self._clean_unit_code(file_name)

            try:
                file_bytes = self.graph_client.download_file_by_folder_id(data_folder_id, file_name)
                buffer = io.BytesIO(file_bytes)
                
                # Đọc dữ liệu trực tiếp nguyên bản
                df_raw = pd.read_excel(buffer, sheet_name=0, engine="openpyxl")

                # Bổ sung thông tin nguồn
                if df_raw is not None and not df_raw.empty:
                    clean_filename = file_name.replace(".xlsx", "").replace(".XLSX", "").strip()
                    df_raw["Source_File"] = clean_filename
                    df_raw["Unit_Code"] = unit_code

                    # Chuẩn hóa cột Trạng thái nếu có
                    for col in df_raw.columns:
                        if "status" in str(col).lower() or "trạng thái" in str(col).lower():
                            df_raw[col] = df_raw[col].apply(self._normalize_status)

                    aggregated_dfs.append(df_raw)

            except Exception as e:
                logger.error(f"Lỗi đọc file {file_name}: {e}")

        if not aggregated_dfs:
            return pd.DataFrame(columns=self.REQUIRED_COLUMNS + ["Unit_Code", "Source_File", "Target_Year"])

        return pd.concat(aggregated_dfs, ignore_index=True)

    def save_unit_dataframe(self, unit_file_name: str, df_unit: pd.DataFrame) -> bool:
        data_folder_id = self.config.onedrive.data_folder_id
        clean_df = df_unit.drop(columns=["Unit_Code", "Source_File", "Target_Year"], errors="ignore")

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            clean_df.to_excel(writer, index=False, sheet_name="OGSM")

        buffer.seek(0)
        self.graph_client.upload_file_by_folder_id(data_folder_id, unit_file_name, buffer.read())
        return True

    def save_master_dataframe(self, df: pd.DataFrame) -> bool:
        raise NotImplementedError("Use save_unit_dataframe instead.")
