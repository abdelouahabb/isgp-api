import os

BASE_DIR = os.path.dirname(__file__)

def _read(filename):
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8") as f:
        return f.read().strip()

DAY_4_DATA = {
    "day_number": 4,
    "folder": "day_4",
    "badge": "Jour 4 • Secrets, Tokens & Rate Limit",
    "title": "Le Cœur d'une API : Gestion des Secrets, Jetons (Bearer Tokens), Clés API et Rate Limiting",
    "goal": "Maîtriser les mécanismes vitaux d'une API professionnelle : isoler les secrets dans les variables d'environnement, générer et vérifier des jetons d'accès signés (Bearer Tokens), authentifier par X-API-Key et protéger le serveur contre la surcharge avec un limiteur de débit (Rate Limiting — HTTP 429).",
    "starter_filename": "day_4/02_bearer_tokens_signes.py",
    "files": [
        "day_4/01_secrets_et_api_key.py",
        "day_4/02_bearer_tokens_signes.py",
        "day_4/03_rate_limiting_429.py",
    ],
    "lessons": [
        {
            "id": "d4-l1",
            "file": "day_4/01_secrets_et_api_key.py",
            "title": "4.1 — Gestion des Secrets (`os.environ`, `SECRET_KEY`) & Clés API (`X-API-Key`)",
            "duration": "55 min",
            "analogy": {
                "title": "Séparer le plan de l'architecte de la combinaison du coffre-fort",
                "text": "Le code source Python est partagé entre collègues et versionné dans Git. Si vous écrivez vos mots de passe ou votre clé maîtresse directement dans le code, toute personne lisant le fichier possède les clés du coffre. Les **Secrets** doivent toujours être stockés dans les **Variables d'Environnement** du système."
            },
            "explanation": [
                "**Règle n°1 — Zéro secret en dur dans le code** : On récupère les secrets via le module standard `os` : `SECRET_KEY = os.environ.get('API_SECRET_KEY')`.",
                "**Règle n°2 — Ne jamais exposer un secret dans l'URL** : Une URL (`?api_key=1234`) reste enregistrée en clair dans l'historique et les journaux (logs) des serveurs. Les clés et jetons se transmettent exclusivement dans les **En-têtes HTTP (`Headers`)**.",
                "**Authentification Machine-à-Machine par `X-API-Key`** : Le client envoie l'en-tête `X-API-Key: <cle>`. Le serveur compare cette valeur en temps constant (`hmac.compare_digest`) avec le secret de son environnement."
            ],
            "code": _read("01_secrets_et_api_key.py"),
            "line_explanations": [
                {"lines": "9-10", "text": "`os.environ.get(...)` interroge les variables d'environnement du système d'exploitation."},
                {"lines": "15", "text": "`request.headers.get('X-API-Key', '')` extrait l'en-tête HTTP d'authentification."},
                {"lines": "18-21", "text": "`hmac.compare_digest(a, b)` compare deux secrets en temps constant et renvoie `401 Unauthorized` en cas d'écart."}
            ],
            "sandbox_preset": {
                "label": "Tester GET /api/sandbox/admin-stats (X-API-Key)",
                "method": "GET",
                "url": "/api/sandbox/admin-stats",
                "headers": {"X-API-Key": "isgp-secret-2026"},
                "body": ""
            },
            "python_runner": {
                "prompt": "Expérimentez la lecture des variables d'environnement et le masquage sécurisé des secrets :",
                "initial_code": '''import os
import hmac

os.environ["ISGP_API_SECRET"] = "sk_live_98f7a6b5c4d3e2f1"

secret_serveur = os.environ.get("ISGP_API_SECRET")
masque = secret_serveur[:7] + "..." + secret_serveur[-4:]
print("Secret chargé depuis l'environnement (masqué) :", masque)

cle_client = "sk_live_98f7a6b5c4d3e2f1"
est_valide = hmac.compare_digest(cle_client, secret_serveur)
print("La clé du client est-elle authentique ?", est_valide)'''
            },
            "vscode_instructions": {
                "filename": "day_4/01_secrets_et_api_key.py",
                "steps": [
                    "Ouvrir le fichier `day_4/01_secrets_et_api_key.py` dans VS Code ou Antigravity IDE.",
                    "Exécuter `.venv/bin/python day_4/01_secrets_et_api_key.py`."
                ]
            }
        },
        {
            "id": "d4-l2",
            "file": "day_4/02_bearer_tokens_signes.py",
            "title": "4.2 — Jetons d'Accès Signés (`Bearer Token` / JWT) : Émission, Signature & Expiration",
            "duration": "65 min",
            "analogy": {
                "title": "La carte magnétique temporaire d'un hôtel",
                "text": "Une clé fixe ne contient ni l'identité de l'utilisateur, ni son rôle, ni de date d'expiration. Avec un **Token (Jeton Bearer)** :\n1. L'utilisateur s'identifie une seule fois sur `POST /api/auth/token`.\n2. Le serveur génère un jeton contenant `{\"utilisateur\": \"stagiaire\", \"role\": \"participant\"}`, le **signe mathématiquement** avec sa `SECRET_KEY`, et lui fixe une **durée de vie** (ex. 300 secondes).\n3. À chaque requête suivante, le client présente ce jeton dans l'en-tête `Authorization: Bearer <token>`."
            },
            "explanation": [
                "**Intégrité par Signature Cryptographique (HMAC)** : Le jeton est composé des données et d'une signature calculée avec la `SECRET_KEY` connue uniquement du serveur. Si un seul caractère du jeton est modifié, la vérification échoue (`BadSignature`).",
                "**Outil intégré dans Flask (`itsdangerous`)** : Flask installe nativement `URLSafeTimedSerializer`, qui permet de signer et de vérifier des tokens avec expiration (`max_age=300` secondes).",
                "**Format standard de l'en-tête HTTP** : `Authorization: Bearer <le_jeton_signe>`."
            ],
            "code": _read("02_bearer_tokens_signes.py"),
            "line_explanations": [
                {"lines": "9-10", "text": "`URLSafeTimedSerializer(SECRET_KEY)` initialise le moteur de signature cryptographique avec le secret du serveur."},
                {"lines": "20", "text": "`signer.dumps(charge_utile)` encode le dictionnaire, ajoute l'horodatage et signe l'ensemble."},
                {"lines": "30-32", "text": "Vérifie la présence de l'en-tête standard `Authorization: Bearer ...`."},
                {"lines": "36-41", "text": "`signer.loads(token, max_age=300)` vérifie la signature cryptographique et l'absence d'expiration."}
            ],
            "sandbox_preset": {
                "label": "1. Émettre un Bearer Token : POST /api/sandbox/auth/token",
                "method": "POST",
                "url": "/api/sandbox/auth/token",
                "body": '{\n  "identifiant": "stagiaire",\n  "mot_de_passe": "isgp2026"\n}'
            },
            "python_runner": {
                "prompt": "Générez un Token signé, vérifiez-le, puis observez la détection immédiate d'une falsification :",
                "initial_code": '''from itsdangerous import URLSafeTimedSerializer, BadSignature

SECRET_SERVEUR = "cle-secrete-inconnue-du-client-2026"
signer = URLSafeTimedSerializer(SECRET_SERVEUR)

# 1. Émission d'un jeton signé
token = signer.dumps({"utilisateur": "amine", "role": "stagiaire"})
print("1. Bearer Token généré :", token)

# 2. Vérification du jeton (valide 300s)
donnees_verifiees = signer.loads(token, max_age=300)
print("2. Contenu vérifié :", donnees_verifiees)

# 3. Tentative d'altération d'un caractère du token
token_falsifie = token[:-1] + ("A" if token[-1] != "A" else "B")
try:
    signer.loads(token_falsifie, max_age=300)
except BadSignature:
    print("3. SÉCURITÉ : Falsification détectée ! Signature rejetée (401 Unauthorized).")'''
            },
            "vscode_instructions": {
                "filename": "day_4/02_bearer_tokens_signes.py",
                "steps": [
                    "Ouvrir `day_4/02_bearer_tokens_signes.py` dans l'éditeur.",
                    "Tester d'abord l'émission du jeton via le bouton ci-dessus, puis appeler `GET /api/sandbox/auth/profil` dans le Client HTTP."
                ]
            }
        },
        {
            "id": "d4-l3",
            "file": "day_4/03_rate_limiting_429.py",
            "title": "4.3 — Rate Limiting (Limitation de Débit & Code `429 Too Many Requests`)",
            "duration": "60 min",
            "analogy": {
                "title": "Le tourniquet de sécurité à débit contrôlé",
                "text": "Si un programme client contient une boucle infinie `while True:` ou qu'un attaquant tente de saturer le service, le **Rate Limiting** applique un quota par client (ex. maximum 3 requêtes par tranche de 20 secondes). Au-delà, le serveur répond **`429 Too Many Requests`**."
            },
            "explanation": [
                "**Algorithme de Fenêtre Glissante (Sliding Window)** :\n  1. Le serveur conserve dans `historique_ip` la liste des horodatages (`time.time()`) des requêtes récentes de chaque adresse IP.\n  2. À chaque appel, il purge les horodatages plus anciens que la fenêtre (`20` secondes).\n  3. Si le nombre d'appels restants atteint `LIMITE_REQUETES` (`3`), il retourne le statut **`429 Too Many Requests`** et l'en-tête `Retry-After`.\n  4. Sinon, il enregistre l'horodatage courant et décrémente `X-RateLimit-Remaining`."
            ],
            "code": _read("03_rate_limiting_429.py"),
            "line_explanations": [
                {"lines": "10-12", "text": "Configuration de la politique : maximum `3` requêtes par fenêtre de `20` secondes."},
                {"lines": "20", "text": "Conservation uniquement des horodatages datant de moins de 20 secondes."},
                {"lines": "23-34", "text": "Si le quota est atteint, retour immédiat du code `429 Too Many Requests` et de l'en-tête `Retry-After`."},
                {"lines": "37-44", "text": "Ajout de l'appel courant et exposition des en-têtes `X-RateLimit-Limit` et `X-RateLimit-Remaining`."}
            ],
            "sandbox_preset": {
                "label": "Tester le Rate Limiter (Cliquez 4 fois !) : GET /api/sandbox/ratelimit-demo",
                "method": "GET",
                "url": "/api/sandbox/ratelimit-demo",
                "body": ""
            },
            "python_runner": {
                "prompt": "Simulez 5 appels successifs d'un client face au limiteur de débit (plafond = 3 requêtes) :",
                "initial_code": '''LIMITE = 3
compteur_appels = []

def simuler_requete_api(numero_appel):
    if len(compteur_appels) >= LIMITE:
        print(f"Appel #{numero_appel} -> BLOQUÉ : HTTP 429 Too Many Requests (Quota de {LIMITE} atteint)")
        return 429
    compteur_appels.append(numero_appel)
    restant = LIMITE - len(compteur_appels)
    print(f"Appel #{numero_appel} -> ACCEPTÉ : HTTP 200 OK (X-RateLimit-Remaining: {restant})")
    return 200

for i in range(1, 6):
    simuler_requete_api(i)'''
            },
            "vscode_instructions": {
                "filename": "day_4/03_rate_limiting_429.py",
                "steps": [
                    "Ouvrir `day_4/03_rate_limiting_429.py` dans l'éditeur.",
                    "Dans le Client HTTP, exécuter 4 fois de suite `GET /api/sandbox/ratelimit-demo` pour observer le passage à `HTTP 429`."
                ]
            }
        }
    ]
}
