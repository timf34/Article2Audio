To run locally:

Set up the server

```angular2html
cd server
pip install -r requirements.txt
python app.py
```

Set up the client

```angular2html
cd client
npm install
npm start
```

To run on Docker:

```angular2html
# Build
docker-compose build

# Run
docker-compose up
```


To run on production:

Run the `setup_ngnix.sh` script to set up the server.

```angular2html
sudo bash setup_nginx.sh
```

Then just run `docker compose up --build` from the root directory. 