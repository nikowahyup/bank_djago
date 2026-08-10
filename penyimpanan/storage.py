import json
from bank_djago.core.bank import Bank


class JsonStorage:

    file_rek = "Data/rekening.json"
    file_nasabah = "Data/nasabah.json"
    file_audit = "Data/audit.json"
    file_depo = "Data/deposito.json"




    @staticmethod
    def muat_bank():
        data_rekening = JsonStorage.muat_json(JsonStorage.file_rek,{})
        data_nasabah = JsonStorage.muat_json(JsonStorage.file_nasabah,{})
        data_audit = JsonStorage.muat_json(JsonStorage.file_audit,[])
        data_deposito= JsonStorage.muat_json(JsonStorage.file_depo,{})
        return Bank("Djago",data_audit,data_rekening,data_nasabah,data_deposito)

    @staticmethod
    def simpan_bank(bank):
        JsonStorage.simpan_json(JsonStorage.file_rek,bank.data_rekening_dict())
        JsonStorage.simpan_json(JsonStorage.file_nasabah,bank.data_nasabah_dict())
        JsonStorage.simpan_json(JsonStorage.file_depo,JsonStorage.buat_data_deposito(bank))
        JsonStorage.simpan_json(JsonStorage.file_audit,bank.audit_log)





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
    def buat_data_deposito(bank):
        data_deposito = {}


        for nik,nasabah in bank.data_nasabah.items():
            if not nasabah.deposito:
                continue

            data_deposito[nik] = {}

            for deposito in nasabah.deposito:
                data_deposito[nik][str(deposito.ID)] = deposito.ke_dict()

        return data_deposito




