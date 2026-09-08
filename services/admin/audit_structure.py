STRUKTUR_AUDIT = {
    "administratif": {
        "nasabah": [
            "pendaftaran_nasabah"
        ],
        "rekening": [
            "pembukaan_rekening",
            "peningkatan_level_rekening",
            "penurunan_level_rekening",
            "pengajuan_penutupan_rekening",
            "persetujuan_penutupan_rekening",
            "penolakan_penutupan_rekening",
            "pemblokiran_rekening",
            "pembukaan_blokir_rekening",
            "penggantian_pin_rekening"
        ],
        "pinjaman": [
            "pengajuan_pinjaman",
            "persetujuan_pinjaman",
            "penolakan_pinjaman"
        ]
    },

    "finansial": {
        "rekening": [
            "setor_tunai",
            "tarik_tunai",
            "transfer_keluar",
            "penerimaan_transfer",
            "pemberian_bunga_tabungan",
            "pemotongan_biaya_admin",
            "penarikan_saldo_penutupan",
            "pemindahan_saldo_penutupan",
            "penerimaan_saldo_penutupan"
        ],
        "deposito": [
            "pembukaan_deposito",
            "pencairan_deposito",
            "perpanjangan_deposito_aro"
        ],
        "pinjaman": [
            "pencairan_pinjaman",
            "pembayaran_cicilan_pinjaman"
        ]
    }
}