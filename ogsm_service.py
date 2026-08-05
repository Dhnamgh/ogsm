"""
OGSM Service - Tự động tìm và đọc toàn bộ tệp Excel dữ liệu OGSM.
"""

import os
from pathlib import Path
import pandas as pd
from logger import get_logger

logger = get_logger()

# Tự động xác định thư mục chứa dữ liệu
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "DATA"


class OGSMService:
    def __init__(self, data_folder: Path = DATA_DIR):
        self.data_folder = data_folder

    def upload_unit_file(self, filename: str, file_bytes: bytes) -> bool:
        """Lưu hoặc ghi đè tệp Excel vào thư mục DATA."""
        try:
            if not self.data_folder.exists():
                self.data_folder.mkdir(parents=True, exist_ok=True)
            target_path = self.data_folder / filename
            with open(target_path, "wb") as f:
                f.write(file_bytes)
            logger.info(f"Đã lưu thành công tệp {filename}")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi lưu tệp {filename}: {e}")
            return False

    def get_full_ogsm_data(self) -> pd.DataFrame:
        """Quét toàn bộ tệp .xlsx trong dự án và tổng hợp dữ liệu."""
        all_dfs = []

        # Tìm tất cả các tệp .xlsx trong thư mục hiện tại và các thư mục con
        excel_files = list(Path(BASE_DIR).glob("**/*.xlsx"))

        for file_path in excel_files:
            if file_path.name.startswith("~$"):
                continue  # Bỏ qua tệp tạm Excel
            try:
                df = pd.read_excel(file_path, engine="openpyxl")
                if df.empty:
                    continue

                # Chuẩn hóa tên cột
                df.columns = [str(c).strip() for c in df.columns]

                # Lấy mã đơn vị từ tên tệp Excel
                unit_code = file_path.stem.replace(".xlsx", "").strip()
                df["Unit_Code"] = unit_code

                all_dfs.append(df)
            except Exception as e:
                logger.error(f"Lỗi khi đọc tệp {file_path.name}: {e}")

        if all_dfs:
            master_df = pd.concat(all_dfs, ignore_index=True)
            return master_df

        return pd.DataFrame()
