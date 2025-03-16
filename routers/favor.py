from fastapi import APIRouter, HTTPException
from tortoise.exceptions import DoesNotExist
from models import User, Project

router = APIRouter()


@router.get("/is_favor")
async def is_favor(model_id: int, user_id: str):
    """Check if the user has favorited a project."""
    try:
        user = await User.get(user_id=user_id)
        # Check if the project is in the user's favor_models list
        is_favor2 = await user.favor_models.filter(project_id=model_id).exists()
        return {"is_favor": is_favor2}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")


@router.post("/add_favor")
async def add_favor(model_id: int, user_id: str):
    """Add a favorite for a project by the user."""
    try:
        user = await User.get(user_id=user_id)
        project = await Project.get(project_id=model_id)

        # Add the project to the user's favorites
        await user.favor_models.add(project)
        return {"message": "Favor added successfully"}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User or Project not found")


@router.delete("/delete_favor")
async def delete_favor(model_id: int, user_id: str):
    """Remove a favorite for a project by the user."""
    try:
        user = await User.get(user_id=user_id)
        project = await Project.get(project_id=model_id)

        # Remove the project from the user's favorites
        await user.favor_models.remove(project)
        return {"message": "Favor removed successfully"}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User or Project not found")


@router.get("/favored_models_by_user")
async def get_favored_models_by_user(user_id: str):
    """Get all models favored by a user."""
    try:
        user = await User.get(user_id=user_id)
        # Get all projects favorited by the user
        favored_projects = await user.favor_models.all()
        return {"favored_projects": [project.project_id for project in favored_projects]}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")


@router.get("/users_who_favored_model")
async def get_users_who_favored_model(model_id: int):
    """Get all users who favored a specific model."""
    try:
        project = await Project.get(project_id=model_id)
        # Get all users who have favorited the project
        users = await project.users.all()
        return {"users_who_favored": [user.user_id for user in users]}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Project not found")
