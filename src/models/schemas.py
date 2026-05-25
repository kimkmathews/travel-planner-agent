from pydantic import BaseModel, Field, field_validator
from typing import Optional

# ── Trip parameter extraction ──────────────────────────────────────────────

class TripParameters(BaseModel):
    """Structured representation of a user's travel request."""
    origin_city: str = Field(description="City the travellers depart from")
    destination: str = Field(description="Travel destination (city/island/country)")
    duration_days: int = Field(description="Number of days including travel days")
    num_adults: int = Field(description="Number of adult travellers (18+)")
    num_children: int = Field(description="Number of child travellers (under 18)")
    budget_inr: int = Field(description="Total trip budget in Indian Rupees")
    travel_month: str = Field(description="Month of travel, e.g. 'November 2026'")
    preferences: list[str] = Field(
        description="User's stated interests e.g. ['beaches', 'food', 'light adventure']"
    )
    special_requirements: Optional[str] = Field(
        default=None,
        description="Dietary needs, accessibility, visa concerns, etc."
    )

    @field_validator("budget_inr")
    @classmethod
    def budget_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Budget must be a positive integer in INR")
        return v


# ── Cost breakdown ─────────────────────────────────────────────────────────

class CostLineItem(BaseModel):
    """A single verifiable line item in the trip cost breakdown."""
    description: str = Field(description="What this cost covers")
    amount_inr: int = Field(description="Cost in INR")
    original_currency: Optional[str] = Field(
        default=None,
        description="Original currency if not INR, e.g. 'VND 2,500,000'"
    )
    source_url: Optional[str] = Field(
        default=None,
        description="URL where this price was found. None = price not verified."
    )
    is_verified: bool = Field(
        description="True only if source_url is populated and price is from a live search"
    )


class CostBreakdown(BaseModel):
    """Complete, verifiable cost breakdown for the trip."""
    flights_inr: int
    accommodation_inr: int
    meals_inr: int
    activities_inr: int
    transport_misc_inr: int
    total_inr: int
    is_within_budget: bool
    unverified_items: list[str] = Field(
        description="List of cost categories where real prices could not be found"
    )
    line_items: list[CostLineItem]

    @field_validator("total_inr")
    @classmethod
    def total_must_match_parts(cls, v, info):
        if "flights_inr" in info.data:
            computed = (
                info.data.get("flights_inr", 0)
                + info.data.get("accommodation_inr", 0)
                + info.data.get("meals_inr", 0)
                + info.data.get("activities_inr", 0)
                + info.data.get("transport_misc_inr", 0)
            )
            # Allow ±5% rounding tolerance
            if abs(v - computed) > computed * 0.05:
                raise ValueError(
                    f"Total {v} does not match sum of parts {computed}"
                )
        return v


# ── Day plan ───────────────────────────────────────────────────────────────

class DayPlan(BaseModel):
    """A single day's itinerary."""
    day_number: int
    title: str = Field(description="Short evocative title for the day")
    morning: str
    afternoon: str
    evening: str
    dining_suggestion: str
    family_tip: str
    estimated_daily_spend_inr: int


# ── Final itinerary ────────────────────────────────────────────────────────

class FinalItinerary(BaseModel):
    """Complete structured itinerary ready for display or export."""
    trip_title: str
    destination: str
    origin: str
    duration_days: int
    travel_month: str
    party: str = Field(description="e.g. '2 adults, 1 child'")
    weather_summary: str
    packing_tips: list[str]
    day_plans: list[DayPlan]
    cost_breakdown: CostBreakdown
    budget_status: str = Field(
        description="'UNDER_BUDGET', 'AT_BUDGET', or 'OVER_BUDGET'"
    )
    remaining_budget_inr: int
    important_notes: list[str] = Field(
        description="Visa requirements, booking deadlines, health advisories"
    )
    data_sources: list[str] = Field(
        description="All URLs consulted during research"
    )
