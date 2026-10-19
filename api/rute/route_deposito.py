from fastapi import APIRouter
from ..skema import RequestBukaDeposito, ResponseBukaDeposito
from bank_djago.services.deposito.deposito_service import DepositoService


router = APIRouter()


@router.post("/deposito/buka_deposito",response_model=ResponseBukaDeposito)
def buka_deposito(data:RequestBukaDeposito):
    id_deposito = DepositoService.buka_deposito(nik=data.nik, norek=data.norek,nominal=data.nominal,pin=data.pin,lama_bulan=data.lama_bulan,jenis_aro=data.jenis_aro,lama_aro=data.lama_aro)
    return {'id_deposito':id_deposito,
            "norek":data.norek,
            "nominal":data.nominal}

