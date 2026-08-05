"""
OGSM Service - Quản lý nạp và tổng hợp dữ liệu báo cáo OGSM.
Tự động đồng bộ file từ OneDrive về thư mục đệm DATA trước khi xử lý.
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
DATA_DIR.mkdir(parents=True, exist_ok=True)


class OGSMService:
    def __init__(self, data_folder: Path = DATA_DIR):
        self.data_folder = data_folder
        self.data_folder.mkdir(parents=True, exist_ok=True)
        
        # Kết nối với dịch vụ OneDrive nếu có trong dự án
        self.onedrive_service = None
        try:
            from onedrive_service import OneDriveService
            self.onedrive_service = OneDriveService()
        except Exception:
            try:
                from excel_repository import ExcelRepository
                self.onedrive_service = ExcelRepository()
            except Exception:
                pass

    def sync_from_onedrive(self):
        """Tải/Đồng bộ lại toàn bộ file Excel từ OneDrive về thư mục DATA."""
        if self.onedrive_service and hasattr(self.onedrive_service, "download_all_files"):
            try:
                self.onedrive_service.download_all_files(self.data_folder)
            except Exception as e:
                logger.error(f"Lỗi khi đồng bộ file từ OneDrive: {e}")

    def upload_unit_file(self, filename: str, file_bytes: bytes) -> bool:
        """Ghi file vào thư mục DATA đệm và tải lên OneDrive."""
        try:
            target_path = self.data_folder / filename
            with open(target_path, "wb") as f:
                f.write(file_bytes)

            if self.onedrive_service and hasattr(self.onedrive_service, "upload_file"):
                self.onedrive_service.upload_file(filename, file_bytes)

            return True
        except Exception as e:
            logger.error(f"Lỗi khi upload file {filename}: {e}")
            return False

    def get_full_ogsm_data(self) -> pd.DataFrame:
        """Tải dữ liệu từ OneDrive (nếu thư mục rỗng) và nạp toàn bộ dữ liệu Excel."""
        # 1. Thử đồng bộ dữ liệu từ OneDrive nếu thư mục local chưa có file
        excel_files = list(self.data_folder.glob("*.xlsx"))
        if not excel_files and self.onedrive_service:
            self.sync_from_onedrive()
            excel_files = list(self.data_folder.glob("*.xlsx"))

        # 2. Đọc và gộp tất cả các file Excel
        all_dfs = []
        for file_path in excel_files:
            if file_path.name.startswith("~$"):
                continue  # Bỏ qua file tạm Excel
            try:
                df = pd.read_excel(file_path, engine="openpyxl")
                if df.empty:
                    continue

                # Làm sạch khoảng trắng tiêu đề cột
                df.columns = [str(c).strip() for c in df.columns]

                # Mã đơn vị lấy chính xác từ tên file Excel
                unit_code = file_path.stem.replace(".xlsx", "").strip()
                df["Unit_Code"] = unit_code

                all_dfs.append(df)
            except Exception as e:
                logger.error(f"Lỗi khi đọc file {file_path.name}: {e}")

        if all_dfs:
            master_df = pd.concat(all_dfs, ignore_index=True)
            return master_df

        return pd.DataFrame()
