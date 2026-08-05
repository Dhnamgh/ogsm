"""
OGSM Service - Quản lý nạp, tổng hợp và chuẩn hóa dữ liệu báo cáo OGSM.
Khôi phục đọc trực tiếp các tệp Excel từ thư mục DATA trên hệ thống.
"""

import os
from pathlib import Path
import pandas as pd
from logger import get_logger

logger = get_logger()

# Đường dẫn đến thư mục DATA chứa các tệp Excel trên Repo
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "DATA"

if not DATA_DIR.exists():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


class OGSMService:
    def __init__(self, data_folder: Path = DATA_DIR):
        self.data_folder = data_folder
        self.data_folder.mkdir(parents=True, exist_ok=True)

    def upload_unit_file(self, filename: str, file_bytes: bytes) -> bool:
        """Lưu hoặc ghi đè file báo cáo Excel của đơn vị vào thư mục DATA."""
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
        """Đọc và gộp tất cả các file Excel hiện có trong thư mục DATA."""
        all_dfs = []
        if not self.data_folder.exists():
            return pd.DataFrame()

        # Quét tất cả file .xlsx trong thư mục DATA
        excel_files = list(self.data_folder.glob("*.xlsx")) + list(self.data_folder.glob("**/*.xlsx"))

        for file_path in excel_files:
            if file_path.name.startswith("~$"):
                continue  # Bỏ qua file tạm Excel
            try:
                df = pd.read_excel(file_path, engine="openpyxl")
                if df.empty:
                    continue

                # Xóa khoảng trắng thừa ở tiêu đề cột
                df.columns = [str(c).strip() for c in df.columns]

                # Mã đơn vị lấy từ tên file (Ví dụ: BV ĐHYD.xlsx -> BV ĐHYD, P.HCTH.xlsx -> P.HCTH)
                unit_code = file_path.stem.replace(".xlsx", "").strip()
                df["Unit_Code"] = unit_code

                all_dfs.append(df)
            except Exception as e:
                logger.error(f"Lỗi khi đọc file {file_path.name}: {e}")

        if all_dfs:
            master_df = pd.concat(all_dfs, ignore_index=True)
            return master_df

        return pd.DataFrame()
