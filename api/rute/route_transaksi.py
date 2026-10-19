from fastapi import APIRouter
from ..skema import RequestSetor, ResponseSetor, RequestTarik, ResponseTarik, RequestTransfer, ResponseTransfer
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

@router.post("/transaksi/transfer",response_model=ResponseTransfer)
def transfer(data:RequestTransfer):
    TransaksiService.transfer(nik_masuk=data.nik, norek_pengirim=data.norek,norek_penerima=data.norek_tujuan, pin=data.pin, nominal=data.nominal)
    data_pengirim = RekeningService.ambil_data_rekening(norek=data.norek)
    return {"nominal":data.nominal,
            "saldo":data_pengirim['saldo'],
            "norek_penerima":data.norek_tujuan}


feat: endpoint POST /transaksi/tarik dan /transaksi/transfer