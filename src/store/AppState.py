class AppState:
    _instance = None

    # Ini memastikan class ini hanya dibuat 1 kali (Singleton)
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppState, cls).__new__(cls)
            # Inisialisasi state kosong saat aplikasi baru dibuka
            # cls._instance.user_aktif = None  
            # cls._instance.keranjang_booking = []
            cls._instance.width = 1280
            cls._instance.height = 720
            cls._instance.isLightTheme = True
            cls._instance.indoDbPath = "D:/Arya/Skripsi/alg_tester/database/indonesia.db"
            cls._instance.appDbPath = "D:/Arya/Skripsi/alg_tester/database/app.db"
        return cls._instance

# Buat variabel globalnya
state = AppState()