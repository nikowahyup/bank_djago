from pydantic import BaseModel,StrictInt, Field

class ResponseProfil(BaseModel):
    norek:str
    saldo:int
    level:int

class RequestProfil(BaseModel):
    norek: str = Field(max_length=16, min_length=16, pattern=r"^\d+$")
    pin:str = Field(min_length=6, max_length=6, pattern=r"^\d+$")
    nik: str = Field(max_length=16, min_length=16, pattern=r"^\d+$")

class RequestSetor(BaseModel):
    norek: str = Field(max_length=16, min_length=16, pattern=r"^\d+$")
    pin:str = Field(min_length=6, max_length=6, pattern=r"^\d+$")
    nik: str = Field(max_length=16, min_length=16, pattern=r"^\d+$")
    nominal:StrictInt = Field(gt=0)

class ResponseSetor(BaseModel):
    nominal:int
    saldo:int
