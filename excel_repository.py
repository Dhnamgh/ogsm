"""
Repository layer to load OGSM files directly from OneDrive API or DATA directory.
Khôi phục kết nối OneDrive API chuẩn xác và hỗ trợ xử lý luồng linh hoạt.
"""

import io
import os
import pandas as pd
from typing import Optional, List, Dict, Any
from logger import get_logger

logger = get_logger()


class ExcelOneDriveRepository:

    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), "DATA")
        self.onedrive_service = None
        
        try:
            from onedrive_service import OneDriveService
            self.onedrive_service = OneDriveService()
        except Exception as e:
            logger.warning(f"Không thể khởi tạo OneDriveService: {e}")

    def fetch_master_dataframe(self) -> pd.DataFrame:
        """Đọc và tổng hợp tất cả các file Excel OGSM."""
        all_dfs = []

        # 1. Thử đọc qua OneDrive Service API
        if self.onedrive_service:
            try:
                # Gọi lấy file trong thư mục DATA qua OneDrive Service
                files = []
                if hasattr(self.onedrive_service, "get_all_excel_files"):
                    files = self.onedrive_service.get_all_excel_files()
                elif hasattr(self.onedrive_service, "list_files_in_data_folder"):
                    files = self.onedrive_service.list_files_in_data_folder()

                if files:
                    for file_info in files:
                        filename = file_info.get("name", "")
                        file_id = file_info.get("id", "")

                        if not filename.lower().endswith(('.xlsx', '.xls')) or filename.startswith('~$'):
                            continue

                        try:
                            content = None
                            if hasattr(self.onedrive_service, "download_file_bytes"):
                                content = self.onedrive_service.download_file_bytes(file_id)
                            elif hasattr(self.onedrive_service, "get_file_content"):
                                content = self.onedrive_service.get_file_content(file_id)

                            if content:
                                bio = io.BytesIO(content)
                                df = pd.read_excel(bio, sheet_name=0, engine="openpyxl")
                                if df is not None and not df.empty:
                                    clean_fn = filename.replace(".xlsx", "").replace(".XLSX", "").strip()
                                    df["Source_File"] = clean_fn
                                    if "Unit_Code" not in df.columns or df["Unit_Code"].dropna().empty:
                                        df["Unit_Code"] = clean_fn
                                    all_dfs.append(df)
                        except Exception as ex:
                            logger.error(f"Lỗi nạp file OneDrive {filename}: {ex}")

                    if all_dfs:
                        return pd.concat(all_dfs, ignore_index=True)
            except Exception as e:
                logger.error(f"Lỗi kết nối OneDrive API: {e}")

        # 2. Thử đọc qua Thư mục Local/DATA dự phòng
        if os.path.exists(self.data_dir):
            try:
                files = [f for f in os.listdir(self.data_dir) if f.lower().endswith(('.xlsx', '.xls')) and not f.startswith('~$')]
                for filename in files:
                    file_path = os.path.join(self.data_dir, filename)
                    try:
                        df = pd.read_excel(file_path, sheet_name=0, engine="openpyxl")
                        if df is not None and not df.empty:
                            clean_fn = filename.replace(".xlsx", "").replace(".XLSX", "").strip()
                            df["Source_File"] = clean_fn
                            if "Unit_Code" not in df.columns or df["Unit_Code"].dropna().empty:
                                df["Unit_Code"] = clean_fn
                            all_dfs.append(df)
                    except Exception as e:
                        logger.error(f"Lỗi đọc file local {filename}: {e}")
            except Exception as e:
                logger.error(f"Lỗi mở thư mục local DATA: {e}")

        if all_dfs:
            return pd.concat(all_dfs, ignore_index=True)

        return pd.DataFrame()

    def save_unit_dataframe(self, filename: str, df: pd.DataFrame) -> bool:
        """Ghi đè file báo cáo đơn vị."""
        try:
            if self.onedrive_service and hasattr(self.onedrive_service, "upload_file_bytes"):
                bio = io.BytesIO()
                df.to_excel(bio, index=False, engine="openpyxl")
                bio.seek(0)
                return self.onedrive_service.upload_file_bytes(filename, bio.getvalue())
            
            file_path = os.path.join(self.data_dir, filename if filename.endswith('.xlsx') else f"{filename}.xlsx")
            df.to_excel(file_path, index=False, engine="openpyxl")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi lưu file {filename}: {e}")
            return False
