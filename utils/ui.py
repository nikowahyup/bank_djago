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

    BIRU   = "\033[94m"
    CYAN   = "\033[96m"
    PUTIH  = "\033[97m"
    HIJAU  = "\033[92m"
    KUNING = "\033[93m"
    MERAH  = "\033[91m"

    RESET = "\033[0m"


    @staticmethod
    def header(judul,warna=None):
        if warna is None:
            warna = UI.BIRU


        print(warna + "╔" + "═" * 50 + "╗")
        print(f"║{judul.center(50)}║")
        print( warna + "╚" + "═" * 50 + "╝")
        print(UI.RESET)
    @staticmethod
    def garis():
        print("─" * 40)


    @staticmethod
    def info(teks):
        return Fore.CYAN + teks + Style.RESET_ALL


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

    kelas = {1:"🥉",
             2:"🥈",
             3:"🥇",
             4:"💎"}
