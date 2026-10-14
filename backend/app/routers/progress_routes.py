from fastapi import APIRouter, Depends
from ..models import ProgressOverview
from ..auth import get_current_user
from ..services.learning_engine import LearningEngine

router = APIRouter(prefix="/progress", tags=["Progress Tracking"])

@router.get("", response_model=ProgressOverview)
def get_my_progress(current_user: dict = Depends(get_current_user)):
    return LearningEngine.get_user_progress(current_user["id"])
