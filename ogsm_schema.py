"""
Domain models and schema definitions for OGSM items.
"""

from typing import Optional
from pydantic import BaseModel, Field


class MeasureItem(BaseModel):
    id: str = Field(..., description="Unique code for the Measure e.g. M1.1")
    strategy_id: str = Field(..., description="Parent Strategy ID e.g. S1")
    description: str = Field(..., description="Actionable measure details")
    unit: str = Field(default="Percent", description="Unit of metric (%, count, score)")
    target: float = Field(..., description="Target quantitative milestone")
    actual: float = Field(default=0.0, description="Actual achieved value")
    owner: str = Field(..., description="Responsible department/person")
    status: str = Field(default="In Progress", description="Status: Not Started, In Progress, Completed, Delayed")
    
    @property
    def completion_rate(self) -> float:
        if self.target == 0:
            return 100.0 if self.actual >= 0 else 0.0
        rate = (self.actual / self.target) * 100.0
        return min(max(rate, 0.0), 100.0)


class StrategyItem(BaseModel):
    id: str = Field(..., description="Strategy identifier e.g. S1")
    goal_id: str = Field(..., description="Parent Goal ID e.g. G1")
    description: str = Field(..., description="Strategy statement")


class GoalItem(BaseModel):
    id: str = Field(..., description="Goal identifier e.g. G1")
    objective_id: str = Field(..., description="Parent Objective ID e.g. O1")
    description: str = Field(..., description="Goal target description")


class ObjectiveItem(BaseModel):
    id: str = Field(..., description="Objective identifier e.g. O1")
    title: str = Field(..., description="High level strategic objective title")
    description: str = Field(..., description="Full narrative of objective")
