from bank_djago.services.nasabah.sesi_service import SesiService
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

skema_bearer = HTTPBearer()


def ambil_sesi(kredensial: HTTPAuthorizationCredentials = Depends(skema_bearer)):
    return SesiService.cek_sesi(kredensial.credentials)
