from bank_djago.services.exceptions import (
    RekeningTerkunci,
    RekeningTidakDitemukan,
    PinTidakCocok,
    InputTidakValid,
    StatusTidakValid,
    NikTidakSesuai,
    PinjamanTidakDitemukan,
    RekeningTidakSesuai,
    JenisAroTidakValid,
    DepositoTidakDitemukan,
    TokenTidakValid,
    TokenKedaluwarsa,
)
from fastapi.responses import JSONResponse
from fastapi import Request

PETA_EXCEPTIONS = {
    PinTidakCocok: 423,
    RekeningTerkunci: 402,
    RekeningTidakDitemukan: 410,
    InputTidakValid: 412,
    StatusTidakValid: 409,
    NikTidakSesuai: 411,
    PinjamanTidakDitemukan: 418,
    RekeningTidakSesuai: 430,
    JenisAroTidakValid: 440,
    DepositoTidakDitemukan: 439,
    TokenTidakValid: 401,
    TokenKedaluwarsa: 403,
}


def tangani_handler(app, exc_class, kode):
    @app.exception_handler(exc_class)
    async def handler(request: Request, exc: exc_class):
        return JSONResponse(status_code=kode, content={"pesan": str(exc)})


def tangani_semua_handler(app):
    for exc_class, kode in PETA_EXCEPTIONS.items():
        tangani_handler(app=app, exc_class=exc_class, kode=kode)
