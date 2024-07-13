# BloodMoney
This is a learning project, of making my own cryptocurrency.

## Features
- [ ] Blockchain
  - [x] Mining
  - [ ] Distributed networking (LAN)
  - [x] Decentralized
  - [x] Sync between instances 
- [ ] Wallet
  - [ ] Transactions
  - [ ] Balance
  - [ ] Mining reward

## How to run

### Start instances
* `FLASK_APP=app.py python app.py 5000`
* `FLASK_APP=app.py python app.py 5001 http://127.0.0.1:5000`
* `FLASK_APP=app.py python app.py 5002 http://127.0.0.1:5000`

### Mining
* `http://127.0.0.1:5001/mine`