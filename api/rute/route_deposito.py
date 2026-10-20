from fastapi import APIRouter, Depends
from ..skema import RequestBukaDeposito, ResponseBukaDeposito, ResponseCairkanDeposito, RequestCairkanDeposito,RequestHentikanAro, ResponseHentikanAro
from bank_djago.services.deposito.deposito_service import DepositoService
from ..dependensi import ambil_sesi


router = APIRouter()


@router.post("/deposito/buka_deposito",response_model=ResponseBukaDeposito)
def buka_deposito(data:RequestBukaDeposito, sesi = Depends(ambil_sesi)):
    id_deposito = DepositoService.buka_deposito(nik=sesi['nik'], norek=sesi['norek'],nominal=data.nominal,pin=data.pin,lama_bulan=data.lama_bulan,jenis_aro=data.jenis_aro,lama_aro=data.lama_aro)
    return {'id_deposito':id_deposito,
            "norek":sesi['norek'],
            "nominal":data.nominal}

@router.post("/deposito/cairkan_deposito", response_model=ResponseCairkanDeposito)
def cairkan_deposito(data: RequestCairkanDeposito, sesi = Depends(ambil_sesi)):
    total_pencairan = DepositoService.cairkan_deposito(
        nik=sesi['nik'],
        norek_pencairan=sesi['norek'],
        pin=data.pin,
        id_deposito=data.id_deposito,
    )
    return {
        "total_pencairan": total_pencairan,
        "norek": sesi['norek'],
        "id_deposito": data.id_deposito,
    }

@router.post("/deposito/hentikan_aro", response_model=ResponseHentikanAro)
def hentikan_aro(data: RequestHentikanAro, sesi = Depends(ambil_sesi)):
    id_deposito = DepositoService.hentikan_aro(
        nik=sesi['nik'],
        norek_pemberhentian=sesi['norek'],
        pin=data.pin,
        id_deposito=data.id_deposito,
    )
    return {"id_deposito": id_deposito}