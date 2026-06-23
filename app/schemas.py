from pydantic import BaseModel, Field


class JobOut(BaseModel):
    id: int
    title: str
    company: str
    description: str
    skills: str
    city: str
    salary_min: int | None
    salary_max: int | None
    grade: str
    views: int
    applications: int

    model_config = {"from_attributes": True}


class RecommendationOut(BaseModel):
    job: JobOut
    score: float
    strategy: str
    position: int


class SearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    top_k: int = Field(default=10, ge=1, le=50)


class EventRequest(BaseModel):
    user_id: int
    job_id: int
    event_type: str = Field(pattern="^(impression|click)$")
    position: int | None = None
    score: float | None = None


class VariantStatsOut(BaseModel):
    variant: str
    impressions: int
    clicks: int
    ctr: float
