from fastapi import FastAPI
from .exception import tangani_semua_handler
from .rute import rekening, transaksi

# inisiasi aplikasi fastapi
app = FastAPI(title="API bank djago")

# ubah exceptiona jadi kode response
tangani_semua_handler(app=app)

# sambungkan rute domain ke app
app.include_router(rekening.router)
app.include_router(transaksi.router)








