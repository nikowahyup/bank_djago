from fastapi import APIRouter, Depends
from ..skema import ResponseProfil
from ..dependensi import ambil_sesi
from bank_djago.services.rekening.rekening_service import RekeningService

router = APIRouter()


@router.post("/rekening/profil", response_model=ResponseProfil)
def lihat_rekening(sesi=Depends(ambil_sesi)):
    data_rekening = RekeningService.ambil_data_rekening(norek=sesi["norek"])

    return {
        "norek": data_rekening["norek"],
        "saldo": data_rekening["saldo"],
        "level": data_rekening["level"],
    }
