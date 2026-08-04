from colorama import Fore,init,Style



init(autoreset=True)
class UI:


    SIMBOL = {
        "bank": "🏦",
        "uang": "💰",
        "rekening": "💳",
        "nasabah": "👤",
        "audit": "📜",
        "rekap": "📊",
        "berhasil": "✔",
        "gagal": "✘",
        "peringatan": "⚠",
        "kunci": "🔒"
    }



    @staticmethod
    def garis():
        print("─" * 40)

    @staticmethod
    def header(judul):
        print("╔" + "═" * 50 + "╗")
        print(f"║{judul.center(50)}║")
        print("╚" + "═" * 50 + "╝")

    @staticmethod
    def wadah_info(nama,norek,saldo):

        print("╔" + "═" * 37 + "╗")
        print(f"  {UI.SIMBOL["nasabah"]} Nama   : {nama}")
        print(f"  {UI.SIMBOL["rekening"]} No.Rek : {norek}")
        print(f"  {UI.SIMBOL["uang"]} Saldo  : Rp{saldo}")
        print("╚" + "═" * 37 + "╝")

    @staticmethod
    def sukses(pesan):
        print(Fore.GREEN + f'✔{pesan}!')

    @staticmethod
    def gagal(pesan):
        print(Fore.RED + f"✘ {pesan}")

    @staticmethod
    def peringatan(pesan):
        print(Fore.YELLOW + f"⚠ {pesan}")

    @staticmethod
    def info(teks):
        return Fore.CYAN + teks + Style.RESET_ALL
