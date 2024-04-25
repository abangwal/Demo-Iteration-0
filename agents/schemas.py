from pydantic import BaseModel, Field
from typing import List


class LoS(BaseModel):
    "Get List of strings to complete the given quries"
    los: List[str] = Field(
        description="List of five strings to complete the provided task"
    )


class SWOTAnalysis(BaseModel):
    "SWOT Strength, weakness, opportunity and threat analysis of given company"
    strength: List[str] = Field(
        description="List of strenghts the given company have that make them unique, with detailed description"
    )
    weakness: List[str] = Field(
        description="List of weakness the given company with detailed description"
    )
    opportunity: List[str] = Field(
        description="List of opportunities the given company have that will contribute in the company future growth with detailed description"
    )
    threats: List[str] = Field(
        description="List of threats the given company have that can make business go bust, with detailed description"
    )
