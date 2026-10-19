from pydantic import BaseModel,StrictInt, Field

class ResponseProfil(BaseModel):
    norek:str
    saldo:int
    level:int

class RequestProfil(BaseModel):
    norek: str = Field(max_length=16, min_length=16, pattern=r"^\d+$")
    pin:str = Field(min_length=6, max_length=6, pattern=r"^\d+$")
    nik: str = Field(max_length=16, min_length=16, pattern=r"^\d+$")




class RequestTransaksi(BaseModel):
    nik: str = Field(min_length=16, max_length=16, pattern=r"^\d+$")
    norek: str = Field(min_length=16, max_length=16, pattern=r"^\d+$")
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


class RequestAjukanPinjaman(BaseModel):
    nik: str = Field(min_length=16, max_length=16, pattern=r"^\d+$")
    norek: str = Field(min_length=16, max_length=16, pattern=r"^\d+$")
    pin: str = Field(min_length=6, max_length=6, pattern=r"^\d+$")
    nominal: StrictInt = Field(gt=0)
    tenor:StrictInt = Field(gt=0)

class ResponseAjukanPinjaman(BaseModel):
    nominal:int
    id_pinjaman:int

