class AdminService:

    PASSWORD = "admin123"


    @staticmethod
    def verifikasi_password(password):
        return password == AdminService.PASSWORD
