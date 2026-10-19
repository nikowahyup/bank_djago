import datetime

from bank_djago.penyimpanan.sqlite.database import buat_koneksi_baca, buat_koneksi_tulis
from bank_djago.services.deposito.deposito_service import StatusDeposito

# 2001211321297690
# 6767454567674545

with buat_koneksi_baca() as koneksi_db:
    percobaan = koneksi_db.execute("SELECT percobaan_gagal FROM rekening WHERE norek = ?",("2001211321297690",)).fetchone()['percobaan_gagal']

    print(percobaan)

nik_pengirim = "6767454567674545"
norek_pengirim = "2001211321297690"
nik_penerima = "1111555599990000"
norek_penerima = "4001541399901664"

jatuh_tempo = datetime.date.today().isoformat()
status_baru = StatusDeposito.JATUH_TEMPO

# with buat_koneksi_tulis() as koneksi:
#     koneksi.execute("UPDATE deposito SET status = ?,jatuh_tempo = ? WHERE id = 27",(status_baru,jatuh_tempo))
#     data_terbaru = koneksi.execute("SELECT * FROM deposito WHERE id = 27").fetchone()
#
#     print(f"jatuh tempo terbaru : {datetime.date.fromisoformat(data_terbaru['jatuh_tempo'])}")
#     print(f"status terbaru : {data_terbaru['status']}")

from bank_djago.penyimpanan.sqlite.database import buat_koneksi_baca

with buat_koneksi_baca() as koneksi:
    for baris in koneksi.execute("SELECT * FROM sesi").fetchall():
        print(baris["token"], baris["nik"], baris["norek"], baris["kadaluwarsa"])
