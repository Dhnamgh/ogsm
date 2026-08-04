"""
OpenPyXL and Pandas Excel Repository handling OGSM Matrix Structure (2025-2029).
Directly matches UMP/HCTH Excel Template format.
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

    def _transform_custom_excel(self, df: pd.DataFrame, unit_code: str) -> pd.DataFrame:
        """Biến đổi bảng Excel thực tế (STT, Objects, Goals HCTH, Measure (KPI)...) về chuẩn OGSM."""
        
        # Chuẩn hóa tên cột bỏ khoảng trắng thừa
        df.columns = [str(c).strip() for c in df.columns]

        rows = []
        for idx, row in df.iterrows():
            # Lấy Objective / Object
            obj_title = str(row.get("Objects", "")).strip() if pd.notna(row.get("Objects")) else "Mục tiêu chung"
            if obj_title == "nan" or not obj_title:
                obj_title = "Mục tiêu chung"

            # Lấy Goal HCTH hoặc Goal UMP
            goal_desc = ""
            if "Goals HCTH" in row and pd.notna(row["Goals HCTH"]):
                goal_desc = str(row["Goals HCTH"]).strip()
            elif "Goals UMP" in row and pd.notna(row["Goals UMP"]):
                goal_desc = str(row["Goals UMP"]).strip()

            # Lấy Measure (KPI)
            measure_desc = str(row.get("Measure (KPI)", "")).strip() if pd.notna(row.get("Measure (KPI)")) else ""
            if not measure_desc or measure_desc == "nan":
                continue  # Bỏ qua dòng trống không có KPI

            # Lấy Mã/STT
            stt = str(row.get("STT", idx + 1)).strip()
            no_val = str(row.get("No", "")).strip() if pd.notna(row.get("No")) else ""

            # Lấy Trạng thái & Tỷ lệ đạt
            status = str(row.get("Trạng thái", "In Progress")).strip() if pd.notna(row.get("Trạng thái")) else "In Progress"
            
            # Tính Target & Actual
            actual_val = row.get("Tỷ lệ đạt (%)", 0.0)
            try:
                actual_val = float(str(actual_val).replace("%", "").strip())
            except Exception:
                actual_val = 0.0

            # Lấy Target 2026 hoặc Năm đích
            target_val = 100.0
            if "2026" in row and pd.notna(row["2026"]):
                try:
                    target_val = float(str(row["2026"]).replace("%", "").strip())
                except Exception:
                    target_val = 100.0

            rows.append({
                "Objective_ID": f"OBJ-{idx+1}",
                "Objective_Title": obj_title,
                "Goal_ID": f"G-{idx+1}",
                "Goal_Desc": goal_desc if goal_desc != "nan" else obj_title,
                "Strategy_ID": f"S-{idx+1}",
                "Strategy_Desc": f"Chiến lược {unit_code}",
                "Measure_ID": f"M{stt}" if stt and stt != "nan" else f"M-{idx+1}",
                "Measure_Desc": measure_desc,
                "Unit": "%",
                "Target": target_val,
                "Actual": actual_val,
                "Owner": unit_code,
                "Status": status if status != "nan" else "In Progress"
            })

        return pd.DataFrame(rows)

    def fetch_master_dataframe(self) -> pd.DataFrame:
        data_folder_id = self.config.onedrive.data_folder_id
        logger.info(f"Scanning DATA folder ID: {data_folder_id}")

        files = self.graph_client.list_files_in_folder_id(data_folder_id)
        if not files:
            logger.warning(f"No Excel files found in DATA folder ID: {data_folder_id}")
            return pd.DataFrame(columns=self.REQUIRED_COLUMNS + ["Unit_Code", "Source_File"])

        aggregated_dfs: List[pd.DataFrame] = []

        for f in files:
            file_name = f["name"]
            unit_code = os.path.splitext(file_name)[0].replace("P.", "").replace("pKHTH", "KHTH")

            try:
                file_bytes = self.graph_client.download_file_by_folder_id(data_folder_id, file_name)
                buffer = io.BytesIO(file_bytes)
                
                # Đọc thử file Excel (bỏ qua dòng tiêu đề phụ nếu có)
                df_raw = pd.read_excel(buffer, engine="openpyxl")

                # Tìm đúng dòng tiêu đề chứa 'Objects' hoặc 'Measure (KPI)'
                header_row = 0
                for r_idx in range(min(5, len(df_raw))):
                    row_vals = [str(v) for v in df_raw.iloc[r_idx].values]
                    if any("Objects" in v or "Measure" in v or "Goals" in v for v in row_vals):
                        header_row = r_idx + 1
                        break

                if header_row > 0:
                    buffer.seek(0)
                    df_raw = pd.read_excel(buffer, engine="openpyxl", header=header_row)

                df_transformed = self._transform_custom_excel(df_raw, unit_code)

                if not df_transformed.empty:
                    df_transformed["Unit_Code"] = unit_code
                    df_transformed["Source_File"] = file_name
                    aggregated_dfs.append(df_transformed)
                    logger.info(f"Transformed {file_name} successfully ({len(df_transformed)} KPIs)")

            except Exception as e:
                logger.error(f"Error reading file {file_name}: {e}")

        if not aggregated_dfs:
            return pd.DataFrame(columns=self.REQUIRED_COLUMNS + ["Unit_Code", "Source_File"])

        master_df = pd.concat(aggregated_dfs, ignore_index=True)
        return master_df

    def save_unit_dataframe(self, unit_file_name: str, df_unit: pd.DataFrame) -> bool:
        data_folder_id = self.config.onedrive.data_folder_id
        clean_df = df_unit.drop(columns=["Unit_Code", "Source_File"], errors="ignore")

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            clean_df.to_excel(writer, index=False, sheet_name="OGSM")

        buffer.seek(0)
        content = buffer.read()

        self.graph_client.upload_file_by_folder_id(data_folder_id, unit_file_name, content)
        return True

    def save_master_dataframe(self, df: pd.DataFrame) -> bool:
        raise NotImplementedError("Use save_unit_dataframe instead.")
