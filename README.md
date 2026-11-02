# Attendance Reminder System

Bot Telegram pengingat jadwal kuliah dan absensi, dibuat dengan Python, SQLite, dan Telegram Bot API.

## Fitur
- `/start` — memulai bot
- `/bantuan` — melihat panduan
- `/tambah Hari | HH:MM | Mata Kuliah | Ruangan` — menambah jadwal mingguan
- `/jadwal` — melihat jadwal milik pengguna
- `/hapus ID` — menghapus jadwal
- Pengingat otomatis 15 menit sebelum kelas
- Zona waktu WITA (`Asia/Makassar`)

## Persiapan Windows
1. Instal Python 3.10 atau lebih baru.
2. Ekstrak ZIP dan buka folder ini di Zed.
3. Buat dan aktifkan virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Instal dependensi:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Buka `.env`, lalu ganti nilai `TELEGRAM_BOT_TOKEN` dengan token dari BotFather.
6. Jalankan:

   ```powershell
   python app.py
   ```

7. Buka bot Telegram, tekan Start atau kirim `/start`.

## Contoh penggunaan
```text
/tambah Senin | 08:00 | Basis Data | Lab 2
/jadwal
/hapus 1
```

Jadwal berulang setiap minggu. Bot harus tetap berjalan dan komputer harus terhubung internet pada waktu pengingat.

## Keamanan
- Jangan bagikan token bot.
- Jangan unggah `.env` ke GitHub.
- Jika token bocor, buat token baru melalui BotFather.
