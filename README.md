# 🔁 Auto Claim & Multi-Token Swapper for 0G EVM Testnet

Script ini akan:
1. Menanyakan nominal swap setiap token (sekali di awal).
2. Menanyakan berapa kali swap dilakukan per pasangan token.
3. Melakukan claim faucet semua token di setiap wallet.
4. Melakukan swap **setiap kombinasi token** (misal: ETH → BTC, ETH → USDT, dst.).
5. Menunggu 24 jam, lalu mengulangi proses **tanpa menanyakan input ulang**.
6. Support **multi-wallet** dari file `wallet.txt`.

---

## 🧩 Dependensi

Instal modul berikut:

```bash
pip install web3
```

---

## 🗂 Struktur File

```bash
.
├── main.py         # Script utama
└── wallet.txt     # Daftar private key (satu per baris)
```

---

## 💡 Cara Menjalankan

```bash
python main.py
```

Kamu akan diminta:

- Nominal swap per token (dalam ETH-like format, misal 0.001)
- Berapa kali swap dilakukan per kombinasi token

Setelah itu proses otomatis berjalan terus-menerus setiap 24 jam.

---

## 🧠 Fitur

✅ Mendukung banyak wallet  
✅ Claim faucet semua token  
✅ Swap otomatis antar semua pasangan token  
✅ Menyesuaikan jumlah swap jika saldo tidak cukup  
✅ Ulangi otomatis setiap 24 jam  
✅ Aman dihentikan dengan Ctrl+C

---

## 🔐 Format wallet.txt

Isi seperti ini:

```txt
0xabc123... (private key)
0xdef456...
```
