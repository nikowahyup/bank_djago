from fastapi import APIRouter
from ..skema import RequestProfil, ResponseProfil
from bank_djago.services.rekening.rekening_service import RekeningService

router = APIRouter()

@router.post("/rekening/profil",response_model=ResponseProfil)
def lihat_rekening(data:RequestProfil):
    RekeningService.verifikasi_pin_rekening(nik_aktif=data.nik, norek_aktif=data.norek,pin_input=data.pin)
    data_rekening = RekeningService.ambil_data_rekening(norek=data.norek)
    return {"norek":data_rekening['norek'],
            "saldo":data_rekening['saldo'],
            "level":data_rekening['level']}


