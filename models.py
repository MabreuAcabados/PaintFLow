from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class LabelRequest(BaseModel):
    pedido_id: int
    factura_id: Optional[int] = None
    producto_sw: str
    cantidad: float
    unidad: str

class LabelResponse(BaseModel):
    label_id: str
    pedido_id: int
    pdf_base64: str
    zpl_code: str
    timestamp: datetime

class FormulasRequest(BaseModel):
    producto_sw: str
    presentacion: str

class FormulasResponse(BaseModel):
    producto_sw: str
    formula_id: int
    colorantes: List[dict]
    conversiones: dict
    timestamp: datetime
