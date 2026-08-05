"""
OGSM Service - Tự động kết nối dịch vụ OneDrive và tổng hợp dữ liệu OGSM.
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
        if not self.data_folder.exists():
            self.data_folder.mkdir(parents=True, exist_ok=True)

    def get_full_ogsm_data(self) -> pd.DataFrame:
        """Đọc và tổng hợp toàn bộ file dữ liệu OGSM từ hệ thống."""
        all_dfs = []

        # 1. Thử gọi dịch vụ kết nối OneDrive sẵn có của hệ thống
        try:
            from onedrive_service import OneDriveService
            svc = OneDriveService()
            if hasattr(svc, "get_all_excel_data"):
                data = svc.get_all_excel_data()
                if isinstance(data, pd.DataFrame) and not data.empty:
                    return data
                elif isinstance(data, list) and len(data) > 0:
                    return pd.concat(data, ignore_index=True)
        except Exception as e:
            logger.debug(f"Không gọi được OneDriveService: {e}")

        # 2. Quét thư mục dữ liệu đồng bộ
        excel_files = list(self.data_folder.glob("*.xlsx")) + list(self.data_folder.glob("**/*.xlsx"))
        if not excel_files:
            excel_files = [f for f in BASE_DIR.glob("**/*.xlsx") if "TEMPLATE" not in f.name.upper()]

        for file_path in excel_files:
            if file_path.name.startswith("~$") or "TEMPLATE" in file_path.name.upper():
                continue
            try:
                df = pd.read_excel(file_path, engine="openpyxl")
                if df.empty:
                    continue

                df.columns = [str(c).strip() for c in df.columns]

                # Chuẩn hóa tên cột
                for col in list(df.columns):
                    c_low = col.lower()
                    if any(k in c_low for k in ["objective_id", "stt_o", "mã o", "mục tiêu chiến lược"]):
                        df.rename(columns={col: "Objective_ID"}, inplace=True)
                    elif any(k in c_low for k in ["goal_id", "strategy_id", "stt_g", "stt_s", "mã g", "mã s"]):
                        df.rename(columns={col: "Goal_ID"}, inplace=True)
                    elif any(k in c_low for k in ["measure_id", "stt_m", "mã m", "mã kpi", "measure"]):
                        df.rename(columns={col: "Measure_ID"}, inplace=True)
                    elif any(k in c_low for k in ["status", "trạng thái", "tiến độ", "đánh giá"]):
                        df.rename(columns={col: "Status"}, inplace=True)

                if "Status" not in df.columns:
                    df["Status"] = "Chưa đến hạn"

                unit_code = file_path.stem.replace(".xlsx", "").strip()
                df["Unit_Code"] = unit_code

                all_dfs.append(df)
            except Exception as e:
                logger.error(f"Lỗi đọc file {file_path.name}: {e}")

        if all_dfs:
            return pd.concat(all_dfs, ignore_index=True)

        return pd.DataFrame()
