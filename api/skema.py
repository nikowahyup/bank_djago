from pydantic import BaseModel,StrictInt, Field
from datetime import date,datetime

class ResponseProfil(BaseModel):
    norek:str
    saldo:int
    level:int

class RequestProfil(BaseModel):
    norek: str = Field(max_length=16, min_length=16, pattern=r"^\d+$")
    pin:str = Field(min_length=6, max_length=6, pattern=r"^\d+$")
    nik: str = Field(max_length=16, min_length=16, pattern=r"^\d+$")


#-------------------------------------------------------------------------------------

class RequestTransaksi(BaseModel):
    pin: str = Field(min_length=6, max_length=6, pattern=r"^\d+$")
    nominal: StrictInt = Field(gt=0)

class RequestSetor(RequestTransaksi):
    pass

class RequestTarik(RequestTransaksi):
    pass

class RequestTransfer(RequestTransaksi):
    norek_tujuan: str = Field(min_length=16, max_length=16, pattern=r"^\d+$")

class ResponseTransaksi(BaseModel):
    nominal:int
    saldo:int

class ResponseSetor(ResponseTransaksi):
    pass

class ResponseTarik(ResponseTransaksi):
    pass

class ResponseTransfer(ResponseTransaksi):
    norek_penerima:str
#-------------------------------------------------------------------------------------

class RequestAjukanPinjaman(BaseModel):
    pin: str = Field(min_length=6, max_length=6, pattern=r"^\d+$")
    nominal: StrictInt = Field(gt=0)
    tenor:StrictInt = Field(gt=0)

class ResponseAjukanPinjaman(BaseModel):
    nominal:int
    id_pinjaman:int

class RequestCairkanPinjaman(BaseModel):
    pin: str = Field(min_length=6, max_length=6, pattern=r"^\d+$")
    id_pinjaman:StrictInt = Field(gt=0)


class ResponseCairkanPinjaman(BaseModel):
    nominal:int
    id_pinjaman:int
    norek:str

class RequestBayarCicilan(BaseModel):
    pin: str = Field(min_length=6, max_length=6, pattern=r"^\d+$")
    id_pinjaman:StrictInt = Field(gt=0)


class ResponseBayarCicilan(BaseModel):
    status:str
    tanggal_bayar_selanjutnya:date | None = None
    cicilan_selanjutnya:int
    id_pinjaman:int

#--------------------------------------------------------------------------------------

class RequestBukaDeposito(BaseModel):
    pin: str = Field(min_length=6, max_length=6, pattern=r"^\d+$")
    lama_bulan:StrictInt = Field(gt=0)
    jenis_aro:str
    lama_aro: StrictInt | None = Field(default=None, gt=0)
    nominal:StrictInt = Field(gt=0)

class ResponseBukaDeposito(BaseModel):
    id_deposito:int
    norek:str
    nominal:int

class RequestCairkanDeposito(BaseModel):
    pin: str = Field(min_length=6, max_length=6, pattern=r"^\d+$")
    id_deposito: StrictInt = Field(gt=0)


class ResponseCairkanDeposito(BaseModel):
    total_pencairan: int
    norek: str
    id_deposito: int


class RequestHentikanAro(BaseModel):
    pin: str = Field(min_length=6, max_length=6, pattern=r"^\d+$")
    id_deposito: StrictInt = Field(gt=0)


class ResponseHentikanAro(BaseModel):
    id_deposito: int

class RequestLogin(BaseModel):
    nik: str = Field(min_length=16, max_length=16, pattern=r"^\d+$")
    norek: str = Field(min_length=16, max_length=16, pattern=r"^\d+$")
    pin: str = Field(min_length=6, max_length=6, pattern=r"^\d+$")

class ResponseLogin(BaseModel):
    token:str
    kedaluwarsa:datetime