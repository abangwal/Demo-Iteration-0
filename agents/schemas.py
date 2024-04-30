from pydantic import BaseModel, Field
from typing import List


class LoS(BaseModel):
    "Get List of strings to complete the given quries"
    los: List[str] = Field(
        description="List of five strings to complete the provided task"
    )


class Timeline(BaseModel):
    "Get description about the company and a timeline of major events and achievements in the company's history"
    timeline: List[str] = Field(
        description="List of major events and achievements happed with the company with detailed description, like founded, acquired, went public and other events."
    )


class About(BaseModel):
    "Get description products and services offered by the company along with their rough estimated prices"
    description: str = Field(description="Short description about the company.")
    offerings: List[str] = Field(
        description="List of products or services offered by the company along with their rough prices"
    )


class SWOTAnalysis(BaseModel):
    "Market share, sales and SWOT (Strength, weakness, opportunity and threat) analysis of given company"
    # numbers : List[str] = Field(description="List of description of key performance indices like market-share, sales, global precense, etc.")
    strength: List[str] = Field(
        description="List of strenghts the given company have that make them unique, with detailed description"
    )
    weakness: List[str] = Field(
        description="List of weakness the given company with detailed description"
    )
    opportunities: List[str] = Field(
        description="List of opportunities the given company have that will contribute in the company future growth with detailed description"
    )
    threats: List[str] = Field(
        description="List of threats the given company have that can make business go bust, with detailed description"
    )
