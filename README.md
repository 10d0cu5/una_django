Possible calls:
Swagger Doc: /

Populate the database: (populates with demo data)
POST - /api/v1/populate/ 

Filtering:
GET - Header: user-id aaa /api/v1/levels?page=0&size=10&start=02-10-2021 00:00&end=02-12-2021 00:00
GET - Header: user-id aaa /api/v1/levels/1
GET - Header: user-id aaa /api/v1/levels/export/json or /csv
GET - Header: user-id aaa /api/v1/highlow?high=150&low=100&page=0&size=10

Running server:
pip3 install requirements.txt
python3 manage.py runserver 8080