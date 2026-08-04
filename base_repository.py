"""
Abstract base repository for OGSM storage operations.
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import List
from models.ogsm_schema import MeasureItem


class BaseOGSMRepository(ABC):

    @abstractmethod
    def fetch_master_dataframe((self) -> pd.DataFrame:
        pass

    @abstractmethod
    def save_master_dataframe(self, df: pd.DataFrame) -> bool:
        pass
