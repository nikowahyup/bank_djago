from fastapi import APIRouter, Depends
from ..skema import (
    RequestSetor,
    ResponseSetor,
    RequestTarik,
    ResponseTarik,
    RequestTransfer,
    ResponseTransfer,
)
from bank_djago.services.rekening.rekening_service import RekeningService
from bank_djago.services.transaksi.transaksi_service import TransaksiService
from ..dependensi import ambil_sesi

router = APIRouter()


@router.post("/transaksi/setor", response_model=ResponseSetor)
def setor_tunai(data: RequestSetor, sesi=Depends(ambil_sesi)):
    TransaksiService.setor_tunai(
        nik_masuk=sesi["nik"], norek=sesi["norek"], pin=data.pin, nominal=data.nominal
    )
    data_rekening = RekeningService.ambil_data_rekening(norek=sesi["norek"])
    return {"saldo": data_rekening["saldo"], "nominal": data.nominal}


@router.post("/transaksi/tarik", response_model=ResponseTarik)
def tarik_tunai(data: RequestTarik, sesi=Depends(ambil_sesi)):
    TransaksiService.tarik_tunai(
        nik_masuk=sesi["nik"],
        norek=sesi["norek"],
        pin=data.pin,
        nominal=data.nominal,
    )
    data_rekening = RekeningService.ambil_data_rekening(norek=sesi["norek"])
    return {
        "saldo": data_rekening["saldo"],
        "nominal": data.nominal,
    }


@router.post("/transaksi/transfer", response_model=ResponseTransfer)
def transfer(data: RequestTransfer, sesi=Depends(ambil_sesi)):
    TransaksiService.transfer(
        nik_masuk=sesi["nik"],
        norek_pengirim=sesi["norek"],
        norek_penerima=data.norek_tujuan,
        pin=data.pin,
        nominal=data.nominal,
    )
    data_pengirim = RekeningService.ambil_data_rekening(norek=sesi["norek"])
    return {
        "nominal": data.nominal,
        "saldo": data_pengirim["saldo"],
        "norek_penerima": data.norek_tujuan,
    }
