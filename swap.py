import asyncio
import base64
import aiohttp
import statistics
import time
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.compute_budget import set_compute_unit_price

async def get_recent_blockhash(client: AsyncClient):
    response = await client.get_latest_blockhash()
    return response.value.blockhash, response.value.last_valid_block_height

async def get_recent_prioritization_fees(client: AsyncClient, input_mint: str, debug: bool):
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getRecentPrioritizationFees",
        "params": [[input_mint]]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(client._provider.endpoint_uri, json=body) as response:
            json_response = await response.json()
            if debug:
                print(f"Prioritization fee response: {json_response}")
            if json_response and "result" in json_response:
                fees = [fee["prioritizationFee"] for fee in json_response["result"]]
                return statistics.median(fees)
    return 0

async def wait_for_confirmation(client: AsyncClient, signature: str, max_timeout: int = 60):
    start_time = time.time()
    while time.time() - start_time < max_timeout:
        try:
            status = await client.get_signature_statuses([signature])
            if status.value[0] is not None:
                return status.value[0].confirmation_status
        except Exception as e:
            print(f"Erreur lors de la vérification du statut de la transaction : {e}")
        await asyncio.sleep(1)
    return None

async def jupiter_swap(
    input_mint: str,
    output_mint: str,
    amount: int,
    auto_multiplier: float,
    debug: bool,
    private_key_base64: str,
    rpc_endpoint: str,
    slippage_bps: int
):
    """
    Effectue le swap via Jupiter.
    """
    # 1) Décoder la clé privée depuis Base64
    try:
        decoded_private_key = base64.b64decode(private_key_base64)
        if len(decoded_private_key) != 64:
            raise ValueError(f"Clé privée décodée incorrecte : {len(decoded_private_key)} bytes (attendu 64 bytes)")
        private_key = Keypair.from_bytes(decoded_private_key)
    except Exception as e:
        print(f"Erreur lors du décodage de la clé privée : {e}")
        return None

    WALLET_ADDRESS = private_key.pubkey()
    if debug:
        print(f"Adresse du wallet: {WALLET_ADDRESS}")

    # 2) Récupération du blockhash et du fee prioritaire
    async with AsyncClient(rpc_endpoint) as client:
        recent_blockhash, last_valid_block_height = await get_recent_blockhash(client)
        prioritization_fee = await get_recent_prioritization_fees(client, input_mint, debug)
        prioritization_fee *= auto_multiplier

    # 3) On ajoute le fee prioritaire au montant total que l'on envoie dans le swap
    total_amount = int(amount + prioritization_fee)
    if debug:
        print(f"Total amount (incluant les frais de priorité) : {total_amount} lamports")

    # 4) Obtenir le quote de Jupiter
    quote_url = (
        f"https://quote-api.jup.ag/v6/quote?"
        f"inputMint={input_mint}&outputMint={output_mint}&amount={total_amount}&slippageBps={slippage_bps}"
    )
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(quote_url, timeout=10) as response:
                response.raise_for_status()
                quote_response = await response.json()
                if debug:
                    print(f"Réponse du quote : {quote_response}")
    except aiohttp.ClientError as e:
        print(f"Erreur lors de la récupération du quote depuis Jupiter : {e}")
        return None

    # 5) Obtenir les données de swap de Jupiter
    swap_url = "https://quote-api.jup.ag/v6/swap"
    swap_data = {
        "quoteResponse": quote_response,
        "userPublicKey": str(WALLET_ADDRESS),
        "wrapUnwrapSOL": True
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(swap_url, json=swap_data, timeout=10) as response:
                response.raise_for_status()
                swap_response = await response.json()
                if debug:
                    print(f"Réponse du swap : {swap_response}")
    except aiohttp.ClientError as e:
        print(f"Erreur lors de la récupération des données de swap depuis Jupiter : {e}")
        return None

    # 6) Créer et signer la transaction
    async with AsyncClient(rpc_endpoint) as client:
        try:
            swap_transaction = swap_response['swapTransaction']
            import base64 as py_base64  # Pour éviter la confusion avec "base64" importé plus haut
            transaction_bytes = py_base64.b64decode(swap_transaction)
            unsigned_tx = VersionedTransaction.from_bytes(transaction_bytes)
            if debug:
                print("Transaction désérialisée avec succès.")

            # Ajouter l'instruction de Compute Budget pour les frais de priorité
            compute_budget_ix = set_compute_unit_price(int(prioritization_fee))
            unsigned_tx.message.instructions.insert(0, compute_budget_ix)

            # Signer la transaction
            signed_tx = VersionedTransaction(unsigned_tx.message, [private_key])
            if debug:
                print("Transaction signée avec succès.")

            # Envoyer la transaction
            result = await client.send_transaction(signed_tx)
            if debug:
                print("Transaction envoyée.")
            tx_signature = result.value
            if debug:
                print(f"Transaction ID : {tx_signature}")

            # On peut, si besoin, récupérer les détails de la transaction
            # (ici on peut juste retourner la signature)
            return result
        except Exception as e:
            print(f"Erreur lors de la création ou de l'envoi de la transaction : {str(e)}")
            return None

async def main(
    PRIVATE_KEY_BASE64: str,
    RPC_ENDPOINT: str,
    INPUT_MINT: str,
    OUTPUT_MINT: str,
    AMOUNT: int,
    AUTO_MULTIPLIER: float,
    SLIPPAGE_BPS: int,
    debug: bool
):
    try:
        # On transmet ici toutes les variables dont `jupiter_swap` a besoin
        result = await jupiter_swap(
            input_mint=INPUT_MINT,
            output_mint=OUTPUT_MINT,
            amount=AMOUNT,
            auto_multiplier=AUTO_MULTIPLIER,
            debug=debug,
            private_key_base64=PRIVATE_KEY_BASE64,
            rpc_endpoint=RPC_ENDPOINT,
            slippage_bps=SLIPPAGE_BPS
        )

        if result:
            tx_signature = result.value
            solscan_url = f"https://solscan.io/tx/{tx_signature}"
            if debug:
                print(f"Signature de la transaction : {tx_signature}")
            print(f"Lien Solscan : {solscan_url}")

            print("Attente de la confirmation de la transaction...")
            async with AsyncClient(RPC_ENDPOINT) as client:
                confirmation_status = await wait_for_confirmation(client, tx_signature)
                print(f"Statut de confirmation de la transaction : {confirmation_status}")

    except Exception as e:
        print(f"Une erreur s'est produite : {str(e)}")
