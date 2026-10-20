from fastapi import APIRouter
from bank_djago.services.nasabah.sesi_service import SesiService

from ..skema import ResponseLogin, RequestLogin

router = APIRouter()


@router.post("/login", response_model=ResponseLogin)
def login(data: RequestLogin):
    token, kedaluwarsa = SesiService.buat_sesi(
        nik=data.nik, norek=data.norek, pin=data.pin
    )

    return {"token": token, "kedaluwarsa": kedaluwarsa}
