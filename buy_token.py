
from swap import main
import asyncio

# Vous définissez vos variables ici, ou vous les chargez d’un config/env
PRIVATE_KEY_BASE64 = ""                                      #Votre Clé Privet en Base 64
RPC_ENDPOINT = "https://api.mainnet-beta.solana.com"         #RPC Mainnet
INPUT_MINT = "So11111111111111111111111111111111111111112"   #Solana
OUTPUT_MINT = "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr" #POPCAT
AMOUNT = 1000000         # 0.001 SOL (en lamports)
AUTO_MULTIPLIER = 1.1    # 10% d'augmentation des fees (0.0 pour qu'aucun fee s'applique a la transaction)
SLIPPAGE_BPS = 1000      # 10% de tolérance de slippage
debug = True

# On exécute la fonction main() asynchrone
asyncio.run(
    main(
        PRIVATE_KEY_BASE64,
        RPC_ENDPOINT,
        INPUT_MINT,
        OUTPUT_MINT,
        AMOUNT,
        AUTO_MULTIPLIER,
        SLIPPAGE_BPS,
        debug
    )
)
