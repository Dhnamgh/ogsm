"""
OGSM Service - Đọc chính xác 29 file Excel trong thư mục DATA.
Chuẩn hóa tiêu đề cột tránh lỗi 'Status' và đếm thiếu chỉ số.
"""

import os
from pathlib import Path
import pandas as pd
from logger import get_logger

logger = get_logger()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "DATA"


class OGSMService:
    def __init__(self, data_folder: Path = DATA_DIR):
        self.data_folder = data_folder

    def upload_unit_file(self, filename: str, file_bytes: bytes) -> bool:
        try:
            if not self.data_folder.exists():
                self.data_folder.mkdir(parents=True, exist_ok=True)
            target_path = self.data_folder / filename
            with open(target_path, "wb") as f:
                f.write(file_bytes)
            logger.info(f"Đã lưu file {filename}")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi lưu file {filename}: {e}")
            return False

    def get_full_ogsm_data(self) -> pd.DataFrame:
        all_dfs = []

        # Chỉ quét các file .xlsx nằm TRỰC TIẾP trong thư mục DATA
        if not self.data_folder.exists():
            return pd.DataFrame()

        excel_files = list(self.data_folder.glob("*.xlsx"))

        for file_path in excel_files:
            if file_path.name.startswith("~$"):
                continue  # Bỏ qua file tạm Excel
            try:
                df = pd.read_excel(file_path, engine="openpyxl")
                if df.empty:
                    continue

                # Chuẩn hóa tên cột
                df.columns = [str(c).strip() for c in df.columns]

                # Ánh xạ tên cột linh hoạt về cột chuẩn
                for col in list(df.columns):
                    c_low = col.lower()
                    if any(k in c_low for k in ["objective_id", "stt_o", "mã o", "mục tiêu chiến lược", "objective"]):
                        df.rename(columns={col: "Objective_ID"}, inplace=True)
                    elif any(k in c_low for k in ["goal_id", "strategy_id", "stt_g", "stt_s", "mã g", "mã s", "goal"]):
                        df.rename(columns={col: "Goal_ID"}, inplace=True)
                    elif any(k in c_low for k in ["measure_id", "stt_m", "mã m", "mã kpi", "measure", "kpi"]):
                        df.rename(columns={col: "Measure_ID"}, inplace=True)
                    elif any(k in c_low for k in ["status", "trạng thái", "tiến độ", "đánh giá"]):
                        df.rename(columns={col: "Status"}, inplace=True)

                # Bổ sung cột Status nếu thiếu
                if "Status" not in df.columns:
                    df["Status"] = "Chưa đến hạn"

                # Mã đơn vị
                unit_code = file_path.stem.replace(".xlsx", "").strip()
                df["Unit_Code"] = unit_code

                all_dfs.append(df)
            except Exception as e:
                logger.error(f"Lỗi khi đọc file {file_path.name}: {e}")

        if all_dfs:
            master_df = pd.concat(all_dfs, ignore_index=True)
            return master_df

        return pd.DataFrame()
