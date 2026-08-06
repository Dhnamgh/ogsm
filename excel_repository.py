"""
Repository layer to load OGSM files directly from OneDrive DATA folder.
Gia cố đọc 100% tất cả các file Excel, tự động sửa lỗi Merge Cell và khoảng trắng tên file.
"""

import io
import os
import re
import unicodedata
import pandas as pd
from typing import Optional, List, Dict, Any
from logger import get_logger

logger = get_logger()


class ExcelOneDriveRepository:

    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), "DATA")

    def fetch_master_dataframe(self) -> pd.DataFrame:
        """Đọc và gộp toàn bộ các file Excel có trong thư mục DATA."""
        all_dfs = []
        
        if not os.path.exists(self.data_dir):
            logger.error(f"Thư mục không tồn tại: {self.data_dir}")
            return pd.DataFrame()

        # Quét tất cả file .xlsx hoặc .xls (bỏ file rác của Office ~$ )
        files = [f for f in os.listdir(self.data_dir) if f.lower().endswith(('.xlsx', '.xls')) and not f.startswith('~$')]
        logger.info(f"Tìm thấy {len(files)} tệp Excel trong thư mục DATA.")

        for filename in files:
            file_path = os.path.join(self.data_dir, filename)
            try:
                # 1. Đọc sheet đầu tiên bất kể tên sheet là gì
                df = pd.read_excel(file_path, sheet_name=0, engine="openpyxl")
                
                # 2. Xử lý trường hợp Dòng 1 bị Merge Cell làm trượt tiêu đề cột
                if df is not None and not df.empty:
                    # Kiểm tra nếu tên cột chưa chứa 'Objective' hay 'Goal' hay 'Measure', thử đẩy dòng 1 lên làm header
                    cols_str = " ".join([str(c) for c in df.columns]).lower()
                    if not any(k in cols_str for k in ["objective", "goal", "measure", "mục tiêu", "kpi"]):
                        # Đọc lại với header ở dòng thứ 2 (header=1)
                        df_retry = pd.read_excel(file_path, sheet_name=0, header=1, engine="openpyxl")
                        if df_retry is not None and not df_retry.empty:
                            df = df_retry

                    # Gán tên file nguồn nguyên bản
                    clean_filename = str(filename).replace(".xlsx", "").replace(".XLSX", "").strip()
                    df["Source_File"] = clean_filename
                    
                    if "Unit_Code" not in df.columns or df["Unit_Code"].dropna().empty:
                        df["Unit_Code"] = clean_filename

                    all_dfs.append(df)
                else:
                    logger.warning(f"File {filename} rỗng.")
            except Exception as e:
                logger.error(f"Lỗi đọc file {filename}: {e}")

        if all_dfs:
            master_df = pd.concat(all_dfs, ignore_index=True)
            return master_df
        
        return pd.DataFrame()

    def save_unit_dataframe(self, filename: str, df: pd.DataFrame) -> bool:
        """Lưu/Ghi đè file đơn vị."""
        try:
            file_path = os.path.join(self.data_dir, filename if filename.endswith('.xlsx') else f"{filename}.xlsx")
            df.to_excel(file_path, index=False, engine="openpyxl")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi lưu file {filename}: {e}")
            return False
