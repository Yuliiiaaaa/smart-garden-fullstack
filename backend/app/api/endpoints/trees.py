# app/api/endpoints/trees.py
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.database import get_db, Tree, Garden, User
from app.models.schemas import TreeCreate, Tree as TreeSchema
from app.api.dependencies import get_current_user, get_manager_user

router = APIRouter()

@router.get("/", response_model=List[TreeSchema])
async def get_trees(
    garden_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)   # добавлена аутентификация
):
    query = db.query(Tree)
    if garden_id:
        garden = db.query(Garden).filter(Garden.id == garden_id).first()
        if not garden:
            raise HTTPException(status_code=404, detail="Сад не найден")
        query = query.filter(Tree.garden_id == garden_id)
    trees = query.offset(skip).limit(limit).all()
    return trees

@router.post("/", response_model=TreeSchema, status_code=201)
async def create_tree(
    tree: TreeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_manager_user)   # только менеджер и выше
):
    garden = db.query(Garden).filter(Garden.id == tree.garden_id).first()
    if not garden:
        raise HTTPException(status_code=404, detail="Сад не найден")

    existing = db.query(Tree).filter(
        Tree.garden_id == tree.garden_id,
        Tree.row_number == tree.row_number,
        Tree.tree_number == tree.tree_number
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Дерево с таким номером уже существует в этом ряду")

    db_tree = Tree(**tree.dict())
    db.add(db_tree)
    db.commit()
    db.refresh(db_tree)
    return db_tree