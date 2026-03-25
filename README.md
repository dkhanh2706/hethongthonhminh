Chạy lệnh sau:

1. Xóa môi trường cũ
   Remove-Item -Recurse -Force venv
2. Tạo môi trường ảo
   python -m venv venv
3. Kích hoạt venv
   .\venv\Scripts\activate
4. Cài pip
   python -m ensurepip
5. Cài thư viện Flask
   pip install flask flask-cors
6. Chạy Backend
   python app.py
