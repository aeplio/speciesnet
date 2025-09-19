from pydantic import BaseModel
from typing import List

class Settings(BaseModel):
    app_name: str = "SpeciesNet API"
    api_prefix: str = "/api"
    allow_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"  # 开发阶段允许任意来源，生产请收紧
    ]

settings = Settings()
