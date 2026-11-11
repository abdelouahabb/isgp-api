import os

BASE_DIR = os.path.dirname(__file__)

def _read(filename):
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8") as f:
        return f.read().strip()

DAY_4_DATA = {
    "day_number": 4,
    "folder": "day_4",
    "badge": "Jour 4 • Secrets, Tokens, RBAC & Rate Limit",
    "title": "Sécurité & Résilience des APIs : Secrets, Jetons Signés (JWT/Bearer), Refresh Tokens, RBAC, Rate Limiting et Webhooks",
    "goal": "Maîtriser l'architecture de sécurité complète d'une API : distinguer encodage, hachage, chiffrement et signature HMAC ; isoler les secrets hors du code ; émettre et vérifier des Bearer Tokens ; implémenter le cycle Access/Refresh Token et le contrôle d'accès par rôle (RBAC : 401 vs 403) ; protéger le serveur par Rate Limiting (429) et authentifier les Webhooks entrants.",
    "starter_filename": "day_4/02_bearer_tokens_signes.py",
    "files": [
        "day_4/01_secrets_et_api_key.py",
        "day_4/02_bearer_tokens_signes.py",
        "day_4/06_authn_vs_authz_scopes.py",
        "day_4/04_refresh_token_et_rbac.py",
        "day_4/03_rate_limiting_429.py",
        "day_4/05_cors_webhooks_headers.py",
        "day_4/07_cookies_et_sessions_securisees.py",
    ],
    "lessons": [
        {
            "id": "d4-l1",
            "file": "day_4/01_secrets_et_api_key.py",
            "title": "4.1 — Fondations Cryptographiques, Gestion des Secrets (`os.environ`) & Clés API (`X-API-Key`)",
            "duration": "60 min",
            "analogy": {
                "title": "Distinguer les 4 opérations fondamentales de sécurité informatique",
                "text": "Quatre opérations mathématiques bien distinctes gouvernent la sécurité des échanges numériques et ne doivent jamais être confondues. **L'encodage** (`Base64`, `UTF-8`) se borne à transcrire des octets dans un alphabet imprimable sans la moindre protection cryptographique, puisque quiconque peut inverser la transformation instantanément sans secret. À l'inverse, **le hachage** (`SHA-256`, `PBKDF2`, `Scrypt`, `Bcrypt`) calcule une empreinte à sens unique mathématiquement irréversible, indispensable pour conserver les mots de passe salés (`salt`) en base de données.\n\nLorsque la donnée doit rester confidentielle tout en pouvant être restituée au destinataire légitime, **le chiffrement** (`AES-GCM`, `TLS/HTTPS`) brouille le message de façon réversible sous réserve de détenir la clé de déchiffrement. Enfin, **la signature cryptographique** (`HMAC-SHA256`) n'occulte pas le contenu mais lui attache un sceau calculé à l'aide d'une `SECRET_KEY` serveur afin de prouver simultanément l'authenticité de l'émetteur et l'intégrité absolue du message."
            },
            "explanation": [
                "**Externalisation stricte des secrets par variables d'environnement (`Twelve-Factor App`).** Le code source Python vocation à être partagé et archivé dans Git : figer `SECRET_KEY = 'mon-secret'` dans un module `.py` compromet irrémédiablement les clés de production auprès de quiconque clone le dépôt. En conformité avec le Facteur III de *Twelve-Factor App*, les secrets sont injectés au démarrage des workers Gunicorn via l'environnement du système d'exploitation et lus dynamiquement par `os.environ.get('API_SECRET_KEY')`.",
                "**Proscription absolue des secrets dans l'URI au profit des en-têtes HTTP.** Même lorsque le transport est chiffré par TLS, la ligne de requête complète incluant `?api_key=...` est consignée en clair dans les journaux `access.log` des proxys inverses Nginx, dans les sondes de supervision et dans l'historique des navigateurs. Tout secret d'authentification doit par conséquent transiter exclusivement dans `request.headers`, tel que `X-API-Key` ou `Authorization`.",
                "**Authentification machine-à-machine par en-tête `X-API-Key`.** Lorsqu'un démon automatisé ou un serveur partenaire interroge une route interne sans contexte d'utilisateur humain, il joint sa clé pré-partagée dans `X-API-Key: <cle>`. La vue Flask extrait cette valeur depuis l'enveloppe Werkzeug et vérifie sa validité avant d'exécuter la moindre requête métier, rejetant tout appel non conforme par un statut `401 Unauthorized`.",
                "**Parade contre les attaques temporelles (`Timing Attacks`) par `hmac.compare_digest`.** L'opérateur standard `==` compare deux chaînes octet par octet et court-circuite l'évaluation dès la première divergence en quelques nanosecondes, permettant à un attaquant statistique de deviner la clé caractère après caractère. La primitive `hmac.compare_digest(a, b)` parcourt l'intégralité des octets en temps strictement constant quelle que soit la position de l'écart, neutralisant toute fuite par canal auxiliaire."
            ],
            "code": _read("01_secrets_et_api_key.py"),
            "line_explanations": [
                {"lines": "11-12", "text": "`os.environ.get(...)` lit les secrets depuis la mémoire du système d'exploitation."},
                {"lines": "17", "text": "`request.headers.get('X-API-Key', '')` extrait la clé transmise dans l'en-tête HTTP."},
                {"lines": "20-23", "text": "`hmac.compare_digest` vérifie l'égalité en temps constant et renvoie `401 Unauthorized` si la clé est absente ou erronée."}
            ],
            "sandbox_preset": {
                "label": "Tester GET /api/sandbox/admin-stats (X-API-Key)",
                "method": "GET",
                "url": "/api/sandbox/admin-stats",
                "headers": {"X-API-Key": "isgp-secret-2026"},
                "body": ""
            },
            "python_runner": {
                "prompt": "Expérimentez le hachage de mot de passe (avec sel) et la comparaison en temps constant d'une clé API :",
                "initial_code": '''import os
import hmac
import hashlib

# 1. Hachage sécurisé d'un mot de passe avec sel aléatoire (PBKDF2-HMAC-SHA256)
mot_de_passe_clair = "isgp2026"
sel = os.urandom(16)
empreinte = hashlib.pbkdf2_hmac("sha256", mot_de_passe_clair.encode(), sel, 100_000)
print("Sel aléatoire (hex) :", sel.hex())
print("Empreinte stockée en base (irréversible) :", empreinte.hex()[:36] + "...")

# 2. Vérification d'une clé API en temps constant
os.environ["ISGP_API_SECRET"] = "sk_live_98f7a6b5c4d3e2f1"
secret_serveur = os.environ.get("ISGP_API_SECRET")
cle_client = "sk_live_98f7a6b5c4d3e2f1"
print("Clé API valide (temps constant) :", hmac.compare_digest(cle_client, secret_serveur))'''
            },
            "vscode_instructions": {
                "filename": "day_4/01_secrets_et_api_key.py",
                "steps": [
                    "Ouvrir le fichier `day_4/01_secrets_et_api_key.py` dans l'éditeur.",
                    "Tester `GET /api/sandbox/admin-stats` avec puis sans l'en-tête `X-API-Key` dans le Client HTTP."
                ]
            }
        },
        {
            "id": "d4-l2",
            "file": "day_4/02_bearer_tokens_signes.py",
            "title": "4.2 — Anatomie des Jetons Signés (`Bearer Token` / JWT) : Émission, Signature HMAC & Expiration",
            "duration": "65 min",
            "analogy": {
                "title": "Le badge électronique temporaire infalsifiable",
                "text": "Une clé API statique ne transporte ni l'identité nominative d'un opérateur humain, ni ses privilèges métier, ni une échéance d'expiration automatique. Avec un **Jeton Signé (`Bearer Token` / JWT)**, l'utilisateur soumet ses identifiants une unique fois sur `POST /api/auth/token`, et le serveur lui délivre un titre numérique encapsulant `{\"utilisateur\": \"stagiaire\", \"role\": \"participant\"}` ainsi que l'horodatage d'émission, le tout scellé par une **signature mathématique HMAC** dérivée de la `SECRET_KEY`.\n\nLors de chaque appel ultérieur, le client joint ce titre dans l'en-tête `Authorization: Bearer <token>`. N'importe quel worker Gunicorn peut alors vérifier l'authenticité et la fraîcheur du jeton par pur calcul cryptographique en mémoire, sans solliciter la base de données relationnelle."
            },
            "explanation": [
                "**Architecture interne segmentée d'un jeton signé (`itsdangerous` / JWT).** Un jeton autonome concatène plusieurs segments encodés en `Base64URL` et séparés par un point `.` : la charge utile (*payload*) rassemble les revendications métier (*claims* tels que `sub`, `role` ou l'horodatage), tandis que le segment final porte l'empreinte cryptographique `HMAC(Base64URL(Payload), SECRET_KEY)`. Dans l'écosystème Flask, la bibliothèque native `itsdangerous` (`URLSafeTimedSerializer`) assure cette sérialisation horodatée avec la même rigueur mathématique qu'un jeton JWT `HS256`.",
                "**Visibilité en clair de la charge utile : signé ne signifie jamais chiffré.** Le segment `Payload` d'un JWT ou d'un jeton `itsdangerous` est simplement encodé en Base64URL afin de traverser sans altération les en-têtes HTTP : toute personne interceptant la chaîne peut décoder et lire instantanément le dictionnaire JSON qu'elle renferme. Il est donc formellement interdit d'y loger un mot de passe, un secret ou une donnée bancaire ; la signature garantit en revanche qu'aucun tiers ne peut altérer `\"role\": \"stagiaire\"` en `\"role\": \"admin\"` sans invalider le sceau HMAC.",
                "**Contrôle déterministe de la durée de vie par `max_age`.** Lorsqu'une vue protégée appelle `signer.loads(token, max_age=300)`, le moteur recalcule d'abord le HMAC en temps constant et lève `BadSignature` à la moindre altération d'un seul caractère. Ce n'est qu'après validation cryptographique du sceau qu'il compare l'horodatage scellé dans le jeton à l'horloge courante du serveur et rejette par `SignatureExpired` tout titre émis depuis plus de 300 secondes."
            ],
            "code": _read("02_bearer_tokens_signes.py"),
            "line_explanations": [
                {"lines": "9-10", "text": "`URLSafeTimedSerializer(SECRET_KEY)` initialise le moteur de signature HMAC-SHA1/SHA256 avec le secret du serveur."},
                {"lines": "19-20", "text": "`signer.dumps(charge_utile)` sérialise le dictionnaire en JSON, l'encode en Base64URL, ajoute l'horodatage et signe l'ensemble."},
                {"lines": "30-34", "text": "Extrait le jeton de l'en-tête standard `Authorization: Bearer <token>`."},
                {"lines": "36-41", "text": "`signer.loads(token, max_age=300)` distingue explicitement un jeton expiré (`SignatureExpired`) d'un jeton falsifié (`BadSignature`)."}
            ],
            "sandbox_preset": {
                "label": "1. Émettre un Bearer Token : POST /api/sandbox/auth/token",
                "method": "POST",
                "url": "/api/sandbox/auth/token",
                "body": '{\n  "identifiant": "stagiaire",\n  "mot_de_passe": "isgp2026"\n}'
            },
            "python_runner": {
                "prompt": "Inspectez l'anatomie d'un jeton signé et observez pourquoi son contenu est lisible mais infalsifiable :",
                "initial_code": '''import base64
from itsdangerous import URLSafeTimedSerializer, BadSignature

SECRET_SERVEUR = "cle-secrete-inconnue-du-client-2026"
signer = URLSafeTimedSerializer(SECRET_SERVEUR)

# 1. Émission du jeton signé
token = signer.dumps({"utilisateur": "amine", "role": "stagiaire"})
print("1. Jeton complet :", token)

# 2. Découpage des segments (Payload.Timestamp.Signature)
segments = token.split(".")
payload_b64 = segments[0]
# Ajout du padding '=' requis par Base64 standard
payload_clair = base64.urlsafe_b64decode(payload_b64 + "===").decode("utf-8")
print("2. Preuve que le Payload est lisible sans clé :", payload_clair)

# 3. Tentative de falsification d'un caractère
token_falsifie = token[:-1] + ("A" if token[-1] != "A" else "B")
try:
    signer.loads(token_falsifie, max_age=300)
except BadSignature:
    print("3. SÉCURITÉ : Signature invalide détectée ! Jeton rejeté (401 Unauthorized).")'''
            },
            "vscode_instructions": {
                "filename": "day_4/02_bearer_tokens_signes.py",
                "steps": [
                    "Ouvrir `day_4/02_bearer_tokens_signes.py` dans l'éditeur.",
                    "Tester d'abord `POST /api/sandbox/auth/token` puis utiliser le bouton d'injection automatique du Bearer Token dans le Client HTTP pour appeler `GET /api/sandbox/auth/profil`."
                ]
            }
        },
        {
            "id": "d4-l3",
            "file": "day_4/06_authn_vs_authz_scopes.py",
            "title": "4.3 — Authentification (`AuthN` / `401`) vs Autorisation (`AuthZ` / `403`) : Rôles (`RBAC`), `Scopes` & Faille `BOLA`",
            "duration": "65 min",
            "analogy": {
                "title": "Le contrôle du passeport à l'entrée de l'aéroport (AuthN) vs La carte d'embarquement pour le cockpit (AuthZ)",
                "text": "En gouvernance d'API (*API Management*), amalgamer **Authentification** et **Autorisation** engendre des contrats d'erreur incohérents. **L'Authentification (`AuthN` — « Qui êtes-vous ? »)** s'apparente au contrôle du passeport au poste frontière : l'agent vérifie que le titre est authentique et en cours de validité, et refoule immédiatement tout voyageur démuni de document ou porteur d'un faux par un statut **`401 Unauthorized`**.\n\n**L'Autorisation (`AuthZ` — « Qu'avez-vous le droit d'accomplir ? »)** intervient une fois la frontière franchie : votre identité est formellement établie, mais vous tentez d'accéder au cockpit de l'appareil muni d'une carte d'embarquement passager. Le serveur sait exactement qui vous êtes mais constate que vos privilèges interdisent cette opération, ce qu'il signifie par le code **`403 Forbidden`**."
            },
            "explanation": [
                "**Subtilité terminologique de la RFC 9110 entre `401 Unauthorized` et `403 Forbidden`.** Bien que l'intitulé historique anglais *Unauthorized* prête à confusion, le code `401` traduit exclusivement un **défaut d'authentification (`AuthN`)** — absence d'en-tête `Authorization`, signature HMAC invalide ou jeton expiré — que le client peut résoudre en fournissant des identifiants valides. Le code `403 Forbidden` exprime quant à lui un **refus d'autorisation (`AuthZ`)** opposé à un appelant déjà identifié : réémettre la requête avec le même jeton aboutira invariablement au même rejet.",
                "**Contrôle d'accès par rôle (`RBAC`) et permissions granulaires (`Scopes` OAuth2).** Un premier niveau d'autorisation évalue le profil organisationnel de l'utilisateur (`stagiaire`, `formateur`, `admin`) afin de réserver les mutations sensibles aux administrateurs. Un second niveau plus fin inspecte la liste explicite des `scopes` inscrits dans le jeton (`[\"formations:read\", \"formations:write\"]`), permettant par exemple à une intégration tierce de consulter le catalogue (`200 OK` sur `GET`) tout en lui interdisant toute création (`403` sur `POST`).",
                "**Vérification de propriété sur l'instance et parade contre la faille `BOLA`.** Classée au premier rang mondial du référentiel **OWASP API Security Top 10**, la vulnérabilité *Broken Object Level Authorization* survient lorsqu'un utilisateur dûment authentifié (`amine`) accède au dossier confidentiel d'un pair (`sara`) en incrémentant simplement l'identifiant dans `GET /api/dossiers/102`. Chaque vue Flask manipulant un identifiant d'entité doit impérativement vérifier l'invariant `dossier.proprietaire == g.utilisateur['sub']` (sauf dérogation explicite de rôle `admin`) avant de sérialiser la ressource."
            ],
            "code": _read("06_authn_vs_authz_scopes.py"),
            "line_explanations": [
                {"lines": "20-29", "text": "**Étape 1 (`AuthN`)** : Vérifie la présence, l'expiration et la signature du jeton. En cas d'échec, renvoie `401 Unauthorized`."},
                {"lines": "38-43", "text": "**Étape 2A (`AuthZ — RBAC`)** : Vérifie si le rôle du jeton correspond au `role_requis` (`403 Forbidden` sinon)."},
                {"lines": "45-50", "text": "**Étape 2B (`AuthZ — Scopes OAuth2`)** : Vérifie que la permission granulaire exigée (`scope_requis`) figure dans la liste `scopes` du jeton (`403` sinon)."},
                {"lines": "52-57", "text": "**Étape 2C (`AuthZ — Anti-BOLA`)** : Vérifie que l'utilisateur connecté est bien le propriétaire légitime de l'enregistrement demandé (`403` sinon)."}
            ],
            "sandbox_preset": {
                "label": "Tester AuthN (401) vs AuthZ (403 / 200) : GET /api/sandbox/authz-demo",
                "method": "GET",
                "url": "/api/sandbox/authz-demo",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez les 5 scénarios illustrant l'Authentification (401) et les 3 niveaux d'Autorisation (403 RBAC, 403 Scope, 403 BOLA et 200 OK) :",
                "initial_code": _read("06_authn_vs_authz_scopes.py")
            },
            "vscode_instructions": {
                "filename": "day_4/06_authn_vs_authz_scopes.py",
                "steps": [
                    "Dans le Client HTTP, appelez `GET /api/sandbox/authz-demo` sans jeton -> observez `401 Unauthorized (Échec AuthN)`.",
                    "Cliquez sur « Générer & injecter un Token (stagiaire) » puis rappelez `GET /api/sandbox/authz-demo` -> observez `403 Forbidden (AuthN réussie, mais Échec AuthZ)`.",
                    "Dans `POST /api/sandbox/auth/token`, remplacez `\"stagiaire\"` par `\"directeur\"` pour obtenir un jeton `admin`, puis rappelez `GET /api/sandbox/authz-demo` -> observez `200 OK (AuthN + AuthZ validées)` !"
                ]
            }
        },
        {
            "id": "d4-l4",
            "file": "day_4/04_refresh_token_et_rbac.py",
            "title": "4.4 — Cycle Access / Refresh Token, Révocation (Blacklist) & Décorateur `@exiger_role`",
            "duration": "65 min",
            "analogy": {
                "title": "Pourquoi avoir deux jetons (Access Token court + Refresh Token long) ?",
                "text": "Émettre un jeton unique valable trente jours ouvre une fenêtre de compromission dramatique en cas d'interception, tandis qu'imposer une expiration sèche toutes les cinq minutes obligerait l'opérateur humain à ressaisir son mot de passe cent fois par journée de travail.\n\nLes architectures OAuth2 et OpenID Connect résolvent ce dilemme en couplant un **`Access Token` éphémère** (5 à 15 minutes) transmis sur chaque appel métier avec un **`Refresh Token` de longue durée** (7 à 30 jours), isolé par un sel cryptographique distinct et présenté exclusivement au guichet `/api/auth/refresh` pour obtenir silencieusement un nouveau jeton d'accès frais."
            },
            "explanation": [
                "**Cloisonnement cryptographique des jetons par sels dédiés (`salt`).** Si l'`Access Token` et le `Refresh Token` partageaient exactement la même signature `URLSafeTimedSerializer`, un attaquant pourrait soumettre un `Refresh Token` directement dans l'en-tête `Authorization: Bearer` d'une route métier. L'instanciation de deux signataires distincts dotés de `salt='access-token'` et `salt='refresh-token'` garantit mathématiquement qu'un jeton de rafraîchissement est rejeté en `401` partout ailleurs que sur `/api/auth/refresh`.",
                "**Factorisation transversale du contrôle d'accès par décorateur `@exiger_role`.** Au lieu de dupliquer vingt-cinq lignes d'extraction d'en-tête et de validation HMAC en tête de chaque vue Flask, un décorateur paramétré `@exiger_role('admin')` encapsule toute la chaîne de décision. Il évalue d'abord l'authenticité et la fraîcheur du jeton (`401`), vérifie ensuite l'adéquation du rôle (`403`), puis injecte le profil décodé dans le contexte de requête `g.utilisateur` avant de déléguer l'exécution à la vue.",
                "**Révocation anticipée des jetons sans état par liste noire (`Token Blacklist`).** Parce qu'un jeton signé est par essence autonome (*stateless*), sa validité mathématique perdure jusqu'à l'échéance `max_age` même après un clic sur « Se déconnecter ». Pour honorer une révocation immédiate ou bloquer un compte compromis sur l'ensemble des workers Gunicorn, l'API consigne l'identifiant unique du jeton (`jti`) ou sa signature dans une structure rapide en mémoire partagée (telle que Redis avec expiration automatique alignée sur `max_age`)."
            ],
            "code": _read("04_refresh_token_et_rbac.py"),
            "line_explanations": [
                {"lines": "13-14", "text": "Utilisation de deux sels cryptographiques distincts (`salt='access-token'` vs `'refresh-token'`) pour empêcher l'utilisation d'un Refresh Token comme Access Token."},
                {"lines": "20-49", "text": "Décorateur `@exiger_role(role_minimum)` gérant successivement le `401` (absence, révocation, expiration, signature) puis le `403` (rôle insuffisant)."},
                {"lines": "52-65", "text": "Route `/api/auth/login` émettant simultanément l'`access_token` (300s) et le `refresh_token` (7 jours)."},
                {"lines": "68-77", "text": "Route `/api/auth/refresh` vérifiant le `refresh_token` et délivrant un nouvel `access_token`."}
            ],
            "python_runner": {
                "prompt": "Simulez le contrôle d'accès par rôle (RBAC : 401 vs 403 vs 200) et le renouvellement par Refresh Token :",
                "initial_code": '''from itsdangerous import URLSafeTimedSerializer

SECRET = "secret-rbac-isgp-2026"
access_signer = URLSafeTimedSerializer(SECRET, salt="access")
refresh_signer = URLSafeTimedSerializer(SECRET, salt="refresh")

def verifier_acces_route_admin(token_recu):
    if not token_recu:
        return 401, "401 Unauthorized : Aucun jeton fourni"
    try:
        user = access_signer.loads(token_recu, max_age=300)
    except Exception:
        return 401, "401 Unauthorized : Jeton invalide ou expiré"
    if user.get("role") != "admin":
        return 403, f"403 Forbidden : Rôle 'admin' requis (rôle actuel : '{user.get('role')}')"
    return 200, f"200 OK : Bienvenue dans l'espace d'administration, {user.get('sub')}"

token_stagiaire = access_signer.dumps({"sub": "amine", "role": "stagiaire"})
token_directeur = access_signer.dumps({"sub": "directeur", "role": "admin"})

print("Appel sans jeton      ->", verifier_acces_route_admin(None))
print("Appel avec Stagiaire  ->", verifier_acces_route_admin(token_stagiaire))
print("Appel avec Directeur  ->", verifier_acces_route_admin(token_directeur))'''
            },
            "vscode_instructions": {
                "filename": "day_4/04_refresh_token_et_rbac.py",
                "steps": [
                    "Ouvrir `day_4/04_refresh_token_et_rbac.py` dans l'éditeur.",
                    "Étudier la structure du décorateur `@exiger_role('admin')` aux lignes 20 à 49."
                ]
            }
        },
        {
            "id": "d4-l5",
            "file": "day_4/03_rate_limiting_429.py",
            "title": "4.5 — Ingénierie du Rate Limiting : Algorithmes, Quotas & En-têtes (`429 Too Many Requests`)",
            "duration": "60 min",
            "analogy": {
                "title": "Le disjoncteur qui protège la centrale électrique contre les courts-circuits",
                "text": "Même derrière une authentification irréprochable, un script partenaire contenant par mégarde une boucle `while True:` dépourvue de temporisation, ou un bot menant une attaque par dictionnaire sur `/api/auth/token`, peut saturer l'ensemble des workers Gunicorn et paralyser la base SQLite pour tous les autres usagers.\n\nLe **Rate Limiting (limitation de débit)** agit comme un disjoncteur individuel par adresse IP, clé API ou identifiant d'utilisateur : dès que le plafond autorisé est franchi, Flask coupe court au traitement en renvoyant immédiatement le statut **`429 Too Many Requests`**."
            },
            "explanation": [
                "**Comparaison algorithmique : Fenêtre Fixe, Fenêtre Glissante et Seau à Jetons.** Le compteur à *Fenêtre Fixe* par minute calendaire souffre d'un effet de bord critique aux frontières temporelles permettant d'écouler le double du quota en deux secondes entre `14h00m59s` et `14h01m01s`. Le journal à *Fenêtre Glissante* (*Sliding Window Log*) élimine ce biais en conservant les horodatages exacts `time.time()` et en purgeant ceux antérieurs à la fenêtre active, tandis que le *Seau à Jetons* (*Token Bucket*) se recharge à cadence constante afin de tolérer de brefs pics légitimes tout en bornant le débit moyen.",
                "**Signalisation contractuelle des quotas par en-têtes HTTP normalisés.** Une API bien conçue permet aux clients disciplinés d'autoréguler leur cadence avant même de subir un blocage en joignant sur chaque réponse `X-RateLimit-Limit` (plafond nominal) et `X-RateLimit-Remaining` (crédit résiduel dans la fenêtre). Lorsque le seuil est atteint et que le code `429 Too Many Requests` est émis, l'en-tête standard RFC 9110 `Retry-After` indique le délai exact en secondes avant la réouverture du quota.",
                "**Partage des compteurs entre processus workers en déploiement WSGI.** Dans une topologie de production exécutant `gunicorn -w 4`, quatre espaces mémoire Python coexistent sans partager leurs dictionnaires locaux : un limiteur purement résident en RAM multiplierait accidentellement le quota par quatre. On externalise alors les compteurs vers un magasin atomique partagé comme Redis (ou une directive `limit_req_zone` en frontal sur Nginx) afin d'appliquer un plafond global strict."
            ],
            "code": _read("03_rate_limiting_429.py"),
            "line_explanations": [
                {"lines": "10-12", "text": "Définit la politique : maximum `3` requêtes sur une fenêtre glissante de `20` secondes par adresse IP."},
                {"lines": "20", "text": "Liste en compréhension filtrant uniquement les horodatages datant de moins de 20 secondes."},
                {"lines": "23-34", "text": "Si le quota est atteint (`>= 3`), calcule le temps d'attente exact et renvoie `429 Too Many Requests` avec `Retry-After`."},
                {"lines": "37-44", "text": "Enregistre l'horodatage courant et renseigne `X-RateLimit-Limit` et `X-RateLimit-Remaining`."}
            ],
            "sandbox_preset": {
                "label": "Tester le Rate Limiter (Cliquez 4 fois !) : GET /api/sandbox/ratelimit-demo",
                "method": "GET",
                "url": "/api/sandbox/ratelimit-demo",
                "body": ""
            },
            "python_runner": {
                "prompt": "Comparez le comportement du limiteur à Fenêtre Glissante sur une rafale d'appels :",
                "initial_code": '''LIMITE = 3
FENETRE = 20
historique = []

def simuler_requete(instant_seconde):
    global historique
    # Purge des appels plus anciens que 20 secondes
    historique = [t for t in historique if instant_seconde - t < FENETRE]
    if len(historique) >= LIMITE:
        retry_after = FENETRE - (instant_seconde - historique[0])
        print(f"[t={instant_seconde:02d}s] -> HTTP 429 Too Many Requests (Retry-After: {retry_after}s)")
        return
    historique.append(instant_seconde)
    restant = LIMITE - len(historique)
    print(f"[t={instant_seconde:02d}s] -> HTTP 200 OK (X-RateLimit-Remaining: {restant})")

# Rafale à t=1s, 2s, 3s, 4s puis nouvel essai à t=22s
for t in [1, 2, 3, 4, 22]:
    simuler_requete(t)'''
            },
            "vscode_instructions": {
                "filename": "day_4/03_rate_limiting_429.py",
                "steps": [
                    "Ouvrir `day_4/03_rate_limiting_429.py` dans l'éditeur.",
                    "Dans le Client HTTP, cliquer 4 fois de suite sur `GET /api/sandbox/ratelimit-demo` pour observer la transition de `200 OK` vers `429 Too Many Requests`."
                ]
            }
        },
        {
            "id": "d4-l6",
            "file": "day_4/05_cors_webhooks_headers.py",
            "title": "4.6 — Sécurité Périmétrique : CORS, Signatures de Webhooks (`HMAC-SHA256`) & Protection `413`",
            "duration": "55 min",
            "analogy": {
                "title": "L'API inversée (Webhook) et le contrôle des origines (CORS)",
                "text": "Jusqu'à présent, notre architecture obéissait exclusivement au modèle tiré (*pull*) où le client sollicite l'API. Mais comment notifier instantanément votre système lorsqu'un règlement interbancaire CIB, Edahabia ou Stripe aboutit chez un prestataire externe ? Plutôt que de gaspiller des ressources en interrogeant la passerelle toutes les secondes (*polling*), c'est le serveur de la banque qui pousse de sa propre initiative une requête `POST` signée vers votre endpoint dédié : ce patron d'API inversée s'appelle un **Webhook**."
            },
            "explanation": [
                "**Authentification cryptographique d'un Webhook entrant sur octets bruts (`request.get_data()`).** Comme l'URL publique `POST /api/webhooks/paiement` est exposée sur Internet, accepter son corps JSON sans vérification permettrait à n'importe quel tiers de simuler un paiement validé. L'émetteur légitime calcule une empreinte `HMAC-SHA256` sur la séquence exacte des octets bruts du corps à l'aide d'un `WEBHOOK_SECRET` partagé et la transmet dans `X-Webhook-Signature` ; côté Flask, la vue lit impérativement `request.get_data()` (et non un dictionnaire re-sérialisé dont les espaces différeraient) et valide la signature via `hmac.compare_digest`.",
                "**Gouvernance de l'isolation inter-origines par `CORS` (`Cross-Origin Resource Sharing`).** Par défaut, la politique *Same-Origin Policy* des navigateurs interdit à une application JavaScript servie depuis `https://portail-isgp.dz` de lire les réponses émises par `https://api-isgp.dz`. Pour autoriser explicitement ce dialogue frontal sans ouvrir de brèche, un crochet `@app.after_request` vérifie l'origine entrante contre une liste blanche stricte avant d'émettre `Access-Control-Allow-Origin: https://portail-isgp.dz`, en proscrivant le joker universel `*` sur toute API manipulant des données privées.",
                "**Plafonnement des charges entrantes par `MAX_CONTENT_LENGTH` (`413 Payload Too Large`).** Un attaquant peut tenter d'épuiser la mémoire vive des workers Gunicorn en expédiant un corps JSON de plusieurs centaines de mégaoctets. Définir `app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024` délègue directement à Werkzeug l'inspection de `Content-Length` et du flux `wsgi.input` : tout dépassement du seuil d'un mégaoctet interrompt immédiatement la lecture avec une exception `RequestEntityTooLarge` traduite en statut `413`."
            ],
            "code": _read("05_cors_webhooks_headers.py"),
            "line_explanations": [
                {"lines": "14", "text": "`MAX_CONTENT_LENGTH` plafonne la taille du corps HTTP entrant à 1 Mo (protection anti-DoS mémoire)."},
                {"lines": "20-30", "text": "Hook `@app.after_request` appliquant la liste blanche CORS et les en-têtes de sécurité (`X-Content-Type-Options: nosniff`, `Cache-Control: no-store`)."},
                {"lines": "35-46", "text": "Vérifie la signature `HMAC-SHA256` calculée sur les octets bruts du corps (`request.get_data()`) avant de traiter l'événement Webhook."}
            ],
            "python_runner": {
                "prompt": "Simulez l'émission d'un Webhook signé par un partenaire bancaire et sa vérification par votre API :",
                "initial_code": '''import hmac
import hashlib
import json

WEBHOOK_SECRET = "whsec_isgp_partenaire_2026"

# 1. Le partenaire bancaire prépare l'événement JSON et le signe en HMAC-SHA256
evenement = {"evenement": "paiement.reussi", "facture_id": "FAC-2026-089", "montant_dzd": 45000}
corps_octets = json.dumps(evenement).encode("utf-8")

signature_emetteur = "sha256=" + hmac.new(
    WEBHOOK_SECRET.encode("utf-8"), corps_octets, hashlib.sha256
).hexdigest()

print("Corps brut envoyé :", corps_octets.decode("utf-8"))
print("En-tête X-Webhook-Signature :", signature_emetteur)

# 2. Votre serveur API recalcule la signature à la réception
signature_attendue = "sha256=" + hmac.new(
    WEBHOOK_SECRET.encode("utf-8"), corps_octets, hashlib.sha256
).hexdigest()

est_authentique = hmac.compare_digest(signature_emetteur, signature_attendue)
print("Webhook authentifié avec succès :", est_authentique)'''
            },
            "vscode_instructions": {
                "filename": "day_4/05_cors_webhooks_headers.py",
                "steps": [
                    "Ouvrir `day_4/05_cors_webhooks_headers.py` dans l'éditeur.",
                    "Observer comment `request.get_data()` récupère les octets bruts exacts pour calculer le HMAC-SHA256."
                ]
            }
        },
        {
            "id": "d4-l7",
            "file": "day_4/07_cookies_et_sessions_securisees.py",
            "title": "4.7 — Gestion & Sécurité des Cookies en API/Web : `Set-Cookie`, Sessions Signées HMAC & Attributs `HttpOnly`, `Secure`, `SameSite` (Anti-XSS / Anti-CSRF)",
            "duration": "65 min",
            "analogy": {
                "title": "Le bracelet d'identification scellé au poignet (Cookie HttpOnly Signé) vs le billet posé sur la table (localStorage)",
                "text": "Où une application Web moderne — qu'il s'agisse d'une interface React/Vue ou d'un portail Jinja2 — doit-elle conserver son titre d'authentification ? Persister un jeton Bearer dans `localStorage.setItem('token', ...)` expose l'intégralité du parc d'utilisateurs à la moindre faille XSS : un unique script tiers compromis exécute `localStorage.getItem('token')` et exfiltre silencieusement les sessions actives.\n\nÀ l'inverse, un **Cookie HTTP verrouillé par les attributs `HttpOnly`, `Secure` et `SameSite=Strict`** demeure confiné au moteur réseau interne du navigateur : aucun code JavaScript (`document.cookie`) ne peut en inspecter la valeur, et Flask en garantit l'intégrité côté serveur par une signature HMAC (`session`)."
            },
            "explanation": [
                "**Cycle protocolaire `Set-Cookie` et restitution automatique dans `request.cookies`.** Lors de l'authentification sur `POST /api/auth/cookie-login`, l'appel `reponse.set_cookie('isgp_auth_token', valeur, ...)` génère un en-tête standard `Set-Cookie` dans la réponse Werkzeug. Le navigateur enregistre cette paire clé-valeur dans son coffre isolé par domaine et la réinjecte automatiquement dans l'en-tête `Cookie` de chaque requête ultérieure, que Flask parse dans le dictionnaire `request.cookies`.",
                "**Triptyque défensif obligatoire : `HttpOnly`, `Secure` et `SameSite`.** Le drapeau `httponly=True` soustrait totalement le cookie à l'API JavaScript `document.cookie`, neutralisant le vol de session par *Cross-Site Scripting* (`XSS`). L'attribut `secure=True` interdit toute transmission sur un canal HTTP non chiffré par TLS, tandis que `samesite='Strict'` (ou `'Lax'`) empêche un site tiers malveillant de déclencher des actions forgées à l'insu de l'utilisateur (*Cross-Site Request Forgery* / `CSRF`).",
                "**Cookies en clair face à l'objet `flask.session` signé par HMAC.** Un cookie ordinaire posé via `set_cookie('theme', 'sombre')` circule en texte brut modifiable par l'utilisateur dans les outils de développement et ne convient qu'aux préférences cosmétiques. À l'opposé, le dictionnaire `flask.session` sérialise ses clés en JSON compressé, les encode en Base64URL et les scelle par HMAC avec `app.secret_key` via `itsdangerous` : le client ne peut altérer son identifiant ou son rôle sans provoquer le rejet immédiat de la signature.",
                "**Invalidation déterministe à la déconnexion par `Max-Age=0` et `session.clear()`.** Comme le serveur ne peut pas effacer directement la mémoire d'un poste distant, révoquer un cookie consiste à purger l'état applicatif par `session.clear()` puis à invoquer `reponse.delete_cookie('isgp_auth_token')`. Werkzeug émet alors un en-tête `Set-Cookie` affecté de `Max-Age=0` et d'une date d'expiration en 1970, ordonnant au navigateur la destruction immédiate de l'entrée."
            ],
            "code": _read("07_cookies_et_sessions_securisees.py"),
            "line_explanations": [
                {"lines": "18-26", "text": "Configuration de `app.secret_key` et durcissement global des cookies de session (`SESSION_COOKIE_HTTPONLY=True`, `SAMESITE='Lax'`)."},
                {"lines": "32-58", "text": "Route `POST /api/auth/cookie-login` : écrit dans `session` (signée HMAC) et émet le cookie `isgp_auth_token` avec `httponly=True` et `samesite='Strict'`."},
                {"lines": "62-81", "text": "Route `GET /api/auth/cookie-inspect` : lit `request.cookies.get(...)`, vérifie la signature HMAC du jeton et lit `session`."},
                {"lines": "97-103", "text": "Route `POST /api/auth/cookie-logout` : vide `session.clear()` et révoque les cookies via `reponse.delete_cookie(...)` (`Max-Age=0`)."}
            ],
            "sandbox_preset": {
                "label": "1. Émettre Cookies Sécurisés (HttpOnly + Session HMAC) : POST /api/sandbox/cookies/login",
                "method": "POST",
                "url": "/api/sandbox/cookies/login",
                "body": '{\n  "identifiant": "yasmine.merabet",\n  "theme": "sombre"\n}'
            },
            "python_runner": {
                "prompt": "Exécutez le cycle complet des Cookies sécurisés (`Set-Cookie` avec `HttpOnly`/`SameSite`, inspection `request.cookies` et révocation `Max-Age=0`) :",
                "initial_code": _read("07_cookies_et_sessions_securisees.py")
            },
            "vscode_instructions": {
                "filename": "day_4/07_cookies_et_sessions_securisees.py",
                "steps": [
                    "Ouvrir `day_4/07_cookies_et_sessions_securisees.py` dans l'éditeur.",
                    "Observer les attributs `HttpOnly`, `Max-Age=3600` et `SameSite=Strict` générés dans l'en-tête HTTP `Set-Cookie`."
                ]
            }
        }
    ]
}
