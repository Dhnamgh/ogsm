"""
OGSM Service - Đọc và chuẩn hóa dữ liệu báo cáo OGSM trực tiếp từ OneDrive.
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
        self.onedrive = None
        
        # Thử khởi tạo kết nối OneDrive gốc của dự án
        try:
            from onedrive_service import OneDriveService
            self.onedrive = OneDriveService()
        except Exception:
            try:
                from excel_repository import ExcelRepository
                self.onedrive = ExcelRepository()
            except Exception as e:
                logger.error(f"Lỗi khởi tạo OneDrive Service: {e}")

    def _normalize_df_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Hàm chuẩn hóa tiêu đề cột dữ liệu tránh lỗi hiển thị."""
        if df is None or df.empty:
            return df

        # Xóa khoảng trắng tiêu đề
        df.columns = [str(c).strip() for c in df.columns]

        # Ánh xạ tên cột linh hoạt
        for col in list(df.columns):
            c_low = col.lower()
            if any(k in c_low for k in ["objective_id", "stt_o", "mã o", "mục tiêu chiến lược"]):
                df.rename(columns={col: "Objective_ID"}, inplace=True)
            elif any(k in c_low for k in ["goal_id", "strategy_id", "stt_g", "stt_s", "mã g", "mã s"]):
                df.rename(columns={col: "Goal_ID"}, inplace=True)
            elif any(k in c_low for k in ["measure_id", "stt_m", "mã m", "mã kpi", "measure", "kpi"]):
                df.rename(columns={col: "Measure_ID"}, inplace=True)
            elif any(k in c_low for k in ["status", "trạng thái", "tiến độ", "đánh giá"]):
                df.rename(columns={col: "Status"}, inplace=True)

        if "Status" not in df.columns:
            df["Status"] = "Chưa đến hạn"

        return df

    def get_full_ogsm_data(self) -> pd.DataFrame:
        """Tải dữ liệu từ OneDrive và chuẩn hóa toàn bộ cột."""
        all_dfs = []

        # 1. Đọc trực tiếp từ OneDrive Service
        if self.onedrive:
            try:
                if hasattr(self.onedrive, "get_all_excel_data"):
                    raw_dfs = self.onedrive.get_all_excel_data()
                    if raw_dfs:
                        for df in raw_dfs:
                            if isinstance(df, pd.DataFrame) and not df.empty:
                                norm_df = self._normalize_df_columns(df)
                                all_dfs.append(norm_df)
                        
                        if all_dfs:
                            return pd.concat(all_dfs, ignore_index=True)

                if hasattr(self.onedrive, "download_all_files"):
                    self.onedrive.download_all_files(self.data_folder)
            except Exception as e:
                logger.error(f"Lỗi truy xuất dữ liệu từ OneDrive: {e}")

        # 2. Đọc từ thư mục cục bộ nếu đã sync file về
        if self.data_folder.exists():
            excel_files = list(self.data_folder.glob("*.xlsx")) + list(self.data_folder.glob("**/*.xlsx"))
            for file_path in excel_files:
                if file_path.name.startswith("~$") or "TEMPLATE" in file_path.name.upper():
                    continue
                try:
                    df = pd.read_excel(file_path, engine="openpyxl")
                    if not df.empty:
                        df = self._normalize_df_columns(df)
                        if "Unit_Code" not in df.columns:
                            df["Unit_Code"] = file_path.stem.replace(".xlsx", "").strip()
                        all_dfs.append(df)
                except Exception as e:
                    logger.error(f"Lỗi đọc file {file_path.name}: {e}")

        if all_dfs:
            return pd.concat(all_dfs, ignore_index=True)

        return pd.DataFrame()
