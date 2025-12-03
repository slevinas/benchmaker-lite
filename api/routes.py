from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class VectorPayload(BaseModel):
  a: list[float]
  b: list[float]


@router.post("/vector/add")
async def vector_add(payload: VectorPayload):
    """Element-wise vector addition."""
    result = [x + y for x, y in zip(payload.a, payload.b)]
    return {"result": result}


@router.post("/vector/sub")
async def vector_sub(payload: VectorPayload):
    """Element-wise vector subtraction."""
    result = [x - y for x, y in zip(payload.a, payload.b)]
    return {"result": result}
