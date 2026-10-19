from fastapi import FastAPI
from .exception import tangani_semua_handler
from .rute import route_rekening, route_transaksi, route_pinjaman,route_deposito

# inisiasi aplikasi fastapi
app = FastAPI(title="API bank djago")

# ubah exceptiona jadi kode response
tangani_semua_handler(app=app)

# sambungkan rute domain ke app
app.include_router(route_rekening.router)
app.include_router(route_transaksi.router)
app.include_router(route_pinjaman.router)
app.include_router(route_deposito.router)







