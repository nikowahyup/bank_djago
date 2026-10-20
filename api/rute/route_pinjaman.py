from fastapi import APIRouter, Depends
from ..skema import (
    RequestAjukanPinjaman,
    ResponseAjukanPinjaman,
    RequestCairkanPinjaman,
    ResponseCairkanPinjaman,
    RequestBayarCicilan,
    ResponseBayarCicilan
)
from bank_djago.services.pinjaman.pinjaman_service import PinjamanService
from ..dependensi import ambil_sesi



router = APIRouter()

@router.post("/pinjaman/ajukan",response_model=ResponseAjukanPinjaman)
def ajukan_pinjaman(data:RequestAjukanPinjaman, sesi = Depends(ambil_sesi)):
    id_pinjaman = PinjamanService.ajukan_pinjaman(nik=sesi['nik'], norek=sesi['norek'],pin=data.pin, nominal=data.nominal, tenor=data.tenor)

    return {"nominal":data.nominal,
            "id_pinjaman":id_pinjaman}


@router.post("/pinjaman/cairkan",response_model=ResponseCairkanPinjaman)
def cairkan_pinjaman(data:RequestCairkanPinjaman, sesi = Depends(ambil_sesi)):
    PinjamanService.cairkan_pinjaman(nik=sesi['nik'], norek_pencairan=sesi['norek'],pin=data.pin,id_pinjaman=data.id_pinjaman)
    data_pinjaman = PinjamanService.cari_data_pinjaman_dengan_id(id_pinjaman=data.id_pinjaman)

    return {'nominal':data_pinjaman['nominal_pinjaman'],
            "norek":data_pinjaman['norek'],
            "id_pinjaman":data_pinjaman['id']}


@router.post("/pinjaman/bayar_cicilan",response_model=ResponseBayarCicilan)
def bayar_cicilan(data:RequestBayarCicilan, sesi = Depends(ambil_sesi)):
    hasil = PinjamanService.bayar_cicilan(nik=sesi['nik'], norek_pembayaran=sesi['norek'], pin=data.pin, id_pinjaman=data.id_pinjaman)
    return{"tanggal_bayar_selanjutnya":hasil['tanggal_bayar_selanjutnya'],
           "status":hasil['status'].value,
           "id_pinjaman":hasil['id_pinjaman'],
           "cicilan_selanjutnya":hasil['cicilan_selanjutnya']}
