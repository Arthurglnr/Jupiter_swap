# **Projet Swap SOL → SPL Token** ⚡

Après **de nombreuses heures** de recherche, d'essais et de tests (parfois infructueux) 🏗️, j'ai enfin réussi à trouver un bout de code pour effectuer un **swap** entre du **SOL** et un **token SPL** sur la blockchain Solana. 

Le code original provient de diverses ressources trouvées sur internet 🕵️‍♀️, mais je l'ai **entièrement adapté** et **simplifié** afin qu'il soit **facile** à intégrer dans vos propres projets (notamment en l'appelant depuis un autre fichier Python). 🎉

---

## ✨ **Fonctionnalités principales** 

- **Swap automatique** entre SOL et le token SPL de votre choix.  
- **Paramétrage simple** : vous définissez vos paramètres (RPC endpoint, mints, clé privée, etc.) dans un fichier séparé.  
- **Support** des frais de priorité et du slippage.  
- **Readability** : Le code est commenté pour une compréhension plus rapide.

---

## 🚀 **Comment l'utiliser ?**

1. **Clonez** ce dépôt ou copiez le code dans votre projet.  
2. Installez les dépendances nécessaires :  
   ```bash
   pip install -r requirements.txt
   ```
(Vérifiez que vous utilisez bien Python 3.9 ou plus récent.)

3. Dans le fichier de configuration (par exemple buy_token.py), modifiez les variables selon vos besoins :
        PRIVATE_KEY_BASE64
        RPC_ENDPOINT (Mainnet, Devnet, etc.)
        INPUT_MINT (ex : So11111111111111111111111111111111111111112 pour SOL)
        OUTPUT_MINT (le token SPL souhaité)
        AMOUNT (montant en lamports)
        SLIPPAGE_BPS, etc.

4. Exécutez simplement votre fichier de configuration :
```bash
    python buy_token.py
```
   ... et tadaaa 🪄 votre swap devrait s’effectuer (si les conditions de marché et la liquidité le permettent).

##🛠️ Personnalisation##

    Vous pouvez modifier les fonctions dans le fichier swap.py pour ajouter ou enlever des fonctionnalités (ajuster les logs, les priorités, etc.).
    Vous pouvez aussi intégrer ce code dans votre propre workflow ou script plus grand.

##🤝 Remerciements##

    Au(x) projet(s) initial(aux) trouvé(s) sur internet pour l'idée de départ.
    À la communauté Solana et Jupiter pour leur documentation.

##⚠️ Avertissement##

    Ce code est fourni tel quel pour des fins d'exemple et de démonstration.
    L'utilisation de clés privées et de transactions sur un réseau principal (Mainnet) implique des risques.
    Soyez prudents avec vos clés privées et assurez-vous de comprendre ce que vous faites.

##Happy Swapping! 🥳##
