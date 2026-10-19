from fastapi import APIRouter
from ..skema import RequestSetor, ResponseSetor, RequestTarik, ResponseTarik
from bank_djago.services.rekening.rekening_service import RekeningService
from bank_djago.services.transaksi.transaksi_service import TransaksiService


router = APIRouter()

@router.post("/transaksi/setor",response_model=ResponseSetor)
def setor_tunai(data:RequestSetor):
    TransaksiService.setor_tunai(nik_masuk=data.nik, norek=data.norek, pin=data.pin, nominal=data.nominal)
    data_rekening = RekeningService.ambil_data_rekening(norek=data.norek)
    return {"saldo":data_rekening['saldo'],
            "nominal":data.nominal}

@router.post("/transaksi/tarik",response_model=ResponseTarik)
def tarik_tunai(data:RequestTarik):
    TransaksiService.tarik_tunai(nik_masuk=data.nik, norek=data.norek, pin=data.pin, nominal=data.nominal)
    data_rekening = RekeningService.ambil_data_rekening(norek=data.norek)
    return {"saldo":data_rekening['saldo'],
            "nominal":data.nominal}

