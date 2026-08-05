"""
OGSM Service - Quản lý nạp, tổng hợp và lưu trữ dữ liệu báo cáo OGSM.
"""

import os
import io
from pathlib import Path
import pandas as pd
from logger import get_logger

logger = get_logger()

# Đường dẫn thư mục lưu dữ liệu Excel
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "DATA"

# Tự động tạo thư mục DATA nếu chưa tồn tại
if not DATA_DIR.exists():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


class OGSMService:
    def __init__(self, data_folder: Path = DATA_DIR):
        self.data_folder = data_folder

    def upload_unit_file(self, filename: str, file_bytes: bytes) -> bool:
        """
        Lưu hoặc ghi đè file báo cáo Excel của đơn vị vào thư mục DATA.
        """
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
        """
        Đọc tất cả các file Excel (.xlsx) trong thư mục DATA và gộp lại thành DataFrame tổng hợp.
        """
        all_dfs = []
        if not self.data_folder.exists():
            return pd.DataFrame()

        for file_path in self.data_folder.glob("*.xlsx"):
            if file_path.name.startswith("~$"):
                continue  # Bỏ qua file tạm của Excel
            try:
                df = pd.read_excel(file_path, engine="openpyxl")
                unit_code = file_path.stem  # Lấy tên file làm Mã Đơn vị (ví dụ: BV ĐHYD, HCTH)
                
                # Đảm bảo có cột Unit_Code
                if "Unit_Code" not in df.columns:
                    df["Unit_Code"] = unit_code
                    
                all_dfs.append(df)
            except Exception as e:
                logger.error(f"Không thể đọc file {file_path.name}: {e}")

        if all_dfs:
            master_df = pd.concat(all_dfs, ignore_index=True)
            return master_df
        return pd.DataFrame()
