"""
Repository layer to load OGSM files directly from OneDrive API or Local DATA folder.
Khôi phục kết nối OneDrive API và hỗ trợ đọc dữ liệu đa nền tảng.
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
        
        # Nạp dịch vụ kết nối OneDrive API
        try:
            from onedrive_service import OneDriveService
            self.onedrive_service = OneDriveService()
        except Exception as e:
            logger.warning(f"Không thể kết nối OneDriveService API: {e}")

    def fetch_master_dataframe(self) -> pd.DataFrame:
        """Đọc và gộp toàn bộ các file Excel từ OneDrive API hoặc thư mục DATA dự phòng."""
        all_dfs = []

        # 1. ƯU TIÊN NẠP TRỰC TIẾP TỪ ONEDRIVE API
        if self.onedrive_service:
            try:
                files = self.onedrive_service.list_files_in_data_folder()
                if files:
                    for file_info in files:
                        filename = file_info.get("name", "")
                        file_id = file_info.get("id", "")

                        if not filename.lower().endswith(('.xlsx', '.xls')) or filename.startswith('~$'):
                            continue

                        try:
                            # Download file content stream từ OneDrive
                            content = self.onedrive_service.download_file_bytes(file_id)
                            if content:
                                bio = io.BytesIO(content)
                                df = pd.read_excel(bio, sheet_name=0, engine="openpyxl")
                                
                                if df is not None and not df.empty:
                                    clean_filename = filename.replace(".xlsx", "").replace(".XLSX", "").strip()
                                    df["Source_File"] = clean_filename
                                    if "Unit_Code" not in df.columns or df["Unit_Code"].dropna().empty:
                                        df["Unit_Code"] = clean_filename
                                    all_dfs.append(df)
                        except Exception as ex:
                            logger.error(f"Lỗi đọc file OneDrive {filename}: {ex}")

                    if all_dfs:
                        return pd.concat(all_dfs, ignore_index=True)
            except Exception as e:
                logger.error(f"Lỗi gọi API OneDrive: {e}")

        # 2. DỰ PHÒNG TỰ ĐỘNG NẠP TỪ THƯ MỤC NỘI BỘ (Local/Synced DATA)
        if os.path.exists(self.data_dir):
            files = [f for f in os.listdir(self.data_dir) if f.lower().endswith(('.xlsx', '.xls')) and not f.startswith('~$')]
            for filename in files:
                file_path = os.path.join(self.data_dir, filename)
                try:
                    df = pd.read_excel(file_path, sheet_name=0, engine="openpyxl")
                    if df is not None and not df.empty:
                        clean_filename = filename.replace(".xlsx", "").replace(".XLSX", "").strip()
                        df["Source_File"] = clean_filename
                        if "Unit_Code" not in df.columns or df["Unit_Code"].dropna().empty:
                            df["Unit_Code"] = clean_filename
                        all_dfs.append(df)
                except Exception as e:
                    logger.error(f"Lỗi đọc file local {filename}: {e}")

        if all_dfs:
            return pd.concat(all_dfs, ignore_index=True)

        return pd.DataFrame()

    def save_unit_dataframe(self, filename: str, df: pd.DataFrame) -> bool:
        """Lưu/Ghi đè file đơn vị."""
        try:
            if self.onedrive_service:
                # Ghi file thông qua OneDrive API
                bio = io.BytesIO()
                df.to_excel(bio, index=False, engine="openpyxl")
                bio.seek(0)
                return self.onedrive_service.upload_file_bytes(filename, bio.getvalue())
            
            # Ghi file local dự phòng
            file_path = os.path.join(self.data_dir, filename if filename.endswith('.xlsx') else f"{filename}.xlsx")
            df.to_excel(file_path, index=False, engine="openpyxl")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi lưu file {filename}: {e}")
            return False
