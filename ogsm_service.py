"""
OGSM Service - Quản lý nạp, tổng hợp, chuẩn hóa và lưu trữ dữ liệu báo cáo OGSM.
Sửa triệt để lỗi Duplicate column names.
"""

import os
import io
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
        Chuẩn hóa tên cột không gây trùng lặp (Avoid duplicate column names).
        """
        new_cols = []
        seen_cols = set()

        for col in df.columns:
            col_clean = str(col).strip().lower()
            mapped_name = str(col).strip()

            if any(k in col_clean for k in ["objective_id", "mã o", "mục tiêu chiến lược", "objective"]):
                mapped_name = "Objective_ID"
            elif any(k in col_clean for k in ["goal_id", "strategy_id", "mã g", "mã s", "chỉ tiêu", "chiến lược", "goal", "strategy"]):
                mapped_name = "Goal_ID"
            elif any(k in col_clean for k in ["measure_id", "mã m", "mã kpi", "measure", "kpi"]):
                mapped_name = "Measure_ID"
            elif any(k in col_clean for k in ["measure_desc", "nội dung", "mô tả", "biện pháp"]):
                mapped_name = "Measure_Desc"
            elif any(k in col_clean for k in ["target_year", "năm hoàn thành", "năm", "thời gian"]):
                mapped_name = "Target_Year"
            elif any(k in col_clean for k in ["target", "chỉ tiêu giao", "mục tiêu đặt ra"]):
                mapped_name = "Target"
            elif any(k in col_clean for k in ["actual", "thực hiện", "kết quả", "đạt được", "tỷ lệ đạt"]):
                mapped_name = "Actual"
            elif any(k in col_clean for k in ["status", "trạng thái", "tiến độ"]):
                mapped_name = "Status"

            # Đảm bảo không tạo tên cột trùng
            if mapped_name in seen_cols:
                suffix = 1
                while f"{mapped_name}_{suffix}" in seen_cols:
                    suffix += 1
                mapped_name = f"{mapped_name}_{suffix}"

            seen_cols.add(mapped_name)
            new_cols.append(mapped_name)

        df.columns = new_cols

        # Đảm bảo các cột tối thiểu bắt buộc
        for c in ["Unit_Code", "Objective_ID", "Goal_ID", "Measure_ID", "Measure_Desc", "Target", "Actual", "Status", "Target_Year"]:
            if c not in df.columns:
                df[c] = ""

        return df

    def get_full_ogsm_data(self) -> pd.DataFrame:
        """Đọc tất cả file Excel trong thư mục DATA và tổng hợp an toàn."""
        all_dfs = []
        if not self.data_folder.exists():
            return pd.DataFrame()

        for file_path in self.data_folder.glob("*.xlsx"):
            if file_path.name.startswith("~$"):
                continue  # Bỏ qua file tạm của Excel
            try:
                df = pd.read_excel(file_path, engine="openpyxl")
                unit_code = file_path.stem.replace(".xlsx", "").strip()

                df = self._normalize_columns(df)
                df["Unit_Code"] = unit_code

                # Chỉ lấy các cột duy nhất nếu có trùng lặp cột ngoài ý muốn
                df = df.loc[:, ~df.columns.duplicated()]

                all_dfs.append(df)
            except Exception as e:
                logger.error(f"Lỗi khi xử lý file {file_path.name}: {e}")

        if all_dfs:
            master_df = pd.concat(all_dfs, ignore_index=True)
            return master_df
        return pd.DataFrame()
