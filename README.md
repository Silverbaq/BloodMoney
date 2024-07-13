# BloodMoney
This is a learning project, of making my own cryptocurrency.

## Features
- [ ] Blockchain
  - [x] Mining
  - [ ] Distributed networking (LAN)
  - [x] Decentralized
  - [x] Sync between instances 
- [x] Wallet
  - [x] Transactions
  - [x] Balance
  - [X] Mining reward

## How to run

### Start instances
* `FLASK_APP=app.py python app.py 5000`
* `FLASK_APP=app.py python app.py 5001 http://127.0.0.1:5000`
* `FLASK_APP=app.py python app.py 5002 http://127.0.0.1:5000`

## Features

### Mining
* HTTP: `POST` 
* URL: `http://127.0.0.1:5001/mine`
* Body:
```
 {
    "wallet_address": "0c259295fed376b86376829a90fe08324db400b9fc6118af5c68254c43c4f2b9db887ac754a60822e35fde7292089a5d36fea8f4d69a9ea5cb2488bf768d0a95" 
 }
```

### Wallet
#### Creating a wallet:
  * HTTP: `GET`
  * URL: `http://127.0.0.1:5001/wallet/new`

#### Get wallet balance:
  * HTTP: `GET`
  * URL: `http://127.0.0.1:5001/wallet/balance/<wallet-address>`

Example: `http://127.0.0.1:5001/wallet/balance/0c259295fed376b86376829a90fe08324db400b9fc6118af5c68254c43c4f2b9db887ac754a60822e35fde7292089a5d36fea8f4d69a9ea5cb2488bf768d0a95`

#### Make transaction
  * HTTP: `POST`
  * URL: `http://127.0.0.1:5001/wallet/transaction`
  * Body:
```
{
    "sender_private_key": "e443639c77170069ed9c8ada7392aacaddc52ed7a7c1866cdd3b3e7b3267deb3",
    "recipient": "dc6f7debebefa8e73abbeba7cdf96d0ec9fbb82139959c7ddb7faf4c46e40ea3242ee3dec15148da244eb2f772116a25467d78b2e7677ffde0260b700b0384d3",
    "amount": "5"
}
```