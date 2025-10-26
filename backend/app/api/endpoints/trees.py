from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter()

class TreeBase(BaseModel):
    garden_id: int
    row_number: int
    tree_number: int
    variety: str

class Tree(TreeBase):
    id: int
    last_harvest_count: int = 0

# Заглушка данных
demo_trees = [
    {
        "id": 1,
        "garden_id": 1,
        "row_number": 1,
        "tree_number": 15,
        "variety": "Голден",
        "last_harvest_count": 42
    },
    {
        "id": 2,
        "garden_id": 1, 
        "row_number": 2,
        "tree_number": 8,
        "variety": "Гала",
        "last_harvest_count": 38
    }
]

@router.get("/", response_model=List[Tree])
async def get_trees(garden_id: int = None):
    """Получить список деревьев"""
    if garden_id:
        return [t for t in demo_trees if t["garden_id"] == garden_id]
    return demo_trees

@router.get("/{tree_id}", response_model=Tree)
async def get_tree(tree_id: int):
    """Получить информацию о дереве"""
    tree = next((t for t in demo_trees if t["id"] == tree_id), None)
    if not tree:
        raise HTTPException(status_code=404, detail="Дерево не найдено")
    return tree

@router.post("/", response_model=Tree)
async def create_tree(tree: TreeBase):
    """Добавить новое дерево"""
    new_tree = {
        "id": len(demo_trees) + 1,
        **tree.dict(),
        "last_harvest_count": 0
    }
    demo_trees.append(new_tree)
    return new_tree