import json
from bank_djago.core.bank import Bank


class JsonStorage:

    file_rek = "Data/rekening.json"
    file_nasabah = "Data/nasabah.json"
    file_audit = "Data/audit.json"

    file_pinjaman = "Data/pinjaman.json"




    @staticmethod
    def muat_bank():
        data_rekening = JsonStorage.muat_json(JsonStorage.file_rek,{})
        data_nasabah = JsonStorage.muat_json(JsonStorage.file_nasabah,{})
        data_audit = JsonStorage.muat_json(JsonStorage.file_audit,[])

        data_pinjaman = JsonStorage.muat_json(JsonStorage.file_pinjaman,{})

        return Bank("Djago",data_audit,data_nasabah,data_rekening,data_pinjaman)

    @staticmethod
    def simpan_bank(bank):

        JsonStorage.simpan_json(JsonStorage.file_nasabah,bank.data_nasabah_dict())

        JsonStorage.simpan_json(JsonStorage.file_rek,bank.data_rekening_dict())



        JsonStorage.simpan_json(JsonStorage.file_audit,bank.audit_log)

        JsonStorage.simpan_json(JsonStorage.file_pinjaman,JsonStorage.buat_data_pinjaman(bank))





    @staticmethod
    def simpan_json(filepath,data):
        try:
            with open(filepath,"w",encoding="utf-8") as file:
                json.dump(data,file,indent=4,ensure_ascii=False)
            return True

        except Exception as e:
            print(f"Gagal menyimpan {filepath} di {e}")
            return False


    @staticmethod
    def muat_json(filepath,default):
        try:
            with open(filepath,"r",encoding="utf-8") as file:
                return json.load(file)

        except FileNotFoundError:
            return default

        except json.JSONDecodeError:
            return default






    @staticmethod
    def buat_data_pinjaman(bank):
        data_pinjaman = {}

        for pinjaman in bank.daftar_pinjaman:
            nik = pinjaman.pemilik.NIK

            if nik not in data_pinjaman:
                data_pinjaman[nik] = {}

            data_pinjaman[nik][str(pinjaman.ID)] = pinjaman.ke_dict()

        return data_pinjaman
