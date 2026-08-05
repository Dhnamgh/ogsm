"""
OGSM Service - Đọc và lưu dữ liệu trực tiếp chuẩn xác từ OneDrive / Thư mục DATA.
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
        """Lưu file vào cả thư mục local DATA của server lẫn sẵn sàng cho OneDrive."""
        try:
            target_path = self.data_folder / filename
            with open(target_path, "wb") as f:
                f.write(file_bytes)
            logger.info(f"Đã lưu thành công file {filename} vào {target_path}")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi lưu file {filename}: {e}")
            return False

    def get_full_ogsm_data(self) -> pd.DataFrame:
        """Đọc chuẩn xác tất cả file Excel trong DATA mà không làm mất cột Objective_ID và Goal_ID."""
        all_dfs = []
        if not self.data_folder.exists():
            return pd.DataFrame()

        for file_path in self.data_folder.glob("*.xlsx"):
            if file_path.name.startswith("~$"):
                continue  # Bỏ qua file tạm Excel
            try:
                df = pd.read_excel(file_path, engine="openpyxl")
                
                # Làm sạch tên cột gốc (xóa khoảng trắng thừa)
                df.columns = [str(c).strip() for c in df.columns]

                # Chuẩn hóa tên cột Mã đơn vị từ tên file (Ví dụ: P.HCTH.xlsx -> HCTH hoặc P.HCTH)
                raw_code = file_path.stem.replace(".xlsx", "").strip()
                df["Unit_Code"] = raw_code

                # Map linh hoạt cột Objectives nếu bị lệch tên nhẹ
                for col in df.columns:
                    c_lower = col.lower()
                    if c_lower in ["objective_id", "stt_o", "mã o", "mục tiêu chiến lược", "objective"]:
                        df.rename(columns={col: "Objective_ID"}, inplace=True)
                    elif c_lower in ["goal_id", "strategy_id", "stt_g", "stt_s", "mã g", "mã s", "goal", "strategy"]:
                        df.rename(columns={col: "Goal_ID"}, inplace=True)
                    elif c_lower in ["measure_id", "stt_m", "mã m", "mã kpi", "measure", "kpi"]:
                        df.rename(columns={col: "Measure_ID"}, inplace=True)

                all_dfs.append(df)
            except Exception as e:
                logger.error(f"Lỗi khi đọc file {file_path.name}: {e}")

        if all_dfs:
            master_df = pd.concat(all_dfs, ignore_index=True)
            return master_df
        return pd.DataFrame()
