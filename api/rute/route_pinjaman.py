from fastapi import APIRouter
from ..skema import RequestAjukanPinjaman, ResponseAjukanPinjaman
from bank_djago.services.pinjaman.pinjaman_service import PinjamanService
from bank_djago.services.rekening.rekening_service import RekeningService


router = APIRouter()

@router.post("/pinjaman/ajukan",response_model=ResponseAjukanPinjaman)
def ajukan_pinjaman(data:RequestAjukanPinjaman):
    id_pinjaman = PinjamanService.ajukan_pinjaman(nik=data.nik, norek=data.norek,pin=data.pin, nominal=data.nominal, tenor=data.tenor)

    return {"nominal":data.nominal,
            "id_pinjaman":id_pinjaman}


