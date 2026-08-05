"""
OGSM Service - Quản lý nạp, tổng hợp và lưu trữ dữ liệu báo cáo OGSM.
Khôi phục cơ chế lưu/đọc file trực tiếp trên Streamlit Cloud, tự động khôi phục cấu trúc O, G, M.
"""

import os
import io
from pathlib import Path
import pandas as pd
from logger import get_logger

logger = get_logger()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "DATA"

# Tự động tạo thư mục DATA nếu chưa có
DATA_DIR.mkdir(parents=True, exist_ok=True)


class OGSMService:
    def __init__(self, data_folder: Path = DATA_DIR):
        self.data_folder = data_folder
        self.data_folder.mkdir(parents=True, exist_ok=True)

    def upload_unit_file(self, filename: str, file_bytes: bytes) -> bool:
        """Ghi đè hoặc tạo mới file báo cáo Excel vào thư mục DATA trên hệ thống."""
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
        """Đọc và tổng hợp tất cả các file Excel hiện có trong thư mục DATA."""
        all_dfs = []
        if not self.data_folder.exists():
            return pd.DataFrame()

        # Quét tất cả file .xlsx trong DATA
        excel_files = list(self.data_folder.glob("*.xlsx"))

        for file_path in excel_files:
            if file_path.name.startswith("~$"):
                continue  # Bỏ qua file tạm Excel
            try:
                df = pd.read_excel(file_path, engine="openpyxl")
                if df.empty:
                    continue

                # Làm sạch tên cột
                df.columns = [str(c).strip() for c in df.columns]

                # Gán mã đơn vị từ tên file
                unit_code = file_path.stem.replace(".xlsx", "").strip()
                df["Unit_Code"] = unit_code

                # Ánh xạ tên cột chuẩn mà không xoá dữ liệu gốc
                for col in list(df.columns):
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
