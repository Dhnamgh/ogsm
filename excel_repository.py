"""
OpenPyXL and Pandas Excel Repository handling OGSM Matrix Structure.
Correctly maps UMP Standard Objectives (O1-O5) and Goals (1.1-5.3).
"""

import io
import os
import re
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

    def _get_objective_id(self, no_val: str, obj_title: str) -> str:
        """Ánh xạ đúng 5 Objectives chuẩn của UMP (O1 đến O5)."""
        no_str = str(no_val).upper().strip()
        if "O1" in no_str: return "O1"
        if "O2" in no_str: return "O2"
        if "O3" in no_str: return "O3"
        if "O4" in no_str: return "O4"
        if "O5" in no_str: return "O5"

        obj_lower = str(obj_title).lower()
        if "giáo dục" in obj_lower: return "O1"
        if "nghiên cứu" in obj_lower: return "O2"
        if "phục vụ cộng đồng" in obj_lower: return "O3"
        if "trí tuệ nhân tạo" in obj_lower or "ai" in obj_lower: return "O4"
        if "quản trị đại học" in obj_lower: return "O5"
        
        return "O_OTHER"

    def _transform_custom_excel(self, df: pd.DataFrame, unit_code: str) -> pd.DataFrame:
        """Bóc tách dữ liệu chuẩn UMP OGSM."""
        df.columns = [str(c).strip() for c in df.columns]

        rows = []
        for idx, row in df.iterrows():
            measure_desc = str(row.get("Measure (KPI)", "")).strip() if pd.notna(row.get("Measure (KPI)")) else ""
            if not measure_desc or measure_desc == "nan":
                continue  # Bỏ qua dòng không có KPI

            no_val = str(row.get("No", "")).strip() if pd.notna(row.get("No")) else ""
            obj_title = str(row.get("Objects", "")).strip() if pd.notna(row.get("Objects")) else "Mục tiêu UMP"
            
            # Chuẩn hóa Objective_ID về đúng O1, O2, O3, O4, O5
            obj_id = self._get_objective_id(no_val, obj_title)

            # Bóc tách Goals UMP
            goal_ump = str(row.get("Goals UMP", "")).strip() if pd.notna(row.get("Goals UMP")) else ""
            goal_hcth = str(row.get("Goals HCTH", "")).strip() if pd.notna(row.get("Goals HCTH")) else ""
            goal_desc = goal_ump if goal_ump and goal_ump != "nan" else (goal_hcth if goal_hcth != "nan" else obj_title)

            # Trích xuất mã Goal ID (ví dụ: 1.1, 1.2, 2.1...)
            goal_match = re.search(r"^(\d+\.\d+)", goal_desc)
            goal_id = f"G_{goal_match.group(1)}" if goal_match else f"G_{obj_id}_{idx+1}"

            # Bóc tách STT & Trạng thái
            stt = str(row.get("STT", idx + 1)).strip()
            status = str(row.get("Trạng thái", "In Progress")).strip() if pd.notna(row.get("Trạng thái")) else "In Progress"
            
            actual_val = row.get("Tỷ lệ đạt (%)", 0.0)
            try:
                actual_val = float(str(actual_val).replace("%", "").strip())
            except Exception:
                actual_val = 0.0

            target_val = 100.0
            if "2026" in row and pd.notna(row["2026"]):
                try:
                    target_val = float(str(row["2026"]).replace("%", "").strip())
                except Exception:
                    target_val = 100.0

            rows.append({
                "Objective_ID": obj_id,
                "Objective_Title": obj_title,
                "Goal_ID": goal_id,
                "Goal_Desc": goal_desc,
                "Strategy_ID": f"S_{unit_code}_{idx+1}",
                "Strategy_Desc": f"Chiến lược thực thi {unit_code}",
                "Measure_ID": f"{unit_code}_M{stt}",
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
        files = self.graph_client.list_files_in_folder_id(data_folder_id)
        if not files:
            return pd.DataFrame(columns=self.REQUIRED_COLUMNS + ["Unit_Code", "Source_File"])

        aggregated_dfs: List[pd.DataFrame] = []

        for f in files:
            file_name = f["name"]
            unit_code = os.path.splitext(file_name)[0].replace("P.", "").replace("pKHTH", "KHTH")

            try:
                file_bytes = self.graph_client.download_file_by_folder_id(data_folder_id, file_name)
                buffer = io.BytesIO(file_bytes)
                df_raw = pd.read_excel(buffer, engine="openpyxl")

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

            except Exception as e:
                logger.error(f"Lỗi đọc file {file_name}: {e}")

        if not aggregated_dfs:
            return pd.DataFrame(columns=self.REQUIRED_COLUMNS + ["Unit_Code", "Source_File"])

        return pd.concat(aggregated_dfs, ignore_index=True)

    def save_unit_dataframe(self, unit_file_name: str, df_unit: pd.DataFrame) -> bool:
        data_folder_id = self.config.onedrive.data_folder_id
        clean_df = df_unit.drop(columns=["Unit_Code", "Source_File"], errors="ignore")

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            clean_df.to_excel(writer, index=False, sheet_name="OGSM")

        buffer.seek(0)
        self.graph_client.upload_file_by_folder_id(data_folder_id, unit_file_name, buffer.read())
        return True

    def save_master_dataframe(self, df: pd.DataFrame) -> bool:
        raise NotImplementedError("Use save_unit_dataframe instead.")
