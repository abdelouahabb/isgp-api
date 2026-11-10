"""
Référentiel des Concepts Fondamentaux & Addendum Technique (OpenSSL, Cryptographie, Linux, Réseau, SQLite/APSW & Temps Réel)
pour le Bootcamp ISGP : Développement d'APIs et Services Web.
Chaque concept ou outil est expliqué sans aucun prérequis, avec une analogie fonctionnelle
et des commandes / exemples prêts pour la production.
"""

GLOSSARY_TERMS = [{'id': 'openssl_rand_secrets',
  'term': 'Génération de Secrets Cryptographiques (openssl rand & secrets)',
  'category': 'Cryptographie & OpenSSL',
  'level': 'Addendum Sécurité',
  'short': 'Commandes permettant de générer des clés secrètes (SECRET_KEY, API Keys) à haute entropie '
           'impossibles à deviner.',
  'analogy': 'Un générateur mécanique de combinaisons de coffre-fort à 256 bits : contrairement à un mot de '
             'passe inventé par un humain, aucun dictionnaire ni supercalculateur ne peut deviner une clé '
             'aléatoire cryptographique de 32 octets.',
  'explanation': '- **Pourquoi ne jamais inventer sa `SECRET_KEY` au clavier ?** Un secret tapé par un '
                 "humain manque d'entropie et peut être cassé par dictionnaire.\n"
                 '- **Avec `openssl rand`** : Utilise le générateur aléatoire matériel/noyau '
                 '(`/dev/urandom`) pour produire des octets imprévisibles en hexadécimal (`-hex 32` = 64 '
                 'caractères) ou en Base64 (`-base64 32`).\n'
                 "- **Avec Python (`module secrets`)** : N'utilisez jamais `random` pour la sécurité (qui "
                 'est prédictible), utilisez toujours le module standard `secrets`.',
  'code_example': '# 1. Générer une clé secrète de 256 bits (32 octets) en hexadécimal avec OpenSSL :\n'
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
  'short': "Calcul d'une empreinte numérique unique à sens unique (irréversible) pour vérifier l'intégrité "
           "d'une donnée ou d'un fichier.",
  'analogy': "L'empreinte digitale d'un document : en un coup d'œil sur les 64 caractères hexadécimaux, on "
             "vérifie qu'aucune virgule n'a changé, mais il est mathématiquement impossible de reconstruire "
             'le document à partir de son empreinte.',
  'explanation': '- **Piège classique sous Linux (`echo` vs `printf`)** : La commande `echo "secret"` ajoute '
                 'un retour à la ligne invisible `\\n` à la fin, ce qui fausse complètement le hash SHA-256 '
                 'par rapport à Python ! Utilisez toujours `printf \'%s\' "secret"` (ou `echo -n`).\n'
                 '- **Vérification de fichiers** : `sha256sum archive.tar.gz` ou `openssl dgst -sha256 '
                 "archive.tar.gz` garantit qu'une sauvegarde ou un binaire n'a pas été corrompu ni altéré.",
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
  'short': "Calcul en ligne de commande d'une signature HMAC-SHA256 avec clé secrète pour tester vos "
           'Webhooks et jetons.',
  'analogy': 'Apposer le sceau officiel du serveur directement depuis votre terminal Linux afin de simuler '
             "l'envoi d'un Webhook authentique (Stripe, GitHub, paiement) vers votre API Flask.",
  'explanation': '- Contrairement à un simple hash SHA-256 que tout le monde peut recalculer, **HMAC '
                 '(`Hash-based Message Authentication Code`)** combine le corps du message avec une **clé '
                 'secrète (`-hmac "cle"`)**.\n'
                 "- C'est l'outil indispensable pour générer l'en-tête `X-Webhook-Signature` lors d'un test "
                 'avec `curl`.',
  'code_example': "# 1. Calculer la signature HMAC-SHA256 d'un corps JSON avec OpenSSL :\n"
                  'printf \'%s\' \'{"id":101,"statut":"paye"}\' | openssl dgst -sha256 -hmac '
                  '"whsec_isgp_2026"\n'
                  '\n'
                  "# 2. Stocker la signature dans une variable Bash et appeler l'API avec curl :\n"
                  'BODY=\'{"id":101,"statut":"paye"}\'\n'
                  'SIG=$(printf \'%s\' "$BODY" | openssl dgst -sha256 -hmac "whsec_isgp_2026" | awk \'{print '
                  "$2}')\n"
                  'curl -i -X POST http://127.0.0.1:5000/api/webhooks -H "X-Webhook-Signature: sha256=$SIG" '
                  '-d "$BODY"'},
 {'id': 'openssl_aes_encryption',
  'term': 'Chiffrement Symétrique AES-256 (openssl enc -aes-256-cbc -pbkdf2)',
  'category': 'Cryptographie & OpenSSL',
  'level': 'Addendum Sécurité',
  'short': "Chiffrement réversible de fichiers sensibles (.env, sauvegardes SQLite .db) à l'aide de "
           "l'algorithme AES-256 et d'une phrase secrète.",
  'analogy': 'Un coffre-fort blindé à clé symétrique : contrairement au hachage (qui broie le document de '
             'manière irréversible), le chiffrement AES verrouille le document dans un coffre ; quiconque '
             "possède la clé secrète peut l'ouvrir et retrouver le fichier exact à l'octet près.",
  'explanation': "- **Hachage != Chiffrement** : On *hache* les mots de passe (car on n'a jamais besoin de "
                 'les relire en clair), mais on *chiffre* les sauvegardes de bases de données, les fichiers '
                 '`.env` ou les numéros de cartes bancaires (car on doit pouvoir les déchiffrer).\n'
                 '- **Options OpenSSL obligatoires** : Toujours utiliser `-salt` (sel aléatoire), `-pbkdf2` '
                 '(dérivation de clé standard) et `-iter 600000` (protection contre la force brute).',
  'code_example': "# 1. CHIFFRER une base SQLite avant de l'envoyer sur le Cloud :\n"
                  'openssl enc -aes-256-cbc -salt -pbkdf2 -iter 600000 \\\n'
                  '  -in ecole_isgp.db -out ecole_isgp.db.enc -pass pass:"MonSecretRobuste2026!"\n'
                  '\n'
                  "# 2. DÉCHIFFRER l'archive (-d) pour restaurer la base SQLite :\n"
                  'openssl enc -d -aes-256-cbc -pbkdf2 -iter 600000 \\\n'
                  '  -in ecole_isgp.db.enc -out ecole_isgp_restauree.db -pass pass:"MonSecretRobuste2026!"'},
 {'id': 'openssl_rsa_ed25519',
  'term': 'Chiffrement Asymétrique RSA / Ed25519 : Clé Privée vs Clé Publique (openssl genpkey)',
  'category': 'Cryptographie & OpenSSL',
  'level': 'Addendum Sécurité',
  'short': "Génération d'une paire de clés mathématiquement liées : la Clé Privée (secrète, qui signe) et la "
           'Clé Publique (partagée, qui vérifie).',
  'analogy': 'Une boîte aux lettres à double serrure ou un tampon notarié : seul le serveur '
             "d'authentification central possède la Clé Privée pour signer les jetons JWT (`RS256` / "
             "`EdDSA`), mais tous les microservices de l'entreprise possèdent la Clé Publique pour vérifier "
             'les jetons sans jamais pouvoir en fabriquer de faux !',
  'explanation': '- **Avantage majeur sur HMAC (`HS256`) en architecture Microservices** : Avec HMAC '
                 '(symétrique), si vous avez 20 microservices qui vérifient les jetons, les 20 serveurs '
                 "doivent connaître la même `SECRET_KEY` (si l'un est piraté, il peut forger des jetons "
                 '`admin`). Avec **RSA / Ed25519 (asymétrique)**, seul le serveur de Login détient la '
                 "`private.pem`, et les 20 autres serveurs n'ont que `public.pem` (lecture seule).",
  'code_example': '# 1. Générer une clé privée RSA de 4096 bits :\n'
                  'openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:4096 -out private_key.pem\n'
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
  'short': 'Création de certificats TLS auto-signés pour le développement HTTPS local et inspection des '
           'certificats de serveurs en production.',
  'analogy': "Le passeport biométrique officiel d'un serveur Web (`X.509`), vérifié par le navigateur lors "
             "de la poignée de main TLS avant même d'envoyer le premier octet HTTP pour garantir que le "
             'canal est chiffré de bout en bout.',
  'explanation': '- **En production** : On utilise un certificat signé par une Autorité de Certification '
                 "reconnue (ex: **Let's Encrypt / Certbot** sur Nginx).\n"
                 '- **En test local ou réseau interne** : `openssl req -x509` génère en une seule commande '
                 'la clé privée (`key.pem`) et le certificat (`cert.pem`).\n'
                 "- **Diagnostic d'expiration** : `openssl s_client` permet de vérifier pourquoi un appel "
                 'API HTTPS échoue (certificat expiré, chaîne incomplète).',
  'code_example': '# 1. Générer un certificat HTTPS auto-signé valable 365 jours pour localhost :\n'
                  'openssl req -x509 -newkey rsa:4096 -nodes \\\n'
                  '  -keyout key.pem -out cert.pem -days 365 \\\n'
                  '  -subj "/C=DZ/ST=Alger/O=ISGP/CN=localhost"\n'
                  '\n'
                  "# 2. Inspecter le contenu et les dates de validité d'un fichier certificat :\n"
                  'openssl x509 -in cert.pem -noout -subject -issuer -dates\n'
                  '\n'
                  "# 3. Vérifier le certificat HTTPS d'un serveur distant en direct :\n"
                  'openssl s_client -connect example.com:443 -servername example.com </dev/null 2>/dev/null '
                  '| openssl x509 -noout -dates -subject'},
 {'id': 'base64_encoding_cli',
  'term': 'Encodage & Décodage Base64 en Terminal (base64 & openssl base64)',
  'category': 'Cryptographie & OpenSSL',
  'level': 'Addendum Sécurité',
  'short': 'Représentation de données binaires ou JSON sous forme de texte ASCII pour les en-têtes HTTP '
           '(Basic Auth, Payload JWT).',
  'analogy': "Traduire un document en alphabet morse pour qu'il passe sur une ligne télégraphique : cela "
             "permet le transport sans erreur d'encodage, mais ce n'est absolument pas un chiffrement "
             'secret.',
  'explanation': "- Utilisé par l'authentification **`Authorization: Basic <base64(user:pass)>`** et pour "
                 "encoder l'en-tête et le Payload d'un **JWT (`Header.Payload.Signature`)**.\n"
                 '- Sous Linux, `base64 -w 0` encode sur une seule ligne (sans coupure tous les 76 '
                 'caractères), et `base64 -d` décode instantanément.',
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
  'term': 'Dérivation de Mots de Passe Salés (PBKDF2, Scrypt, Argon2, openssl passwd)',
  'category': 'Cryptographie & OpenSSL',
  'level': 'Addendum Sécurité',
  'short': 'Hachage volontairement ralenti et salé destiné exclusivement à protéger les mots de passe '
           'humains stockés en base de données.',
  'analogy': 'Ajouter un labyrinthe de 600 000 portes (itérations) et un grain de sable unique (Salt) devant '
             'chaque mot de passe : un utilisateur légitime met 0,1 seconde à se connecter, mais un pirate '
             'qui tente 1 milliard de mots de passe mettra plusieurs siècles.',
  'explanation': '- **Pourquoi SHA-256 seul est interdit pour les mots de passe ?** SHA-256 est conçu pour '
                 'être ultra-rapide (des milliards de calculs/seconde sur carte graphique). Pour les mots de '
                 'passe, on utilise une fonction **KDF (*Key Derivation Function*)** lente avec sel '
                 'aléatoire : `scrypt`, `pbkdf2:sha256` (intégrés à `werkzeug.security`) ou `openssl passwd '
                 '-6`.',
  'code_example': '# 1. Générer un hash de mot de passe salé SHA-512 sous Linux :\n'
                  'openssl passwd -6 "MotDePasseStagiaire2026!"\n'
                  '\n'
                  '# 2. Générer et vérifier un hash Scrypt / PBKDF2 en Python (Werkzeug/Flask) :\n'
                  'python3 -c "from werkzeug.security import generate_password_hash, check_password_hash; '
                  '\\\n'
                  "h = generate_password_hash('Secret2026!'); print('Hash:', h); print('Valide:', "
                  'check_password_hash(h, \'Secret2026!\'))"'},
 {'id': 'linux_ports_ss_lsof',
  'term': 'Inspection des Ports & Processus Linux (ss -tulpn, lsof -i, kill)',
  'category': 'Linux & Réseau Prod',
  'level': 'Addendum Linux',
  'short': "Commandes système permettant d'identifier quel programme écoute sur un port TCP (ex. :5000) et "
           'de libérer un port bloqué.',
  'analogy': 'Le tableau de contrôle de la capitainerie du port : permet de voir instantanément quel navire '
             "(processus `PID`) est amarré au quai n°5000 lorsque Flask affiche l'erreur `Address already in "
             'use`.',
  'explanation': '- **`ss -tulpn`** (*Socket Statistics*, remplaçant moderne de `netstat`) : Liste tous les '
                 'ports TCP (`-t`) et UDP (`-u`) en écoute (`-l`), avec le numéro de port numérique (`-n`) '
                 'et le nom/PID du processus (`-p`).\n'
                 '- **`lsof -i :5000`** (*List Open Files*) : Cible directement le port `5000`.\n'
                 "- **Arrêt propre vs forcé** : Utilisez d'abord `kill -15 <PID>` (`SIGTERM`, laisse Flask "
                 'fermer SQLite proprement) avant `kill -9 <PID>` (`SIGKILL`, arrêt brutal).',
  'code_example': '# 1. Lister tous les serveurs en écoute sur la machine Linux :\n'
                  'sudo ss -tulpn | grep -E "5000|8000|80|443"\n'
                  '\n'
                  '# 2. Trouver le PID exact qui bloque le port 5000 :\n'
                  'lsof -i :5000\n'
                  '# ou :\n'
                  'fuser 5000/tcp\n'
                  '\n'
                  '# 3. Terminer proprement le processus (ex. PID 14520) :\n'
                  'kill -15 14520'},
 {'id': 'linux_dns_netcat',
  'term': 'Diagnostic Réseau, DNS & Pare-feu (dig, nc -zv, ip a, ping)',
  'category': 'Linux & Réseau Prod',
  'level': 'Addendum Linux',
  'short': 'Utilitaires de diagnostic permettant de vérifier la résolution de nom de domaine (DNS) et '
           "l'ouverture d'un port TCP distant.",
  'analogy': "Vérifier d'abord que l'adresse figure bien dans l'annuaire (`dig`), puis vérifier que la route "
             "est praticable (`ping`) et que le guichet est ouvert (`nc -zv`) avant d'accuser le code "
             'Python.',
  'explanation': '- **`ip -br a`** : Affiche de façon compacte toutes les adresses IP de votre serveur '
                 'Linux.\n'
                 "- **`dig +short domaine.dz`** : Interroge le serveur DNS pour obtenir l'adresse IP "
                 'associée à un nom de domaine.\n'
                 '- **`nc -zv HOTE PORT` (Netcat)** : Teste uniquement la poignée de main TCP (*3-way '
                 'handshake*) sur un port précis (ex: vérifier si PostgreSQL `:5432` ou Flask `:5000` est '
                 'joignable à travers le pare-feu).',
  'code_example': '# 1. Afficher les adresses IP locales du serveur de manière lisible :\n'
                  'ip -br addr show\n'
                  '\n'
                  '# 2. Tester si le port TCP 5000 est ouvert en local ou à distance :\n'
                  'nc -zv 127.0.0.1 5000\n'
                  '\n'
                  '# 3. Résoudre un nom de domaine en adresse IP via DNS :\n'
                  'dig +short api.github.com'},
 {'id': 'linux_jq_json',
  'term': 'Traitement et Filtrage JSON en Terminal (jq & json.tool)',
  'category': 'Linux & Réseau Prod',
  'level': 'Addendum Linux',
  'short': "Processeur JSON en ligne de commande permettant d'indenter, coloriser, extraire et filtrer les "
           'réponses de `curl`.',
  'analogy': "Un scalpel chirurgical pour réponses d'API : au lieu de lire un bloc compact de 5 000 "
             'caractères JSON renvoyé par `curl`, `jq` extrait en une fraction de seconde uniquement les '
             'champs qui vous intéressent.',
  'explanation': '- **`python3 -m json.tool`** : Toujours disponible sans rien installer dès que Python est '
                 "présent ; indente et valide n'importe quel flux JSON.\n"
                 "- **`jq`** : Permet d'extraire une clé (`.meta.total_items`), de parcourir un tableau "
                 '(`.data[]`), ou de filtrer selon une condition (`select(.duree_jours >= 5)`).',
  'code_example': '# 1. Indenter une réponse curl avec Python (sans installer jq) :\n'
                  'curl -s http://127.0.0.1:5000/api/sandbox/formations | python3 -m json.tool\n'
                  '\n'
                  '# 2. Extraire uniquement les titres des formations avec jq :\n'
                  "curl -s http://127.0.0.1:5000/api/sandbox/formations | jq '.data[].titre'\n"
                  '\n'
                  '# 3. Filtrer les formations de 5 jours ou plus avec jq :\n'
                  "curl -s http://127.0.0.1:5000/api/sandbox/formations | jq '.data[] | select(.duree_jours "
                  ">= 5)'"},
 {'id': 'linux_logs_audit',
  'term': 'Analyse de Journaux (Logs) en Temps Réel (tail -f, grep, awk, journalctl)',
  'category': 'Linux & Réseau Prod',
  'level': 'Addendum Linux',
  'short': "Commandes d'exploitation permettant de surveiller le trafic HTTP en direct, isoler les erreurs "
           '500 et détecter les adresses IP suspectes.',
  'analogy': 'Les écrans de vidéosurveillance et la boîte noire du serveur : permettent de suivre chaque '
             'requête à la milliseconde près et de repérer immédiatement une anomalie ou une attaque.',
  'explanation': '- **`tail -f fichier.log`** : Affiche en temps réel chaque nouvelle ligne ajoutée au '
                 'journal.\n'
                 '- **`grep`** : Filtre les lignes contenant un motif précis (ex: `" 500 "`, `" 401 "` ou un '
                 '`X-Request-ID`).\n'
                 "- **`awk` + `sort` + `uniq -c`** : Permet d'agréger les logs Nginx/Gunicorn pour calculer "
                 'le top 10 des adresses IP consommatrices.',
  'code_example': '# 1. Suivre les logs en temps réel en filtrant uniquement les erreurs 4xx et 5xx :\n'
                  'tail -f /var/log/nginx/access.log | grep --line-buffered -E " (401|403|429|500) "\n'
                  '\n'
                  "# 2. Retrouver toute l'histoire d'une requête grâce à son X-Request-ID :\n"
                  'grep "req-8f2a9c01" /var/log/api_isgp/*.log\n'
                  '\n'
                  "# 3. Identifier le Top 10 des adresses IP qui appellent le plus l'API :\n"
                  "awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -nr | head -n 10"},
 {'id': 'linux_chmod_env',
  'term': "Permissions Linux (chmod 600) & Variables d'Environnement (export / .env)",
  'category': 'Linux & Réseau Prod',
  'level': 'Addendum Linux',
  'short': "Verrouillage des droits d'accès aux fichiers secrets (.env, clés privées .pem) et injection de "
           "variables d'environnement sous Linux.",
  'analogy': "Mettre les clés du serveur dans un tiroir dont seul l'utilisateur propriétaire possède la clé "
             '(`chmod 600`), au lieu de les laisser sur une table accessible à tous les comptes de la '
             'machine (`chmod 644` ou `777`).',
  'explanation': '- **Code `chmod 600` (`-rw-------`)** : Seul le propriétaire du fichier peut le lire et '
                 "l'écrire ; les autres utilisateurs du serveur n'ont aucun droit (`0`). C'est obligatoire "
                 'pour `.env`, `private.pem` et `~/.ssh/id_rsa`.\n'
                 "- **Commande `export`** : Définit une variable d'environnement transmise au processus "
                 'Python/Gunicorn lancé depuis ce terminal (`os.environ.get(...)`).',
  'code_example': '# 1. Restreindre la lecture du fichier .env et de la clé privée au seul propriétaire :\n'
                  'chmod 600 .env private_key.pem\n'
                  'ls -l .env  # Affiche : -rw------- 1 abdelouahab abdelouahab ...\n'
                  '\n'
                  "# 2. Exporter une variable d'environnement et lancer l'API :\n"
                  'export API_SECRET_KEY="$(openssl rand -hex 32)"\n'
                  '.venv/bin/python app.py'},
 {'id': 'linux_systemd_nginx',
  'term': 'Déploiement Linux : Service systemd, Gunicorn & Reverse Proxy Nginx',
  'category': 'Linux & Réseau Prod',
  'level': 'Addendum Linux',
  'short': 'Architecture standard permettant de faire tourner une API Flask 24h/24 en tâche de fond avec '
           'redémarrage automatique et HTTPS.',
  'analogy': 'Transformer un moteur posé sur un établi (`python app.py`) en une centrale électrique '
             'automatisée (`systemd` + `Gunicorn`) protégée par un poste de garde blindé (`Nginx`).',
  'explanation': '- **`systemd` (`/etc/systemd/system/isgp-api.service`)** : Gère le cycle de vie du serveur '
                 '(`systemctl start/restart/status isgp-api`) et le relance automatiquement en 2 secondes '
                 "s'il plante (`Restart=always`).\n"
                 '- **`Nginx`** : Écoute sur les ports publics `80`/`443` (HTTPS) et relaie les requêtes '
                 'propres vers `http://127.0.0.1:8000` (`proxy_pass`).',
  'code_example': "# Commandes d'exploitation du service systemd en production :\n"
                  'sudo systemctl daemon-reload\n'
                  'sudo systemctl enable --now isgp-api\n'
                  'sudo systemctl status isgp-api\n'
                  '\n'
                  '# Consulter les journaux du service en temps réel :\n'
                  'sudo journalctl -u isgp-api -f'},
 {'id': 'mime_content_type_accept_415',
  'term': 'Types MIME (Content-Type vs Accept), request.mimetype & Code 415',
  'category': 'Types MIME & Flask',
  'level': 'Fondamental',
  'short': "Identifiant normalisé IANA (type/sous-type) décrivant le format exact d'un flux d'octets HTTP et "
           'pilotant la négociation de contenu dans Flask.',
  'analogy': "L'étiquette réglementaire collée sur un conteneur maritime : 'Liquide', 'Poudre' ou 'Gaz'. "
             'Sans cette étiquette (Content-Type), le destinataire ne sait pas avec quel outil ouvrir le '
             'conteneur.',
  'explanation': '- **`Content-Type`** : Indique le type MIME du corps actuellement transporté (ex: '
                 '`application/json; charset=utf-8`). Dans Flask, `request.mimetype` renvoie le type pur '
                 "(`'application/json'`) sans les paramètres (`charset`, `boundary`).\n"
                 "- **`Accept`** : Envoyé par le client pour indiquer les formats de réponse qu'il accepte "
                 "(`request.accept_mimetypes.best_match(['application/json', 'text/html'])`).\n"
                 "- **Code `415 Unsupported Media Type`** : Code HTTP officiel à retourner lorsqu'un client "
                 'envoie un `Content-Type` que votre route ne supporte pas.',
  'code_example': '# Inspecter le type MIME entrant et rejeter proprement en 415 :\n'
                  'if request.mimetype not in ("application/json", "application/x-www-form-urlencoded"):\n'
                  '    return jsonify({"erreur": f"Type MIME {request.mimetype} non supporté"}), 415'},
 {'id': 'mime_json_vs_form_vs_multipart',
  'term': "Types MIME d'Entrée (POST) : application/json vs x-www-form-urlencoded vs multipart/form-data",
  'category': 'Types MIME & Flask',
  'level': "Cœur d'API",
  'short': "Les trois grands types MIME utilisés pour envoyer des données à un serveur Flask lors d'une "
           'requête POST ou PUT.',
  'analogy': "Trois façons de transmettre un dossier à l'administration : un fichier informatique structuré "
             '(`application/json`), un coupon-réponse papier (`application/x-www-form-urlencoded`), ou une '
             'pochette cartonnée contenant à la fois le coupon papier et des pièces jointes PDF '
             '(`multipart/form-data`).',
  'explanation': "- **`application/json`** : Envoyé par `fetch()`, Axios, Mobile ou `curl -H 'Content-Type: "
                 "application/json'`. Lu dans Flask via **`request.get_json(silent=True)`**.\n"
                 "- **`application/x-www-form-urlencoded`** : Format par défaut d'un `<form method='POST'>` "
                 "HTML ou de `curl -d 'a=1&b=2'`. Lu dans Flask via **`request.form.get('champ')`**.\n"
                 "- **`multipart/form-data`** : Format d'un `<form method='POST' "
                 "enctype='multipart/form-data'>` ou de `curl -F`. Texte dans **`request.form`**, fichiers "
                 'binaires dans **`request.files`**.',
  'code_example': 'if request.mimetype == "application/json":\n'
                  '    data = request.get_json(silent=True) or {}\n'
                  'elif request.mimetype in ("application/x-www-form-urlencoded", "multipart/form-data"):\n'
                  '    data = request.form\n'
                  '    fichier = request.files.get("document_pdf")'},
 {'id': 'mime_response_csv_xml_sse',
  'term': 'Émettre des Types MIME Personnalisés (Response : CSV, XML, Problem+JSON, SSE)',
  'category': 'Types MIME & Flask',
  'level': "Cœur d'API",
  'short': "Utilisation de l'objet Response(corps, status=..., mimetype=...) dans Flask pour retourner tout "
           'format autre que HTML ou JSON standard.',
  'analogy': "Si `render_template()` est l'imprimante de brochures HTML et `jsonify()` l'emballeur de colis "
             "JSON, `Response(..., mimetype=...)` est l'atelier sur mesure capable d'expédier des feuilles "
             'Excel CSV, des actes XML ou un flux continu.',
  'explanation': '- **`text/csv`** : Export de données tabulaires (combiné avec `Content-Disposition: '
                 'attachment; filename="export.csv"`).\n'
                 "- **`application/problem+json`** : Réponses d'erreur normalisées selon le standard **RFC "
                 '7807**.\n'
                 '- **`application/xml`** : Enveloppes SOAP ou flux XML.\n'
                 "- **`text/event-stream`** : Flux temps réel **Server-Sent Events (SSE)** à partir d'un "
                 'générateur Python (`yield f"data: ...\\n\\n"`).',
  'code_example': 'from flask import Response\n'
                  '\n'
                  '@app.route("/api/export.csv")\n'
                  'def exporter_csv():\n'
                  '    csv_data = "id,titre,duree\\n1,API REST,5\\n"\n'
                  '    return Response(\n'
                  '        csv_data,\n'
                  '        mimetype="text/csv; charset=utf-8",\n'
                  '        headers={"Content-Disposition": "attachment; filename=formations.csv"}\n'
                  '    )'},
 {'id': 'mime_send_file_disposition_nosniff',
  'term': 'Fichiers Binaires (send_file : application/pdf, image/png) & X-Content-Type-Options: nosniff',
  'category': 'Types MIME & Flask',
  'level': 'Intermédiaire',
  'short': "Transmission de fichiers binaires avec send_file(), contrôle de l'ouverture navigateur (inline "
           'vs attachment) et protection contre le MIME Sniffing.',
  'analogy': 'Envoyer un document PDF soit sous verre pour être lu sur place dans le navigateur (`inline`), '
             'soit dans une enveloppe scellée que le navigateur enregistre directement dans le dossier '
             'Téléchargements (`attachment`).',
  'explanation': "- **`send_file(chemin_ou_bytesio, mimetype='application/pdf', as_attachment=...)`** :\n"
                 '  - `as_attachment=False` (`Content-Disposition: inline`) : Le navigateur affiche le PDF '
                 "ou l'image (`image/png`, `image/svg+xml`) directement dans l'onglet.\n"
                 "  - `as_attachment=True, download_name='facture.pdf'` (`Content-Disposition: attachment`) "
                 ': Force le téléchargement du fichier.\n'
                 "- **Sécurité `X-Content-Type-Options: nosniff`** : Empêche un navigateur d'interpréter un "
                 'fichier texte ou image uploadé par un utilisateur comme du code HTML/JavaScript '
                 'exécutable.',
  'code_example': 'import io\n'
                  'from flask import send_file\n'
                  '\n'
                  '@app.route("/api/facture.pdf")\n'
                  'def facture_pdf():\n'
                  '    buffer = io.BytesIO(b"%PDF-1.4 ...")\n'
                  '    return send_file(buffer, mimetype="application/pdf", as_attachment=True, '
                  'download_name="facture.pdf")'},
 {'id': 'api_versioning_v1_vs_v2',
  'term': 'Pourquoi voit-on toujours /api/v1 et rarement /api/v2 ? (Loi de Postel & Assurance-Vie)',
  'category': 'Architecture Web',
  'level': "Cœur d'API",
  'short': 'Explication architecturale de la longévité de /api/v1 (ajouts rétrocompatibles) et de '
           "l'obligation de préfixer par /v1 dès le premier jour.",
  'analogy': 'Construire une maison avec un compteur électrique prévu pour un 2e étage (/api/v1) : tant '
             "qu'on ajoute des meubles dans les pièces existantes (nouveaux champs JSON optionnels), on "
             "reste au 1er étage pendant 10 ans. Mais le jour où l'on doit refaire les fondations (Breaking "
             "Change), la réservation du 2e étage (/api/v2) évite de démolir le 1er pendant qu'il est "
             'habité.',
  'explanation': '- **Pourquoi `v1` dure 5 à 10 ans (Loi de Postel / *Tolerant Reader*)** : Ajouter un champ '
                 'JSON dans une réponse, ajouter une route ou un paramètre optionnel ne casse aucun client '
                 "existant. 90 % des évolutions d'une API se font donc à l'intérieur de `/api/v1`.\n"
                 '- **Pourquoi mettre `/api/v1` dès le Jour 1** : Si vous publiez `/api/formations` sans '
                 '`/v1` dans 50 000 applications mobiles compilées, le jour où un changement incompatible '
                 "survient, vous ne pouvez plus créer de nouvelle version sans casser l'URL existante.",
  'code_example': '# Coexistence de /api/v1 et /api/v2 via deux Blueprints Flask :\n'
                  'bp_v1 = Blueprint("v1", __name__, url_prefix="/api/v1/formations")\n'
                  'bp_v2 = Blueprint("v2", __name__, url_prefix="/api/v2/formations")\n'
                  'app.register_blueprint(bp_v1)\n'
                  'app.register_blueprint(bp_v2)'},
 {'id': 'breaking_vs_non_breaking_changes',
  'term': 'Évolution Rétrocompatible (Non-Breaking) vs Rupture de Contrat (Breaking Change)',
  'category': 'Architecture Web',
  'level': "Cœur d'API",
  'short': 'Distinction chirurgicale entre une modification qui préserve les clients v1 existants et une '
           'modification qui exige la création de /api/v2.',
  'analogy': "Ajouter une colonne supplémentaire à la fin d'un catalogue imprimé ne gêne personne "
             '(Non-Breaking). En revanche, remplacer les prix en Dinars par un objet complexe ou supprimer '
             "la colonne 'Titre' fait planter tous les lecteurs automatiques (Breaking Change).",
  'explanation': '- **Non-Breaking (Rester en `v1`)** : Ajouter une clé JSON en sortie, créer un nouvel '
                 'endpoint (`GET /api/v1/certificats`), ajouter un query param optionnel (`?lang=fr`).\n'
                 '- **Breaking Change (Exige `v2`)** : Renommer ou supprimer une clé JSON (`intitule` -> '
                 '`titre`), changer le type d\'une clé (`"duree": 5` -> `"duree": {"valeur": 5, "unite": '
                 '"jours"}`), ou rendre un nouveau champ obligatoire en `POST`.',
  'code_example': '# v1 (Schéma plat historique) :\n'
                  '{"id": 1, "intitule": "Architecture API", "duree": 5}\n'
                  '\n'
                  '# v2 (Breaking Change sur le nom et le type des champs) :\n'
                  '{"id": 1, "titre": "Architecture API", "duree": {"valeur": 5, "unite": "jours"}}'},
 {'id': 'rfc8594_deprecation_sunset_410',
  'term': "Dépréciation d'API (Norme RFC 8594 : En-têtes Deprecation, Sunset, Link & Code 410 Gone)",
  'category': 'Architecture Web',
  'level': "Cœur d'API",
  'short': "Protocole standard IETF permettant d'avertir les clients qu'une version d'API (/api/v1) est en "
           'fin de vie avant son extinction définitive (410 Gone).',
  'analogy': "Les panneaux d'information routiers posés 6 mois avant la fermeture d'un ancien pont : ils "
             'indiquent que le pont est en fin de vie (`Deprecation: true`), la date exacte de fermeture '
             '(`Sunset`), et la flèche vers le nouveau pont (`Link: </api/v2>; rel="successor-version"`).',
  'explanation': '- **`Deprecation: true`** : Indique aux clients et outils de monitoring que la route '
                 'appelée est obsolète.\n'
                 '- **`Sunset: Thu, 31 Dec 2026 23:59:59 GMT`** (RFC 8594) : Date HTTP officielle à laquelle '
                 '`v1` cessera de fonctionner.\n'
                 '- **`Link: </api/v2/formations>; rel="successor-version"`** : Pointe vers la nouvelle '
                 'version.\n'
                 '- **`410 Gone`** : Code HTTP renvoyé une fois la date `Sunset` dépassée (contrairement à '
                 '`404`, `410` signifie que la ressource a existé mais a été définitivement retirée).',
  'code_example': '@formations_v1_bp.after_request\n'
                  'def avertir_depreciation_v1(response):\n'
                  '    response.headers["Deprecation"] = "true"\n'
                  '    response.headers["Sunset"] = "Thu, 31 Dec 2026 23:59:59 GMT"\n'
                  '    response.headers["Link"] = \'</api/v2/formations>; rel="successor-version"\'\n'
                  '    return response'},
 {'id': 'api_envelope_pagination_cursor_offset',
  'term': 'Enveloppe JSON (meta / data / links) & Pagination (Offset/Limit vs Cursor)',
  'category': 'Architecture Web',
  'level': 'Intermédiaire',
  'short': "Structuration racine d'une réponse JSON de collection pour permettre l'évolution sans Breaking "
           'Change et la pagination haute performance.',
  'analogy': 'Ne jamais expédier des feuilles volantes sans chemise cartonnée : l\'objet enveloppe `{"meta": '
             '..., "data": [...]}` est la chemise sur laquelle on peut inscrire le numéro de page et le '
             'total sans toucher aux feuilles `data`.',
  'explanation': '- **Pourquoi proscrire `[...]` à la racine** : Si `GET /api/v1/formations` renvoie '
                 'directement un tableau JSON `[...]`, vous ne pourrez jamais ajouter `total_items` ou '
                 '`next_page` sans casser le type racine (forçant une `v2`). Encapsulez toujours dans '
                 '`{"meta": {...}, "data": [...]}`.\n'
                 '- **Pagination `Offset/Limit` (`?page=2&per_page=20`)** : Simple (`LIMIT 20 OFFSET 20`), '
                 'idéale pour les interfaces avec numéros de pages.\n'
                 '- **Pagination par Curseur (`?after_id=1042&limit=20`)** : Utilise `WHERE id > 1042 LIMIT '
                 '20` (index SQL direct), indispensable sur des tables de millions de lignes ou des flux '
                 'temps réel.',
  'code_example': 'return jsonify({\n'
                  '    "meta": {"version": "v2", "page": 1, "per_page": 20, "total_items": 145},\n'
                  '    "data": formations,\n'
                  '    "links": {"self": "/api/v2/formations?page=1", "next": "/api/v2/formations?page=2"}\n'
                  '}), 200'},
 {'id': 'swagger_openapi_3',
  'term': 'Swagger UI (/api/docs), Swagger Editor & Spécification OpenAPI 3.0 (OAS)',
  'category': 'Architecture Web',
  'level': "Cœur d'API",
  'short': "Norme mondiale de contrat d'API (OpenAPI 3.0 JSON/YAML) et portail Web interactif (Swagger UI) "
           'permettant de documenter et tester une API dans le navigateur.',
  'analogy': "OpenAPI 3.0 est le plan d'architecte coté et normalisé de l'immeuble (`openapi.json`), tandis "
             'que Swagger UI est la visite virtuelle interactive générée automatiquement à partir de ce plan '
             '(boutons « Authorize » et « Try it out »).',
  'explanation': '- **OpenAPI Specification (OAS 3.0 / 3.1)** : Standard géré par la Linux Foundation '
                 'décrivant formellement `info`, `servers`, `paths` (avec paramètres entre accolades '
                 '`{id}`), `components.schemas` (`$ref`) et `components.securitySchemes` (`BearerAuth` JWT, '
                 '`ApiKeyAuth` `X-API-Key`).\n'
                 '- **Swagger UI (`/api/docs`)** : Portail HTML/JS qui lit `/api/openapi.json` et offre le '
                 'bouton cadenas **« Authorize »** ainsi que le bouton **« Try it out »** sur chaque route.\n'
                 '- **Import universel** : Le fichier `openapi.json` peut être importé en un clic dans '
                 'Postman, Insomnia ou `openapi-generator` pour générer les SDK clients.',
  'code_example': '# Route Flask exposant le contrat OpenAPI 3.0.3 :\n'
                  '@app.route("/api/openapi.json")\n'
                  'def spec():\n'
                  '    return jsonify({"openapi": "3.0.3", "info": {"title": "API ISGP", "version": '
                  '"1.0.0"}, "paths": {...}})'},
 {'id': 'curl_postman_httpie',
  'term': 'curl, Postman, HTTPie & REST Client (.http)',
  'category': 'Architecture Web',
  'level': 'Fondamental',
  'short': 'Outils de test et de diagnostic permettant de forger des requêtes HTTP (GET, POST, PUT, PATCH, '
           'DELETE, Headers) sans navigateur.',
  'analogy': "Un multimètre d'ingénieur réseau : là où un navigateur classique ne sait envoyer que des "
             'requêtes GET simples, curl et Postman permettent de contrôler chaque en-tête, chaque méthode '
             'et chaque octet JSON.',
  'explanation': '- **`curl`** : Outil en ligne de commande présent sur tous les serveurs (`-i` pour voir '
                 'les Headers, `-v` pour le mode verbeux, `-X` pour la méthode, `-H` pour un Header, `-d` '
                 'pour le corps JSON).\n'
                 '- **Postman / Bruno / Insomnia** : Interfaces graphiques permettant de sauvegarder des '
                 'Collections de requêtes.\n'
                 '- **HTTPie (`http`) & REST Client (`.http`)** : Outils modernes en terminal ou intégrés à '
                 'VS Code.',
  'code_example': 'curl -i -X POST "http://127.0.0.1:5000/api/sandbox/formations" \\\n'
                  '  -H "Content-Type: application/json" \\\n'
                  '  -H "X-API-Key: isgp-secret-2026" \\\n'
                  '  -d \'{"titre": "API Flask", "duree_jours": 5}\''},
 {'id': 'rate_limiting',
  'term': 'Rate Limiting (Limitation de Débit & Code 429)',
  'category': 'Sécurité & Architecture API',
  'level': "Cœur d'API",
  'short': "Mécanisme qui limite le nombre de requêtes qu'un client peut envoyer sur une période donnée (ex. "
           '60 requêtes par minute).',
  'analogy': 'Comme un distributeur bancaire qui autorise au maximum 3 essais ou un plafond de retrait par '
             'heure : si un programme envoie 10 000 demandes par seconde (par erreur ou par attaque), le '
             'guichet le bloque temporairement pour ne pas paralyser toute la banque.',
  'explanation': 'Sans Rate Limiting, un seul script mal codé (une boucle `while True`) ou un pirate peut '
                 'faire tomber votre serveur Flask. Le serveur compte les requêtes par adresse IP ou par clé '
                 'API (Fenêtre Glissante ou Token Bucket). Quand le quota est dépassé, il renvoie le code '
                 'officiel **`429 Too Many Requests`** accompagné des en-têtes `X-RateLimit-Remaining: 0` et '
                 '`Retry-After`.',
  'code_example': '# Si le client dépasse 3 requêtes en 20 secondes :\n'
                  'return jsonify({\n'
                  '    "erreur": "Quota dépassé (Rate Limit)",\n'
                  '    "reessayer_dans_secondes": 20\n'
                  '}), 429'},
 {'id': 'token_bearer',
  'term': "Token / Bearer Token & JWT (Jeton d'Accès Signé)",
  'category': 'Sécurité & Architecture API',
  'level': "Cœur d'API",
  'short': 'Un laissez-passer numérique temporaire et signé (HMAC), remis au client après connexion pour '
           'prouver son identité à chaque requête.',
  'analogy': "La carte magnétique d'une chambre d'hôtel : vous montrez votre pièce d'identité une seule fois "
             'à la réception (`/api/auth/token`), on vous remet une carte valable 24h (le Token). Ensuite, '
             'vous présentez simplement cette carte devant chaque porte (`Authorization: Bearer <token>`).',
  'explanation': "Attention : le contenu (`Payload`) d'un Token JWT ou `itsdangerous` est encodé en Base64 "
                 '(lisible par tous), mais **signé mathématiquement** avec la `SECRET_KEY` du serveur '
                 "(infalsifiable). N'y stockez jamais de mot de passe en clair !",
  'code_example': '# En-tête HTTP envoyé par le client :\n'
                  '# Authorization: Bearer eyJhbGciOi...\n'
                  '\n'
                  'auth = request.headers.get("Authorization", "")\n'
                  'if auth.startswith("Bearer "):\n'
                  '    token = auth.split(" ")[1]'},
 {'id': 'refresh_token_rbac',
  'term': 'Authentification (AuthN / 401) vs Autorisation (AuthZ / 403, RBAC, Scopes & BOLA)',
  'category': 'Sécurité & Architecture API',
  'level': "Cœur d'API",
  'short': 'AuthN vérifie QUI vous êtes (échec = 401 Unauthorized) ; AuthZ vérifie QUELS sont vos droits sur '
           'la ressource (échec = 403 Forbidden).',
  'analogy': "Le passeport contrôlé à l'entrée de l'aéroport est l'Authentification (`AuthN` -> `401` si "
             "absent). La carte d'accès réservée aux pilotes pour entrer dans le cockpit est l'Autorisation "
             '(`AuthZ` -> `403` si vous êtes un simple passager).',
  'explanation': "- **Authentification (`AuthN`)** : Vérifie l'identité via `Bearer Token` ou `X-API-Key`.\n"
                 '- **Autorisation (`AuthZ`)** : Trois niveaux complémentaires en API Management :\n'
                 '  1. **RBAC** : Contrôle par rôle (`stagiaire` vs `admin`).\n'
                 '  2. **Scopes OAuth2** : Permissions granulaires intégrées au jeton (`formations:read`, '
                 '`audit:admin`).\n'
                 "  3. **Propriété de l'objet (Anti-BOLA / OWASP API #1)** : Vérifier que l'enregistrement "
                 "ciblé appartient bien à l'utilisateur authentifié (`dossier.proprietaire == user.sub`).",
  'code_example': 'if not token_valide:\n'
                  '    return jsonify({"etape": "AuthN", "erreur": "Non authentifié"}), 401\n'
                  'if user["role"] != "admin" or "audit:admin" not in user["scopes"]:\n'
                  '    return jsonify({"etape": "AuthZ", "erreur": "Droits insuffisants"}), 403'},
 {'id': 'secret_env',
  'term': "Secrets & Variables d'Environnement (.env / os.environ)",
  'category': 'Sécurité & Architecture API',
  'level': "Cœur d'API",
  'short': "Pratique fondamentale consistant à stocker les mots de passe, clés de signature et clés d'API "
           'hors du code source Python.',
  'analogy': 'Vous ne gravez jamais le code de votre coffre-fort sur la façade extérieure de votre maison. '
             "Vous le gardez dans une enveloppe scellée à l'intérieur du coffre de la direction (les "
             "variables d'environnement du serveur).",
  'explanation': "Règle d'or absolue : **on n'écrit jamais un secret en dur dans `app.py`** (car si vous "
                 'partagez le code sur Git, tout le monde voit vos mots de passe). On stocke les secrets '
                 "dans l'environnement du système et Python les lit avec `os.environ.get('API_SECRET_KEY')`.",
  'code_example': 'import os\n'
                  '\n'
                  "# Lecture sécurisée depuis l'environnement du serveur :\n"
                  'SECRET_KEY = os.environ.get("API_SECRET_KEY", "cle-dev-locale")'},
 {'id': 'signature_hmac',
  'term': 'Signature Cryptographique HMAC & Webhooks',
  'category': 'Sécurité & Architecture API',
  'level': "Cœur d'API",
  'short': "Sceau mathématique calculé avec une clé secrète garantissant qu'un Token ou un Webhook entrant "
           "n'a pas été falsifié.",
  'analogy': "Le cachet de cire officiel d'un ministère sur un diplôme : tout le monde peut lire ce qui est "
             'écrit sur le diplôme, mais personne ne peut modifier son nom ou sa note sans briser le cachet, '
             'car seul le ministère possède le tampon officiel (`SECRET_KEY`).',
  'explanation': "Utilisé à la fois pour signer les Bearer Tokens et pour vérifier l'authenticité des "
                 '**Webhooks** entrants (`X-Webhook-Signature: sha256=...`). La comparaison doit toujours '
                 'utiliser `hmac.compare_digest(a, b)` pour contrer les attaques temporelles (*Timing '
                 'Attacks*).',
  'code_example': 'import hmac, hashlib\n'
                  'sig = hmac.new(SECRET.encode(), corps_brut, hashlib.sha256).hexdigest()\n'
                  'est_valide = hmac.compare_digest(sig_recue, sig)'},
 {'id': 'cookies_httponly_secure_samesite',
  'term': 'Cookies HTTP Sécurisés : Set-Cookie, HttpOnly (Anti-XSS), Secure (HTTPS) & SameSite (Anti-CSRF)',
  'category': 'Sécurité & Architecture API',
  'level': "Cœur d'API",
  'short': 'Mécanisme standard (RFC 6265) permettant au serveur de stocker un jeton ou un état dans le '
           "navigateur en l'isolant de JavaScript et des sites tiers.",
  'analogy': 'Stocker un jeton dans `localStorage` revient à poser ses clés sur la table du café (tout '
             'script XSS peut les voler). Un Cookie `HttpOnly; Secure; SameSite=Strict` place les clés dans '
             'un coffre blindé du navigateur que seul le serveur peut ouvrir.',
  'explanation': '- **`Set-Cookie` (Serveur $\\rightarrow$ Client) / `Cookie` (Client $\\rightarrow$ '
                 'Serveur)** : Émis via `response.set_cookie(...)`, lu via `request.cookies.get(...)`, '
                 'supprimé via `response.delete_cookie(...)` (`Max-Age=0`).\n'
                 '- **`HttpOnly`** (`httponly=True`) : Interdit à JavaScript (`document.cookie`) de lire le '
                 'cookie $\\rightarrow$ **Bouclier contre le vol de session par XSS**.\n'
                 '- **`Secure`** (`secure=True`) : Transmis uniquement sur **HTTPS (TLS)**.\n'
                 "- **`SameSite=Strict` ou `Lax`** : Empêche l'envoi automatique du cookie lors de requêtes "
                 'inter-sites $\\rightarrow$ **Bouclier contre les attaques CSRF**.',
  'code_example': 'resp = make_response(jsonify({"statut": "Connecté"}))\n'
                  'resp.set_cookie(\n'
                  '    "isgp_auth_token",\n'
                  '    jeton_signe,\n'
                  '    max_age=3600,\n'
                  '    httponly=True,     # Invisible pour document.cookie (Anti-XSS)\n'
                  '    secure=True,       # HTTPS uniquement\n'
                  '    samesite="Strict"  # Anti-CSRF\n'
                  ')'},
 {'id': 'signed_session_cookie_hmac',
  'term': 'Cookie de Session Signé HMAC (flask.session) vs Cookie Standard en Clair',
  'category': 'Sécurité & Architecture API',
  'level': "Cœur d'API",
  'short': "Différence fondamentale entre un cookie ordinaire modifiable par l'utilisateur et le "
           'dictionnaire session signé cryptographiquement avec secret_key.',
  'analogy': "Un cookie ordinaire (`set_cookie('theme', 'sombre')`) est écrit au crayon à papier : le client "
             "peut le gommer et le modifier. Le cookie `session` est scellé par l'empreinte mathématique "
             '`HMAC` de `app.secret_key` : la moindre retouche brise le sceau.',
  'explanation': '- **Cookie standard (`request.cookies`)** : Non signé. À réserver aux préférences '
                 "d'interface non sensibles (`lang=fr`, `theme=sombre`).\n"
                 '- **Session signée (`from flask import session`)** : Sérialise le dictionnaire en JSON, '
                 "l'encode en Base64URL et le signe avec `app.secret_key` via `itsdangerous`. Toute "
                 'altération côté client dans les outils de développement (F12) invalide la signature HMAC '
                 'et purge la session.',
  'code_example': 'app.secret_key = os.environ["FLASK_SECRET_KEY"]\n'
                  '\n'
                  '# Écriture signée par HMAC :\n'
                  'session["utilisateur"] = "yasmine.merabet"\n'
                  'session["role"] = "auditeur"\n'
                  '\n'
                  '# Révocation complète :\n'
                  'session.clear()'},
 {'id': 'cors_preflight',
  'term': 'CORS (Cross-Origin Resource Sharing) & Requête Preflight OPTIONS',
  'category': 'Sécurité & Architecture API',
  'level': "Cœur d'API",
  'short': 'Mécanisme de sécurité des navigateurs Web contrôlant quels domaines externes sont autorisés à '
           'lire les réponses de votre API.',
  'analogy': "Une liste d'invités accrochée à l'entrée d'un salon privé : si une application React hébergée "
             "sur un domaine inconnu tente d'interroger l'API depuis le navigateur d'un client, le "
             "navigateur vérifie d'abord si ce domaine figure sur la liste blanche "
             '(`Access-Control-Allow-Origin`).',
  'explanation': "- **Pourquoi `curl` n'est jamais bloqué par CORS ?** Parce que la politique *Same-Origin* "
                 'est appliquée uniquement par les navigateurs Web.\n'
                 '- **Requête `OPTIONS` (*Preflight*)** : Avant un `POST`/`PUT`/`DELETE` avec JSON ou '
                 '`Authorization`, le navigateur envoie une requête `OPTIONS` pour vérifier les en-têtes '
                 '`Access-Control-Allow-Methods` et `Access-Control-Allow-Headers`.',
  'code_example': '@app.after_request\n'
                  'def ajouter_cors(resp):\n'
                  '    origine = request.headers.get("Origin")\n'
                  '    if origine in {"https://portail.isgp.dz", "http://localhost:3000"}:\n'
                  '        resp.headers["Access-Control-Allow-Origin"] = origine\n'
                  '    return resp'},
 {'id': 'idempotence_put_patch',
  'term': 'Idempotence, PUT vs PATCH & Idempotency-Key',
  'category': 'Architecture Web',
  'level': "Cœur d'API",
  'short': "Propriété mathématique d'une opération qui produit le même état sur le serveur qu'elle soit "
           'exécutée 1 fois ou 10 fois.',
  'analogy': "Appuyer 5 fois sur le bouton d'appel d'un ascenseur au 3ème étage est **idempotent** "
             "(l'ascenseur vient une seule fois au 3ème). Appuyer 5 fois sur « Débiter 10 000 DZD » ne l'est "
             'pas !',
  'explanation': '- `GET`, `PUT` (remplacement intégral), `DELETE` sont **idempotents**.\n'
                 "- `PATCH` effectue une modification partielle d'un ou plusieurs champs.\n"
                 "- `POST` n'est **pas idempotent** par défaut : pour éviter les doublons de paiement en cas "
                 'de coupure réseau, le client envoie un en-tête `Idempotency-Key: <uuid>`.',
  'code_example': '# En-tête envoyé sur un POST critique :\n'
                  '# Idempotency-Key: tx-2026-0001\n'
                  'cle = request.headers.get("Idempotency-Key")'},
 {'id': 'pagination_filtering',
  'term': 'Pagination (page/limit), Filtrage & Tri',
  'category': 'Architecture Web',
  'level': 'Fondamental',
  'short': "Découpage d'une grande collection en tranches via les paramètres d'URL "
           '`?page=1&limit=20&tri=duree_jours`.',
  'analogy': "Consulter un catalogue de 50 000 articles par pages de 20 résultats au lieu d'imprimer les 50 "
             "000 lignes d'un seul bloc.",
  'explanation': 'Formule mathématique du découpage (Offset Pagination) :\n'
                 '`offset = (page - 1) * limit`\n'
                 "En Python : `resultats[offset : offset + limit]`. En SQL : `LIMIT ? OFFSET ?`. L'API "
                 'retourne une enveloppe contenant `meta` (`total_items`, `total_pages`, `has_next`) et '
                 '`data`.',
  'code_example': 'page = max(1, request.args.get("page", 1, type=int))\n'
                  'limit = min(100, request.args.get("limit", 10, type=int))\n'
                  'offset = (page - 1) * limit'},
 {'id': 'jinja2_forms_request_form',
  'term': 'Templates Jinja2 (render_template) & Formulaires HTML (request.form / request.files)',
  'category': 'Flask',
  'level': "Cœur d'API",
  'short': 'Séparation propre du HTML dans le dossier templates/ avec Jinja2 et traitement des formulaires '
           'Web envoyés en application/x-www-form-urlencoded ou multipart/form-data.',
  'analogy': "Jinja2 est le moule d'imprimerie (`.html`) dans lequel Flask injecte les variables Python (`{{ "
             'titre }}`) sans jamais mélanger le HTML dans le code Python. `request.form` est le guichet qui '
             "lit les bordereaux papier (`<form method='POST'>`), tandis que `request.get_json()` lit les "
             'colis électroniques JSON.',
  'explanation': '- **Zéro HTML en dur dans Python** : On place les fichiers `.html` dans `templates/` et on '
                 "appelle `render_template('page.html', formations=liste)`. Jinja2 échappe automatiquement "
                 '`{{ variable }}` contre les failles XSS et permet les boucles `{% for %}` et conditions '
                 '`{% if %}`.\n'
                 "- **Lecture d'un formulaire `<form method='POST'>`** : Le navigateur envoie les champs "
                 "munis d'un attribut `name='...'` sous le type `application/x-www-form-urlencoded`. Dans "
                 'Flask, **`request.get_json()` vaut `None`** : on lit les données avec '
                 "**`request.form.get('titre')`**.\n"
                 "- **Upload de fichiers (`enctype='multipart/form-data'`)** : Lus via "
                 "**`request.files.get('fichier')`** et sécurisés par `secure_filename()`.",
  'code_example': '@app.route("/formations", methods=["GET", "POST"])\n'
                  'def page_formations():\n'
                  '    if request.method == "POST":\n'
                  '        titre = request.form.get("titre", "").strip()  # Lecture du <input name="titre">\n'
                  '        duree = request.form.get("duree_jours", type=int)\n'
                  '    return render_template("formations.html", formations=FORMATIONS)'},
 {'id': 'path_variables_syntax',
  'term': "Variables d'URL : <variable> (Flask) vs :variable (Postman/Node) vs {variable} (OpenAPI)",
  'category': 'Flask',
  'level': 'Fondamental',
  'short': 'Les trois notations différentes utilisées selon les frameworks et outils pour représenter un '
           "paramètre dynamique dans le chemin d'une URL.",
  'analogy': "Trois façons d'écrire un champ à remplir sur un formulaire administratif selon le pays : `« "
             'Votre Nom : <___> »` (Flask), `« Votre Nom : :nom »` (Postman/Express), ou `« Votre Nom : '
             '{nom} »` (OpenAPI/FastAPI). Le principe est identique, seule la ponctuation change selon '
             "l'outil.",
  'explanation': "- **`<variable>` et `<int:id>` (Chevrons — Flask & Django)** : C'est la **seule syntaxe "
                 'valide dans `@app.route(...)` en Flask**. Elle permet de typer le paramètre (`<int:id>`, '
                 '`<float:prix>`, `<uuid:code>`, `<path:chemin>`).\n'
                 '- **`:variable` (Deux-points — Postman, Express.js/Node, Ruby on Rails, Go Gin)** : Dans '
                 '**Postman**, écrire `/api/formations/:id` active automatiquement la table *Path '
                 "Variables*. **Attention** : n'écrivez jamais `:id` dans une route Flask (Flask chercherait "
                 "le texte littéral `':id'`) !\n"
                 '- **`{variable}` (Accolades — OpenAPI 3.0 / Swagger, FastAPI, Spring Boot, f-strings '
                 'Python)** : Standard IETF RFC 6570.\n'
                 '- **Dans `curl` ou le navigateur** : On remplace toujours la variable par la **valeur '
                 'concrète** (`/api/formations/42`).',
  'code_example': '# 1. Dans le code serveur Python Flask (Chevrons <...>) :\n'
                  '@app.route("/api/v1/formations/<int:id>", methods=["GET"])\n'
                  'def lire_formation(id):\n'
                  '    return jsonify({"id": id})\n'
                  '\n'
                  '# 2. Dans Postman (Deux-points :variable) :\n'
                  '# GET http://127.0.0.1:5000/api/v1/formations/:id\n'
                  '\n'
                  '# 3. Dans OpenAPI 3.0 / FastAPI (Accolades {variable}) :\n'
                  '# GET /api/v1/formations/{id}\n'
                  '\n'
                  '# 4. Dans curl (Valeur réelle) :\n'
                  '# curl -i http://127.0.0.1:5000/api/v1/formations/42'},
 {'id': 'middlewares_hooks',
  'term': 'Middlewares (@before_request / @after_request) & X-Request-ID',
  'category': 'Flask',
  'level': 'Intermédiaire',
  'short': 'Fonctions exécutées automatiquement avant et après chaque route pour la journalisation, le '
           'chronométrage et la corrélation.',
  'analogy': "Le portique de sécurité à l'entrée d'un bâtiment qui enregistre l'heure d'arrivée de chaque "
             "visiteur (`before_request`) et l'heure de sortie (`after_request`).",
  'explanation': "Permet d'attacher un identifiant unique `X-Request-ID` (UUID) dans le contexte `flask.g`, "
                 "de mesurer la latence exacte en millisecondes (`X-Response-Time-Ms`) et d'injecter les "
                 'en-têtes de sécurité ou CORS sans dupliquer de code.',
  'code_example': '@app.before_request\n'
                  'def debut():\n'
                  '    g.start = time.perf_counter()\n'
                  '\n'
                  '@app.after_request\n'
                  'def fin(reponse):\n'
                  '    reponse.headers["X-Response-Time-Ms"] = str(round((time.perf_counter()-g.start)*1000, '
                  '2))\n'
                  '    return reponse'},
 {'id': 'wsgi_blueprints',
  'term': 'Blueprints, Application Factory & Serveur WSGI (Gunicorn)',
  'category': 'Flask',
  'level': "Cœur d'API",
  'short': "Organisation modulaire d'une API Flask (`Blueprint`) et déploiement multi-processus en "
           'production (`Gunicorn`).',
  'analogy': "Les `Blueprints` sont les départements spécialisés d'une entreprise, et `Gunicorn` est "
             "l'équipe de guichetiers parallèles (Workers) remplaçant le guichet unique d'entraînement "
             '(`app.run()`).',
  'explanation': "- **`Blueprint`** : Découpe l'API en fichiers par domaine (`/api/v1/formations`, "
                 '`/api/health`).\n'
                 "- **`app.test_client()`** : Exécute des tests automatisés d'API en mémoire sans serveur "
                 'réseau.\n'
                 '- **`Gunicorn` (WSGI)** : Serveur de production lançant plusieurs workers Python '
                 'parallèles derrière un Reverse Proxy Nginx.',
  'code_example': '# Commande de lancement en production (4 workers) :\n'
                  '# gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"'},
 {'id': 'apikey_vs_token',
  'term': 'Clé API (X-API-Key) vs Jeton Bearer (Token)',
  'category': 'Sécurité & Architecture API',
  'level': "Cœur d'API",
  'short': 'La Clé API identifie une application/machine (longue durée), tandis que le Bearer Token '
           'identifie un utilisateur connecté (courte durée).',
  'analogy': "La **Clé API** est comme le badge d'accès permanent d'une société de livraison partenaire. Le "
             "**Bearer Token** est le ticket nominatif temporaire d'un visiteur valable uniquement pour la "
             'séance.',
  'explanation': '- **`X-API-Key`** : Chaîne secrète fixe donnée à un serveur partenaire pour appeler votre '
                 'API.\n'
                 '- **`Authorization: Bearer <token>`** : Jeton généré dynamiquement après un login '
                 "(`/api/auth/token`), qui expire automatiquement et contient l'identité et le rôle de "
                 "l'utilisateur.",
  'code_example': '# Cas 1 : Clé machine-à-machine\n'
                  'cle = request.headers.get("X-API-Key")\n'
                  '\n'
                  '# Cas 2 : Jeton temporaire utilisateur\n'
                  'auth = request.headers.get("Authorization") # "Bearer <token>"'},
 {'id': 'variable',
  'term': 'Variable (Python)',
  'category': 'Bases Python',
  'level': 'Débutant Absolu',
  'short': "Emplacement nommé dans la mémoire de l'ordinateur permettant de conserver une valeur typée.",
  'analogy': 'Un dossier suspendu dans une armoire sur lequel vous collez une étiquette « Budget_2026 ». '
             'Vous pouvez consulter son contenu ou le mettre à jour à tout moment.',
  'explanation': "En programmation, on associe un nom (à gauche) à une valeur (à droite) avec l'opérateur "
                 "d'affectation `=`. Les 4 types primitifs compatibles JSON sont `str`, `int`/`float`, "
                 '`bool` (`True`/`False`) et `None`.',
  'code_example': 'nom_stagiaire = "Amine"\nage = 25\n# Utiliser nom_stagiaire renvoie désormais "Amine"'},
 {'id': 'dictionnaire',
  'term': 'Dictionnaire (dict)',
  'category': 'Bases Python',
  'level': 'Débutant Absolu',
  'short': 'Structure de données Python associant des clés uniques à des valeurs (`{clé: valeur}`).',
  'analogy': 'Une fiche signalétique structurée où chaque champ possède un intitulé précis (« Nom », « '
             'Prénom », « Ville ») associé à sa valeur.',
  'explanation': "Délimité par des accolades `{ }`. C'est la structure fondamentale pour le développement "
                 "d'APIs en Python car un dictionnaire se convertit directement en objet JSON. Utilisez "
                 "`.get('cle', defaut)` pour éviter `KeyError`.",
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
  'analogy': 'Un registre numéroté ligne par ligne (en informatique, la première ligne porte toujours le '
             'numéro 0).',
  'explanation': "Délimitée par des crochets `[ ]`. Lorsqu'une API renvoie une collection d'enregistrements "
                 '(ex. la liste des formations), elle renvoie généralement une liste contenant plusieurs '
                 'dictionnaires.',
  'code_example': 'formations = ["Python", "API REST", "Flask"]\n'
                  'print(formations[0])  # Affiche le 1er élément : Python'},
 {'id': 'fonction',
  'term': 'Fonction (def) & Décorateur (@)',
  'category': 'Bases Python',
  'level': 'Débutant Absolu',
  'short': "Bloc d'instructions réutilisable prenant des paramètres en entrée et retournant un résultat via "
           '`return`.',
  'analogy': 'Une unité de traitement : vous lui fournissez des matières premières (paramètres), elle '
             'applique une procédure interne, et restitue le produit fini (`return`).',
  'explanation': "Déclarée avec `def`. Un **décorateur (`@`)** est une fonction d'ordre supérieur qui "
                 'enveloppe une autre fonction pour lui ajouter un comportement (routage `@app.route`, '
                 'sécurité `@exiger_role`).',
  'code_example': '@app.route("/bonjour")\n'
                  'def dire_bonjour():\n'
                  '    return jsonify({"message": "Service opérationnel"}), 200'},
 {'id': 'api',
  'term': 'API REST & Modèle de Maturité de Richardson',
  'category': 'Architecture Web',
  'level': 'Fondamental',
  'short': 'Architecture normalisée où chaque URL identifie une ressource (nom au pluriel) manipulée par les '
           'verbes et statuts HTTP.',
  'analogy': "Un guichet de liaison standardisé : l'application cliente dépose un bordereau de demande normé "
             '(Requête HTTP) et reçoit un colis de données structuré (Réponse JSON) sans dépendre du langage '
             'interne du serveur.',
  'explanation': 'Niveaux de Richardson :\n'
                 '- Niveau 0 : 1 seule URL RPC/SOAP.\n'
                 '- Niveau 1 : URLs distinctes par ressource (`/api/formations/1`).\n'
                 '- Niveau 2 : Verbes HTTP (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`) + Codes de statut '
                 'précis (`200`, `201`, `401`, `403`, `422`, `429`).\n'
                 '- Niveau 3 : HATEOAS (liens hypermédias).',
  'code_example': '# Anti-pattern RPC : POST /api/creerFormation\n'
                  '# Standard REST    : POST /api/formations  -> 201 Created'},
 {'id': 'status_code',
  'term': 'Codes de Statut HTTP & RFC 7807 (Problem Details)',
  'category': 'Architecture Web',
  'level': 'Fondamental',
  'short': "Code numérique à 3 chiffres normalisé indiquant le résultat d'une requête, complété en cas "
           "d'erreur par un JSON RFC 7807.",
  'analogy': "Un code d'état standardisé sur un terminal bancaire : transaction acceptée (200), création "
             'validée (201), erreur de saisie (422), carte non reconnue (401), droits insuffisants (403), '
             'plafond dépassé (429).',
  'explanation': 'Classification essentielle :\n'
                 '- **2xx** : `200 OK`, `201 Created`, `204 No Content`\n'
                 '- **4xx** : `400 Bad Request` (JSON cassé), `401 Unauthorized` (non authentifié), `403 '
                 'Forbidden` (rôle insuffisant), `404 Not Found`, `405 Method Not Allowed`, `413 Payload Too '
                 'Large`, `422 Unprocessable Entity` (validation métier échouée), `429 Too Many Requests` '
                 '(Rate Limit)\n'
                 '- **5xx** : `500 Internal Server Error`, `502 Bad Gateway`, `503 Service Unavailable`, '
                 '`504 Gateway Timeout`',
  'code_example': 'return jsonify({\n'
                  '    "type": "https://api.isgp.dz/erreurs/validation",\n'
                  '    "title": "Erreur de validation",\n'
                  '    "status": 422,\n'
                  '    "errors": [{"champ": "duree_jours", "message": "Doit être >= 1"}]\n'
                  '}), 422'},
 {'id': 'sqlite',
  'term': 'SQLite, Transactions ACID & Requêtes Paramétrées (?)',
  'category': 'Données',
  'level': 'Intermédiaire',
  'short': 'Moteur de base de données relationnelle SQL transactionnel intégré à Python (`sqlite3`).',
  'analogy': 'Un registre comptable permanent écrit sur disque dur, protégé par des transactions atomiques '
             '(tout réussit avec `commit` ou tout est annulé avec `rollback`).',
  'explanation': "Sécurité fondamentale : lors d'une requête SQL, on n'insère jamais une variable "
                 'directement avec `+` ou `f"..."` (risque critique d\'**Injection SQL**). On utilise '
                 'toujours des marqueurs `?` (requêtes paramétrées).',
  'code_example': "# SÉCURISÉ (Requête paramétrée contre l'injection SQL) :\n"
                  'conn.execute("SELECT * FROM formations WHERE id = ?", (id,))'},
 {'id': 'sqlite_wal_pragmas',
  'term': 'SQLite Mode WAL (Write-Ahead Logging) & Pragmas de Production',
  'category': 'Données',
  'level': 'Avancé',
  'short': 'Mode de journalisation SQLite autorisant les lectures concurrentes pendant une écriture sans '
           "erreur 'database is locked'.",
  'analogy': "Au lieu de fermer toute la bibliothèque chaque fois qu'un bibliothécaire corrige une fiche "
             '(mode DELETE), celui-ci note ses ajouts dans un carnet annexe (-wal) pendant que tous les '
             'lecteurs continuent de consulter les rayons librement.',
  'explanation': '- **`PRAGMA journal_mode = WAL;`** : Sépare les écritures séquentielles (`.db-wal`) des '
                 'lectures sur le fichier principal.\n'
                 '- **`PRAGMA foreign_keys = ON;`** : Indispensable sur **chaque nouvelle connexion** car '
                 'SQLite désactive les contraintes `FOREIGN KEY` par défaut.\n'
                 "- **`PRAGMA busy_timeout = 5000;`** : Attend jusqu'à 5 s qu'un autre écrivain termine sa "
                 'micro-transaction avant de lever `OperationalError`.',
  'code_example': 'conn.execute("PRAGMA journal_mode = WAL;")\n'
                  'conn.execute("PRAGMA synchronous = NORMAL;")\n'
                  'conn.execute("PRAGMA foreign_keys = ON;")\n'
                  'conn.execute("PRAGMA busy_timeout = 5000;")'},
 {'id': 'sqlite_cursor_closing',
  'term': 'Curseur DB-API 2.0 (PEP 249) & Fermeture Déterministe (contextlib.closing)',
  'category': 'Données',
  'level': 'Intermédiaire',
  'short': "Itérateur d'exécution SQL dont la fermeture explicite libère immédiatement les verrous de pages "
           'de lecture et la mémoire C.',
  'analogy': "Un marque-page posé sur un registre ouvert : tant que le marque-page n'est pas retiré "
             "(`cur.close()`), l'archiviste considère que la page est encore en cours de consultation.",
  'explanation': '- **Piège classique** : `with conn:` en `sqlite3` valide (`COMMIT`) ou annule (`ROLLBACK`) '
                 'la transaction, mais **ne ferme ni le curseur ni la connexion**.\n'
                 '- **Bonne pratique** : Envelopper le curseur dans `with contextlib.closing(conn.cursor()) '
                 "as cur:` garantit l'appel à `cur.close()` même si une exception survient.",
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
  'short': 'Comparaison entre le pilote standard DB-API 2.0 inclus dans Python (`sqlite3`) et le wrapper bas '
           "niveau 1-pour-1 de l'API C SQLite (`apsw`).",
  'analogy': '`sqlite3` est une boîte de vitesses automatique universelle commune à toutes les voitures '
             "Python (PEP 249), tandis qu'`APSW` est un volant de Formule 1 branché en prise directe sur "
             'chaque capteur mécanique du moteur C de SQLite.',
  'explanation': '- **`sqlite3` (bibliothèque standard)** : Zéro dépendance externe, compatible DB-API 2.0, '
                 'supporté nativement par SQLAlchemy.\n'
                 '- **`apsw`** : Aucun `BEGIN` implicite caché, Streaming Blob I/O (`zeroblob` / '
                 "`blobopen`), tables virtuelles Python, Backup API à chaud et codes d'erreur étendus "
                 '(`SQLITE_BUSY_SNAPSHOT`).',
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
  'short': "Standard HTML5/HTTP permettant au serveur de pousser un flux continu d'événements texte vers le "
           'client sur une simple requête GET.',
  'analogy': "Un panneau d'affichage d'aéroport connecté : le voyageur ouvre une seule fois le canal "
             "d'écoute, et la tour de contrôle pousse chaque changement de porte en direct sans que le "
             'voyageur ait à redemander toutes les 2 secondes.',
  'explanation': '- **Format filaire** : Chaque message se compose de lignes `id:`, `event:`, `data:` '
                 'terminées par une **double fin de ligne `\\n\\n`**.\n'
                 "- **Résilience native** : L'API navigateur `EventSource` se reconnecte automatiquement en "
                 "cas de micro-coupure réseau en renvoyant l'en-tête `Last-Event-ID`.\n"
                 '- Idéal pour les flux de progression, tableaux de bord temps réel et streaming de réponses '
                 'LLM.',
  'code_example': 'from flask import Response, stream_with_context\n'
                  '\n'
                  '@app.get("/api/sse")\n'
                  'def flux_sse():\n'
                  '    def generateur():\n'
                  '        yield "id: 1\\nevent: progression\\ndata: {\\"pct\\": 50}\\n\\n"\n'
                  '    return Response(stream_with_context(generateur()), mimetype="text/event-stream")'},
 {'id': 'websocket_rfc6455',
  'term': 'WebSocket (RFC 6455 & HTTP 101 Switching Protocols)',
  'category': 'Temps Réel & Streaming',
  'level': 'Avancé',
  'short': 'Protocole de communication bidirectionnelle (Full-Duplex) persistante sur un unique socket TCP '
           'après une mise à niveau HTTP 101.',
  'analogy': 'Un appel téléphonique ouvert en continu : contrairement au courrier postal (HTTP '
             'requête/réponse) ou à la radio unidirectionnelle (SSE), les deux interlocuteurs peuvent parler '
             'et écouter simultanément à la milliseconde près.',
  'explanation': '- **Handshake HTTP -> WS** : Le client envoie `Upgrade: websocket` + `Connection: Upgrade` '
                 '+ `Sec-WebSocket-Key`, et le serveur répond `HTTP/1.1 101 Switching Protocols`.\n'
                 '- **Quand choisir WS plutôt que SSE ?** Messagerie collaborative bidirectionnelle, '
                 'curseurs multi-utilisateurs en direct, télémétrie IoT haute fréquence.',
  'code_example': '# En-têtes de mise à niveau (Upgrade Handshake RFC 6455) :\n'
                  '# Client  -> GET /ws HTTP/1.1 | Upgrade: websocket | Connection: Upgrade\n'
                  '# Serveur -> HTTP/1.1 101 Switching Protocols | Sec-WebSocket-Accept: ...'},
 {'id': 'multipart_magic_bytes',
  'term': 'Upload Multipart (RFC 7578), Magic Bytes & Défense 413 / 415',
  'category': 'Temps Réel & Streaming',
  'level': 'Intermédiaire',
  'short': 'Transport binaire natif de fichiers par frontières HTTP, sécurisé par plafond de taille (413), '
           "inspection des octets d'en-tête (Magic Bytes) et renommage UUID.",
  'analogy': "Un contrôle douanier aux rayons X : le douanier ne croit jamais l'étiquette collée sur la "
             "valise (`rapport.pdf`), il pèse d'abord le bagage (`413`), ouvre les premiers centimètres pour "
             'vérifier la nature réelle du contenu (`%PDF-` -> sinon `415`), puis lui attribue un numéro de '
             'scellé interne (`UUID4`).',
  'explanation': '- **Pourquoi pas Base64 dans du JSON ?** Base64 alourdit le fichier de `+33 %` et force le '
                 'chargement complet en RAM.\n'
                 '- **3 barrières de sécurité obligatoires** :\n'
                 "  1. Plafond d'octets strict (`413 Content Too Large`).\n"
                 '  2. Vérification des *Magic Bytes* réels (`%PDF-` = `25 50 44 46 2D`, PNG = `89 50 4E '
                 '47`).\n'
                 '  3. Jamais de chemin client brut (`../../etc/passwd` = *Path Traversal*) : nom interne '
                 '`uuid4().hex`.',
  'code_example': 'app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # Plafond 5 Mo -> 413\n'
                  'f = request.files["document"]\n'
                  'entete = f.stream.read(5); f.stream.seek(0)\n'
                  'if not entete.startswith(b"%PDF-"): abort(415)'},
 {'id': 'async_job_202_accepted',
  'term': "Tâches d'Arrière-Plan & Patron HTTP 202 Accepted + Location",
  'category': 'Architecture Web',
  'level': 'Intermédiaire',
  'short': "Découplage d'un traitement lourd (PDF, export CSV, e-mail, IA) en répondant immédiatement 202 "
           "Accepted avec une URL de suivi d'état.",
  'analogy': "Le bipper vibrant d'un restaurant : au lieu de bloquer toute la file d'attente devant la "
             'caisse pendant les 15 minutes de cuisson de votre plat, le caissier encaisse en 10 secondes et '
             'vous remet un jeton (`job_id`) qui indique quand la commande est prête.',
  'explanation': "- Évite l'épuisement des workers HTTP et les coupures `504 Gateway Timeout` des proxys "
                 'inverses (Nginx, Cloudflare).\n'
                 "- **Flux normalisé** : `POST /api/exports` -> crée l'entrée `EN_ATTENTE` -> répond `202 "
                 'Accepted` + `Location: /api/jobs/job-8a2f` -> le client consulte `GET /api/jobs/job-8a2f` '
                 "jusqu'à `TERMINE`.",
  'code_example': '# Réponse immédiate (< 10 ms) :\n'
                  '# HTTP/1.1 202 Accepted\n'
                  '# Location: /api/jobs/job-9f41c2\n'
                  '# {"job_id": "job-9f41c2", "statut": "EN_ATTENTE", "progression_pct": 0}'},
 {'id': 'etag_304_conditional_cache',
  'term': 'Cache HTTP Conditionnel : ETag, If-None-Match & 304 Not Modified',
  'category': 'Performance & Cache',
  'level': 'Intermédiaire',
  'short': "Empreinte de version d'une ressource permettant au serveur d'éviter de renvoyer le corps JSON si "
           'la copie du client est toujours à jour.',
  'analogy': "Demander au libraire : « J'ai déjà l'édition hash #a4f9 du catalogue, y en a-t-il une nouvelle "
             '? » — « Non, gardez la vôtre (`304 Not Modified`) ! », évitant de réimprimer et réexpédier 500 '
             'pages pour rien.',
  'explanation': '- **`Cache-Control: no-store`** : Obligatoire sur les données confidentielles (`/profil`, '
                 'jetons).\n'
                 "- **`ETag` + `If-None-Match` sur `GET`** : Si l'empreinte SHA-256 de la ressource n'a pas "
                 'changé, le serveur renvoie `304 Not Modified` avec **0 octet de Body**, économisant bande '
                 'passante mobile et sérialisation JSON.',
  'code_example': 'if request_if_none_match == current_etag:\n'
                  '    # 304 Not Modified : en-têtes seuls, ZÉRO corps JSON !\n'
                  '    return "", 304, {"ETag": current_etag}'},
 {'id': 'optimistic_locking_412',
  'term': 'Verrouillage Optimiste HTTP : If-Match & 412 Precondition Failed',
  'category': 'Performance & Cache',
  'level': 'Avancé',
  'short': "Protection contre l'écrasement silencieux d'écritures concurrentes (Lost Update) en exigeant "
           "l'ETag de la version lue lors d'un PUT/PATCH.",
  'analogy': 'Un système anti-collision sur un document partagé : si votre collègue a enregistré la version '
             'v2 pendant que vous modifiiez encore la version v1, le serveur refuse votre sauvegarde (`412`) '
             "et vous montre la v2 plutôt que d'effacer le travail de votre collègue en silence.",
  'explanation': '- Sans verrouillage optimiste, **le dernier qui clique gagne** (*Lost Update*).\n'
                 '- Avec `If-Match: "v1-..."` sur `PUT /api/catalogue/1`, le serveur vérifie atomiquement '
                 'que la ligne est toujours en `v1` (`UPDATE ... WHERE id = ? AND version = ?`). Si '
                 '`rowcount == 0`, il renvoie `412 Precondition Failed`.',
  'code_example': '# Client B tente de sauvegarder sur une version obsolète :\n'
                  '# PUT /api/catalogue/1\n'
                  '# If-Match: "v1-8b2c4d10"\n'
                  "# -> HTTP/1.1 412 Precondition Failed (conflit d'édition détecté !)"},
 {'id': 'x_request_id_correlation',
  'term': 'Traçabilité Distribuée : X-Request-ID & X-Process-Time-Ms',
  'category': 'Architecture Web',
  'level': 'Intermédiaire',
  'short': "Middleware transversal attachant un identifiant de corrélation unique et la durée d'exécution "
           'exacte à chaque requête HTTP.',
  'analogy': 'Le numéro de suivi Colissimo imprimé dès le dépôt du colis et scanné à chaque entrepôt : en '
             "cas d'incident, un seul code permet de reconstituer tout le parcours à la milliseconde près.",
  'explanation': "- Si le client ou l'API Gateway fournit déjà un `X-Request-ID` sain, le serveur le propage "
                 '; sinon il génère un `uuid4`.\n'
                 '- Combiné à `time.perf_counter()`, le middleware injecte `X-Request-ID` et '
                 '`X-Process-Time-Ms` dans les en-têtes de réponse et dans les journaux JSON.',
  'code_example': 'debut = time.perf_counter()\n'
                  'req_id = client_req_id or f"req-{uuid.uuid4().hex[:12]}"\n'
                  '# ... exécution de la route ...\n'
                  'duree_ms = (time.perf_counter() - debut) * 1000.0\n'
                  '# En-têtes : X-Request-ID: req-... | X-Process-Time-Ms: 1.84'}]
