"""
OGSM Service - Quản lý nạp và tổng hợp dữ liệu báo cáo OGSM trực tiếp từ OneDrive.
"""

import os
import io
import pandas as pd
from logger import get_logger

logger = get_logger()


class OGSMService:
    def __init__(self):
        # Kết nối dịch vụ OneDrive đã cấu hình ban đầu
        try:
            from onedrive_service import OneDriveService
            self.onedrive = OneDriveService()
        except Exception as e:
            logger.error(f"Không thể khởi tạo OneDriveService: {e}")
            self.onedrive = None

    def upload_unit_file(self, filename: str, file_bytes: bytes) -> bool:
        """Tải file Excel báo cáo lên trực tiếp thư mục DATA trên OneDrive."""
        if not self.onedrive:
            logger.error("Dịch vụ OneDrive chưa được kết nối.")
            return False
        try:
            return self.onedrive.upload_file(filename, file_bytes)
        except Exception as e:
            logger.error(f"Lỗi khi upload file {filename} lên OneDrive: {e}")
            return False

    def get_full_ogsm_data(self) -> pd.DataFrame:
        """Tải và tổng hợp toàn bộ dữ liệu file Excel từ thư mục DATA trên OneDrive."""
        if not self.onedrive:
            logger.error("OneDriveService không khả dụng.")
            return pd.DataFrame()

        try:
            # Đọc danh sách file trực tiếp từ OneDrive
            all_dfs = self.onedrive.get_all_excel_data()
            if not all_dfs:
                return pd.DataFrame()

            master_df = pd.concat(all_dfs, ignore_index=True)
            return master_df
        except Exception as e:
            logger.error(f"Lỗi khi đọc dữ liệu từ OneDrive: {e}")
            return pd.DataFrame()
