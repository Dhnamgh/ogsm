"""
OpenPyXL and Pandas Excel Repository matching official 29 UMP Units.
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

    def _clean_unit_code(self, file_name: str) -> str:
        """Chuẩn hóa tên file thành đúng Mã đơn vị trong bảng 29 đơn vị."""
        base_name = os.path.splitext(file_name)[0].strip()
        
        # Bảng ánh xạ linh hoạt tên file cũ sang mã đơn vị chuẩn
        mapping = {
            "P.QTGT": "P.QTGT", "P.QT": "P.QTGT",
            "PK.RHM": "PKCK RHM", "PKCK RHM": "PKCK RHM",
            "T.DƯỢC": "T.DƯỢC", "T.DUOC": "T.DƯỢC", "K.DUOC": "T.DƯỢC",
            "TT.KCXN": "TT.KCCLXN", "TT.KCCLXN": "TT.KCCLXN",
            "THƯ VIỆN": "THƯ VIỆN", "TV": "THƯ VIỆN",
            "BV.ĐHYD": "BV ĐHYD", "BV ĐHYD": "BV ĐHYD"
        }
        
        return mapping.get(base_name, base_name)

    def _get_objective_id(self, obj_title: str) -> str:
        obj_lower = str(obj_title).lower()
        if "giáo dục" in obj_lower: return "O1"
        if "nghiên cứu" in obj_lower: return "O2"
        if "phục vụ cộng đồng" in obj_lower: return "O3"
        if "trí tuệ nhân tạo" in obj_lower or "ai" in obj_lower: return "O4"
        if "quản trị đại học" in obj_lower: return "O5"
        return "O1"

    def _get_goal_id_by_text(self, text: str) -> str:
        t = text.lower()
        if "kiểm định" in t or "1.1" in t: return "1.1"
        if "đối sánh" in t or "1.2" in t: return "1.2"
        if "chương trình quốc tế" in t or "trao đổi sinh viên" in t or "1.3" in t: return "1.3"
        if "nhóm nghiên cứu mạnh" in t or "2.1" in t: return "2.1"
        if "bài báo quốc tế" in t or "2.2" in t: return "2.2"
        if "chuyển giao kỹ thuật" in t or "tnhh 1 thành viên" in t or "2.3" in t: return "2.3"
        if "kiểu mẫu" in t or "3.1" in t: return "3.1"
        if "đào tạo liên tục" in t or "3.2" in t: return "3.2"
        if "một cổng" in t or "3.3" in t: return "3.3"
        if "20% số học phần" in t or "4.1" in t: return "4.1"
        if "50 đề tài" in t or "4.2" in t: return "4.2"
        if "hành chính và quản trị" in t or "4.3" in t: return "4.3"
        if "nguồn lực tài chính" in t or "10%/ năm" in t or "5.1" in t: return "5.1"
        if "văn hoá ump" in t or "5.2" in t: return "5.2"
        if "erp" in t or "chuyển đổi số" in t or "5.3" in t: return "5.3"
        return "OTHER_GOAL"

    def _transform_custom_excel(self, df: pd.DataFrame, unit_code: str) -> pd.DataFrame:
        df.columns = [str(c).strip() for c in df.columns]

        rows = []
        for idx, row in df.iterrows():
            measure_desc = str(row.get("Measure (KPI)", "")).strip() if pd.notna(row.get("Measure (KPI)")) else ""
            if not measure_desc or measure_desc == "nan":
                continue

            obj_title = str(row.get("Objects", "")).strip() if pd.notna(row.get("Objects")) else "Mục tiêu UMP"
            obj_id = self._get_objective_id(obj_title)

            goal_ump = str(row.get("Goals UMP", "")).strip() if pd.notna(row.get("Goals UMP")) else ""
            goal_desc = goal_ump if goal_ump and goal_ump != "nan" else obj_title
            strat_code = self._get_goal_id_by_text(goal_desc)

            target_yr = row.get("Năm đích", 2029)

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
                "Goal_ID": f"G_{strat_code}",
                "Goal_Desc": goal_desc,
                "Strategy_ID": f"S_{strat_code}",
                "Strategy_Desc": goal_desc,
                "Measure_ID": f"{unit_code}_M{stt}",
                "Measure_Desc": measure_desc,
                "Unit": "%",
                "Target": target_val,
                "Actual": actual_val,
                "Owner": unit_code,
                "Status": status if status != "nan" else "In Progress",
                "Target_Year": target_yr if pd.notna(target_yr) else 2029
            })

        return pd.DataFrame(rows)

    def fetch_master_dataframe(self) -> pd.DataFrame:
        data_folder_id = self.config.onedrive.data_folder_id
        files = self.graph_client.list_files_in_folder_id(data_folder_id)
        if not files:
            return pd.DataFrame(columns=self.REQUIRED_COLUMNS + ["Unit_Code", "Source_File", "Target_Year"])

        aggregated_dfs: List[pd.DataFrame] = []

        for f in files:
            file_name = f["name"]
            unit_code = self._clean_unit_code(file_name)

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
