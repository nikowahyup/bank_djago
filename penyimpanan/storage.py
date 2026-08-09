import json
from bank_djago.core.bank import Bank


class JSOnbase:

    file_rek = "Data/rekening.json"
    file_nasabah = "Data/nasabah.json"
    file_audit = "Data/audit.json"
    file_depo = "Data/deposito.json"


    @staticmethod
    def muat_bank():
        data_rekening = JSOnbase.muat_rekening(JSOnbase.file_rek)
        data_nasabah  = JSOnbase.muat_nasabah(JSOnbase.file_nasabah)
        data_deposito = JSOnbase.muat_deposito(JSOnbase.file_depo)
        data_audit    = JSOnbase.muat_audit()
        return Bank("Djago",data_audit,data_rekening,data_nasabah,data_deposito)

    @staticmethod
    def simpan_bank(bank):
        JSOnbase.simpan_nasabah(JSOnbase.file_nasabah,bank.data_nasabah_dict())
        JSOnbase.simpan_rekening(JSOnbase.file_rek,bank.data_rekening_dict())
        JSOnbase.simpan_deposito(JSOnbase.file_depo,JSOnbase.buat_data_deposito(bank))
        JSOnbase.simpan_audit(bank.audit_log)



    @staticmethod
    def simpan_rekening(filepath:str,data:dict):
        try:
            with open(filepath,"w") as file:
                json.dump(data,file,indent=4)
                return True

        except Exception as a:
            print(f"Gagal menyimpan {filepath} di {a}")
            return False
    @staticmethod
    def muat_rekening(filepath:str):
        try:
            with open(filepath,'r') as file:
                data = json.load(file)

            return data
        except FileNotFoundError:
            print("File tidak ditemukan. Memuat dengan file kosong")
            return {}

        except json.JSONDecodeError:
            # print(f"❌ File '{filepath}' rusak/format JSON salah. Menggunakan data kosong.")
            return {}


    @staticmethod
    def simpan_nasabah(filepath:str,data:dict):
        try:
            with open(filepath,"w") as file:
                json.dump(data,file,indent=4)
                return True

        except Exception as a:
            print(f"Gagal menyimpan {filepath} di {a}")
            return False


    @staticmethod
    def muat_nasabah(filepath:str):
        try:
            with open(filepath,'r') as file:
                data = json.load(file)
            return data

        except FileNotFoundError:
            print("File tidak ditemukan. Memuat dengan file kosong")
            return {}

        except json.JSONDecodeError:
            # print(f"❌ File '{filepath}' rusak/format JSON salah. Menggunakan data kosong.")
            return {}

    @staticmethod
    def simpan_audit(audit_log):
        with open(JSOnbase.file_audit, "w", encoding="utf-8") as file:
            json.dump(audit_log, file, indent=4, ensure_ascii=False)

    @staticmethod
    def muat_audit():
        try:
            with open(JSOnbase.file_audit, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []



    @staticmethod
    def buat_data_deposito(bank):
        data_deposito = {}


        for nik,nasabah in bank.data_nasabah.items():
            if not nasabah.deposito:
                continue

            data_deposito[nik] = {}

            for deposito in nasabah.deposito:
                data_deposito[nik][str(deposito.ID)] = deposito.ke_dict()

        return data_deposito

    @staticmethod
    def simpan_deposito(filepath,data):
        try:
            with open(filepath,"w") as file:
                json.dump(data,file,indent=4)
                return True
        except Exception as e:
            print(f"Gagal menyimpan {filepath} ke {e}")


    @staticmethod
    def muat_deposito(filepath):
        try:
            with open(filepath,"r") as file:
                data = json.load(file)

            return data
        except FileNotFoundError:
            # print("File tidak ditemukan. Memuat dengan file kosong")
            return {}

        except json.JSONDecodeError:
            # print(f"❌ File '{filepath}' rusak/format JSON salah. Menggunakan data kosong.")
            return {}