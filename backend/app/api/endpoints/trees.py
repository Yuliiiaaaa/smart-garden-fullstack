from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db, Tree, Garden
from app.models.schemas import TreeCreate, Tree as TreeSchema

router = APIRouter()

@router.get("/", response_model=List[TreeSchema])
async def get_trees(
    garden_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить список деревьев с фильтрацией по саду"""
    try:
        query = db.query(Tree)
        if garden_id:
            # Проверяем существование сада
            garden = db.query(Garden).filter(Garden.id == garden_id).first()
            if not garden:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Сад с ID {garden_id} не найден"
                )
            query = query.filter(Tree.garden_id == garden_id)
        
        trees = query.offset(skip).limit(limit).all()
        return trees
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении списка деревьев: {str(e)}"
        )

@router.post("/", response_model=TreeSchema, status_code=status.HTTP_201_CREATED)
async def create_tree(tree: TreeCreate, db: Session = Depends(get_db)):
    """Добавить новое дерево"""
    try:
        # Проверяем существование сада
        garden = db.query(Garden).filter(Garden.id == tree.garden_id).first()
        if not garden:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Сад с ID {tree.garden_id} не найден"
            )
        
        # Проверяем, нет ли уже дерева с таким номером в этом ряду и саду
        existing_tree = db.query(Tree).filter(
            Tree.garden_id == tree.garden_id,
            Tree.row_number == tree.row_number,
            Tree.tree_number == tree.tree_number
        ).first()
        
        if existing_tree:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Дерево с таким номером уже существует в этом ряду"
            )
        
        # Создаем новое дерево
        db_tree = Tree(**tree.dict())
        db.add(db_tree)
        db.commit()
        db.refresh(db_tree)
        
        return db_tree
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании дерева: {str(e)}"
        )