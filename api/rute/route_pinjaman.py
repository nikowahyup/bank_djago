from fastapi import APIRouter
from ..skema import RequestAjukanPinjaman, ResponseAjukanPinjaman, RequestCairkanPinjaman, ResponseCairkanPinjaman
from bank_djago.services.pinjaman.pinjaman_service import PinjamanService



router = APIRouter()

@router.post("/pinjaman/ajukan",response_model=ResponseAjukanPinjaman)
def ajukan_pinjaman(data:RequestAjukanPinjaman):
    id_pinjaman = PinjamanService.ajukan_pinjaman(nik=data.nik, norek=data.norek,pin=data.pin, nominal=data.nominal, tenor=data.tenor)

    return {"nominal":data.nominal,
            "id_pinjaman":id_pinjaman}


@router.post("/pinjaman/cairkan",response_model=ResponseCairkanPinjaman)
def cairkan_pinjaman(data:RequestCairkanPinjaman):
    PinjamanService.cairkan_pinjaman(nik=data.nik, norek_pencairan=data.norek,pin=data.pin,id_pinjaman=data.id_pinjaman)
    data_pinjaman = PinjamanService.cari_data_pinjaman_dengan_id(id_pinjaman=data.id_pinjaman)

    return {'nominal':data_pinjaman['nominal_pinjaman'],
            "norek":data_pinjaman['norek'],
            "id_pinjaman":data_pinjaman['id']}
