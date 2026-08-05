"""
OGSM Service - Tự động tải và đọc toàn bộ file Excel báo cáo từ OneDrive.
"""

import os
from pathlib import Path
import pandas as pd
from logger import get_logger

logger = get_logger()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "DATA"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class OGSMService:
    def __init__(self, data_folder: Path = DATA_DIR):
        self.data_folder = data_folder
        self.data_folder.mkdir(parents=True, exist_ok=True)
        
        # Khởi tạo kết nối OneDrive Service gốc của dự án
        self.onedrive = None
        try:
            from onedrive_service import OneDriveService
            self.onedrive = OneDriveService()
        except Exception as e:
            try:
                from excel_repository import ExcelRepository
                self.onedrive = ExcelRepository()
            except Exception as ex:
                logger.error(f"Không thể khởi tạo kết nối OneDrive: {ex}")

    def upload_unit_file(self, filename: str, file_bytes: bytes) -> bool:
        """Upload file lên OneDrive và lưu thư mục đệm."""
        try:
            target_path = self.data_folder / filename
            with open(target_path, "wb") as f:
                f.write(file_bytes)

            if self.onedrive and hasattr(self.onedrive, "upload_file"):
                self.onedrive.upload_file(filename, file_bytes)

            return True
        except Exception as e:
            logger.error(f"Lỗi khi upload file {filename}: {e}")
            return False

    def get_full_ogsm_data(self) -> pd.DataFrame:
        """Đọc toàn bộ file báo cáo Excel từ OneDrive."""
        all_dfs = []

        # 1. Ưu tiên đọc trực tiếp từ dịch vụ OneDrive nếu có
        if self.onedrive:
            try:
                # Nếu dịch vụ OneDrive có hàm đọc tất cả file
                if hasattr(self.onedrive, "get_all_excel_data"):
                    all_dfs = self.onedrive.get_all_excel_data()
                    if all_dfs:
                        master_df = pd.concat(all_dfs, ignore_index=True)
                        return master_df
                
                # Nếu dịch vụ OneDrive có hàm download file về thư mục đệm DATA
                if hasattr(self.onedrive, "download_all_files"):
                    self.onedrive.download_all_files(self.data_folder)
            except Exception as e:
                logger.error(f"Lỗi khi truy xuất dữ liệu từ OneDrive: {e}")

        # 2. Đọc tất cả file Excel hiện có trong thư mục DATA (bỏ qua file OGSM_TEMPLATE mẫu)
        excel_files = list(self.data_folder.glob("*.xlsx")) + list(self.data_folder.glob("**/*.xlsx"))

        for file_path in excel_files:
            # Bỏ qua file tạm của Excel và file Template mẫu
            if file_path.name.startswith("~$") or "TEMPLATE" in file_path.name.upper():
                continue

            try:
                df = pd.read_excel(file_path, engine="openpyxl")
                if df.empty:
                    continue

                # Làm sạch tên cột
                df.columns = [str(c).strip() for c in df.columns]

                # Ánh xạ tên cột chuẩn
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
