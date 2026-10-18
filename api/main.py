from fastapi import FastAPI
from pydantic import  BaseModel,StrictInt, Field
from bank_djago import TransaksiService
from bank_djago.services.rekening.rekening_service import RekeningService
from .exception import tangani_semua_handler

# inisiasi aplikasi fastapi
app = FastAPI(title="API bank djago")

tangani_semua_handler(app=app)
# 2001211321297690
# 6767454567674545

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



