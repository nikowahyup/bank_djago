from pydantic import Field

from fastapi import FastAPI
from fastapi import Request
from pydantic import  BaseModel,StrictInt
from fastapi.responses import JSONResponse

from bank_djago import TransaksiService
from bank_djago.services.rekening.rekening_service import RekeningService
from bank_djago.services.exceptions import RekeningTerkunci,PinTidakCocok,RekeningTidakDitemukan, InputTidakValid





# inisiasi aplikasi fastapi
app = FastAPI(title="API bank djago")

PETA_EXCEPTIONS = {
    PinTidakCocok : 423,
    RekeningTerkunci : 402,
    RekeningTidakDitemukan : 410,
    InputTidakValid : 412
}


class ResponseProfil(BaseModel):
    saldo:int
    norek:str
    level:int = 1

class RequestProfil(BaseModel):
    norek: str = Field(max_length=16, min_length=16, pattern=r"^\d+$")
    pin:str = Field(min_length=6, max_length=6, pattern=r"^\d+$")
    nik: str = Field(max_length=16, min_length=16, pattern=r"^\d+$")

#response untuk melihat data rekening
@app.post('/rekening/profil',response_model=ResponseProfil)
def lihat_rekening(data:RequestProfil):
    RekeningService.verifikasi_pin_rekening(nik_aktif=data.nik, norek_aktif=data.norek, pin_input=data.pin)
    data_rekening = RekeningService.ambil_data_rekening(norek=data.norek)

    return{"saldo":data_rekening['saldo'],
           "norek":data_rekening['norek'],
           "level":data_rekening['level']}


class RequestSetor(BaseModel):
    norek: str = Field(max_length=16, min_length=16, pattern=r"^\d+$")
    pin:str = Field(min_length=6, max_length=6, pattern=r"^\d+$")
    nik: str = Field(max_length=16, min_length=16, pattern=r"^\d+$")
    nominal:StrictInt = Field(gt=0)

class ResponseSetor(BaseModel):
    nominal:int
    saldo:int

@app.post('/rekening/setor',response_model=ResponseSetor)
def setor_tunai(data:RequestSetor):
    TransaksiService.setor_tunai(nik_masuk=data.nik,norek=data.norek, pin=data.pin, nominal=data.nominal)
    data_rekening = RekeningService.ambil_data_rekening(norek=data.norek)
    return {'nominal':data.nominal,
            "saldo":data_rekening['saldo']}



def daftarkan_handler(exc_class, kode):
    @app.exception_handler(exc_class)
    async def handler(request: Request, exc: exc_class):
        return JSONResponse(status_code=kode, content={"pesan": str(exc)})

for exc_class, kode in PETA_EXCEPTIONS.items():
    daftarkan_handler(exc_class, kode)