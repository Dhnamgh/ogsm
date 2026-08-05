"""
OGSM Service - Quản lý nạp, tổng hợp, chuẩn hóa và lưu trữ dữ liệu báo cáo OGSM.
"""

import os
import io
import re
from pathlib import Path
import pandas as pd
from logger import get_logger

logger = get_logger()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "DATA"

if not DATA_DIR.exists():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


class OGSMService:
    def __init__(self, data_folder: Path = DATA_DIR):
        self.data_folder = data_folder

    def upload_unit_file(self, filename: str, file_bytes: bytes) -> bool:
        """Lưu hoặc ghi đè file báo cáo Excel của đơn vị vào thư mục DATA."""
        try:
            target_path = self.data_folder / filename
            with open(target_path, "wb") as f:
                f.write(file_bytes)
            logger.info(f"Đã lưu thành công file {filename} vào {target_path}")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi lưu file {filename}: {e}")
            return False

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Tự động ánh xạ tên cột trong Excel (dù tiếng Anh hay tiếng Việt) về tên cột chuẩn.
        """
        column_mapping = {}
        for col in df.columns:
            col_clean = str(col).strip().lower()
            
            # Map Objective
            if any(k in col_clean for k in ["objective_id", "mục tiêu", "objective", "stt_o", "mã o"]):
                column_mapping[col] = "Objective_ID"
            # Map Goal
            elif any(k in col_clean for k in ["goal_id", "chỉ tiêu", "goal", "stt_g", "mã g"]):
                column_mapping[col] = "Goal_ID"
            # Map Measure_ID
            elif any(k in col_clean for k in ["measure_id", "mã kpi", "mã measure", "kpi_id", "stt_m"]):
                column_mapping[col] = "Measure_ID"
            # Map Measure_Desc
            elif any(k in col_clean for k in ["measure_desc", "nội dung", "mô tả", "biện pháp", "measure", "kpi"]):
                column_mapping[col] = "Measure_Desc"
            # Map Target
            elif any(k in col_clean for k in ["target", "chỉ tiêu giao", "mục tiêu đặt ra", "kế hoạch"]):
                column_mapping[col] = "Target"
            # Map Actual
            elif any(k in col_clean for k in ["actual", "thực hiện", "kết quả", "đạt được", "tỷ lệ đạt"]):
                column_mapping[col] = "Actual"
            # Map Status
            elif any(k in col_clean for k in ["status", "trạng thái", "tiến độ", "đánh giá"]):
                column_mapping[col] = "Status"
            # Map Target_Year
            elif any(k in col_clean for k in ["target_year", "năm hoàn thành", "năm", "thời gian"]):
                column_mapping[col] = "Target_Year"

        df = df.rename(columns=column_mapping)

        # Đảm bảo đủ các cột chuẩn, thiếu cột nào sẽ điền chuỗi rỗng
        required_cols = [
            "Unit_Code", "Objective_ID", "Goal_ID", "Measure_ID", 
            "Measure_Desc", "Target", "Actual", "Status", "Target_Year"
        ]
        for c in required_cols:
            if c not in df.columns:
                df[c] = ""

        return df

    def get_full_ogsm_data(self) -> pd.DataFrame:
        """Đọc tất cả các file Excel (.xlsx) trong thư mục DATA và chuẩn hóa dữ liệu."""
        all_dfs = []
        if not self.data_folder.exists():
            return pd.DataFrame()

        for file_path in self.data_folder.glob("*.xlsx"):
            if file_path.name.startswith("~$"):
                continue  # Bỏ qua file tạm Excel
            try:
                df = pd.read_excel(file_path, engine="openpyxl")
                unit_code = file_path.stem.replace(".xlsx", "").strip()

                # Đưa về cột chuẩn
                df = self._normalize_columns(df)
                df["Unit_Code"] = unit_code

                all_dfs.append(df)
            except Exception as e:
                logger.error(f"Không thể đọc file {file_path.name}: {e}")

        if all_dfs:
            master_df = pd.concat(all_dfs, ignore_index=True)
            return master_df
        return pd.DataFrame()
