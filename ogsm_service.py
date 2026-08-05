"""
OGSM Service - Tự động tìm và đọc toàn bộ tệp Excel dữ liệu OGSM.
"""

import os
from pathlib import Path
import pandas as pd
from logger import get_logger

logger = get_logger()

BASE_DIR = Path(__file__).resolve().parent


class OGSMService:
    def __init__(self, data_folder: Path = None):
        if data_folder is None:
            found_dir = None
            for p in BASE_DIR.glob("*"):
                if p.is_dir() and p.name.lower() == "data":
                    found_dir = p
                    break
            self.data_folder = found_dir if found_dir else (BASE_DIR / "DATA")
        else:
            self.data_folder = data_folder

        if not self.data_folder.exists():
            self.data_folder.mkdir(parents=True, exist_ok=True)

    def upload_unit_file(self, filename: str, file_bytes: bytes) -> bool:
        try:
            target_path = self.data_folder / filename
            with open(target_path, "wb") as f:
                f.write(file_bytes)
            logger.info(f"Đã lưu thành công file {filename}")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi lưu file {filename}: {e}")
            return False

    def get_full_ogsm_data(self) -> pd.DataFrame:
        all_dfs = []

        excel_files = list(self.data_folder.glob("*.xlsx")) + list(self.data_folder.glob("**/*.xlsx"))
        if not excel_files:
            excel_files = list(BASE_DIR.glob("**/*.xlsx"))

        for file_path in excel_files:
            if file_path.name.startswith("~$"):
                continue
            try:
                df = pd.read_excel(file_path, engine="openpyxl")
                if df.empty:
                    continue

                df.columns = [str(c).strip() for c in df.columns]

                for col in list(df.columns):
                    c_low = col.lower()
                    if any(k in c_low for k in ["objective_id", "stt_o", "mã o", "mục tiêu chiến lược", "objective"]):
                        df.rename(columns={col: "Objective_ID"}, inplace=True)
                    elif any(k in c_low for k in ["goal_id", "strategy_id", "stt_g", "stt_s", "mã g", "mã s", "goal", "strategy"]):
                        df.rename(columns={col: "Goal_ID"}, inplace=True)
                    elif any(k in c_low for k in ["measure_id", "stt_m", "mã m", "mã kpi", "measure", "kpi"]):
                        df.rename(columns={col: "Measure_ID"}, inplace=True)
                    elif any(k in c_low for k in ["status", "trạng thái", "tiến độ", "đánh giá"]):
                        df.rename(columns={col: "Status"}, inplace=True)

                if "Status" not in df.columns:
                    df["Status"] = "Chưa đến hạn"

                unit_code = file_path.stem.replace(".xlsx", "").strip()
                df["Unit_Code"] = unit_code

                all_dfs.append(df)
            except Exception as e:
                logger.error(f"Lỗi khi đọc file {file_path.name}: {e}")

        if all_dfs:
            master_df = pd.concat(all_dfs, ignore_index=True)
            return master_df

        return pd.DataFrame()
