from fastapi import FastAPI

from bank_djago import TransaksiService
from bank_djago.services.rekening.rekening_service import RekeningService
from .exception import tangani_semua_handler
from .skema import RequestSetor
from .skema import ResponseSetor
from .rute import rekening

# inisiasi aplikasi fastapi
app = FastAPI(title="API bank djago")

tangani_semua_handler(app=app)
app.include_router(rekening.router)




@app.post('/rekening/setor',response_model=ResponseSetor)
def setor_tunai(data:RequestSetor):
    TransaksiService.setor_tunai(nik_masuk=data.nik,norek=data.norek, pin=data.pin, nominal=data.nominal)
    data_rekening = RekeningService.ambil_data_rekening(norek=data.norek)
    return {'nominal':data.nominal,
            "saldo":data_rekening['saldo']}



