from fastapi import APIRouter, Depends
from ..skema import RequestProfil, ResponseProfil
from ..dependensi import ambil_sesi
from bank_djago.services.rekening.rekening_service import RekeningService

router = APIRouter()

@router.post("/rekening/profil")
def lihat_rekening(sesi = Depends(ambil_sesi)):
    return {'nik':sesi['nik'],
            "norek":sesi['norek']}


