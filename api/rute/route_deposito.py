from fastapi import APIRouter
from ..skema import RequestBukaDeposito, ResponseBukaDeposito, ResponseCairkanDeposito, RequestCairkanDeposito,RequestHentikanAro, ResponseHentikanAro
from bank_djago.services.deposito.deposito_service import DepositoService


router = APIRouter()


@router.post("/deposito/buka_deposito",response_model=ResponseBukaDeposito)
def buka_deposito(data:RequestBukaDeposito):
    id_deposito = DepositoService.buka_deposito(nik=data.nik, norek=data.norek,nominal=data.nominal,pin=data.pin,lama_bulan=data.lama_bulan,jenis_aro=data.jenis_aro,lama_aro=data.lama_aro)
    return {'id_deposito':id_deposito,
            "norek":data.norek,
            "nominal":data.nominal}

@router.post("/deposito/cairkan_deposito", response_model=ResponseCairkanDeposito)
def cairkan_deposito(data: RequestCairkanDeposito):
    total_pencairan = DepositoService.cairkan_deposito(
        nik=data.nik,
        norek_pencairan=data.norek,
        pin=data.pin,
        id_deposito=data.id_deposito,
    )
    return {
        "total_pencairan": total_pencairan,
        "norek": data.norek,
        "id_deposito": data.id_deposito,
    }

@router.post("/deposito/hentikan_aro", response_model=ResponseHentikanAro)
def hentikan_aro(data: RequestHentikanAro):
    id_deposito = DepositoService.hentikan_aro(
        nik=data.nik,
        norek_pemberhentian=data.norek,
        pin=data.pin,
        id_deposito=data.id_deposito,
    )
    return {"id_deposito": id_deposito}