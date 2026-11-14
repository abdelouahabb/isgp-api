"""
Référentiel des Concepts Fondamentaux & Addendum Technique — Édition FASTAPI (69 fiches).
Chaque concept ou outil est expliqué sans aucun prérequis, avec une analogie fonctionnelle
et des commandes / exemples prêts pour la production.
"""

GLOSSARY_TERMS = [{'id': 'openssl_rand_secrets',
  'term': 'Génération de Secrets Cryptographiques (openssl rand & secrets)',
  'category': 'Cryptographie & OpenSSL',
  'level': 'Addendum Sécurité',
  'short': 'Commandes permettant de générer des clés secrètes (SECRET_KEY, API Keys) à haute '
           'entropie impossibles à deviner.',
  'analogy': 'Un générateur mécanique de combinaisons de coffre-fort à 256 bits : contrairement à '
             'un mot de passe inventé par un humain, aucun dictionnaire ni supercalculateur ne '
             'peut deviner une clé aléatoire cryptographique de 32 octets.',
  'explanation': "Une clé secrète inventée manuellement au clavier souffre systématiquement d'une "
                 'entropie insuffisante et demeure vulnérable aux attaques par dictionnaire ou par '
                 "tables arc-en-ciel. La génération d'une `SECRET_KEY` ou d'une clé partenaire "
                 'impose donc le recours au générateur pseudo-aléatoire cryptographique du noyau '
                 'système (`/dev/urandom`).\n'
                 '\n'
                 'En ligne de commande, `openssl rand` produit des séquences imprévisibles codées '
                 'en hexadécimal (`-hex 32`, soit 64 caractères) ou en Base64 (`-base64 32`). Au '
                 "sein d'une application Python/FastAPI, le module `random` est strictement "
                 'proscrit en sécurité au profit du module standard `secrets` (`secrets.token_hex` '
                 'et `secrets.token_urlsafe`).',
  'code_example': '# 1. Générer une clé secrète de 256 bits (32 octets) en hexadécimal avec '
                  'OpenSSL :\n'
                  'openssl rand -hex 32\n'
                  '\n'
                  '# 2. Générer une clé secrète en Base64 :\n'
                  'openssl rand -base64 48\n'
                  '\n'
                  '# 3. Équivalent avec la bibliothèque standard Python :\n'
                  'python3 -c "import secrets; print(secrets.token_hex(32))"\n'
                  'python3 -c "import secrets; print(secrets.token_urlsafe(32))"'},
 {'id': 'openssl_dgst_hash',
  'term': 'Hachage Irréversible SHA-256 / SHA-512 (openssl dgst & sha256sum)',
  'category': 'Cryptographie & OpenSSL',
  'level': 'Addendum Sécurité',
  'short': "Calcul d'une empreinte numérique unique à sens unique (irréversible) pour vérifier "
           "l'intégrité d'une donnée ou d'un fichier.",
  'analogy': "L'empreinte digitale d'un document : en un coup d'œil sur les 64 caractères "
             "hexadécimaux, on vérifie qu'aucune virgule n'a changé, mais il est mathématiquement "
             'impossible de reconstruire le document à partir de son empreinte.',
  'explanation': "Lors du calcul d'une empreinte cryptographique sous Linux, la commande `echo "
                 '"secret"` ajoute implicitement un caractère de fin de ligne `\\n`, ce qui '
                 'produit un condensat SHA-256 différent de celui calculé par Python sur la chaîne '
                 'brute. L\'usage de `printf \'%s\' "secret"` (ou `echo -n`) garantit la '
                 'correspondance exacte des octets hachés.\n'
                 '\n'
                 "Pour le contrôle d'intégrité des livrables et sauvegardes, les utilitaires "
                 '`sha256sum archive.tar.gz` et `openssl dgst -sha256 archive.tar.gz` permettent '
                 "d'attester qu'aucun bit du fichier n'a été altéré ou corrompu durant le "
                 'transfert.',
  'code_example': '# 1. Hacher une chaîne en SHA-256 (SANS retour à la ligne parasite) :\n'
                  'printf \'%s\' "isgp-secret-2026" | openssl dgst -sha256\n'
                  '\n'
                  '# 2. Hacher en SHA-512 :\n'
                  'printf \'%s\' "isgp-secret-2026" | openssl dgst -sha512\n'
                  '\n'
                  "# 3. Calculer et vérifier l'empreinte SHA-256 d'un fichier SQLite :\n"
                  'sha256sum ecole_isgp.db > ecole_isgp.db.sha256\n'
                  'sha256sum -c ecole_isgp.db.sha256'},
 {'id': 'openssl_hmac_cli',
  'term': 'Signature HMAC-SHA256 en Terminal (openssl dgst -hmac)',
  'category': 'Cryptographie & OpenSSL',
  'level': 'Addendum Sécurité',
  'short': "Calcul en ligne de commande d'une signature HMAC-SHA256 avec clé secrète pour tester "
           'vos Webhooks et jetons.',
  'analogy': 'Apposer le sceau officiel du serveur directement depuis votre terminal Linux afin de '
             "simuler l'envoi d'un Webhook authentique (Stripe, GitHub, paiement) vers votre API "
             'FastAPI.',
  'explanation': "Contrairement à un condensat SHA-256 ordinaire que n'importe quel tiers peut "
                 'recalculer après avoir modifié un message, le mécanisme **HMAC** (*Hash-based '
                 'Message Authentication Code*) mêle les octets du corps de requête à une clé '
                 'secrète partagée (`-hmac "cle"`).\n'
                 '\n'
                 "En phase de recette ou de débogage système, cette commande constitue l'outil de "
                 'référence pour forger un en-tête `X-Webhook-Signature` authentique avant '
                 "d'invoquer une route FastAPI avec `curl`.",
  'code_example': "# 1. Calculer la signature HMAC-SHA256 d'un corps JSON avec OpenSSL :\n"
                  'printf \'%s\' \'{"id":101,"statut":"paye"}\' | openssl dgst -sha256 -hmac '
                  '"whsec_isgp_2026"\n'
                  '\n'
                  "# 2. Stocker la signature dans une variable Bash et appeler l'API FastAPI avec "
                  'curl :\n'
                  'BODY=\'{"id":101,"statut":"paye"}\'\n'
                  'SIG=$(printf \'%s\' "$BODY" | openssl dgst -sha256 -hmac "whsec_isgp_2026" | '
                  "awk '{print $2}')\n"
                  'curl -i -X POST http://127.0.0.1:8000/api/webhooks/paiement -H '
                  '"X-Webhook-Signature: sha256=$SIG" -d "$BODY"'},
 {'id': 'openssl_aes_encryption',
  'term': 'Chiffrement Symétrique AES-256 (openssl enc -aes-256-cbc -pbkdf2)',
  'category': 'Cryptographie & OpenSSL',
  'level': 'Addendum Sécurité',
  'short': "Chiffrement réversible de fichiers sensibles (.env, sauvegardes SQLite .db) à l'aide "
           "de l'algorithme AES-256 et d'une phrase secrète.",
  'analogy': 'Un coffre-fort blindé à clé symétrique : contrairement au hachage (qui broie le '
             'document de manière irréversible), le chiffrement AES verrouille le document dans un '
             "coffre ; quiconque possède la clé secrète peut l'ouvrir et retrouver le fichier "
             "exact à l'octet près.",
  'explanation': "L'ingénierie de sécurité distingue rigoureusement le hachage irréversible, "
                 'réservé aux mots de passe qui ne doivent jamais être relus en clair, du '
                 "chiffrement réversible tel qu'**AES-256**, employé pour protéger les sauvegardes "
                 "SQLite, les fichiers `.env` d'archive ou les identifiants bancaires.\n"
                 '\n'
                 "Lors d'un chiffrement via OpenSSL, l'activation conjointe des options `-salt` "
                 '(sel aléatoire), `-pbkdf2` (fonction standard de dérivation de clé) et `-iter '
                 '600000` est indispensable pour neutraliser les attaques par force brute '
                 'accélérées matériellement.',
  'code_example': "# 1. CHIFFRER une base SQLite avant de l'envoyer sur le Cloud :\n"
                  'openssl enc -aes-256-cbc -salt -pbkdf2 -iter 600000 \\\n'
                  '  -in ecole_isgp.db -out ecole_isgp.db.enc -pass pass:"MonSecretRobuste2026!"\n'
                  '\n'
                  "# 2. DÉCHIFFRER l'archive (-d) pour restaurer la base SQLite :\n"
                  'openssl enc -d -aes-256-cbc -pbkdf2 -iter 600000 \\\n'
                  '  -in ecole_isgp.db.enc -out ecole_isgp_restauree.db -pass '
                  'pass:"MonSecretRobuste2026!"'},
 {'id': 'openssl_rsa_ed25519',
  'term': 'Chiffrement Asymétrique RSA / Ed25519 : Clé Privée vs Clé Publique (openssl genpkey)',
  'category': 'Cryptographie & OpenSSL',
  'level': 'Addendum Sécurité',
  'short': "Génération d'une paire de clés mathématiquement liées : la Clé Privée (secrète, qui "
           'signe) et la Clé Publique (partagée, qui vérifie).',
  'analogy': 'Une boîte aux lettres à double serrure ou un tampon notarié : seul le serveur '
             "d'authentification central possède la Clé Privée pour signer les jetons JWT (`RS256` "
             "/ `EdDSA`), mais tous les microservices FastAPI de l'entreprise possèdent la Clé "
             'Publique pour vérifier les jetons sans jamais pouvoir en fabriquer de faux !',
  'explanation': 'Dans une architecture distribuée comptant une vingtaine de microservices, la '
                 'signature symétrique HMAC (`HS256`) oblige chaque service vérificateur à détenir '
                 "la même `SECRET_KEY` : la compromission d'un seul conteneur périphérique suffit "
                 'alors à forger des jetons administrateur.\n'
                 '\n'
                 'La cryptographie asymétrique (**RSA** ou **Ed25519**) résout structurellement ce '
                 "risque en séparant les rôles : seul le serveur d'authentification détient la clé "
                 'privée `private.pem` pour signer les jetons, tandis que les microservices '
                 'métiers ne disposent que de la clé publique `public.pem` en lecture seule.',
  'code_example': '# 1. Générer une clé privée RSA de 4096 bits :\n'
                  'openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:4096 -out '
                  'private_key.pem\n'
                  'chmod 600 private_key.pem\n'
                  '\n'
                  '# 2. Extraire la clé publique correspondante (à distribuer aux APIs) :\n'
                  'openssl pkey -in private_key.pem -pubout -out public_key.pem\n'
                  '\n'
                  '# 3. Alternative moderne ultra-rapide (Courbe elliptique Ed25519) :\n'
                  'openssl genpkey -algorithm Ed25519 -out ed25519_priv.pem\n'
                  'openssl pkey -in ed25519_priv.pem -pubout -out ed25519_pub.pem'},
 {'id': 'openssl_tls_x509',
  'term': 'Certificats HTTPS / TLS (X.509) & Diagnostic SSL (openssl req / s_client)',
  'category': 'Cryptographie & OpenSSL',
  'level': 'Addendum Sécurité',
  'short': 'Création de certificats TLS auto-signés pour le développement HTTPS local et '
           'inspection des certificats de serveurs en production.',
  'analogy': "Le passeport biométrique officiel d'un serveur Web (`X.509`), vérifié par le "
             "navigateur lors de la poignée de main TLS avant même d'envoyer le premier octet HTTP "
             'pour garantir que le canal est chiffré de bout en bout.',
  'explanation': "En environnement de production exposé sur Internet, la terminaison TLS s'appuie "
                 'sur un certificat X.509 émis par une Autorité de Certification reconnue telle '
                 "que **Let's Encrypt** (automatisée par Certbot sur Nginx). En réseau interne ou "
                 "sur un poste de développement, `openssl req -x509` permet d'engendrer en une "
                 'commande le couple clé privée (`key.pem`) et certificat auto-signé (`cert.pem`) '
                 'directement exploitable par `uvicorn --ssl-keyfile key.pem --ssl-certfile '
                 'cert.pem`.\n'
                 '\n'
                 "Lorsqu'un appel HTTPS échoue entre deux services, l'outil `openssl s_client` "
                 'inspecte à chaud la chaîne de certification, la version du protocole négociée et '
                 "la date exacte d'expiration.",
  'code_example': '# 1. Générer un certificat HTTPS auto-signé valable 365 jours pour localhost :\n'
                  'openssl req -x509 -newkey rsa:4096 -nodes \\\n'
                  '  -keyout key.pem -out cert.pem -days 365 \\\n'
                  '  -subj "/C=DZ/ST=Alger/O=ISGP/CN=localhost"\n'
                  '\n'
                  "# 2. Inspecter le contenu et les dates de validité d'un fichier certificat :\n"
                  'openssl x509 -in cert.pem -noout -subject -issuer -dates\n'
                  '\n'
                  "# 3. Vérifier le certificat HTTPS d'un serveur distant en direct :\n"
                  'openssl s_client -connect example.com:443 -servername example.com </dev/null '
                  '2>/dev/null | openssl x509 -noout -dates -subject'},
 {'id': 'base64_encoding_cli',
  'term': 'Encodage & Décodage Base64 en Terminal (base64 & openssl base64)',
  'category': 'Cryptographie & OpenSSL',
  'level': 'Addendum Sécurité',
  'short': 'Représentation de données binaires ou JSON sous forme de texte ASCII pour les en-têtes '
           'HTTP (Basic Auth, Payload JWT).',
  'analogy': "Traduire un document en alphabet morse pour qu'il passe sur une ligne télégraphique "
             ": cela permet le transport sans erreur d'encodage, mais ce n'est absolument pas un "
             'chiffrement secret.',
  'explanation': "L'encodage **Base64** assure la représentation fiable d'octets arbitraires sous "
                 'forme de caractères ASCII imprimables ; il intervient notamment dans le schéma '
                 'HTTP `Authorization: Basic <base64(user:pass)>` ainsi que dans la variante '
                 "Base64URL qui structure l'en-tête et la charge utile d'un jeton **JWT** "
                 '(`Header.Payload.Signature`).\n'
                 '\n'
                 "Sous Linux, l'option `base64 -w 0` supprime le retour à la ligne automatique "
                 'tous les 76 caractères afin de produire une chaîne continue prête pour un '
                 "en-tête HTTP, tandis que `base64 -d` restitue le texte ou les octets d'origine.",
  'code_example': '# 1. Encoder des identifiants pour un en-tête HTTP Basic Auth :\n'
                  'printf \'%s\' "admin:secret2026" | base64\n'
                  '# Résultat : YWRtaW46c2VjcmV0MjAyNg==\n'
                  '\n'
                  "# 2. Décoder une chaîne Base64 (ex: lire le Payload d'un Token) :\n"
                  'echo -n "eyJ1c2VyIjoiYW1pbmUiLCJyb2xlIjoiYWRtaW4ifQ==" | base64 -d\n'
                  '# Résultat : {"user":"amine","role":"admin"}\n'
                  '\n'
                  '# 3. Avec OpenSSL :\n'
                  'printf \'%s\' "Texte à encoder" | openssl base64 -A'},
 {'id': 'password_hashing_kdf',
  'term': 'Dérivation de Mots de Passe Salés (PBKDF2, Scrypt, Argon2, hashlib.pbkdf2_hmac)',
  'category': 'Cryptographie & OpenSSL',
  'level': 'Addendum Sécurité',
  'short': 'Hachage volontairement ralenti et salé destiné exclusivement à protéger les mots de '
           'passe humains stockés en base de données.',
  'analogy': 'Ajouter un labyrinthe de 600 000 portes (itérations) et un grain de sable unique '
             '(Salt) devant chaque mot de passe : un utilisateur légitime met 0,1 seconde à se '
             'connecter, mais un pirate qui tente 1 milliard de mots de passe mettra plusieurs '
             'siècles.',
  'explanation': 'Les fonctions de hachage générales comme SHA-256 sont optimisées pour le débit '
                 "matériel et permettent à un processeur graphique moderne d'évaluer plusieurs "
                 "milliards d'empreintes par seconde, ce qui les rend impropres au stockage direct "
                 'des mots de passe.\n'
                 '\n'
                 "La protection conforme aux recommandations de l'ANSSI et de l'OWASP repose "
                 'exclusivement sur une fonction de dérivation de clé (**KDF**) délibérément '
                 'coûteuse en temps et en mémoire, associée à un sel aléatoire unique par compte, '
                 "telle que **Argon2id**, `hashlib.scrypt` ou `hashlib.pbkdf2_hmac('sha256', "
                 '...)`.',
  'code_example': '# 1. Générer un hash de mot de passe salé SHA-512 sous Linux :\n'
                  'openssl passwd -6 "MotDePasseStagiaire2026!"\n'
                  '\n'
                  '# 2. Générer un hash PBKDF2-HMAC-SHA256 (600 000 itérations) en Python standard '
                  ':\n'
                  'python3 -c "import hashlib, secrets; sel = secrets.token_bytes(16); \\\n'
                  "h = hashlib.pbkdf2_hmac('sha256', b'Secret2026!', sel, 600000); print('Hash "
                  'hex:\', h.hex())"'},
 {'id': 'linux_ports_ss_lsof',
  'term': 'Inspection des Ports & Processus Linux (ss -tulpn, lsof -i, kill)',
  'category': 'Linux & Réseau Prod',
  'level': 'Addendum Linux',
  'short': "Commandes système permettant d'identifier quel programme écoute sur un port TCP (ex. "
           ':8000) et de libérer un port bloqué.',
  'analogy': 'Le tableau de contrôle de la capitainerie du port : permet de voir instantanément '
             'quel navire (processus `PID`) est amarré au quai n°8000 lorsque Uvicorn affiche '
             "l'erreur `Address already in use`.",
  'explanation': "L'utilitaire **`ss -tulpn`** (*Socket Statistics*, successeur direct de "
                 "`netstat`) dresse l'inventaire instantané des sockets TCP (`-t`) et UDP (`-u`) "
                 "en écoute (`-l`) sur l'hôte Linux, en affichant les numéros de ports numériques "
                 '(`-n`) ainsi que le PID du processus propriétaire (`-p`), tandis que `lsof -i '
                 ":8000` cible spécifiquement l'occupation d'un port donné.\n"
                 '\n'
                 'Pour libérer un port retenu par une instance Uvicorn résiduelle, il convient '
                 "d'émettre d'abord le signal `kill -15 <PID>` (`SIGTERM`), qui autorise "
                 "l'extinction gracieuse des connexions ASGI et SQLite, en réservant `kill -9 "
                 '<PID>` (`SIGKILL`) aux seuls processus totalement figés.',
  'code_example': '# 1. Lister tous les serveurs en écoute sur la machine Linux :\n'
                  'sudo ss -tulpn | grep -E "8000|8001|80|443"\n'
                  '\n'
                  '# 2. Trouver le PID exact qui bloque le port 8000 :\n'
                  'lsof -i :8000\n'
                  '# ou :\n'
                  'fuser 8000/tcp\n'
                  '\n'
                  '# 3. Terminer proprement le processus (ex. PID 14520) :\n'
                  'kill -15 14520'},
 {'id': 'linux_dns_netcat',
  'term': 'Diagnostic Réseau, DNS & Pare-feu (dig, nc -zv, ip a, ping)',
  'category': 'Linux & Réseau Prod',
  'level': 'Addendum Linux',
  'short': 'Utilitaires de diagnostic permettant de vérifier la résolution de nom de domaine (DNS) '
           "et l'ouverture d'un port TCP distant.",
  'analogy': "Vérifier d'abord que l'adresse figure bien dans l'annuaire (`dig`), puis vérifier "
             'que la route est praticable (`ping`) et que le guichet est ouvert (`nc -zv`) avant '
             "d'accuser le code Python.",
  'explanation': "Le diagnostic méthodique d'une panne réseau procède couche par couche : `ip -br "
                 "a` vérifie d'abord la configuration des interfaces locales, puis `dig +short "
                 'domaine.dz` valide la résolution du nom de domaine auprès du serveur DNS.\n'
                 '\n'
                 "Enfin, la commande `nc -zv HOTE PORT` (**Netcat**) éprouve isolément l'ouverture "
                 'du pare-feu et la poignée de main TCP (*3-way handshake*) vers une cible '
                 'précise, comme une base PostgreSQL sur `:5432` ou un worker Uvicorn sur `:8000`, '
                 "avant même d'envoyer la moindre trame applicative.",
  'code_example': '# 1. Afficher les adresses IP locales du serveur de manière lisible :\n'
                  'ip -br addr show\n'
                  '\n'
                  '# 2. Tester si le port TCP 8000 est ouvert en local ou à distance :\n'
                  'nc -zv 127.0.0.1 8000\n'
                  '\n'
                  '# 3. Résoudre un nom de domaine en adresse IP via DNS :\n'
                  'dig +short api.github.com'},
 {'id': 'linux_jq_json',
  'term': 'Traitement et Filtrage JSON en Terminal (jq & json.tool)',
  'category': 'Linux & Réseau Prod',
  'level': 'Addendum Linux',
  'short': "Processeur JSON en ligne de commande permettant d'indenter, coloriser, extraire et "
           'filtrer les réponses de `curl`.',
  'analogy': "Un scalpel chirurgical pour réponses d'API : au lieu de lire un bloc compact de 5 "
             '000 caractères JSON renvoyé par `curl`, `jq` extrait en une fraction de seconde '
             'uniquement les champs qui vous intéressent.',
  'explanation': 'Dès que Python est présent sur un serveur, la commande `python3 -m json.tool` '
                 "permet de valider syntaxiquement et d'indenter tout flux JSON reçu sur l'entrée "
                 'standard sans installer de paquet tiers.\n'
                 '\n'
                 "Pour l'exploitation avancée en pipeline shell, le processeur **`jq`** offre un "
                 "langage de requêtage complet permettant d'extraire une métadonnée imbriquée "
                 "(`.meta.total_items`), d'itérer sur une collection (`.data[]`) ou de filtrer les "
                 'objets selon un prédicat métier (`select(.duree_jours >= 5)`).',
  'code_example': '# 1. Indenter une réponse curl avec Python (sans installer jq) :\n'
                  'curl -s http://127.0.0.1:8000/api/sandbox/formations | python3 -m json.tool\n'
                  '\n'
                  '# 2. Extraire uniquement les titres des formations avec jq :\n'
                  "curl -s http://127.0.0.1:8000/api/sandbox/formations | jq '.data[].titre'\n"
                  '\n'
                  '# 3. Filtrer les formations de 5 jours ou plus avec jq :\n'
                  "curl -s http://127.0.0.1:8000/api/sandbox/formations | jq '.data[] | "
                  "select(.duree_jours >= 5)'"},
 {'id': 'linux_logs_audit',
  'term': 'Analyse de Journaux (Logs) en Temps Réel (tail -f, grep, awk, journalctl)',
  'category': 'Linux & Réseau Prod',
  'level': 'Addendum Linux',
  'short': "Commandes d'exploitation permettant de surveiller le trafic HTTP en direct, isoler les "
           'erreurs 500 et détecter les adresses IP suspectes.',
  'analogy': 'Les écrans de vidéosurveillance et la boîte noire du serveur : permettent de suivre '
             'chaque requête à la milliseconde près et de repérer immédiatement une anomalie ou '
             'une attaque.',
  'explanation': "La surveillance opérationnelle d'un service ASGI s'appuie sur `tail -f "
                 "fichier.log` (ou `journalctl -u isgp-api -f`) pour suivre en continu l'arrivée "
                 "des événements, combiné à `grep` afin d'isoler un code d'anomalie (`500`, `401`) "
                 "ou de reconstituer le parcours complet d'un identifiant `X-Request-ID`.\n"
                 '\n'
                 "Pour l'analyse volumétrique rapide d'un incident ou d'un pic de charge, "
                 "l'enchaînement `awk`, `sort` et `uniq -c` agrège les journaux d'accès Nginx ou "
                 'Uvicorn et fait ressortir immédiatement les adresses IP les plus '
                 'sollicitatrices.',
  'code_example': '# 1. Suivre les logs en temps réel en filtrant uniquement les erreurs 4xx et '
                  '5xx :\n'
                  'tail -f /var/log/nginx/access.log | grep --line-buffered -E " (401|403|429|500) '
                  '"\n'
                  '\n'
                  "# 2. Retrouver toute l'histoire d'une requête grâce à son X-Request-ID :\n"
                  'grep "req-8f2a9c01" /var/log/api_isgp/*.log\n'
                  '\n'
                  "# 3. Identifier le Top 10 des adresses IP qui appellent le plus l'API :\n"
                  "awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -nr | head "
                  '-n 10'},
 {'id': 'linux_chmod_env',
  'term': "Permissions Linux (chmod 600) & Variables d'Environnement (export / .env)",
  'category': 'Linux & Réseau Prod',
  'level': 'Addendum Linux',
  'short': "Verrouillage des droits d'accès aux fichiers secrets (.env, clés privées .pem) et "
           "injection de variables d'environnement sous Linux.",
  'analogy': "Mettre les clés du serveur dans un tiroir dont seul l'utilisateur propriétaire "
             'possède la clé (`chmod 600`), au lieu de les laisser sur une table accessible à tous '
             'les comptes de la machine (`chmod 644` ou `777`).',
  'explanation': "L'application du masque **`chmod 600`** (`-rw-------`) restreint la lecture et "
                 "l'écriture du fichier au seul compte système propriétaire en retirant toute "
                 'permission aux autres utilisateurs locaux ; cette mesure est impérative pour les '
                 'fichiers `.env`, les clés privées `private.pem` et les clés SSH.\n'
                 '\n'
                 'Parallèlement, la directive shell `export` injecte les variables de '
                 "configuration sensibles dans l'environnement du processus fils Uvicorn, où "
                 "l'application FastAPI les récupère proprement via `os.environ.get(...)` sans "
                 'jamais les inscrire dans le dépôt source.',
  'code_example': '# 1. Restreindre la lecture du fichier .env et de la clé privée au seul '
                  'propriétaire :\n'
                  'chmod 600 .env private_key.pem\n'
                  'ls -l .env  # Affiche : -rw------- 1 abdelouahab abdelouahab ...\n'
                  '\n'
                  "# 2. Exporter une variable d'environnement et lancer l'API FastAPI :\n"
                  'export API_SECRET_KEY="$(openssl rand -hex 32)"\n'
                  '.venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000'},
 {'id': 'linux_systemd_nginx',
  'term': 'Déploiement Linux : Service systemd, Uvicorn / Gunicorn ASGI & Reverse Proxy Nginx',
  'category': 'Linux & Réseau Prod',
  'level': 'Addendum Linux',
  'short': 'Architecture standard permettant de faire tourner une API FastAPI 24h/24 en tâche de '
           'fond avec redémarrage automatique et HTTPS.',
  'analogy': 'Transformer un moteur posé sur un établi (`uvicorn --reload`) en une centrale '
             'électrique automatisée (`systemd` + `Uvicorn Workers`) protégée par un poste de '
             'garde blindé (`Nginx`).',
  'explanation': 'En production Linux, une unité **`systemd`** '
                 '(`/etc/systemd/system/isgp-api.service`) supervise le processus ASGI Uvicorn ou '
                 'Gunicorn, collecte ses journaux standards et garantit son redémarrage '
                 "automatique en quelques secondes en cas d'arrêt inattendu (`Restart=always`).\n"
                 '\n'
                 'En frontal, le serveur **`Nginx`** assure la terminaison HTTPS sur les ports '
                 'publics `80` et `443`, filtre les requêtes malformées et répartit le trafic HTTP '
                 'propre vers la grappe locale `http://isgp_fastapi_cluster` via la directive '
                 '`proxy_pass`.',
  'code_example': "# Commandes d'exploitation du service systemd en production :\n"
                  'sudo systemctl daemon-reload\n'
                  'sudo systemctl enable --now isgp-api\n'
                  'sudo systemctl status isgp-api\n'
                  '\n'
                  '# Consulter les journaux du service en temps réel :\n'
                  'sudo journalctl -u isgp-api -f'},
 {'id': 'mime_content_type_accept_415',
  'term': "Types MIME (Content-Type vs Accept), request.headers['content-type'] & Code 415",
  'category': 'Types MIME & FastAPI',
  'level': 'Fondamental',
  'short': "Identifiant normalisé IANA (type/sous-type) décrivant le format exact d'un flux "
           "d'octets HTTP et pilotant la négociation de contenu dans FastAPI.",
  'analogy': "L'étiquette réglementaire collée sur un conteneur maritime : 'Liquide', 'Poudre' ou "
             "'Gaz'. Sans cette étiquette (Content-Type), le destinataire ne sait pas avec quel "
             'outil ouvrir le conteneur.',
  'explanation': "Dans la négociation HTTP, l'en-tête **`Content-Type`** qualifie la nature exacte "
                 'des octets transportés dans le corps du message courant (par exemple '
                 '`application/json; charset=utf-8`), accessible dans FastAPI via '
                 "`request.headers.get('content-type', '')`, tandis que l'en-tête **`Accept`** "
                 'exprime les formats de représentation que le client sait traiter en retour.\n'
                 '\n'
                 "Lorsqu'un appelant soumet une charge utile dans un format que l'endpoint refuse "
                 'de décoder, la norme RFC 9110 prescrit le renvoi explicite du code **`415 '
                 'Unsupported Media Type`**.',
  'code_example': '# Inspecter le type MIME entrant et rejeter proprement en 415 :\n'
                  'mime = request.headers.get("content-type", "").split(";")[0].strip()\n'
                  'if mime not in ("application/json", "application/x-www-form-urlencoded"):\n'
                  '    raise HTTPException(status_code=415, detail=f"Type MIME {mime} non '
                  'supporté")'},
 {'id': 'mime_json_vs_form_vs_multipart',
  'term': "Types MIME d'Entrée (POST) : BaseModel (JSON) vs Form(...) vs UploadFile = File(...)",
  'category': 'Types MIME & FastAPI',
  'level': "Cœur d'API",
  'short': 'Les trois grands types MIME utilisés pour envoyer des données à un serveur FastAPI '
           "lors d'une requête POST ou PUT.",
  'analogy': "Trois façons de transmettre un dossier à l'administration : un fichier informatique "
             'structuré (`application/json` validé par Pydantic), un coupon-réponse papier '
             '(`application/x-www-form-urlencoded` lu par `Form`), ou une pochette cartonnée '
             'contenant à la fois le coupon papier et des pièces jointes PDF '
             '(`multipart/form-data` lu par `Form` + `UploadFile`).',
  'explanation': "FastAPI sélectionne le mécanisme d'extraction des données entrantes selon le "
                 'type MIME de la requête `POST`. Une charge **`application/json`** émise par '
                 '`fetch()` ou un client mobile est désérialisée et validée par un schéma héritant '
                 'de **`pydantic.BaseModel`**.\n'
                 '\n'
                 "À l'inverse, la soumission classique d'un formulaire HTML `<form method='POST'>` "
                 'transite en **`application/x-www-form-urlencoded`** et se déclare via '
                 "**`Form(...)`**, tandis qu'un formulaire comportant des pièces jointes utilise "
                 '**`multipart/form-data`**, combinant `Form(...)` pour les champs textuels et '
                 '**`UploadFile = File(...)`** pour les flux binaires.',
  'code_example': '# 1. Route JSON (application/json) :\n'
                  '@app.post("/api/formations")\n'
                  'def creer_json(payload: FormationCreate):\n'
                  '    return payload\n'
                  '\n'
                  '# 2. Route Formulaire + Fichier (multipart/form-data) :\n'
                  '@app.post("/formations")\n'
                  'async def creer_form(titre: str = Form(...), pdf: UploadFile = File(None)):\n'
                  '    return {"titre": titre, "filename": pdf.filename if pdf else None}'},
 {'id': 'mime_response_csv_xml_sse',
  'term': 'Émettre des Types MIME Personnalisés (Response, JSONResponse, HTMLResponse, '
          'StreamingResponse)',
  'category': 'Types MIME & FastAPI',
  'level': "Cœur d'API",
  'short': 'Utilisation des classes de réponse Starlette/FastAPI avec media_type=... pour '
           'retourner tout format (CSV, XML, Problem+JSON, SSE).',
  'analogy': "Si `Jinja2Templates` est l'imprimante de brochures HTML et `JSONResponse` "
             "l'emballeur de colis JSON, `Response(..., media_type=...)` et `StreamingResponse` "
             "sont l'atelier sur mesure capable d'expédier des feuilles Excel CSV, des actes XML "
             'ou un flux continu.',
  'explanation': 'Bien que FastAPI sérialise par défaut les retours Python en `application/json`, '
                 "ses classes de réponse permettent d'émettre tout type MIME normalisé : "
                 '`text/csv` couplé à `Content-Disposition: attachment` pour les extractions '
                 "tabulaires, `application/problem+json` pour les diagnostics d'erreur conformes à "
                 "la norme **RFC 7807**, ou encore `application/xml` pour l'interopérabilité avec "
                 'des partenaires SOAP.\n'
                 '\n'
                 "Pour la diffusion continue d'événements serveur vers le navigateur (**SSE**), "
                 "l'utilisation de `StreamingResponse(generateur(), "
                 "media_type='text/event-stream')` maintient la connexion HTTP ouverte sur la "
                 'boucle asynchrone ASGI.',
  'code_example': 'from fastapi.responses import Response\n'
                  '\n'
                  '@app.get("/api/export.csv")\n'
                  'def exporter_csv():\n'
                  '    csv_data = "id,titre,duree\\n1,API REST FastAPI,5\\n"\n'
                  '    return Response(\n'
                  '        content=csv_data,\n'
                  '        media_type="text/csv; charset=utf-8",\n'
                  '        headers={"Content-Disposition": "attachment; filename=formations.csv"}\n'
                  '    )'},
 {'id': 'mime_send_file_disposition_nosniff',
  'term': 'Fichiers Binaires (FileResponse / StreamingResponse : PDF, PNG) & '
          'X-Content-Type-Options: nosniff',
  'category': 'Types MIME & FastAPI',
  'level': 'Intermédiaire',
  'short': 'Transmission de fichiers binaires avec FileResponse ou Response, contrôle de '
           "l'ouverture navigateur (inline vs attachment) et protection contre le MIME Sniffing.",
  'analogy': 'Envoyer un document PDF soit sous verre pour être lu sur place dans le navigateur '
             '(`inline`), soit dans une enveloppe scellée que le navigateur enregistre directement '
             'dans le dossier Téléchargements (`attachment`).',
  'explanation': "La restitution d'un document binaire tel qu'une attestation PDF ou un graphique "
                 "PNG s'opère dans FastAPI via `FileResponse` ou `Response(content=octets, "
                 "media_type='application/pdf')`. L'en-tête `Content-Disposition: inline` invite "
                 "le navigateur à afficher le document directement dans l'onglet, tandis que "
                 '`Content-Disposition: attachment; filename="facture.pdf"` déclenche '
                 "l'enregistrement sur le poste client.\n"
                 '\n'
                 "Sur toute route servant des fichiers fournis par des utilisateurs, l'ajout "
                 "systématique de l'en-tête **`X-Content-Type-Options: nosniff`** interdit au "
                 "navigateur de deviner le type du contenu et bloque l'exécution furtive de "
                 'scripts HTML ou JavaScript déguisés.',
  'code_example': 'from fastapi.responses import Response\n'
                  '\n'
                  '@app.get("/api/facture.pdf")\n'
                  'def facture_pdf():\n'
                  '    pdf_bytes = b"%PDF-1.4 ..."\n'
                  '    return Response(\n'
                  '        content=pdf_bytes,\n'
                  '        media_type="application/pdf",\n'
                  '        headers={"Content-Disposition": \'attachment; '
                  'filename="facture.pdf"\'}\n'
                  '    )'},
 {'id': 'api_versioning_v1_vs_v2',
  'term': 'Pourquoi voit-on toujours /api/v1 et rarement /api/v2 ? (Loi de Postel & Assurance-Vie)',
  'category': 'Architecture Web',
  'level': "Cœur d'API",
  'short': 'Explication architecturale de la longévité de /api/v1 (ajouts rétrocompatibles) et de '
           "l'obligation de préfixer par /v1 dès le premier jour.",
  'analogy': 'Construire une maison avec un compteur électrique prévu pour un 2e étage (/api/v1) : '
             "tant qu'on ajoute des meubles dans les pièces existantes (nouveaux champs JSON "
             "optionnels), on reste au 1er étage pendant 10 ans. Mais le jour où l'on doit refaire "
             'les fondations (Breaking Change), la réservation du 2e étage (/api/v2) évite de '
             "démolir le 1er pendant qu'il est habité.",
  'explanation': 'Conformément au principe de robustesse de la **Loi de Postel** (*Tolerant '
                 "Reader*), l'enrichissement d'une réponse JSON par de nouveaux attributs, la "
                 "création de routes inédites ou l'ajout de paramètres de requête facultatifs "
                 'préservent intégralement la compatibilité ascendante : plus de 90 % du cycle '
                 "d'évolution d'un service s'accomplit ainsi sans jamais quitter l'espace "
                 '`/api/v1`.\n'
                 '\n'
                 'Intégrer le préfixe `/api/v1` dès la première mise en production constitue '
                 'néanmoins une assurance architecturale indispensable : si des dizaines de '
                 "milliers d'applications mobiles compilées appellent `/api/formations` sans "
                 'segment de version, aucune refonte structurelle future ne pourra être déployée '
                 'en parallèle sans rompre les clients existants.',
  'code_example': '# Coexistence de /api/v1 et /api/v2 via deux APIRouter FastAPI :\n'
                  'router_v1 = APIRouter(prefix="/api/v1/formations", tags=["Formations v1"])\n'
                  'router_v2 = APIRouter(prefix="/api/v2/formations", tags=["Formations v2"])\n'
                  'app.include_router(router_v1)\n'
                  'app.include_router(router_v2)'},
 {'id': 'breaking_vs_non_breaking_changes',
  'term': 'Évolution Rétrocompatible (Non-Breaking) vs Rupture de Contrat (Breaking Change)',
  'category': 'Architecture Web',
  'level': "Cœur d'API",
  'short': 'Distinction chirurgicale entre une modification qui préserve les clients v1 existants '
           'et une modification qui exige la création de /api/v2.',
  'analogy': "Ajouter une colonne supplémentaire à la fin d'un catalogue imprimé ne gêne personne "
             '(Non-Breaking). En revanche, remplacer les prix en Dinars par un objet complexe ou '
             "supprimer la colonne 'Titre' fait planter tous les lecteurs automatiques (Breaking "
             'Change).',
  'explanation': "Une évolution est qualifiée de **rétrocompatible** (*Non-Breaking*) lorsqu'elle "
                 'se limite à exposer un champ supplémentaire en sortie, à publier un nouvel '
                 'endpoint tel que `GET /api/v1/certificats` ou à accepter un critère optionnel '
                 "comme `?lang=fr` ; ces ajouts s'intègrent directement dans la version `v1`.\n"
                 '\n'
                 'En revanche, renommer ou supprimer un attribut existant (`intitule` remplacé par '
                 '`titre`), modifier la structure d\'une valeur (`"duree": 5` devenant un objet '
                 '`{"valeur": 5, "unite": "jours"}`) ou imposer un nouveau champ obligatoire en '
                 'entrée constitue une **rupture de contrat** (*Breaking Change*) qui exige '
                 "l'ouverture d'une branche `/api/v2`.",
  'code_example': '# v1 (Schéma plat historique) :\n'
                  '{"id": 1, "intitule": "Architecture API", "duree": 5}\n'
                  '\n'
                  '# v2 (Breaking Change sur le nom et le type des champs) :\n'
                  '{"id": 1, "titre": "Architecture API", "duree": {"valeur": 5, "unite": '
                  '"jours"}}'},
 {'id': 'rfc8594_deprecation_sunset_410',
  'term': "Dépréciation d'API (Norme RFC 8594 : En-têtes Deprecation, Sunset, Link & Code 410 "
          'Gone)',
  'category': 'Architecture Web',
  'level': "Cœur d'API",
  'short': "Protocole standard IETF permettant d'avertir les clients qu'une version d'API "
           '(/api/v1) est en fin de vie avant son extinction définitive (410 Gone).',
  'analogy': "Les panneaux d'information routiers posés 6 mois avant la fermeture d'un ancien pont "
             ': ils indiquent que le pont est en fin de vie (`Deprecation: true`), la date exacte '
             'de fermeture (`Sunset`), et la flèche vers le nouveau pont (`Link: </api/v2>; '
             'rel="successor-version"`).',
  'explanation': "L'extinction maîtrisée d'une version historique d'API s'appuie sur la "
                 "signalisation protocolaire définie par l'IETF (**RFC 8594**). Tant que "
                 "l'ancienne branche demeure active en période de transition, le serveur joint aux "
                 "réponses l'en-tête `Deprecation: true`, la date butoir `Sunset: Thu, 31 Dec 2026 "
                 '23:59:59 GMT` ainsi que le pointeur `Link: </api/v2/formations>; '
                 'rel="successor-version"`.\n'
                 '\n'
                 "Une fois l'échéance `Sunset` franchie et la version retirée du service, "
                 "l'endpoint ne renvoie pas un simple `404`, mais le code sémantique **`410 "
                 'Gone`**, signifiant explicitement aux intégrateurs que la ressource a existé '
                 'mais a été définitivement décommissionnée.',
  'code_example': 'def injecter_headers_depreciation_v1(response: Response):\n'
                  '    response.headers["Deprecation"] = "true"\n'
                  '    response.headers["Sunset"] = "Thu, 31 Dec 2026 23:59:59 GMT"\n'
                  '    response.headers["Link"] = \'</api/v2/formations>; '
                  'rel="successor-version"\'\n'
                  '\n'
                  'router_v1 = APIRouter(prefix="/api/v1/formations", '
                  'dependencies=[Depends(injecter_headers_depreciation_v1)])'},
 {'id': 'api_envelope_pagination_cursor_offset',
  'term': 'Enveloppe JSON (meta / data / links) & Pagination (Offset/Limit vs Cursor)',
  'category': 'Architecture Web',
  'level': 'Intermédiaire',
  'short': "Structuration racine d'une réponse JSON de collection pour permettre l'évolution sans "
           'Breaking Change et la pagination haute performance.',
  'analogy': "Ne jamais expédier des feuilles volantes sans chemise cartonnée : l'objet enveloppe "
             '`{"meta": ..., "data": [...]}` est la chemise sur laquelle on peut inscrire le '
             'numéro de page et le total sans toucher aux feuilles `data`.',
  'explanation': "Retourner un tableau JSON brut `[...]` à la racine d'une collection fige "
                 "irrémédiablement le contrat, car l'ajout ultérieur d'un compteur total ou d'un "
                 'curseur de navigation obligerait à transformer la racine en objet `{...}` au '
                 "prix d'une rupture de compatibilité. L'encapsulation systématique dans une "
                 'enveloppe `{"meta": {...}, "data": [...]}` prévient cet écueil.\n'
                 '\n'
                 "Pour les volumes modérés dotés d'un sélecteur de numéros de pages, l'approche "
                 '**`Offset/Limit`** (`LIMIT 20 OFFSET 20`) offre une ergonomie immédiate. Sur des '
                 'tables comptant plusieurs millions de lignes ou alimentées en continu, la '
                 '**pagination par curseur** (`WHERE id > :after_id ORDER BY id ASC LIMIT 20`) '
                 "exploite l'index primaire en temps constant `O(1)` sans dérive de décalage.",
  'code_example': 'return {\n'
                  '    "meta": {"version": "v2", "page": 1, "per_page": 20, "total_items": 145},\n'
                  '    "data": formations,\n'
                  '    "links": {"self": "/api/v2/formations?page=1", "next": '
                  '"/api/v2/formations?page=2"}\n'
                  '}'},
 {'id': 'swagger_openapi_3',
  'term': 'Swagger UI (/docs), ReDoc (/redoc) & Spécification OpenAPI 3.1 Auto-Générée',
  'category': 'Architecture Web',
  'level': "Cœur d'API",
  'short': "Norme mondiale de contrat d'API (OpenAPI 3.1 JSON) et portails Web interactifs (/docs "
           'et /redoc) générés automatiquement par FastAPI.',
  'analogy': "OpenAPI 3.1 est le plan d'architecte coté et normalisé de l'immeuble "
             '(`/openapi.json`), tandis que Swagger UI (`/docs`) et ReDoc (`/redoc`) sont les '
             'visites virtuelles interactives générées automatiquement à partir de vos modèles '
             'Pydantic (boutons « Authorize » et « Try it out »).',
  'explanation': 'Par simple introspection des annotations Python, des schémas `BaseModel` '
                 'Pydantic v2, des contraintes `Query`/`Path` et des dépendances `HTTPBearer` ou '
                 '`APIKeyHeader`, FastAPI synthétise dynamiquement le document normatif **OpenAPI '
                 '3.1.0** sur la route `/openapi.json`.\n'
                 '\n'
                 'À partir de ce contrat unique, le framework sert nativement les portails '
                 'interactifs **Swagger UI** (`/docs`, doté du bouton cadenas *Authorize* et du '
                 "banc d'essai *Try it out*) et **ReDoc** (`/redoc`), tout en permettant "
                 "l'importation directe du schéma dans Postman, Insomnia ou les générateurs de "
                 'SDKs.',
  'code_example': 'app = FastAPI(\n'
                  '    title="API Catalogue ISGP",\n'
                  '    version="2.0.0",\n'
                  '    docs_url="/docs",          # Swagger UI interactif\n'
                  '    redoc_url="/redoc",        # Documentation ReDoc\n'
                  '    openapi_url="/openapi.json"\n'
                  ')'},
 {'id': 'curl_postman_httpie',
  'term': 'curl, Postman, HTTPie & REST Client (.http)',
  'category': 'Architecture Web',
  'level': 'Fondamental',
  'short': 'Outils de test et de diagnostic permettant de forger des requêtes HTTP (GET, POST, '
           'PUT, PATCH, DELETE, Headers) sans navigateur.',
  'analogy': "Un multimètre d'ingénieur réseau : là où un navigateur classique ne sait envoyer que "
             'des requêtes GET simples, curl et Postman permettent de contrôler chaque en-tête, '
             'chaque méthode et chaque octet JSON.',
  'explanation': "L'utilitaire **`curl`** demeure l'instrument universel présent sur tout serveur "
                 'Linux pour forger une requête HTTP sans intermédiaire graphique : ses '
                 "commutateurs permettent d'afficher les en-têtes de réponse (`-i`), d'inspecter "
                 "la négociation complète (`-v`), de fixer le verbe (`-X`), d'injecter un en-tête "
                 '(`-H`) et de transmettre un corps JSON (`-d`).\n'
                 '\n'
                 'Au quotidien sur le poste de développement, cet outil est complété par les '
                 'clients graphiques comme **Postman**, **Bruno** ou **Insomnia** pour organiser '
                 'des collections partageables, ainsi que par **HTTPie** (`http`) et les fichiers '
                 'déclaratifs **REST Client** (`.http`) versionnés directement dans VS Code ou '
                 'Antigravity IDE.',
  'code_example': 'curl -i -X POST "http://127.0.0.1:8000/api/sandbox/formations" \\\n'
                  '  -H "Content-Type: application/json" \\\n'
                  '  -H "X-API-Key: isgp-secret-2026" \\\n'
                  '  -d \'{"titre": "API FastAPI", "duree_jours": 5}\''},
 {'id': 'rate_limiting',
  'term': 'Rate Limiting (Limitation de Débit & Code 429)',
  'category': 'Sécurité & Architecture API',
  'level': "Cœur d'API",
  'short': "Mécanisme qui limite le nombre de requêtes qu'un client peut envoyer sur une période "
           'donnée (ex. 60 requêtes par minute).',
  'analogy': 'Comme un distributeur bancaire qui autorise au maximum 3 essais ou un plafond de '
             'retrait par heure : si un programme envoie 10 000 demandes par seconde (par erreur '
             'ou par attaque), le guichet le bloque temporairement pour ne pas paralyser toute la '
             'banque.',
  'explanation': 'Sans Rate Limiting, un seul script mal codé (une boucle `while True`) ou un '
                 'pirate peut saturer votre serveur. Le serveur compte les requêtes par adresse IP '
                 'ou par clé API (Fenêtre Glissante ou Token Bucket). Quand le quota est dépassé, '
                 'il renvoie le code officiel **`429 Too Many Requests`** accompagné des en-têtes '
                 '`X-RateLimit-Remaining: 0` et `Retry-After`.',
  'code_example': '# Si le client dépasse 3 requêtes en 20 secondes :\n'
                  'return JSONResponse(\n'
                  '    status_code=429,\n'
                  '    headers={"Retry-After": "20", "X-RateLimit-Remaining": "0"},\n'
                  '    content={"erreur": "Quota dépassé (Rate Limit)", "reessayer_dans_secondes": '
                  '20}\n'
                  ')'},
 {'id': 'token_bearer',
  'term': "Token / Bearer Token & JWT (HTTPBearer & Jeton d'Accès Signé)",
  'category': 'Sécurité & Architecture API',
  'level': "Cœur d'API",
  'short': 'Un laissez-passer numérique temporaire et signé (HMAC), remis au client après '
           'connexion pour prouver son identité à chaque requête.',
  'analogy': "La carte magnétique d'une chambre d'hôtel : vous montrez votre pièce d'identité une "
             'seule fois à la réception (`/api/auth/token`), on vous remet une carte valable 24h '
             '(le Token). Ensuite, vous présentez simplement cette carte devant chaque porte '
             '(`Authorization: Bearer <token>`).',
  'explanation': "Attention : le contenu (`Payload`) d'un Token JWT ou `itsdangerous` est encodé "
                 'en Base64 (lisible par tous), mais **signé mathématiquement** avec la '
                 "`SECRET_KEY` du serveur (infalsifiable). N'y stockez jamais de mot de passe en "
                 'clair !',
  'code_example': 'from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials\n'
                  '\n'
                  'security = HTTPBearer()\n'
                  '\n'
                  'def verifier_token(creds: HTTPAuthorizationCredentials = Depends(security)):\n'
                  '    token = creds.credentials'},
 {'id': 'refresh_token_rbac',
  'term': 'Authentification (AuthN / 401) vs Autorisation (AuthZ / 403, RBAC, Scopes & BOLA)',
  'category': 'Sécurité & Architecture API',
  'level': "Cœur d'API",
  'short': 'AuthN vérifie QUI vous êtes (échec = 401 Unauthorized) ; AuthZ vérifie QUELS sont vos '
           'droits sur la ressource (échec = 403 Forbidden).',
  'analogy': "Le passeport contrôlé à l'entrée de l'aéroport est l'Authentification (`AuthN` -> "
             "`401` si absent). La carte d'accès réservée aux pilotes pour entrer dans le cockpit "
             "est l'Autorisation (`AuthZ` -> `403` si vous êtes un simple passager).",
  'explanation': "La gouvernance des accès distingue strictement l'**authentification** (`AuthN`, "
                 "vérifiant l'identité de l'appelant par jeton Bearer ou clé API sous peine "
                 "d'erreur `401 Unauthorized`) de l'**autorisation** (`AuthZ`, validant ses droits "
                 "effectifs sous peine d'erreur `403 Forbidden`).\n"
                 '\n'
                 "Dans une architecture FastAPI professionnelle, l'autorisation combine trois "
                 'garde-fous injectés via `Depends(...)` : le contrôle par rôle (**RBAC**, '
                 'distinguant par exemple `stagiaire` et `admin`), les **scopes OAuth2** '
                 'granulaires portés par le jeton (`formations:read`, `audit:admin`), et la '
                 "vérification systématique de la propriété de l'enregistrement ciblé "
                 "(`dossier['proprietaire'] == user['sub']`) afin d'éliminer la faille critique "
                 '**BOLA** (*Broken Object Level Authorization*, risque OWASP API n° 1).',
  'code_example': 'if not token_valide:\n'
                  '    raise HTTPException(status_code=401, detail={"etape": "AuthN", "erreur": '
                  '"Non authentifié"})\n'
                  'if user["role"] != "admin" or "audit:admin" not in user["scopes"]:\n'
                  '    raise HTTPException(status_code=403, detail={"etape": "AuthZ", "erreur": '
                  '"Droits insuffisants"})'},
 {'id': 'secret_env',
  'term': "Secrets & Variables d'Environnement (.env / os.environ)",
  'category': 'Sécurité & Architecture API',
  'level': "Cœur d'API",
  'short': 'Pratique fondamentale consistant à stocker les mots de passe, clés de signature et '
           "clés d'API hors du code source Python.",
  'analogy': 'Vous ne gravez jamais le code de votre coffre-fort sur la façade extérieure de votre '
             "maison. Vous le gardez dans une enveloppe scellée à l'intérieur du coffre de la "
             "direction (les variables d'environnement du serveur).",
  'explanation': "Règle d'or absolue : **on n'écrit jamais un secret en dur dans `app.py`** (car "
                 'si vous partagez le code sur Git, tout le monde voit vos mots de passe). On '
                 "stocke les secrets dans l'environnement du système et Python les lit avec "
                 "`os.environ.get('API_SECRET_KEY')`.",
  'code_example': 'import os\n'
                  '\n'
                  "# Lecture sécurisée depuis l'environnement du serveur :\n"
                  'SECRET_KEY = os.environ.get("API_SECRET_KEY", "cle-dev-locale")'},
 {'id': 'signature_hmac',
  'term': 'Signature Cryptographique HMAC & Webhooks',
  'category': 'Sécurité & Architecture API',
  'level': "Cœur d'API",
  'short': "Sceau mathématique calculé avec une clé secrète garantissant qu'un Token ou un Webhook "
           "entrant n'a pas été falsifié.",
  'analogy': "Le cachet de cire officiel d'un ministère sur un diplôme : tout le monde peut lire "
             'ce qui est écrit sur le diplôme, mais personne ne peut modifier son nom ou sa note '
             'sans briser le cachet, car seul le ministère possède le tampon officiel '
             '(`SECRET_KEY`).',
  'explanation': "Utilisé à la fois pour signer les Bearer Tokens et pour vérifier l'authenticité "
                 'des **Webhooks** entrants (`X-Webhook-Signature: sha256=...`) sur les octets '
                 'bruts `await request.body()`. La comparaison doit toujours utiliser '
                 '`hmac.compare_digest(a, b)` pour contrer les attaques temporelles (*Timing '
                 'Attacks*).',
  'code_example': 'import hmac, hashlib\n'
                  'corps_brut = await request.body()\n'
                  'sig = hmac.new(SECRET.encode(), corps_brut, hashlib.sha256).hexdigest()\n'
                  'est_valide = hmac.compare_digest(sig_recue, sig)'},
 {'id': 'cookies_httponly_secure_samesite',
  'term': 'Cookies HTTP Sécurisés : Set-Cookie, HttpOnly (Anti-XSS), Secure (HTTPS) & SameSite '
          '(Anti-CSRF)',
  'category': 'Sécurité & Architecture API',
  'level': "Cœur d'API",
  'short': 'Mécanisme standard (RFC 6265) permettant au serveur de stocker un jeton ou un état '
           "dans le navigateur en l'isolant de JavaScript et des sites tiers.",
  'analogy': 'Stocker un jeton dans `localStorage` revient à poser ses clés sur la table du café '
             '(tout script XSS peut les voler). Un Cookie `HttpOnly; Secure; SameSite=strict` '
             'place les clés dans un coffre blindé du navigateur que seul le serveur peut ouvrir.',
  'explanation': "Dans FastAPI, le cycle d'un cookie repose sur l'émission de l'en-tête "
                 '`Set-Cookie` via `response.set_cookie(...)`, sa lecture déclarative par '
                 '`Cookie(default=None)` et sa révocation immédiate via '
                 '`response.delete_cookie(...)` (`Max-Age=0`).\n'
                 '\n'
                 "Tout cookie de session ou d'authentification exige trois attributs défensifs "
                 'complémentaires : **`HttpOnly`** (`httponly=True`) soustrait la valeur à '
                 '`document.cookie` pour bloquer le vol par injection **XSS**, **`Secure`** '
                 '(`secure=True`) restreint le transport aux seuls canaux **HTTPS/TLS**, et '
                 '**`SameSite`** (`strict` ou `lax`) neutralise les requêtes forgées inter-sites '
                 '(**CSRF**).',
  'code_example': 'response.set_cookie(\n'
                  '    key="isgp_auth_token",\n'
                  '    value=jeton_signe,\n'
                  '    max_age=3600,\n'
                  '    httponly=True,     # Invisible pour document.cookie (Anti-XSS)\n'
                  '    secure=True,       # HTTPS uniquement\n'
                  '    samesite="strict"  # Anti-CSRF\n'
                  ')'},
 {'id': 'signed_session_cookie_hmac',
  'term': 'Cookie de Session Signé HMAC (URLSafeTimedSerializer / SessionMiddleware) vs Cookie '
          'Standard en Clair',
  'category': 'Sécurité & Architecture API',
  'level': "Cœur d'API",
  'short': "Différence fondamentale entre un cookie ordinaire modifiable par l'utilisateur et un "
           'cookie de session signé cryptographiquement avec SECRET_KEY.',
  'analogy': "Un cookie ordinaire (`set_cookie('theme', 'sombre')`) est écrit au crayon à papier : "
             'le client peut le gommer et le modifier. Le cookie de session signé est scellé par '
             "l'empreinte mathématique `HMAC` de `SECRET_KEY` : la moindre retouche brise le "
             'sceau.',
  'explanation': 'Un cookie ordinaire lu par `Cookie(default=None)` voyage en clair chez le client '
                 "et doit rester cantonné aux préférences cosmétiques dépourvues d'enjeu de "
                 'sécurité, telles que la langue ou le thème visuel.\n'
                 '\n'
                 "Dès qu'un état d'authentification est stocké côté navigateur sans base de "
                 "session serveur, l'emploi d'un **cookie de session signé** "
                 '(`URLSafeTimedSerializer` ou `SessionMiddleware` de Starlette) sérialise les '
                 'attributs en Base64URL et y appose une signature **HMAC** liée à `SECRET_KEY` : '
                 "la moindre modification effectuée dans l'inspecteur F12 entraîne le rejet "
                 'cryptographique immédiat du cookie.',
  'code_example': 'from itsdangerous import URLSafeTimedSerializer\n'
                  'signataire = URLSafeTimedSerializer(os.environ["SECRET_KEY"], '
                  'salt="isgp-session")\n'
                  '\n'
                  '# Écriture signée par HMAC :\n'
                  'valeur_scellee = signataire.dumps({"utilisateur": "yasmine.merabet", "role": '
                  '"auditeur"})\n'
                  'response.set_cookie(key="session", value=valeur_scellee, httponly=True, '
                  'samesite="lax")'},
 {'id': 'cors_preflight',
  'term': 'CORS (CORSMiddleware) & Requête Preflight OPTIONS',
  'category': 'Sécurité & Architecture API',
  'level': "Cœur d'API",
  'short': 'Mécanisme de sécurité des navigateurs Web contrôlant quels domaines externes sont '
           'autorisés à lire les réponses de votre API.',
  'analogy': "Une liste d'invités accrochée à l'entrée d'un salon privé : si une application React "
             "hébergée sur un domaine inconnu tente d'interroger l'API depuis le navigateur d'un "
             "client, le navigateur vérifie d'abord si ce domaine figure sur la liste blanche "
             '(`Access-Control-Allow-Origin`).',
  'explanation': 'La politique de même origine (*Same-Origin Policy*) est un mécanisme de '
                 "confinement propre aux navigateurs Web, ce qui explique qu'un appel direct "
                 'depuis `curl` ou un script serveur Python ne subisse jamais de blocage '
                 '**CORS**.\n'
                 '\n'
                 "Lorsqu'une application frontale JavaScript hébergée sur une origine distincte "
                 'émet une requête mutative (`POST`, `PUT`, `DELETE`) ou joint un en-tête '
                 '`Authorization`, le navigateur déclenche au préalable une requête **`OPTIONS`** '
                 'dite *Preflight*, que le composant `CORSMiddleware` de FastAPI traite '
                 'automatiquement selon la liste blanche `allow_origins`.',
  'code_example': 'from fastapi.middleware.cors import CORSMiddleware\n'
                  '\n'
                  'app.add_middleware(\n'
                  '    CORSMiddleware,\n'
                  '    allow_origins=["https://portail.isgp.dz", "http://localhost:3000"],\n'
                  '    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],\n'
                  '    allow_headers=["Content-Type", "Authorization"],\n'
                  ')'},
 {'id': 'idempotence_put_patch',
  'term': 'Idempotence, PUT vs PATCH & Idempotency-Key',
  'category': 'Architecture Web',
  'level': "Cœur d'API",
  'short': "Propriété mathématique d'une opération qui produit le même état sur le serveur qu'elle "
           'soit exécutée 1 fois ou 10 fois.',
  'analogy': "Appuyer 5 fois sur le bouton d'appel d'un ascenseur au 3ème étage est **idempotent** "
             "(l'ascenseur vient une seule fois au 3ème). Appuyer 5 fois sur « Débiter 10 000 DZD "
             "» ne l'est pas !",
  'explanation': "Au sens du standard HTTP, les méthodes `GET`, `PUT` (remplacement intégral d'une "
                 "ressource identifiée) et `DELETE` possèdent la propriété d'**idempotence** : "
                 "répéter une requête identique laisse l'état du serveur inchangé après la "
                 'première application, tandis que `PATCH` opère une modification partielle ciblée '
                 'grâce à `payload.model_dump(exclude_unset=True)`.\n'
                 '\n'
                 "La méthode `POST`, en revanche, n'est pas nativement idempotente : pour prévenir "
                 "toute double facturation ou double inscription lors d'un réessai consécutif à "
                 "une coupure réseau, le client accompagne sa requête d'un identifiant unique "
                 '**`Idempotency-Key`** mémorisé côté serveur.',
  'code_example': '# En-tête déclaré dans FastAPI sur un POST critique :\n'
                  'def creer_commande(idempotency_key: str | None = Header(default=None, '
                  'alias="Idempotency-Key")):'},
 {'id': 'pagination_filtering',
  'term': 'Pagination (Query page/limit), Filtrage & Tri',
  'category': 'Architecture Web',
  'level': 'Fondamental',
  'short': "Découpage d'une grande collection en tranches via les paramètres d'URL "
           '`?page=1&limit=20&tri=duree_jours`.',
  'analogy': 'Consulter un catalogue de 50 000 articles par pages de 20 résultats au lieu '
             "d'imprimer les 50 000 lignes d'un seul bloc.",
  'explanation': 'Formule mathématique du découpage (Offset Pagination) :\n'
                 '`offset = (page - 1) * limit`\n'
                 'En Python : `resultats[offset : offset + limit]`. En SQL : `LIMIT ? OFFSET ?`. '
                 "L'API retourne une enveloppe contenant `meta` (`total_items`, `total_pages`, "
                 '`has_next`) et `data`.',
  'code_example': 'def lister(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):\n'
                  '    offset = (page - 1) * limit'},
 {'id': 'jinja2_forms_request_form',
  'term': 'Templates Jinja2 (Jinja2Templates) & Formulaires HTML (Form / UploadFile)',
  'category': 'FastAPI',
  'level': "Cœur d'API",
  'short': 'Séparation propre du HTML dans le dossier templates/ avec Jinja2Templates et '
           'traitement des formulaires Web envoyés en application/x-www-form-urlencoded ou '
           'multipart/form-data.',
  'analogy': "Jinja2 est le moule d'imprimerie (`.html`) dans lequel FastAPI injecte les variables "
             'Python (`{{ titre }}`) sans jamais mélanger le HTML dans le code Python. `Form(...)` '
             "est le guichet qui lit les bordereaux papier (`<form method='POST'>`), tandis que "
             '`BaseModel` lit les colis électroniques JSON.',
  'explanation': 'Une architecture FastAPI propre bannit toute chaîne HTML concaténée dans le code '
                 'Python en confiant le rendu visuel à **`Jinja2Templates`** '
                 "(`templates.TemplateResponse(request=request, name='page.html', "
                 'context={...})`), qui échappe automatiquement les expressions `{{ variable }}` '
                 'contre les injections XSS tout en offrant les structures `{% for %}` et `{% if '
                 '%}`.\n'
                 '\n'
                 "Côté réception, les champs nommés (`name='...'`) d'un formulaire `<form "
                 "method='POST'>` encodés en `application/x-www-form-urlencoded` sont validés "
                 'déclarativement par **`Form(...)`**, tandis que les pièces jointes soumises en '
                 '`multipart/form-data` sont réceptionnées via **`UploadFile = File(...)`**.',
  'code_example': '@app.post("/formations", response_class=HTMLResponse)\n'
                  'async def soumettre_form(request: Request, titre: str = Form(...), duree_jours: '
                  'int = Form(...)):\n'
                  '    return templates.TemplateResponse(request=request, name="formations.html", '
                  'context={"formations": FORMATIONS})'},
 {'id': 'path_variables_syntax',
  'term': "Variables d'URL : {variable} (FastAPI/OpenAPI) vs <variable> (Flask) vs :variable "
          '(Postman/Node)',
  'category': 'FastAPI',
  'level': 'Fondamental',
  'short': 'Les trois notations différentes utilisées selon les frameworks et outils pour '
           "représenter un paramètre dynamique dans le chemin d'une URL.",
  'analogy': "Trois façons d'écrire un champ à remplir sur un formulaire administratif selon le "
             'pays : `« Votre Nom : {nom} »` (FastAPI/OpenAPI), `« Votre Nom : <___> »` (Flask), '
             'ou `« Votre Nom : :nom »` (Postman/Express). Le principe est identique, seule la '
             "ponctuation change selon l'outil.",
  'explanation': "La déclaration d'un segment dynamique d'URL suit dans **FastAPI** et **OpenAPI "
                 '3.1** la notation par accolades de la norme RFC 6570 '
                 "(`@app.get('/api/v1/formations/{id}')`) associée à une annotation de type Python "
                 'telle que `id: int`.\n'
                 '\n'
                 "À titre de repère comparatif, l'écosystème historique Flask/Werkzeug emploie des "
                 "chevrons (`<int:id>`), tandis qu'Express.js et l'interface **Postman** utilisent "
                 "le préfixe deux-points (`/api/formations/:id`, qui alimente l'onglet *Path "
                 "Variables*). Lors de l'appel effectif dans `curl` ou la barre d'adresse du "
                 'navigateur, ce marqueur cède toujours la place à la valeur concrète '
                 '(`/api/formations/42`).',
  'code_example': '# 1. Dans le code serveur Python FastAPI (Accolades {...} + Type Hint) :\n'
                  '@app.get("/api/v1/formations/{id}")\n'
                  'def lire_formation(id: int):\n'
                  '    return {"id": id}\n'
                  '\n'
                  '# 2. Dans Flask (Chevrons <int:id>) :\n'
                  '# @app.route("/api/v1/formations/<int:id>")\n'
                  '\n'
                  '# 3. Dans Postman (Deux-points :variable) :\n'
                  '# GET http://127.0.0.1:8000/api/v1/formations/:id\n'
                  '\n'
                  '# 4. Dans curl (Valeur réelle) :\n'
                  '# curl -i http://127.0.0.1:8000/api/v1/formations/42'},
 {'id': 'middlewares_hooks',
  'term': "Middleware HTTP Asynchrone (@app.middleware('http')) & X-Request-ID",
  'category': 'FastAPI',
  'level': 'Intermédiaire',
  'short': 'Fonction asynchrone enveloppant chaque requête autour de await call_next(request) pour '
           'la journalisation, le chronométrage et la corrélation.',
  'analogy': "Le portique de sécurité à l'entrée d'un bâtiment qui enregistre l'heure d'arrivée de "
             "chaque visiteur (avant `await call_next(request)`) et l'heure de sortie (après "
             '`await call_next(request)`).',
  'explanation': "Permet d'attacher un identifiant unique `X-Request-ID` (UUID) dans "
                 '`request.state.request_id`, de mesurer la latence exacte en millisecondes '
                 "(`X-Response-Time-Ms`) et d'injecter les en-têtes de sécurité sans dupliquer de "
                 'code.',
  'code_example': '@app.middleware("http")\n'
                  'async def audit_middleware(request: Request, call_next):\n'
                  '    start = time.perf_counter()\n'
                  '    response = await call_next(request)\n'
                  '    response.headers["X-Response-Time-Ms"] = str(round((time.perf_counter() - '
                  'start) * 1000, 2))\n'
                  '    return response'},
 {'id': 'wsgi_blueprints',
  'term': 'APIRouter, Application Factory & Serveur ASGI (Uvicorn / Gunicorn)',
  'category': 'FastAPI',
  'level': "Cœur d'API",
  'short': "Organisation modulaire d'une API FastAPI (`APIRouter`) et déploiement multi-processus "
           'asynchrone en production (`Uvicorn`).',
  'analogy': "Les `APIRouter` sont les départements spécialisés d'une entreprise, et `Uvicorn` est "
             "l'équipe de guichetiers asynchrones parallèles (Workers ASGI) remplaçant le mode "
             'développement (`--reload`).',
  'explanation': "À mesure qu'une API grandit, la classe **`APIRouter`** permet de scinder "
                 "l'application en modules cohérents par domaine fonctionnel et par version "
                 '(`/api/v1/formations`, `/api/v2/formations`, `/api/health`), assemblés au sein '
                 "d'une fabrique applicative par `app.include_router(...)`.\n"
                 '\n'
                 "Cette organisation facilite les tests d'intégration en mémoire via "
                 '**`TestClient(app)`** sans ouverture de socket réseau, ainsi que la mise en '
                 'production sur un serveur **ASGI** multi-processus (**Uvicorn** ou **Gunicorn** '
                 "muni d'`UvicornWorker`) placé derrière un proxy inverse Nginx.",
  'code_example': '# Commande de lancement en production (4 workers ASGI) :\n'
                  '# uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4 --proxy-headers\n'
                  '# ou : gunicorn -w 4 -k uvicorn.workers.UvicornWorker "app:create_app()"'},
 {'id': 'apikey_vs_token',
  'term': 'Clé API (X-API-Key) vs Jeton Bearer (Token)',
  'category': 'Sécurité & Architecture API',
  'level': "Cœur d'API",
  'short': 'La Clé API identifie une application/machine (longue durée), tandis que le Bearer '
           'Token identifie un utilisateur connecté (courte durée).',
  'analogy': "La **Clé API** est comme le badge d'accès permanent d'une société de livraison "
             "partenaire. Le **Bearer Token** est le ticket nominatif temporaire d'un visiteur "
             'valable uniquement pour la séance.',
  'explanation': 'Une clé **`X-API-Key`** est un secret statique à longue durée de vie attribué à '
                 'un système partenaire pour des échanges serveur-à-serveur, extrait dans FastAPI '
                 "par `Header(alias='X-API-Key')` ou `APIKeyHeader` et comparé en temps constant.\n"
                 '\n'
                 "À l'opposé, un jeton **`Authorization: Bearer <token>`** est délivré "
                 "dynamiquement à l'issue d'une authentification (`/api/auth/token`), embarque "
                 "l'identité ainsi que le rôle ou les scopes de l'appelant, et expire "
                 "automatiquement au terme d'une fenêtre courte afin de limiter la surface "
                 "d'exposition.",
  'code_example': '# Cas 1 : Clé machine-à-machine\n'
                  'def verifier_cle(x_api_key: str = Header(alias="X-API-Key")):\n'
                  '\n'
                  '# Cas 2 : Jeton temporaire utilisateur\n'
                  'def verifier_jwt(authorization: str = Header(...)):'},
 {'id': 'variable',
  'term': 'Variable (Python)',
  'category': 'Bases Python',
  'level': 'Débutant Absolu',
  'short': "Emplacement nommé dans la mémoire de l'ordinateur permettant de conserver une valeur "
           'typée.',
  'analogy': 'Un dossier suspendu dans une armoire sur lequel vous collez une étiquette « '
             'Budget_2026 ». Vous pouvez consulter son contenu ou le mettre à jour à tout moment.',
  'explanation': 'En programmation, on associe un nom (à gauche) à une valeur (à droite) avec '
                 "l'opérateur d'affectation `=`. Les 4 types primitifs compatibles JSON sont "
                 '`str`, `int`/`float`, `bool` (`True`/`False`) et `None`.',
  'code_example': 'nom_stagiaire: str = "Amine"\n'
                  'age: int = 25\n'
                  '# Utiliser nom_stagiaire renvoie désormais "Amine"'},
 {'id': 'dictionnaire',
  'term': 'Dictionnaire (dict) & Modèle Pydantic (BaseModel)',
  'category': 'Bases Python',
  'level': 'Débutant Absolu',
  'short': 'Structure de données Python associant des clés uniques à des valeurs (`{clé: '
           'valeur}`), validée et typée par `BaseModel` dans FastAPI.',
  'analogy': 'Une fiche signalétique structurée où chaque champ possède un intitulé précis (« Nom '
             '», « Prénom », « Ville ») associé à sa valeur.',
  'explanation': "Délimité par des accolades `{ }`. C'est la structure fondamentale pour le "
                 "développement d'APIs en Python car un dictionnaire ou un `BaseModel` Pydantic se "
                 'convertit directement en objet JSON.',
  'code_example': 'stagiaire = {\n'
                  '    "nom": "Benali",\n'
                  '    "prenom": "Sara",\n'
                  '    "present": True\n'
                  '}\n'
                  'print(stagiaire.get("prenom"))  # Affiche: Sara'},
 {'id': 'liste',
  'term': 'Liste (list)',
  'category': 'Bases Python',
  'level': 'Débutant Absolu',
  'short': "Collection ordonnée et modifiable d'éléments indexés à partir de 0.",
  'analogy': 'Un registre numéroté ligne par ligne (en informatique, la première ligne porte '
             'toujours le numéro 0).',
  'explanation': "Délimitée par des crochets `[ ]`. Lorsqu'une API renvoie une collection "
                 "d'enregistrements (ex. la liste des formations), elle renvoie généralement une "
                 'liste contenant plusieurs dictionnaires.',
  'code_example': 'formations = ["Python", "API REST", "FastAPI"]\n'
                  'print(formations[0])  # Affiche le 1er élément : Python'},
 {'id': 'fonction',
  'term': 'Fonction (def / async def), Décorateur (@) & Depends()',
  'category': 'Bases Python',
  'level': 'Débutant Absolu',
  'short': "Bloc d'instructions réutilisable prenant des paramètres typés en entrée et retournant "
           'un résultat via `return`.',
  'analogy': 'Une unité de traitement : vous lui fournissez des matières premières (paramètres), '
             'elle applique une procédure interne, et restitue le produit fini (`return`).',
  'explanation': 'Déclarée avec `def` ou `async def`. Un **décorateur (`@app.get`)** enregistre la '
                 'fonction comme route HTTP, et **`Depends(...)`** injecte automatiquement le '
                 "résultat d'une fonction de sécurité ou de base de données.",
  'code_example': '@app.get("/bonjour")\n'
                  'def dire_bonjour():\n'
                  '    return {"message": "Service FastAPI opérationnel"}'},
 {'id': 'api',
  'term': 'API REST & Modèle de Maturité de Richardson',
  'category': 'Architecture Web',
  'level': 'Fondamental',
  'short': 'Architecture normalisée où chaque URL identifie une ressource (nom au pluriel) '
           'manipulée par les verbes et statuts HTTP.',
  'analogy': "Un guichet de liaison standardisé : l'application cliente dépose un bordereau de "
             'demande normé (Requête HTTP) et reçoit un colis de données structuré (Réponse JSON) '
             'sans dépendre du langage interne du serveur.',
  'explanation': 'Le **modèle de maturité de Richardson** évalue la conformité architecturale '
                 "d'une API Web selon quatre paliers progressifs : le niveau 0 regroupe tous les "
                 'appels sur un tunnel unique de style RPC ou SOAP, puis le niveau 1 introduit des '
                 'URI distinctes identifiant chaque ressource métier (`/api/formations/1`).\n'
                 '\n'
                 'Le niveau 2, standard industriel des APIs REST modernes sous FastAPI, exploite '
                 'pleinement la sémantique des verbes HTTP (`GET`, `POST`, `PUT`, `PATCH`, '
                 '`DELETE`) alliée aux codes de statut normalisés (`200`, `201`, `401`, `403`, '
                 '`422`, `429`), tandis que le niveau 3 (**HATEOAS**) enrichit les réponses de '
                 'liens hypermédias guidant dynamiquement le client.',
  'code_example': '# Anti-pattern RPC : POST /api/creerFormation\n'
                  '# Standard REST    : POST /api/formations  -> 201 Created'},
 {'id': 'status_code',
  'term': 'Codes de Statut HTTP & RFC 7807 (Problem Details)',
  'category': 'Architecture Web',
  'level': 'Fondamental',
  'short': "Code numérique à 3 chiffres normalisé indiquant le résultat d'une requête, complété en "
           "cas d'erreur par un JSON RFC 7807.",
  'analogy': "Un code d'état standardisé sur un terminal bancaire : transaction acceptée (200), "
             'création validée (201), erreur de saisie (422), carte non reconnue (401), droits '
             'insuffisants (403), plafond dépassé (429).',
  'explanation': "Les codes d'état HTTP structurent le dialogue protocolaire en trois grandes "
                 'familles opérationnelles. La classe **2xx** confirme le succès du traitement : '
                 "`200 OK` pour une lecture ou mise à jour, `201 Created` lors d'une création "
                 "accompagnée de l'en-tête `Location`, et `204 No Content` après une suppression "
                 'sans corps de retour.\n'
                 '\n'
                 'La classe **4xx** impute le rejet à la requête cliente : `400 Bad Request` '
                 '(syntaxe JSON malformée), `401 Unauthorized` (authentification manquante ou '
                 'invalide), `403 Forbidden` (droits insuffisants), `404 Not Found`, `405 Method '
                 'Not Allowed`, `413 Content Too Large`, `422 Unprocessable Content` (violation du '
                 'contrat Pydantic ou métier formalisée selon **RFC 7807**) et `429 Too Many '
                 'Requests`. Enfin, la classe **5xx** (`500`, `502`, `503`, `504`) signale une '
                 'défaillance côté infrastructure serveur.',
  'code_example': 'return JSONResponse(\n'
                  '    status_code=422,\n'
                  '    media_type="application/problem+json",\n'
                  '    content={\n'
                  '        "type": "https://api.isgp.dz/erreurs/validation",\n'
                  '        "title": "Erreur de validation",\n'
                  '        "status": 422,\n'
                  '        "errors": [{"champ": "duree_jours", "message": "Doit être >= 1"}]\n'
                  '    }\n'
                  ')'},
 {'id': 'sqlite',
  'term': 'SQLite, Transactions ACID & Requêtes Paramétrées (?)',
  'category': 'Données',
  'level': 'Intermédiaire',
  'short': 'Moteur de base de données relationnelle SQL transactionnel intégré à Python '
           '(`sqlite3`).',
  'analogy': 'Un registre comptable permanent écrit sur disque dur, protégé par des transactions '
             'atomiques (tout réussit avec `commit` ou tout est annulé avec `rollback`).',
  'explanation': "Sécurité fondamentale : lors d'une requête SQL, on n'insère jamais une variable "
                 'directement avec `+` ou `f"..."` (risque critique d\'**Injection SQL**). On '
                 'utilise toujours des marqueurs `?` (requêtes paramétrées).',
  'code_example': "# SÉCURISÉ (Requête paramétrée contre l'injection SQL) :\n"
                  'conn.execute("SELECT * FROM formations WHERE id = ?", (id,))'},
 {'id': 'sqlite_wal_pragmas',
  'term': 'SQLite Mode WAL (Write-Ahead Logging) & Pragmas de Production',
  'category': 'Données',
  'level': 'Avancé',
  'short': 'Mode de journalisation SQLite autorisant les lectures concurrentes pendant une '
           "écriture sans erreur 'database is locked'.",
  'analogy': "Au lieu de fermer toute la bibliothèque chaque fois qu'un bibliothécaire corrige une "
             'fiche (mode DELETE), celui-ci note ses ajouts dans un carnet annexe (-wal) pendant '
             'que tous les lecteurs continuent de consulter les rayons librement.',
  'explanation': 'Pour exploiter **SQLite** avec fiabilité sous charge concurrente dans une API '
                 "Web, trois directives `PRAGMA` doivent être appliquées à l'ouverture de chaque "
                 'connexion. Le mode **`PRAGMA journal_mode = WAL;`** (*Write-Ahead Logging*) '
                 'consigne les écritures séquentiellement dans un fichier `.db-wal` annexe afin '
                 "que les lecteurs ne bloquent plus l'écrivain et réciproquement.\n"
                 '\n'
                 "Conjointement, **`PRAGMA foreign_keys = ON;`** réactive le contrôle d'intégrité "
                 'référentielle désactivé par défaut par le moteur C SQLite, tandis que **`PRAGMA '
                 "busy_timeout = 5000;`** accorde jusqu'à cinq secondes d'attente active avant de "
                 'lever une exception `OperationalError: database is locked`.',
  'code_example': 'conn.execute("PRAGMA journal_mode = WAL;")\n'
                  'conn.execute("PRAGMA synchronous = NORMAL;")\n'
                  'conn.execute("PRAGMA foreign_keys = ON;")\n'
                  'conn.execute("PRAGMA busy_timeout = 5000;")'},
 {'id': 'sqlite_cursor_closing',
  'term': 'Curseur DB-API 2.0 (PEP 249) & Fermeture Déterministe (contextlib.closing)',
  'category': 'Données',
  'level': 'Intermédiaire',
  'short': "Itérateur d'exécution SQL dont la fermeture explicite libère immédiatement les verrous "
           'de pages de lecture et la mémoire C.',
  'analogy': "Un marque-page posé sur un registre ouvert : tant que le marque-page n'est pas "
             "retiré (`cur.close()`), l'archiviste considère que la page est encore en cours de "
             'consultation.',
  'explanation': "En Python conforme à la spécification **PEP 249 (DB-API 2.0)**, l'emploi du "
                 'gestionnaire de contexte `with conn:` sur une connexion `sqlite3` valide '
                 "automatiquement la transaction (`COMMIT`) ou l'annule (`ROLLBACK`) en cas "
                 "d'erreur, mais ne ferme ni le curseur sous-jacent ni le descripteur de "
                 'connexion.\n'
                 '\n'
                 "Encapsuler l'exécution dans `with contextlib.closing(conn.cursor()) as cur:` "
                 "couplé à un générateur FastAPI `Depends(get_db)` muni d'un bloc `finally: "
                 'conn.close()` garantit la libération déterministe des verrous et de la mémoire '
                 'sur chaque requête HTTP.',
  'code_example': 'from contextlib import closing\n'
                  '\n'
                  'with conn:  # Gère COMMIT / ROLLBACK\n'
                  '    with closing(conn.cursor()) as cur:  # Garantit cur.close()\n'
                  '        cur.execute("SELECT * FROM formations WHERE id = ?", (42,))\n'
                  '        ligne = cur.fetchone()'},
 {'id': 'sqlite_vs_apsw',
  'term': 'SQLite3 Standard (PEP 249) vs APSW (Another Python SQLite Wrapper)',
  'category': 'Données',
  'level': 'Avancé',
  'short': 'Comparaison entre le pilote standard DB-API 2.0 inclus dans Python (`sqlite3`) et le '
           "wrapper bas niveau 1-pour-1 de l'API C SQLite (`apsw`).",
  'analogy': '`sqlite3` est une boîte de vitesses automatique universelle commune à toutes les '
             "voitures Python (PEP 249), tandis qu'`APSW` est un volant de Formule 1 branché en "
             'prise directe sur chaque capteur mécanique du moteur C de SQLite.',
  'explanation': 'Le module **`sqlite3`** intégré à la bibliothèque standard Python offre '
                 "l'avantage décisif d'une disponibilité immédiate sans dépendance compilée "
                 "externe, d'une conformité **DB-API 2.0** et d'une intégration native avec "
                 "l'écosystème SQLAlchemy.\n"
                 '\n'
                 'Pour des besoins systèmes spécialisés, la bibliothèque **`apsw`** (*Another '
                 "Python SQLite Wrapper*) expose fidèlement l'intégralité de l'API C officielle de "
                 'SQLite : absence totale de `BEGIN` implicite, lecture/écriture incrémentale de '
                 'BLOBs en flux (`zeroblob` / `blobopen`), tables virtuelles Python, sauvegarde '
                 'transactionnelle à chaud et codes de diagnostic étendus tels que '
                 '`SQLITE_BUSY_SNAPSHOT`.',
  'code_example': '# sqlite3 standard (Python 3.12+ PEP 249 strict) :\n'
                  'conn = sqlite3.connect("ecole.db", autocommit=False)\n'
                  '\n'
                  "# APSW (contrôle explicite total sur l'API C SQLite) :\n"
                  '# import apsw\n'
                  '# conn = apsw.Connection("ecole.db")'},
 {'id': 'sse_server_sent_events',
  'term': 'SSE — Server-Sent Events (text/event-stream & Last-Event-ID)',
  'category': 'Temps Réel & Streaming',
  'level': 'Intermédiaire',
  'short': "Standard HTML5/HTTP permettant au serveur de pousser un flux continu d'événements "
           'texte vers le client sur une simple requête GET.',
  'analogy': "Un panneau d'affichage d'aéroport connecté : le voyageur ouvre une seule fois le "
             "canal d'écoute, et la tour de contrôle pousse chaque changement de porte en direct "
             'sans que le voyageur ait à redemander toutes les 2 secondes.',
  'explanation': 'Le protocole **Server-Sent Events** (**SSE**, `text/event-stream`) structure un '
                 "canal unidirectionnel du serveur vers le client au-dessus d'une simple connexion "
                 'HTTP : chaque événement est constitué de champs textuels `id:`, `event:` et '
                 '`data:` clos par une double fin de ligne obligatoire `\\n\\n`.\n'
                 '\n'
                 "L'interface native du navigateur `EventSource` gère d'elle-même la reconnexion "
                 "automatique après une coupure réseau en transmettant l'en-tête `Last-Event-ID`, "
                 'ce qui fait de SSE le choix privilégié pour les barres de progression, les '
                 'tableaux de bord en direct et la restitution progressive de jetons LLM.',
  'code_example': 'from fastapi.responses import StreamingResponse\n'
                  '\n'
                  '@app.get("/api/sse")\n'
                  'async def flux_sse():\n'
                  '    async def generateur():\n'
                  '        yield "id: 1\\nevent: progression\\ndata: {\\"pct\\": 50}\\n\\n"\n'
                  '    return StreamingResponse(generateur(), media_type="text/event-stream")'},
 {'id': 'websocket_rfc6455',
  'term': 'WebSocket (RFC 6455 & HTTP 101 Switching Protocols)',
  'category': 'Temps Réel & Streaming',
  'level': 'Avancé',
  'short': 'Protocole de communication bidirectionnelle (Full-Duplex) persistante sur un unique '
           'socket TCP après une mise à niveau HTTP 101.',
  'analogy': 'Un appel téléphonique ouvert en continu : contrairement au courrier postal (HTTP '
             'requête/réponse) ou à la radio unidirectionnelle (SSE), les deux interlocuteurs '
             'peuvent parler et écouter simultanément à la milliseconde près.',
  'explanation': "L'ouverture d'un canal **WebSocket** (**RFC 6455**) débute par une requête HTTP "
                 'comportant les en-têtes `Upgrade: websocket`, `Connection: Upgrade` et '
                 '`Sec-WebSocket-Key`, à laquelle le serveur ASGI répond par `HTTP/1.1 101 '
                 'Switching Protocols` afin de basculer le socket TCP en mode trames binaires ou '
                 'textuelles bidirectionnelles.\n'
                 '\n'
                 "On privilégie WebSocket par rapport à SSE lorsque l'application exige des "
                 "échanges symétriques à très faible latence dans les deux sens, tels qu'une "
                 'messagerie instantanée, un éditeur collaboratif multi-utilisateurs ou la '
                 'collecte de télémétrie industrielle haute fréquence.',
  'code_example': '# En-têtes de mise à niveau (Upgrade Handshake RFC 6455) :\n'
                  '# Client  -> GET /ws HTTP/1.1 | Upgrade: websocket | Connection: Upgrade\n'
                  '# Serveur -> HTTP/1.1 101 Switching Protocols | Sec-WebSocket-Accept: ...'},
 {'id': 'multipart_magic_bytes',
  'term': 'Upload Multipart (RFC 7578), Magic Bytes & Défense 413 / 415',
  'category': 'Temps Réel & Streaming',
  'level': 'Intermédiaire',
  'short': 'Transport binaire natif de fichiers par frontières HTTP, sécurisé par plafond de '
           "taille (413), inspection des octets d'en-tête (Magic Bytes) et renommage UUID.",
  'analogy': "Un contrôle douanier aux rayons X : le douanier ne croit jamais l'étiquette collée "
             "sur la valise (`rapport.pdf`), il pèse d'abord le bagage (`413`), ouvre les premiers "
             'centimètres pour vérifier la nature réelle du contenu (`%PDF-` -> sinon `415`), puis '
             'lui attribue un numéro de scellé interne (`UUID4`).',
  'explanation': "Transporter un document binaire encodé en Base64 au cœur d'un objet JSON gonfle "
                 "inutilement le volume réseau d'environ 33 % et contraint le serveur à charger "
                 "l'intégralité de la chaîne en mémoire vive avant décodage ; l'encodage "
                 '**`multipart/form-data`** (**RFC 7578**) résout ce goulot par lecture en flux.\n'
                 '\n'
                 "La sécurisation d'un téléversement exige trois défenses cumulatives : appliquer "
                 "un plafond strict d'octets (`413 Content Too Large`), contrôler la signature "
                 'binaire réelle (*Magic Bytes*, telle que `25 50 44 46 2D` pour `%PDF-` ou `89 50 '
                 "4E 47` pour PNG) plutôt que l'extension déclarée, et attribuer un identifiant "
                 "interne `uuid4().hex` afin d'neutraliser toute traversée d'arborescence (*Path "
                 'Traversal*).',
  'code_example': 'from fastapi import UploadFile, HTTPException\n'
                  '\n'
                  'entete = await document.read(5)\n'
                  'await document.seek(0)\n'
                  'if not entete.startswith(b"%PDF-"):\n'
                  '    raise HTTPException(415, "Signature binaire PDF invalide")'},
 {'id': 'async_job_202_accepted',
  'term': "Tâches d'Arrière-Plan & Patron HTTP 202 Accepted + Location",
  'category': 'Architecture Web',
  'level': 'Intermédiaire',
  'short': "Découplage d'un traitement lourd (PDF, export CSV, e-mail, IA) en répondant "
           "immédiatement 202 Accepted avec une URL de suivi d'état.",
  'analogy': "Le bipper vibrant d'un restaurant : au lieu de bloquer toute la file d'attente "
             'devant la caisse pendant les 15 minutes de cuisson de votre plat, le caissier '
             'encaisse en 10 secondes et vous remet un jeton (`job_id`) qui indique quand la '
             'commande est prête.',
  'explanation': "Exécuter un traitement lourd (génération d'archive, rapport analytique massif) "
                 'de manière synchrone pendant la requête HTTP monopolise les workers ASGI et '
                 'provoque des erreurs `504 Gateway Timeout` au niveau du proxy inverse Nginx.\n'
                 '\n'
                 'Le patron asynchrone normalisé consiste à enregistrer immédiatement la tâche à '
                 "l'état `EN_ATTENTE`, à répondre **`202 Accepted`** muni d'un en-tête `Location: "
                 "/api/jobs/job-8a2f`, puis à permettre au client d'interroger périodiquement "
                 "cette ressource d'état jusqu'à sa complétion.",
  'code_example': '# Réponse immédiate (< 10 ms) :\n'
                  '# HTTP/1.1 202 Accepted\n'
                  '# Location: /api/jobs/job-9f41c2\n'
                  '# {"job_id": "job-9f41c2", "statut": "EN_ATTENTE", "progression_pct": 0}'},
 {'id': 'etag_304_conditional_cache',
  'term': 'Cache HTTP Conditionnel : ETag, If-None-Match & 304 Not Modified',
  'category': 'Performance & Cache',
  'level': 'Intermédiaire',
  'short': "Empreinte de version d'une ressource permettant au serveur d'éviter de renvoyer le "
           'corps JSON si la copie du client est toujours à jour.',
  'analogy': "Demander au libraire : « J'ai déjà l'édition hash #a4f9 du catalogue, y en a-t-il "
             'une nouvelle ? » — « Non, gardez la vôtre (`304 Not Modified`) ! », évitant de '
             'réimprimer et réexpédier 500 pages pour rien.',
  'explanation': "La maîtrise du cache HTTP distingue d'abord les ressources strictement privées "
                 "(`/profil`, jetons), sur lesquelles l'en-tête **`Cache-Control: no-store`** "
                 'interdit toute mise en mémoire intermédiaire.\n'
                 '\n'
                 'Sur les catalogues et référentiels consultés fréquemment en `GET`, le serveur '
                 'joint une empreinte **`ETag`** que le client renvoie lors des appels ultérieurs '
                 'dans `If-None-Match` : si la ressource demeure identique, FastAPI répond **`304 '
                 'Not Modified`** sans corps JSON, épargnant à la fois la bande passante mobile et '
                 'le coût CPU de sérialisation.',
  'code_example': 'if request_if_none_match == current_etag:\n'
                  '    # 304 Not Modified : en-têtes seuls, ZÉRO corps JSON !\n'
                  '    return "", 304, {"ETag": current_etag}'},
 {'id': 'optimistic_locking_412',
  'term': 'Verrouillage Optimiste HTTP : If-Match & 412 Precondition Failed',
  'category': 'Performance & Cache',
  'level': 'Avancé',
  'short': "Protection contre l'écrasement silencieux d'écritures concurrentes (Lost Update) en "
           "exigeant l'ETag de la version lue lors d'un PUT/PATCH.",
  'analogy': 'Un système anti-collision sur un document partagé : si votre collègue a enregistré '
             'la version v2 pendant que vous modifiiez encore la version v1, le serveur refuse '
             "votre sauvegarde (`412`) et vous montre la v2 plutôt que d'effacer le travail de "
             'votre collègue en silence.',
  'explanation': 'Lorsque deux opérateurs modifient simultanément une même fiche sans mécanisme de '
                 'coordination, la seconde sauvegarde écrase silencieusement la première selon '
                 "l'anomalie classique du *Lost Update*.\n"
                 '\n'
                 'Le **verrouillage optimiste HTTP** élimine ce conflit sans bloquer la base : le '
                 'client accompagne son `PUT` de l\'en-tête `If-Match: "v1"`, et le serveur '
                 'exécute une mise à jour atomique conditionnelle (`UPDATE ... WHERE id = ? AND '
                 "version = ?`). Si aucune ligne n'est affectée (`rowcount == 0`), l'API rejette "
                 "l'écriture avec le code **`412 Precondition Failed`**.",
  'code_example': '# Client B tente de sauvegarder sur une version obsolète :\n'
                  '# PUT /api/catalogue/1\n'
                  '# If-Match: "v1-8b2c4d10"\n'
                  "# -> HTTP/1.1 412 Precondition Failed (conflit d'édition détecté !)"},
 {'id': 'x_request_id_correlation',
  'term': 'Traçabilité Distribuée : X-Request-ID & X-Process-Time-Ms',
  'category': 'Architecture Web',
  'level': 'Intermédiaire',
  'short': 'Middleware transversal attachant un identifiant de corrélation unique et la durée '
           "d'exécution exacte à chaque requête HTTP.",
  'analogy': 'Le numéro de suivi Colissimo imprimé dès le dépôt du colis et scanné à chaque '
             "entrepôt : en cas d'incident, un seul code permet de reconstituer tout le parcours à "
             'la milliseconde près.',
  'explanation': 'Dans un système distribué, un middleware ASGI de traçabilité inspecte chaque '
                 "requête entrante : s'il reçoit déjà un identifiant **`X-Request-ID`** conforme "
                 "émis par la passerelle d'entrée, il le conserve, faute de quoi il forge un "
                 'identifiant unique `uuid4`.\n'
                 '\n'
                 'Associé à une mesure monotone `time.perf_counter()`, ce même middleware restitue '
                 'dans la réponse les en-têtes `X-Request-ID` et **`X-Process-Time-Ms`** tout en '
                 'enrichissant chaque ligne de journal structuré, rendant immédiate la corrélation '
                 "de bout en bout d'un incident.",
  'code_example': 'debut = time.perf_counter()\n'
                  'req_id = client_req_id or f"req-{uuid.uuid4().hex[:12]}"\n'
                  '# ... exécution de la route ...\n'
                  'duree_ms = (time.perf_counter() - debut) * 1000.0\n'
                  '# En-têtes : X-Request-ID: req-... | X-Process-Time-Ms: 1.84'},
 {'id': 'nginx_upload_x_accel_offload',
  'term': 'Délégation Fichiers Nginx : client_max_body_size, $request_body_file & X-Accel-Redirect',
  'category': 'Déploiement & Production',
  'level': 'Avancé',
  'short': "Architecture à deux étages déléguant à Nginx le filtrage 413, l'écriture disque des "
           "uploads lents et l'envoi noyau (sendfile) des fichiers privés.",
  'analogy': "Le quai logistique d'un ministère : le service de sécurité du quai (Nginx) pèse les "
             "camions à l'entrée (413), décharge les palettes lourdes en entrepôt et ne remet au "
             'magistrat (Python) que le bordereau scellé (X-Uploaded-File-Path) pour contrôle de '
             'conformité.',
  'explanation': 'Par défaut, Nginx limite la taille des requêtes entrantes via '
                 '`client_max_body_size` à **1 Mo** ; une configuration durcie maintient ce seuil '
                 "bas sur les routes JSON générales et n'accorde une enveloppe élargie (`25M`) "
                 "qu'aux seuls chemins dédiés au téléversement.\n"
                 '\n'
                 'Pour soulager complètement les workers Python des transferts volumineux, Nginx '
                 'peut écrire le flux entrant sur disque (`client_body_in_file_only clean;`) et ne '
                 'transmettre à FastAPI que le chemin local `X-Uploaded-File-Path`. En sens '
                 "inverse, après contrôle des droits en Python, l'émission de l'en-tête interne "
                 '**`X-Accel-Redirect`** délègue à Nginx (`internal; sendfile on;`) la diffusion '
                 'noyau du fichier.',
  'code_example': 'location = /api/v1/upload-offload {\n'
                  '    client_max_body_size 25M;\n'
                  '    client_body_in_file_only clean;\n'
                  '    proxy_pass_request_body off;\n'
                  '    proxy_set_header Content-Length "";\n'
                  '    proxy_set_header X-Uploaded-File-Path $request_body_file;\n'
                  '    proxy_pass http://isgp_cluster;\n'
                  '}'},
 {'id': 'api_fundamentals_decoupling',
  'term': 'API (Application Programming Interface) — Frontière de Découplage',
  'category': 'Architecture & Contrats API',
  'level': 'Fondamental',
  'short': "Interface formelle exposant des capacités (Quoi) tout en encapsulant l'implémentation "
           "interne (Comment), qu'elle soit système, bibliothèque ou réseau.",
  'analogy': "Le tableau de bord normalisé d'un véhicule (volant, pédales, compteur) : vous "
             'pilotez de la même manière un moteur thermique, hybride ou électrique sans ouvrir le '
             'capot moteur.',
  'explanation': 'Une **API** (*Application Programming Interface*) matérialise une frontière '
                 "contractuelle stable qui dissocie l'usage d'une capacité logicielle de son "
                 'implémentation interne. Cette abstraction se décline à quatre échelles '
                 "complémentaires de l'informatique moderne : les appels système du noyau POSIX "
                 '(`open()`, `epoll()`) et les interfaces matérielles ou IPC par sockets locaux.\n'
                 '\n'
                 'Au niveau applicatif, on distingue les contrats de bibliothèques en mémoire tels '
                 "que **PEP 249 (`DB-API 2.0`)**, qui unifie l'accès à `sqlite3`, `psycopg` et "
                 '`pymysql`, des **APIs Web et réseau** distribuées couvrant **REST** sur HTTP, '
                 '**GraphQL**, **gRPC** (Protocol Buffers sur HTTP/2), les **Webhooks** '
                 'événementiels et les **WebSockets**.',
  'code_example': "# Même contrat d'appel HTTP, peu importe que le serveur soit en Python, Go ou "
                  'Rust :\n'
                  '# GET /api/v2/formations/42  ->  200 OK (application/json)'},
 {'id': 'api_contract_vs_documentation',
  'term': "Contrat d'API (Machine) vs Documentation d'API (Humain)",
  'category': 'Architecture & Contrats API',
  'level': 'Fondamental',
  'short': 'Le Contrat est la spécification formelle exécutable (OpenAPI 3.1, Protobuf, JSON '
           'Schema) ; la Documentation est le guide pédagogique humain généré à partir de ce '
           'contrat.',
  'analogy': "Le **Contrat** est le plan d'architecte coté au millimètre vérifié par les machines "
             "de chantier ; la **Documentation** est le livret d'accueil illustré remis aux "
             'nouveaux occupants.',
  'explanation': "Le **contrat d'API** constitue un engagement formel, lisible par la machine et "
                 'vérifiable en intégration continue : il fige les types de données, les bornes de '
                 "validation, les codes de statut HTTP, les schémas d'erreur **RFC 7807** et les "
                 "exigences de sécurité, de sorte que tout retrait ou renommage d'un champ "
                 'existant représente une rupture de contrat.\n'
                 '\n'
                 "La **documentation d'API** s'adresse quant à elle aux ingénieurs humains à "
                 'travers des guides de démarrage, des scénarios métiers et des consoles '
                 'interactives telles que Swagger UI ou ReDoc. Dériver automatiquement cette '
                 'documentation du contrat exécutable supprime tout risque de dérive documentaire '
                 '(*Documentation Drift*).',
  'code_example': "# Extrait d'un Contrat JSON Schema / OpenAPI 3.1 vérifiable par machine :\n"
                  '# properties:\n'
                  '#   duree_jours: { type: integer, minimum: 1, maximum: 30 }'},
 {'id': 'idempotence_and_keys',
  'term': "Idempotence HTTP & Clé d'Idempotence (Idempotency-Key)",
  'category': 'Architecture & Contrats API',
  'level': "Cœur d'API",
  'short': "Propriété mathématique garantissant qu'exécuter 1 fois ou N fois la même requête "
           'produit exactement le même état final sur le serveur.',
  'analogy': "Appuyer 5 fois sur le bouton d'appel d'un ascenseur déjà appelé n'appelle pas 5 "
             "cabines différentes : l'état (« étage demandé ») reste identique.",
  'explanation': 'Selon la norme **RFC 9110**, les méthodes HTTP `GET`, `HEAD`, `OPTIONS`, `PUT` '
                 '(remplacement complet) et `DELETE` sont nativement **idempotentes**, tandis que '
                 "`POST` ne l'est pas : rejouer automatiquement un `POST /paiements` après une "
                 "perte momentanée de connexion mobile expose au risque critique d'un double "
                 'débit.\n'
                 '\n'
                 'La parade industrielle consiste pour le client à générer un UUID unique transmis '
                 "dans l'en-tête **`Idempotency-Key`**. Le serveur associe cette clé au résultat "
                 'validé durant une fenêtre de rétention (typiquement 24 heures) et restitue à '
                 "l'identique la réponse initiale en cas de rejeu sans ré-exécuter l'opération "
                 'métier.',
  'code_example': '# POST sécurisé contre les doubles débits réseau :\n'
                  '# En-tête : Idempotency-Key: 9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d'},
 {'id': 'contract_first_vs_code_first',
  'term': 'Approche Contract-First vs Code-First & Loi de Postel',
  'category': 'Architecture & Contrats API',
  'level': 'Avancé',
  'short': 'Deux méthodologies de conception : rédiger le fichier OpenAPI avant de coder '
           '(Contract-First) ou générer le schéma depuis les annotations du code Python '
           '(Code-First).',
  'analogy': 'Soit on fait signer le cahier des charges technique aux équipes Mobile et Backend '
             "avant d'usiner les pièces (**Contract-First**), soit l'atelier fabrique le prototype "
             'et un scanner 3D en déduit le plan (**Code-First**).',
  'explanation': 'La démarche **Contract-First** consiste à concevoir et valider le fichier '
                 'normatif `openapi.yaml` en amont (via des linters comme Spectral), ce qui permet '
                 "aux équipes frontales (à l'aide de serveurs de simulation) et aux équipes "
                 'backend de développer simultanément contre la même spécification.\n'
                 '\n'
                 "L'approche **Code-First**, emblématique de FastAPI et Pydantic v2, engendre "
                 '`/openapi.json` directement depuis les annotations de types Python et garantit '
                 'ainsi une fidélité permanente entre le code exécuté et le schéma publié. Dans '
                 "les deux cas, le cycle de vie s'appuie sur des ajouts *Non-Breaking* et sur les "
                 "en-têtes **RFC 8594** (`Deprecation` et `Sunset`) lors du retrait planifié d'une "
                 'version.',
  'code_example': "# En-têtes standards RFC 8594 de cycle de vie d'API :\n"
                  '# Deprecation: true\n'
                  '# Sunset: Wed, 30 Dec 2026 23:59:59 GMT'},
 {'id': 'north_south_vs_east_west',
  'term': 'Trafic Nord-Sud vs Trafic Est-Ouest',
  'category': 'Topologie Réseau & Zero-Trust',
  'level': 'Fondamental',
  'short': 'Le flux Nord-Sud traverse la frontière externe (Client Internet <-> API Gateway), '
           'tandis que le flux Est-Ouest circule latéralement entre microservices internes.',
  'analogy': "Le **Nord-Sud** est le poste de contrôle frontalier d'un aéroport international ; "
             "l'**Est-Ouest** représente les navettes techniques circulant sur le tarmac entre les "
             'hangars sécurisés.',
  'explanation': "L'architecture réseau distingue deux axes de circulation aux contraintes "
                 'opposées. Le trafic **Nord-Sud** désigne les flux entrant depuis des réseaux '
                 'externes non maîtrisés (Internet, terminaux mobiles) vers la bordure du système '
                 "d'information, où opèrent le DNS, le CDN, le pare-feu applicatif WAF, le "
                 "chiffrement TLS public, le Rate-Limiting et l'**API Gateway**.\n"
                 '\n'
                 'Le trafic **Est-Ouest** regroupe les communications latérales entre '
                 "microservices internes au sein du cluster : parce qu'un seul appel Nord-Sud peut "
                 "déclencher une dizaine d'appels Est-Ouest en cascade (*fan-out*), cet axe impose "
                 "des budgets de latence serrés, des délais d'expiration courts et une "
                 'authentification mutuelle **mTLS** dans un modèle **Zero-Trust**.',
  'code_example': '# Nord-Sud : Navigateur --(HTTPS TLS 1.3)--> Nginx / API Gateway\n'
                  '# Est-Ouest : Service-Inscriptions --(mTLS + Token Exchange)--> '
                  'Service-Paiement'},
 {'id': 'api_gateway_phantom_token',
  'term': 'API Gateway & Patron du Jeton Fantôme (Phantom Token)',
  'category': 'Topologie Réseau & Zero-Trust',
  'level': 'Avancé',
  'short': 'Architecture où le client externe détient un jeton opaque (sans données lisibles), '
           "converti par l'API Gateway en JWT signé interne pour les microservices.",
  'analogy': "À l'entrée d'un centre de recherche, vous recevez un badge plastique neutre à numéro "
             'aléatoire (Opaque Token) ; les portiques internes traduisent ce numéro en fiche '
             "d'habilitation complète pour les laboratoires.",
  'explanation': 'Dans le patron architectural du **Jeton Fantôme** (*Phantom Token*), le client '
                 "externe ne détient qu'un jeton opaque aléatoire dépourvu de toute information "
                 'lisible : la topologie interne, les rôles métiers et les identifiants sensibles '
                 'demeurent ainsi totalement invisibles depuis Internet.\n'
                 '\n'
                 "À la traversée de l'**API Gateway** (frontière Nord-Sud), ce jeton opaque est "
                 'révocable instantanément puis échangé à la volée contre un jeton **JWT** interne '
                 'signé cryptographiquement, permettant aux microservices Est-Ouest de vérifier '
                 'les droits de façon autonome via les clés publiques **JWKS**.',
  'code_example': '# Internet (Nord-Sud) : Authorization: Bearer opq_8f92a1c4... (Opaque)\n'
                  '# Interne  (Est-Ouest): Authorization: Bearer eyJhbGciOiJSUzI1Ni... (JWT '
                  'signé)'},
 {'id': 'zero_trust_mtls_spiffe',
  'term': 'Zero-Trust, mTLS (TLS Mutuel) & Identité SPIFFE',
  'category': 'Topologie Réseau & Zero-Trust',
  'level': 'Avancé',
  'short': "Modèle de sécurité refusant toute confiance implicite liée à l'adresse IP interne : "
           'chaque microservice prouve cryptographiquement son identité machine.',
  'analogy': "Même à l'intérieur du coffre-fort d'une banque (réseau local privé), deux employés "
             'qui se remettent des fonds doivent mutuellement présenter leur carte professionnelle '
             'biométrique.',
  'explanation': "La doctrine **Zero-Trust** abandonne l'hypothèse historique du périmètre « "
                 'château-fort » selon laquelle le réseau interne serait intrinsèquement sûr : si '
                 "un attaquant prend pied dans un conteneur frontal, l'absence d'authentification "
                 'interne lui ouvrirait un mouvement latéral libre vers toutes les bases.\n'
                 '\n'
                 'Le chiffrement mutuel **mTLS** verrouille chaque liaison Est-Ouest en exigeant '
                 'lors de la poignée de main TLS une preuve cryptographique X.509 des deux côtés — '
                 'serveur comme microservice appelant — le plus souvent normalisée sous forme '
                 "d'identité **SPIFFE** (`spiffe://isgp.mesh/ns/prod/sa/service-inscriptions`).",
  'code_example': '# Identité machine vérifiée par certificat X.509 client (SAN URI SPIFFE) :\n'
                  '# spiffe://isgp.mesh/ns/prod/sa/service-inscriptions'},
 {'id': 'oauth2_roles_and_scopes',
  'term': "OAuth 2.0 (RFC 6749) — Délégation d'Autorisation & 4 Rôles",
  'category': 'OAuth 2.0, OIDC & Délégation',
  'level': 'Fondamental',
  'short': "Cadre standard permettant à un utilisateur d'autoriser une application tierce à agir "
           'en son nom avec des droits limités (scopes), sans jamais lui confier son mot de passe.',
  'analogy': "La **Clé de Voiturier (*Valet Key*)** d'une voiture : elle permet au voiturier de "
             "rouler sur 2 km pour garer le véhicule, mais bloque l'ouverture du coffre, de la "
             'boîte à gants et limite la vitesse.',
  'explanation': "Le cadre d'autorisation **OAuth 2.0** (**RFC 6749**) articule quatre acteurs aux "
                 "responsabilités strictement découplées : le **Resource Owner** (l'utilisateur "
                 "humain titulaire des données) et le **Client** (l'application Web, mobile ou "
                 'serveur qui sollicite un accès délégué en son nom).\n'
                 '\n'
                 "L'**Authorization Server** (fournisseur d'identité ou IdP) authentifie "
                 "l'utilisateur, recueille son consentement éventuel et délivre les jetons signés, "
                 'tandis que le **Resource Server** (votre API Python FastAPI) vérifie la '
                 'signature cryptographique ainsi que les attributs `exp`, `aud` et `scope` avant '
                 "d'autoriser l'opération.",
  'code_example': '# En-tête présenté au Resource Server :\n'
                  '# Authorization: Bearer <Access_Token_JWT>\n'
                  "# Claims vérifiés : aud == 'api-inscriptions' et 'inscriptions:write' in scope"},
 {'id': 'oauth2_pkce_rfc7636',
  'term': 'Authorization Code + PKCE (RFC 7636) — Standard OAuth 2.1',
  'category': 'OAuth 2.0, OIDC & Délégation',
  'level': "Cœur d'API",
  'short': "Flux d'autorisation sécurisé par preuve cryptographique dynamique (`code_verifier` / "
           '`code_challenge`), obligatoire pour les SPA, applications mobiles et clients modernes.',
  'analogy': "Pour retirer un colis recommandé, vous déposez d'abord l'empreinte scellée d'un code "
             'secret lors de la commande (`code_challenge`), puis vous révélez le secret original '
             '(`code_verifier`) au guichet final : un voleur qui intercepte le bon de retrait ne '
             'peut rien en faire.',
  'explanation': "L'extension **PKCE** (*Proof Key for Code Exchange*, **RFC 7636**) protège le "
                 "flux d'autorisation contre l'interception du code temporaire : avant la "
                 'redirection vers `/authorize`, le client engendre un secret éphémère '
                 "`code_verifier` et n'en transmet que le condensat `code_challenge = "
                 'BASE64URL(SHA256(code_verifier))`.\n'
                 '\n'
                 'Après réception du `code` à usage unique, le client présente conjointement '
                 '`code` et `code_verifier` sur le point de terminaison `/token` ; le serveur '
                 "d'autorisation recalcule l'empreinte SHA-256 avant de délivrer l'`access_token`, "
                 "remplaçant ainsi définitivement l'ancien flux *Implicit* déprécié.",
  'code_example': 'import hashlib, base64, secrets\n'
                  'verifier = secrets.token_urlsafe(48)\n'
                  'challenge = '
                  "base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b'=').decode()"},
 {'id': 'oidc_id_token_vs_access_token',
  'term': 'OpenID Connect (OIDC) : ID Token vs Access Token',
  'category': 'OAuth 2.0, OIDC & Délégation',
  'level': "Cœur d'API",
  'short': "Couche d'identité bâtie au-dessus d'OAuth 2.0 : l'ID Token prouve QUI est "
           "l'utilisateur au Client, tandis que l'Access Token autorise l'appel aux APIs.",
  'analogy': "L'**ID Token** est votre carte nationale d'identité (lue par l'accueil pour afficher "
             "« Bonjour Amine ») ; l'**Access Token** est votre forfait magnétique d'accès aux "
             'pistes de ski (lu par les tourniquets des APIs).',
  'explanation': "La couche d'identité **OpenID Connect** (**OIDC**) sépare rigoureusement la "
                 "preuve d'authentification de l'autorisation d'accès : un **`ID Token`** est "
                 "destiné au seul client frontal pour connaître l'identité connectée et ne doit "
                 'jamais être transmis dans `Authorization: Bearer` vers une API métier, pas plus '
                 "qu'une interface frontale ne doit tenter d'interpréter le contenu interne d'un "
                 '**`Access Token`**.\n'
                 '\n'
                 "Lorsqu'un traitement automatisé s'exécute sans intervention humaine (tâche "
                 "planifiée ou échange machine-à-machine), l'architecture recourt directement au "
                 'flux **`Client Credentials`** (`grant_type=client_credentials`).',
  'code_example': "# ID Token     -> Audience (aud) = client_id de l'application Frontend\n"
                  "# Access Token -> Audience (aud) = identifiant URI de l'API (Resource Server)"},
 {'id': 'oauth2_token_exchange_rfc8693',
  'term': 'OAuth 2.0 Token Exchange (RFC 8693) & Anti-Confused Deputy',
  'category': 'OAuth 2.0, OIDC & Délégation',
  'level': 'Avancé',
  'short': "Protocole d'échange de jeton Est-Ouest permettant à un microservice A d'obtenir un "
           "nouveau jeton restreint pour appeler le microservice B au nom de l'utilisateur (`act` "
           '+ `aud`).',
  'analogy': 'Un avocat mandaté par un client ne donne pas la procuration générale originale au '
             "greffe d'un tribunal spécialisé : il présente son propre titre d'avocat (`act`) "
             "accompagné d'un mandat restreint à cette seule audience (`aud` + `scope`).",
  'explanation': "Transférer tel quel le jeton initial d'un appelant externe d'un microservice A "
                 'vers un microservice B (*Blind Token Passthrough*) crée la vulnérabilité du '
                 '**Confused Deputy** : tout service intermédiaire compromis pourrait réutiliser '
                 "ce jeton à large portée auprès d'autres ressources internes.\n"
                 '\n'
                 'Le standard **OAuth 2.0 Token Exchange** (**RFC 8693**) impose au service A '
                 "d'échanger le jeton reçu auprès de l'IdP contre un nouveau jeton à durée de vie "
                 "très brève (`120s`), restreint à l'audience exacte `aud: service-paiement`, doté "
                 "d'un `scope` minimal et traçant la délégation dans la réclamation d'audit "
                 '**`act`** (*Actor*).',
  'code_example': "# Claims d'un jeton délégué Est-Ouest RFC 8693 :\n"
                  '# {\n'
                  "#   'sub': 'user:amine.benali',\n"
                  "#   'aud': 'https://internal.isgp.mesh/service-paiement',\n"
                  "#   'act': {'sub': 'spiffe://isgp.mesh/ns/prod/sa/service-inscriptions'}\n"
                  '# }'},
 {'id': 'openapi_vs_swagger_suite',
  'term': 'OpenAPI (OAS 3.1) vs Swagger (UI, Editor, Codegen)',
  'category': 'OpenAPI & Écosystème Swagger',
  'level': 'Fondamental',
  'short': 'OpenAPI est la spécification standard ouverte (Linux Foundation) décrivant un contrat '
           "d'API REST ; Swagger désigne la suite d'outils logiciels qui exploitent ce contrat.",
  'analogy': "La même distinction qu'entre **HTML5** (la norme ouverte du W3C) et **Firefox / "
             'Chrome** (les logiciels qui lisent et affichent une page HTML5) — ou entre **SQL** '
             'et **DBeaver**.',
  'explanation': "Créée en 2010 par Tony Tam sous l'appellation *Swagger Specification*, la "
                 'grammaire de description des APIs REST a été confiée en novembre 2015 à la '
                 "**Linux Foundation** (OpenAPI Initiative) sous le nom officiel d'**OpenAPI "
                 'Specification** (`OAS 3.0`, puis **`OAS 3.1`** alignée à 100 % sur JSON Schema '
                 'Draft 2020-12).\n'
                 '\n'
                 "Le terme **Swagger** désigne désormais la gamme d'outils logiciels qui "
                 'exploitent ce contrat ouvert — notamment **Swagger Editor**, **Swagger UI** '
                 '(*Try it out*) et **Swagger Codegen** — aux côtés des solutions modernes de '
                 "l'écosystème telles que **OpenAPI Generator**, **ReDoc**, **Scalar** et le "
                 'moteur de tests par fuzzing **Schemathesis**.',
  'code_example': '# FastAPI : génération native OpenAPI 3.1 (/openapi.json) + Swagger UI (/docs)\n'
                  'from fastapi import FastAPI\n'
                  "app = FastAPI(title='API ISGP', version='2.1.0')"}]
