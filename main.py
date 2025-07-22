from web3 import Web3
from eth_account import Account
import time

# === KONFIGURASI ===
RPC_URL = "https://evmrpc-testnet.0g.ai/"
ROUTER_ADDRESS = Web3.to_checksum_address("0x21Dcc0c3d0d1b4e1c92ef154F30329d4c165a6F8")
CHAIN_ID = 16601
GAS_PRICE = Web3.to_wei("2", "gwei")
DELAY_SEHARI = 86400  # 24 jam

# === TOKEN ===
TOKENS = {
    "ETH":  Web3.to_checksum_address("0x0fe9b43625fa7edd663adcec0728dd635e4abf7c"),
    "BTC":  Web3.to_checksum_address("0x36f6414ff1df609214ddaba71c84f18bcf00f67d"),
    "USDT": Web3.to_checksum_address("0x3ec8a8705be1d5ca90066b37ba62c4183b024ebf"),
    "GIMO": Web3.to_checksum_address("0xba2ae6c8cddd628a087d7e43c1ba9844c5bf9638"),
    "STOG": Web3.to_checksum_address("0x14d2f76020c1ecb29bcd673b51d8026c6836a66a")
}

# === ABI ===
ERC20_ABI = [
    {"name": "approve", "type": "function", "inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}],
     "outputs": [{"name": "", "type": "bool"}], "stateMutability": "nonpayable"},
    {"name": "balanceOf", "type": "function", "inputs": [{"name": "owner", "type": "address"}],
     "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view"}
]

ROUTER_ABI = [{
    "name": "swapExactTokensForTokens",
    "type": "function",
    "inputs": [
        {"name": "amountIn", "type": "uint256"},
        {"name": "amountOutMin", "type": "uint256"},
        {"name": "path", "type": "address[]"},
        {"name": "to", "type": "address"},
        {"name": "deadline", "type": "uint256"}
    ],
    "outputs": [{"name": "", "type": "uint256[]"}],
    "stateMutability": "nonpayable"
}]

# === INISIALISASI ===
w3 = Web3(Web3.HTTPProvider(RPC_URL))
router = w3.eth.contract(address=ROUTER_ADDRESS, abi=ROUTER_ABI)

def read_wallets():
    with open("wallet.txt") as f:
        return [line.strip() for line in f if line.strip().startswith("0x")]

def claim_token(address, private_key, token_addr):
    try:
        tx = {
            "to": token_addr,
            "value": 0,
            "gas": 100000,
            "gasPrice": GAS_PRICE,
            "nonce": w3.eth.get_transaction_count(address),
            "data": "0x1249c58b",
            "chainId": CHAIN_ID,
        }
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"    [✓] Claim TX sent: {tx_hash.hex()}")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            print("    [✓] Claim berhasil")
        else:
            print("    [!] Claim gagal (tunggu 24 jam)")
    except Exception as e:
        print(f"    [!] Claim error: {e}")

def swap_token(address, private_key, token_in_addr, token_out_addr, amount_to_swap):
    token_in = w3.eth.contract(address=token_in_addr, abi=ERC20_ABI)
    balance = token_in.functions.balanceOf(address).call()

    if balance == 0:
        print("    [-] Tidak ada saldo")
        return
    if amount_to_swap > balance:
        amount_to_swap = balance
        print(f"    [-] Disesuaikan ke saldo: {amount_to_swap}")
    if amount_to_swap == 0:
        print("    [-] Tidak bisa swap 0")
        return

    try:
        # Approve
        nonce = w3.eth.get_transaction_count(address)
        approve_tx = token_in.functions.approve(ROUTER_ADDRESS, amount_to_swap).build_transaction({
            "from": address,
            "gas": 60000,
            "gasPrice": GAS_PRICE,
            "nonce": nonce,
            "chainId": CHAIN_ID,
        })
        signed_approve = w3.eth.account.sign_transaction(approve_tx, private_key)
        w3.eth.send_raw_transaction(signed_approve.raw_transaction)
        w3.eth.wait_for_transaction_receipt(signed_approve.hash)
        time.sleep(2)

        # Swap
        nonce += 1
        deadline = int(time.time()) + 300
        swap_tx = router.functions.swapExactTokensForTokens(
            amount_to_swap,
            0,
            [token_in_addr, token_out_addr],
            address,
            deadline
        ).build_transaction({
            "from": address,
            "gas": 200000,
            "gasPrice": GAS_PRICE + w3.to_wei("0.1", "gwei"),
            "nonce": nonce,
            "chainId": CHAIN_ID
        })
        signed_swap = w3.eth.account.sign_transaction(swap_tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_swap.raw_transaction)
        name_in = [k for k, v in TOKENS.items() if v == token_in_addr][0]
        name_out = [k for k, v in TOKENS.items() if v == token_out_addr][0]
        print(f"    [✓] Swap {name_in} → {name_out} TX: {tx_hash.hex()}")

        w3.eth.wait_for_transaction_receipt(tx_hash)
    except Exception as e:
        print(f"    [!] Swap error: {e}")

def main():
    wallets = read_wallets()

    # Input nominal swap per token
    nominal_swap = {}
    for name in TOKENS:
        try:
            val = input(f"Masukkan nominal {name} yang ingin di-swap: ")
            nominal_swap[name] = int(float(val) * 1e18)
        except:
            print("    [-] Input tidak valid, default 0")
            nominal_swap[name] = 0

    try:
        jumlah_swap = int(input("Berapa kali swap diulang per pair? "))
    except:
        jumlah_swap = 1

    # Loop setiap 24 jam
    try:
        while True:
            print("\n🔁 Menjalankan proses claim dan swap...\n")
            for idx, pk in enumerate(wallets, 1):
                acct = Account.from_key(pk)
                address = acct.address
                print(f"\n[{idx}] Wallet: {address}")

                # Claim semua token
                for name, token_addr in TOKENS.items():
                    print(f"--- Claim {name} ---")
                    claim_token(address, pk, token_addr)
                    time.sleep(1)

                # Swap kombinasi antar semua token
                for name_in, token_in in TOKENS.items():
                    amount = nominal_swap.get(name_in, 0)
                    if amount > 0:
                        for name_out, token_out in TOKENS.items():
                            if name_in != name_out:
                                for i in range(jumlah_swap):
                                    print(f"--- Swap {name_in} → {name_out} ke-{i+1} ---")
                                    swap_token(address, pk, token_in, token_out, amount)
                                    time.sleep(1)

            print("\n🕐 Selesai. Menunggu 24 jam...\n")
            time.sleep(DELAY_SEHARI)
    except KeyboardInterrupt:
        print("\nProses dihentikan oleh pengguna.")

if __name__ == "__main__":
    main()
