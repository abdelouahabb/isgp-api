"""
Référentiel des Concepts Fondamentaux & Addendum Technique — Édition FLASK (69 fiches).
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
  'explanation': 'Une clé secrète inventée au clavier par un opérateur humain souffre '
                 "inévitablement d'un déficit d'entropie et demeure vulnérable aux attaques par "
                 "dictionnaire ou par table arc-en-ciel. La génération d'une `SECRET_KEY` Flask ou "
                 "d'une clé d'API partenaire doit donc toujours reposer sur une source d'aléa "
                 "cryptographique du système d'exploitation.\n"
                 '\n'
                 "En ligne de commande, l'utilitaire `openssl rand` puise directement dans le "
                 'générateur matériel et noyau (`/dev/urandom`) pour produire des séquences '
                 'imprévisibles encodées en hexadécimal (`-hex 32`, soit 64 caractères) ou en '
                 'Base64 (`-base64 32`). Au sein du code Python, le module standard `random` '
                 '(pseudo-aléatoire et prédictible) est formellement proscrit au profit du module '
                 "`secrets`, conçu spécifiquement pour l'émission de jetons et de clés "
                 'cryptographiques.',
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
  'explanation': 'Lors du calcul d\'une empreinte sous Linux, la commande `echo "secret"` ajoute '
                 'silencieusement un caractère de saut de ligne `\\n` en fin de flux, ce qui '
                 'modifie intégralement le condensat SHA-256 obtenu par rapport au calcul effectué '
                 "en Python. Pour garantir une correspondance exacte à l'octet près, il convient "
                 'd\'utiliser systématiquement `printf \'%s\' "secret"` (ou `echo -n`).\n'
                 '\n'
                 'Au-delà des chaînes de caractères, les commandes `sha256sum archive.tar.gz` et '
                 "`openssl dgst -sha256 archive.tar.gz` permettent de certifier qu'une sauvegarde "
                 "de base SQLite ou une archive de déploiement n'a subi aucune altération réseau "
                 'ni corruption disque.',
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
             'Flask.',
  'explanation': "Contrairement à un condensat SHA-256 classique que n'importe quel tiers peut "
                 'recalculer sur un message intercepté, le mécanisme **HMAC (`Hash-based Message '
                 'Authentication Code`)** mêle mathématiquement les octets bruts du corps HTTP à '
                 'une **clé secrète partagée (`-hmac "cle"`)** connue uniquement de l\'émetteur et '
                 'du serveur Flask.\n'
                 '\n'
                 "En phase de développement et d'audit, la commande `openssl dgst -sha256 -hmac` "
                 "constitue l'outil de référence pour forger en terminal un en-tête "
                 '`X-Webhook-Signature` authentique et éprouver la robustesse de vos routes de '
                 'réception Webhook avec `curl`.',
  'code_example': "# 1. Calculer la signature HMAC-SHA256 d'un corps JSON avec OpenSSL :\n"
                  'printf \'%s\' \'{"id":101,"statut":"paye"}\' | openssl dgst -sha256 -hmac '
                  '"whsec_isgp_2026"\n'
                  '\n'
                  "# 2. Stocker la signature dans une variable Bash et appeler l'API avec curl :\n"
                  'BODY=\'{"id":101,"statut":"paye"}\'\n'
                  'SIG=$(printf \'%s\' "$BODY" | openssl dgst -sha256 -hmac "whsec_isgp_2026" | '
                  "awk '{print $2}')\n"
                  'curl -i -X POST http://127.0.0.1:5000/api/webhooks -H "X-Webhook-Signature: '
                  'sha256=$SIG" -d "$BODY"'},
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
  'explanation': 'Il est fondamental de distinguer le hachage du chiffrement : les mots de passe '
                 "utilisateurs sont toujours *hachés* de manière irréversible car le serveur n'a "
                 "jamais besoin d'en connaître le texte clair, tandis que les archives SQLite "
                 '`.db`, les fichiers `.env` de secours et les secrets métier sont *chiffrés* afin '
                 "de pouvoir être restaurés à l'identique par les opérateurs habilités.\n"
                 '\n'
                 "Lors d'un chiffrement symétrique AES-256 avec OpenSSL, l'activation conjointe "
                 'des options `-salt` (sel aléatoire unique par archive), `-pbkdf2` (algorithme '
                 'standard de dérivation de clé) et `-iter 600000` (coût de calcul ralentissant '
                 'drastiquement la force brute) est impérative.',
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
             "/ `EdDSA`), mais tous les microservices de l'entreprise possèdent la Clé Publique "
             'pour vérifier les jetons sans jamais pouvoir en fabriquer de faux !',
  'explanation': 'Dans une architecture distribuée comptant une vingtaine de microservices, la '
                 'signature symétrique HMAC (`HS256`) impose de dupliquer la même `SECRET_KEY` sur '
                 "les vingt serveurs : la compromission d'un seul service secondaire permet alors "
                 "à l'attaquant de forger des jetons `admin` acceptés partout.\n"
                 '\n'
                 'La cryptographie asymétrique **RSA** ou à courbe elliptique **Ed25519** élimine '
                 'ce risque systémique en dissociant les rôles. Seul le serveur central '
                 "d'authentification détient la clé privée `private.pem` autorisée à signer les "
                 'jetons, tandis que les microservices consommateurs ne reçoivent que la clé '
                 'publique `public.pem`, suffisante pour vérifier mathématiquement les signatures '
                 'en lecture seule.',
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
  'explanation': 'En environnement de production exposé sur Internet, la terminaison HTTPS sur le '
                 "proxy inverse Nginx s'appuie sur un certificat X.509 délivré par une Autorité de "
                 "Certification publique reconnue telle que **Let's Encrypt** via l'agent "
                 'automatisé Certbot.\n'
                 '\n'
                 'Sur un poste de développement ou un réseau interne isolé, la commande `openssl '
                 "req -x509` permet d'engendrer en une seule étape une clé privée (`key.pem`) et "
                 'un certificat auto-signé (`cert.pem`). En exploitation, `openssl s_client` offre '
                 "en outre un diagnostic immédiat lorsqu'un appel API échoue pour cause de "
                 "certificat expiré ou de chaîne d'autorités intermédiaires incomplète.",
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
  'explanation': "L'encodage Base64 assure le transport fiable de données binaires ou structurées "
                 "au sein d'en-têtes HTTP strictement textuels : il intervient notamment dans le "
                 "schéma d'authentification **`Authorization: Basic <base64(user:pass)>`** ainsi "
                 "que dans la représentation des segments `Header` et `Payload` d'un jeton **JWT "
                 '(`Header.Payload.Signature`)**.\n'
                 '\n'
                 "Sous Linux, l'option `base64 -w 0` produit une chaîne continue sur une seule "
                 'ligne sans insertion de retours chariot tous les 76 caractères, tandis que '
                 "`base64 -d` restitue instantanément les octets d'origine. Rappelons que Base64 "
                 'est un simple codage réversible sans clé et ne procure aucune confidentialité.',
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
  'short': 'Hachage volontairement ralenti et salé destiné exclusivement à protéger les mots de '
           'passe humains stockés en base de données.',
  'analogy': 'Ajouter un labyrinthe de 600 000 portes (itérations) et un grain de sable unique '
             '(Salt) devant chaque mot de passe : un utilisateur légitime met 0,1 seconde à se '
             'connecter, mais un pirate qui tente 1 milliard de mots de passe mettra plusieurs '
             'siècles.',
  'explanation': 'Les fonctions de hachage généralistes comme SHA-256 sont optimisées pour la '
                 "vitesse pure, permettant à un processeur graphique moderne d'évaluer plusieurs "
                 "milliards de candidats par seconde lors d'une attaque hors ligne sur une table "
                 'utilisateurs compromise.\n'
                 '\n'
                 'Le stockage de mots de passe exige par conséquent une fonction de dérivation de '
                 'clé (**KDF — *Key Derivation Function***) volontairement coûteuse en temps CPU '
                 'et en mémoire vive, systématiquement associée à un sel aléatoire unique : '
                 '`scrypt` et `pbkdf2:sha256` (fournis nativement par `werkzeug.security`) ou '
                 '`openssl passwd -6` constituent le socle de sécurité obligatoire.',
  'code_example': '# 1. Générer un hash de mot de passe salé SHA-512 sous Linux :\n'
                  'openssl passwd -6 "MotDePasseStagiaire2026!"\n'
                  '\n'
                  '# 2. Générer et vérifier un hash Scrypt / PBKDF2 en Python (Werkzeug/Flask) :\n'
                  'python3 -c "from werkzeug.security import generate_password_hash, '
                  'check_password_hash; \\\n'
                  "h = generate_password_hash('Secret2026!'); print('Hash:', h); print('Valide:', "
                  'check_password_hash(h, \'Secret2026!\'))"'},
 {'id': 'linux_ports_ss_lsof',
  'term': 'Inspection des Ports & Processus Linux (ss -tulpn, lsof -i, kill)',
  'category': 'Linux & Réseau Prod',
  'level': 'Addendum Linux',
  'short': "Commandes système permettant d'identifier quel programme écoute sur un port TCP (ex. "
           ':5000) et de libérer un port bloqué.',
  'analogy': 'Le tableau de contrôle de la capitainerie du port : permet de voir instantanément '
             'quel navire (processus `PID`) est amarré au quai n°5000 lorsque Flask affiche '
             "l'erreur `Address already in use`.",
  'explanation': "Lorsqu'un serveur Flask ou Gunicorn refuse de démarrer en signalant `Address "
                 "already in use`, l'administrateur inspecte la table des sockets du noyau Linux à "
                 "l'aide de **`ss -tulpn`** (*Socket Statistics*, successeur moderne de "
                 '`netstat`), qui recense les ports TCP (`-t`) et UDP (`-u`) en écoute (`-l`) avec '
                 'résolution numérique (`-n`) et identification du processus propriétaire (`-p`), '
                 'ou cible directement un port via **`lsof -i :5000`**.\n'
                 '\n'
                 "Pour libérer le port, la discipline opérationnelle commande d'envoyer d'abord un "
                 "signal d'arrêt gracieux `kill -15 <PID>` (`SIGTERM`), qui laisse à Gunicorn et "
                 "Flask le temps d'achever les requêtes en cours et de refermer proprement SQLite, "
                 "avant d'envisager en dernier recours `kill -9 <PID>` (`SIGKILL`).",
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
  'short': 'Utilitaires de diagnostic permettant de vérifier la résolution de nom de domaine (DNS) '
           "et l'ouverture d'un port TCP distant.",
  'analogy': "Vérifier d'abord que l'adresse figure bien dans l'annuaire (`dig`), puis vérifier "
             'que la route est praticable (`ping`) et que le guichet est ouvert (`nc -zv`) avant '
             "d'accuser le code Python.",
  'explanation': "Le diagnostic méthodique d'une panne de connectivité API procède toujours du bas "
                 "vers le haut de la pile réseau. La commande **`ip -br a`** vérifie d'abord la "
                 'configuration des interfaces locales du serveur, puis **`dig +short '
                 "domaine.dz`** confirme que la résolution DNS renvoie bien l'adresse IP "
                 'attendue.\n'
                 '\n'
                 'Enfin, **`nc -zv HOTE PORT`** (*Netcat*) éprouve isolément la poignée de main '
                 'TCP en trois temps (*3-way handshake*) vers le port cible, permettant de savoir '
                 "immédiatement si un pare-feu bloque l'accès à Gunicorn (`:8000`) ou PostgreSQL "
                 "(`:5432`) avant même d'analyser la couche HTTP.",
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
  'short': "Processeur JSON en ligne de commande permettant d'indenter, coloriser, extraire et "
           'filtrer les réponses de `curl`.',
  'analogy': "Un scalpel chirurgical pour réponses d'API : au lieu de lire un bloc compact de 5 "
             '000 caractères JSON renvoyé par `curl`, `jq` extrait en une fraction de seconde '
             'uniquement les champs qui vous intéressent.',
  'explanation': 'Sur tout serveur disposant de Python, la commande intégrée **`python3 -m '
                 'json.tool`** valide la syntaxe et indente proprement les réponses JSON '
                 "retournées par `curl` sans nécessiter l'installation d'aucun paquet tiers.\n"
                 '\n'
                 "Pour l'exploitation avancée et les scripts d'automatisation, le processeur "
                 "**`jq`** offre un véritable langage de requête en pipeline capable d'extraire un "
                 "compteur précis (`.meta.total_items`), d'itérer sur une collection (`.data[]`) "
                 'ou de filtrer dynamiquement les objets selon un prédicat métier '
                 '(`select(.duree_jours >= 5)`).',
  'code_example': '# 1. Indenter une réponse curl avec Python (sans installer jq) :\n'
                  'curl -s http://127.0.0.1:5000/api/sandbox/formations | python3 -m json.tool\n'
                  '\n'
                  '# 2. Extraire uniquement les titres des formations avec jq :\n'
                  "curl -s http://127.0.0.1:5000/api/sandbox/formations | jq '.data[].titre'\n"
                  '\n'
                  '# 3. Filtrer les formations de 5 jours ou plus avec jq :\n'
                  "curl -s http://127.0.0.1:5000/api/sandbox/formations | jq '.data[] | "
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
  'explanation': "L'investigation en direct d'un incident de production s'appuie sur le pipeline "
                 "textuel POSIX appliqué aux journaux d'accès et d'erreurs. La commande **`tail -f "
                 'fichier.log`** diffuse en continu chaque nouvelle requête traitée, tandis que '
                 '**`grep`** isole instantanément les statuts critiques (`" 500 "`, `" 401 "`) ou '
                 "reconstitue le parcours complet d'un identifiant de corrélation `X-Request-ID`.\n"
                 '\n'
                 "En combinant **`awk`**, **`sort`** et **`uniq -c`**, l'ingénieur agrège en "
                 'quelques secondes des centaines de milliers de lignes Nginx ou Gunicorn pour '
                 'identifier les dix adresses IP les plus consommatrices et détecter un abus de '
                 'débit ou un balayage automatisé.',
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
  'explanation': "L'application des permissions restrictives **`chmod 600` (`-rw-------`)** "
                 'garantit que seul le compte système propriétaire peut lire et modifier un '
                 "fichier sensible, retirant tout droit d'accès (`0`) aux autres utilisateurs "
                 'locaux du serveur : cette mesure est impérative pour protéger les fichiers '
                 '`.env`, les clés privées TLS `private.pem` et les clés SSH.\n'
                 '\n'
                 'Parallèlement, la directive shell **`export`** injecte les secrets et paramètres '
                 "de configuration dans l'environnement mémoire du processus enfant Gunicorn ou "
                 'Flask, où Python les récupère proprement via `os.environ.get(...)` sans jamais '
                 'les inscrire dans le code source versionné.',
  'code_example': '# 1. Restreindre la lecture du fichier .env et de la clé privée au seul '
                  'propriétaire :\n'
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
  'short': 'Architecture standard permettant de faire tourner une API Flask 24h/24 en tâche de '
           'fond avec redémarrage automatique et HTTPS.',
  'analogy': 'Transformer un moteur posé sur un établi (`python app.py`) en une centrale '
             'électrique automatisée (`systemd` + `Gunicorn`) protégée par un poste de garde '
             'blindé (`Nginx`).',
  'explanation': "Une API de production ne s'exécute jamais dans une session interactive fragile "
                 "susceptible de s'interrompre à la fermeture du terminal SSH. Le gestionnaire de "
                 'services **`systemd`** (`/etc/systemd/system/isgp-api.service`) supervise le '
                 "démon Gunicorn en arrière-plan, démarre l'application automatiquement au "
                 'démarrage machine et la ressuscite en deux secondes en cas de défaillance grâce '
                 'à la directive `Restart=always`.\n'
                 '\n'
                 'En frontal, le serveur **`Nginx`** assure la terminaison TLS sur les ports '
                 'publics `80` et `443`, absorbe les connexions lentes des clients distants et '
                 'achemine les requêtes assainies vers le socket local des workers Gunicorn '
                 '(`proxy_pass http://127.0.0.1:8000`).',
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
  'short': "Identifiant normalisé IANA (type/sous-type) décrivant le format exact d'un flux "
           "d'octets HTTP et pilotant la négociation de contenu dans Flask.",
  'analogy': "L'étiquette réglementaire collée sur un conteneur maritime : 'Liquide', 'Poudre' ou "
             "'Gaz'. Sans cette étiquette (Content-Type), le destinataire ne sait pas avec quel "
             'outil ouvrir le conteneur.',
  'explanation': 'La négociation de contenu HTTP repose sur deux en-têtes complémentaires. '
                 '**`Content-Type`** déclare la nature exacte des octets présents dans le corps du '
                 'message courant (par exemple `application/json; charset=utf-8`), dont Flask '
                 "extrait le type pur sans paramètres via `request.mimetype`. À l'inverse, "
                 "**`Accept`** est émis par le client pour indiquer les représentations qu'il "
                 'souhaite recevoir en réponse (`request.accept_mimetypes.best_match(...)`).\n'
                 '\n'
                 "Lorsqu'un appelant soumet un corps encodé dans un format que la route refuse de "
                 'traiter — tel du texte brut là où du JSON est requis —, la norme HTTP prescrit '
                 'de rejeter la requête avec le statut explicite **`415 Unsupported Media Type`**.',
  'code_example': '# Inspecter le type MIME entrant et rejeter proprement en 415 :\n'
                  'if request.mimetype not in ("application/json", '
                  '"application/x-www-form-urlencoded"):\n'
                  '    return jsonify({"erreur": f"Type MIME {request.mimetype} non supporté"}), '
                  '415'},
 {'id': 'mime_json_vs_form_vs_multipart',
  'term': "Types MIME d'Entrée (POST) : application/json vs x-www-form-urlencoded vs "
          'multipart/form-data',
  'category': 'Types MIME & Flask',
  'level': "Cœur d'API",
  'short': 'Les trois grands types MIME utilisés pour envoyer des données à un serveur Flask lors '
           "d'une requête POST ou PUT.",
  'analogy': "Trois façons de transmettre un dossier à l'administration : un fichier informatique "
             'structuré (`application/json`), un coupon-réponse papier '
             '(`application/x-www-form-urlencoded`), ou une pochette cartonnée contenant à la fois '
             'le coupon papier et des pièces jointes PDF (`multipart/form-data`).',
  'explanation': 'Flask aiguille le décodage du corps HTTP vers trois attributs distincts selon le '
                 'type MIME entrant. Une charge **`application/json`** émise par `fetch()`, une '
                 "application mobile ou `curl -H 'Content-Type: application/json'` est "
                 'désérialisée en structures Python par **`request.get_json(silent=True)`**.\n'
                 '\n'
                 "Un formulaire Web classique `<form method='POST'>` transmet ses champs en "
                 '**`application/x-www-form-urlencoded`**, lus exclusivement dans '
                 '**`request.form`** (tandis que `request.get_json()` renvoie alors `None`). '
                 "Enfin, un formulaire d'envoi de pièces jointes en **`multipart/form-data`** "
                 'répartit les champs textuels dans **`request.form`** et les flux binaires '
                 'téléversés dans **`request.files`**.',
  'code_example': 'if request.mimetype == "application/json":\n'
                  '    data = request.get_json(silent=True) or {}\n'
                  'elif request.mimetype in ("application/x-www-form-urlencoded", '
                  '"multipart/form-data"):\n'
                  '    data = request.form\n'
                  '    fichier = request.files.get("document_pdf")'},
 {'id': 'mime_response_csv_xml_sse',
  'term': 'Émettre des Types MIME Personnalisés (Response : CSV, XML, Problem+JSON, SSE)',
  'category': 'Types MIME & Flask',
  'level': "Cœur d'API",
  'short': "Utilisation de l'objet Response(corps, status=..., mimetype=...) dans Flask pour "
           'retourner tout format autre que HTML ou JSON standard.',
  'analogy': "Si `render_template()` est l'imprimante de brochures HTML et `jsonify()` l'emballeur "
             "de colis JSON, `Response(..., mimetype=...)` est l'atelier sur mesure capable "
             "d'expédier des feuilles Excel CSV, des actes XML ou un flux continu.",
  'explanation': 'Bien que `application/json` domine les échanges REST contemporains, un backend '
                 "Flask industriel produit fréquemment d'autres types MIME normalisés selon "
                 "l'usage métier. Le type **`text/csv`** couplé à l'en-tête `Content-Disposition: "
                 'attachment; filename="export.csv"` alimente directement les tableurs comptables, '
                 'tandis que **`application/problem+json`** identifie officiellement les rapports '
                 "d'erreur structurés conformes au standard **RFC 7807**.\n"
                 '\n'
                 "Pour l'interopérabilité avec les progiciels historiques, Flask émet des "
                 'enveloppes SOAP sous **`application/xml`**, et pour la diffusion continue de '
                 "notifications en temps réel vers le navigateur, il s'appuie sur un générateur "
                 'Python retournant un flux **`text/event-stream`** (**Server-Sent Events**).',
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
  'term': 'Fichiers Binaires (send_file : application/pdf, image/png) & X-Content-Type-Options: '
          'nosniff',
  'category': 'Types MIME & Flask',
  'level': 'Intermédiaire',
  'short': "Transmission de fichiers binaires avec send_file(), contrôle de l'ouverture navigateur "
           '(inline vs attachment) et protection contre le MIME Sniffing.',
  'analogy': 'Envoyer un document PDF soit sous verre pour être lu sur place dans le navigateur '
             '(`inline`), soit dans une enveloppe scellée que le navigateur enregistre directement '
             'dans le dossier Téléchargements (`attachment`).',
  'explanation': "L'utilitaire Flask **`send_file(chemin_ou_bytesio, mimetype='application/pdf', "
                 'as_attachment=...)`** gouverne la restitution de documents binaires au '
                 'navigateur. Lorsque `as_attachment=False` (`Content-Disposition: inline`), le '
                 "client affiche directement le document PDF ou l'image au sein de l'onglet actif "
                 "; lorsque `as_attachment=True` est associé à `download_name='facture.pdf'` "
                 "(`Content-Disposition: attachment`), le navigateur déclenche l'enregistrement "
                 'sur disque.\n'
                 '\n'
                 "Toute route servant des fichiers doit impérativement joindre l'en-tête défensif "
                 '**`X-Content-Type-Options: nosniff`**, qui interdit au navigateur de deviner '
                 "heuristiquement le format réel et empêche ainsi qu'un fichier téléversé déguisé "
                 'ne soit exécuté comme une page HTML ou un script JavaScript.',
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
  'analogy': 'Construire une maison avec un compteur électrique prévu pour un 2e étage (/api/v1) : '
             "tant qu'on ajoute des meubles dans les pièces existantes (nouveaux champs JSON "
             "optionnels), on reste au 1er étage pendant 10 ans. Mais le jour où l'on doit refaire "
             'les fondations (Breaking Change), la réservation du 2e étage (/api/v2) évite de '
             "démolir le 1er pendant qu'il est habité.",
  'explanation': 'En vertu du principe de robustesse de Postel (*Tolerant Reader*), enrichir une '
                 "réponse JSON d'un attribut supplémentaire, publier une nouvelle route ou "
                 'introduire un paramètre de requête facultatif ne perturbe aucun client existant '
                 ": plus de 90 % de la vie évolutive d'un service s'accomplit donc paisiblement "
                 "pendant cinq à dix ans à l'intérieur du même préfixe `/api/v1`.\n"
                 '\n'
                 "Inscrire explicitement `/api/v1` dans l'URI dès le premier jour demeure "
                 'néanmoins indispensable : si cinquante mille terminaux mobiles compilés '
                 'appellent une racine non versionnée `/api/formations`, la moindre refonte '
                 'structurelle future deviendra impossible à isoler sans briser instantanément le '
                 'parc installé.',
  'code_example': '# Coexistence de /api/v1 et /api/v2 via deux Blueprints Flask :\n'
                  'bp_v1 = Blueprint("v1", __name__, url_prefix="/api/v1/formations")\n'
                  'bp_v2 = Blueprint("v2", __name__, url_prefix="/api/v2/formations")\n'
                  'app.register_blueprint(bp_v1)\n'
                  'app.register_blueprint(bp_v2)'},
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
  'explanation': "La gouvernance d'un contrat d'API distingue rigoureusement les évolutions "
                 'rétrocompatibles des ruptures de contrat. Une évolution **Non-Breaking** — ajout '
                 "d'une propriété JSON en sortie, ouverture d'un nouvel endpoint tel que `GET "
                 "/api/v1/certificats` ou prise en charge d'un filtre optionnel `?lang=fr` — se "
                 'déploie directement dans la version majeure courante `v1`.\n'
                 '\n'
                 "À l'inverse, constitue un **Breaking Change** toute modification susceptible de "
                 "faire échouer le code d'un consommateur existant : renommer ou supprimer une clé "
                 "JSON (`intitule` remplacé par `titre`), muter le type d'une valeur scalaire en "
                 'objet imbriqué, ou exiger soudainement un nouveau champ obligatoire en entrée '
                 "`POST`. Une telle rupture impose la publication parallèle d'une branche "
                 '`/api/v2`.',
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
  'explanation': "L'extinction d'une ancienne version d'API obéit à un protocole d'avertissement "
                 "normalisé par l'IETF afin d'accorder aux équipes clientes un préavis de "
                 'migration mesurable. Pendant la période de coexistence, chaque réponse de la '
                 '`v1` injecte les en-têtes **`Deprecation: true`**, **`Sunset: Thu, 31 Dec 2026 '
                 "23:59:59 GMT`** (**RFC 8594**) fixant l'échéance d'arrêt, ainsi que **`Link: "
                 '</api/v2/formations>; rel="successor-version"`** désignant la cible de '
                 'remplacement.\n'
                 '\n'
                 "Une fois l'échéance `Sunset` échue et la branche décommissionnée, le serveur ne "
                 'répond pas par un `404` ambigu, mais par le statut sémantique **`410 Gone`**, '
                 'qui atteste explicitement que la ressource a bien existé par le passé mais a été '
                 'définitivement retirée du service.',
  'code_example': '@formations_v1_bp.after_request\n'
                  'def avertir_depreciation_v1(response):\n'
                  '    response.headers["Deprecation"] = "true"\n'
                  '    response.headers["Sunset"] = "Thu, 31 Dec 2026 23:59:59 GMT"\n'
                  '    response.headers["Link"] = \'</api/v2/formations>; '
                  'rel="successor-version"\'\n'
                  '    return response'},
 {'id': 'api_envelope_pagination_cursor_offset',
  'term': 'Enveloppe JSON (meta / data / links) & Pagination (Offset/Limit vs Cursor)',
  'category': 'Architecture Web',
  'level': 'Intermédiaire',
  'short': "Structuration racine d'une réponse JSON de collection pour permettre l'évolution sans "
           'Breaking Change et la pagination haute performance.',
  'analogy': "Ne jamais expédier des feuilles volantes sans chemise cartonnée : l'objet enveloppe "
             '`{"meta": ..., "data": [...]}` est la chemise sur laquelle on peut inscrire le '
             'numéro de page et le total sans toucher aux feuilles `data`.',
  'explanation': "Retourner un tableau JSON nu `[...]` à la racine d'une route de collection "
                 "enferme l'API dans une impasse évolutive, car il devient impossible d'y "
                 'adjoindre ultérieurement des compteurs ou des liens de navigation sans briser le '
                 'type racine attendu par les désérialiseurs clients. Toute collection '
                 'professionnelle encapsule donc ses résultats dans une enveloppe stable `{"meta": '
                 '{...}, "data": [...]}`.\n'
                 '\n'
                 "Pour les volumes modérés dotés d'une navigation par numéros de pages, la "
                 'pagination **`Offset/Limit`** (`?page=2&per_page=20`, traduite en `LIMIT 20 '
                 'OFFSET 20`) offre une ergonomie directe. Sur des tables comptant plusieurs '
                 "millions d'enregistrements ou des flux temps réel à forte cadence d'insertion, "
                 'la pagination par **Curseur** (`?after_id=1042&limit=20`, exécutée par `WHERE id '
                 "> 1042 ORDER BY id ASC LIMIT 20`) garantit un temps d'accès constant O(1) par "
                 "exploitation directe de l'index primaire SQL.",
  'code_example': 'return jsonify({\n'
                  '    "meta": {"version": "v2", "page": 1, "per_page": 20, "total_items": 145},\n'
                  '    "data": formations,\n'
                  '    "links": {"self": "/api/v2/formations?page=1", "next": '
                  '"/api/v2/formations?page=2"}\n'
                  '}), 200'},
 {'id': 'swagger_openapi_3',
  'term': 'Swagger UI (/api/docs), Swagger Editor & Spécification OpenAPI 3.0 (OAS)',
  'category': 'Architecture Web',
  'level': "Cœur d'API",
  'short': "Norme mondiale de contrat d'API (OpenAPI 3.0 JSON/YAML) et portail Web interactif "
           '(Swagger UI) permettant de documenter et tester une API dans le navigateur.',
  'analogy': "OpenAPI 3.0 est le plan d'architecte coté et normalisé de l'immeuble "
             '(`openapi.json`), tandis que Swagger UI est la visite virtuelle interactive générée '
             'automatiquement à partir de ce plan (boutons « Authorize » et « Try it out »).',
  'explanation': 'La **Spécification OpenAPI (OAS 3.0 / 3.1)**, gouvernée par la Linux Foundation, '
                 "formalise dans un document déclaratif JSON ou YAML l'intégralité du contrat d'un "
                 'service REST : métadonnées `info`, environnements `servers`, routes `paths` à '
                 'paramètres entre accolades `{id}`, modèles réutilisables `components.schemas` '
                 "(`$ref`) et mécanismes d'authentification `components.securitySchemes` "
                 '(`BearerAuth`, `ApiKeyAuth`).\n'
                 '\n'
                 'À partir de ce contrat `/api/openapi.json`, le portail **Swagger UI '
                 '(`/api/docs`)** génère automatiquement une console Web interactive munie du '
                 "cadenas **Authorize** et du bouton d'essai **Try it out**. Ce même fichier "
                 "s'importe en un clic dans Postman, Insomnia ou `openapi-generator` pour produire "
                 'des SDKs clients typés.',
  'code_example': '# Route Flask exposant le contrat OpenAPI 3.0.3 :\n'
                  '@app.route("/api/openapi.json")\n'
                  'def spec():\n'
                  '    return jsonify({"openapi": "3.0.3", "info": {"title": "API ISGP", '
                  '"version": "1.0.0"}, "paths": {...}})'},
 {'id': 'curl_postman_httpie',
  'term': 'curl, Postman, HTTPie & REST Client (.http)',
  'category': 'Architecture Web',
  'level': 'Fondamental',
  'short': 'Outils de test et de diagnostic permettant de forger des requêtes HTTP (GET, POST, '
           'PUT, PATCH, DELETE, Headers) sans navigateur.',
  'analogy': "Un multimètre d'ingénieur réseau : là où un navigateur classique ne sait envoyer que "
             'des requêtes GET simples, curl et Postman permettent de contrôler chaque en-tête, '
             'chaque méthode et chaque octet JSON.',
  'explanation': "Tester une API REST ne peut se limiter à la barre d'adresse d'un navigateur, qui "
                 "n'émet que des requêtes `GET` dépourvues d'en-têtes personnalisés et de corps "
                 'JSON. Omniprésent sur chaque serveur Linux et conteneur Docker, **`curl`** '
                 "constitue l'instrument universel de diagnostic en ligne de commande (`-i` pour "
                 'inspecter les en-têtes, `-v` pour la trace complète, `-X` pour le verbe, `-H` '
                 'pour un en-tête et `-d` pour la charge utile).\n'
                 '\n'
                 'Au quotidien sur le poste de développement, cet outil est avantageusement '
                 'complété par les clients graphiques tels que **Postman**, **Bruno** ou '
                 '**Insomnia** pour organiser des collections partagées, ainsi que par **HTTPie '
                 "(`http`)** et l'extension **REST Client (`.http`)** intégrée à l'éditeur de "
                 'code.',
  'code_example': 'curl -i -X POST "http://127.0.0.1:5000/api/sandbox/formations" \\\n'
                  '  -H "Content-Type: application/json" \\\n'
                  '  -H "X-API-Key: isgp-secret-2026" \\\n'
                  '  -d \'{"titre": "API Flask", "duree_jours": 5}\''},
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
  'explanation': "En l'absence de régulation de débit, une simple boucle infinie accidentelle chez "
                 'un partenaire ou une attaque par force brute suffit à saturer les workers '
                 'Gunicorn et à provoquer un déni de service généralisé. Le mécanisme de **Rate '
                 'Limiting** comptabilise les appels par adresse IP ou par identité cliente au '
                 "moyen d'une fenêtre glissante ou d'un seau à jetons (*Token Bucket*).\n"
                 '\n'
                 "Dès que le plafond autorisé est franchi, l'API interrompt le traitement métier "
                 'et retourne immédiatement le statut normalisé **`429 Too Many Requests`**, '
                 'enrichi des en-têtes `X-RateLimit-Remaining: 0` et `Retry-After` indiquant au '
                 'client le délai exact en secondes avant toute nouvelle tentative.',
  'code_example': '# Si le client dépasse 3 requêtes en 20 secondes :\n'
                  'return jsonify({\n'
                  '    "erreur": "Quota dépassé (Rate Limit)",\n'
                  '    "reessayer_dans_secondes": 20\n'
                  '}), 429'},
 {'id': 'token_bearer',
  'term': "Token / Bearer Token & JWT (Jeton d'Accès Signé)",
  'category': 'Sécurité & Architecture API',
  'level': "Cœur d'API",
  'short': 'Un laissez-passer numérique temporaire et signé (HMAC), remis au client après '
           'connexion pour prouver son identité à chaque requête.',
  'analogy': "La carte magnétique d'une chambre d'hôtel : vous montrez votre pièce d'identité une "
             'seule fois à la réception (`/api/auth/token`), on vous remet une carte valable 24h '
             '(le Token). Ensuite, vous présentez simplement cette carte devant chaque porte '
             '(`Authorization: Bearer <token>`).',
  'explanation': "Un jeton porteur transmis dans l'en-tête `Authorization: Bearer <token>` (qu'il "
                 'suive le standard JWT ou le sérialiseur `itsdangerous` de Flask) permet au '
                 "serveur de vérifier l'identité de l'appelant sans interroger de table de "
                 'sessions en base à chaque requête.\n'
                 '\n'
                 "Une précaution de sécurité essentielle s'impose toutefois : la charge utile "
                 "(`Payload`) d'un tel jeton est simplement encodée en Base64URL — donc lisible en "
                 "clair par quiconque l'intercepte — et **signée mathématiquement** avec la "
                 '`SECRET_KEY` du serveur pour la rendre infalsifiable. Aucun mot de passe ni '
                 'donnée secrète ne doit jamais y figurer.',
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
  'short': 'AuthN vérifie QUI vous êtes (échec = 401 Unauthorized) ; AuthZ vérifie QUELS sont vos '
           'droits sur la ressource (échec = 403 Forbidden).',
  'analogy': "Le passeport contrôlé à l'entrée de l'aéroport est l'Authentification (`AuthN` -> "
             "`401` si absent). La carte d'accès réservée aux pilotes pour entrer dans le cockpit "
             "est l'Autorisation (`AuthZ` -> `403` si vous êtes un simple passager).",
  'explanation': "Une architecture de sécurité d'API sépare rigoureusement l'**Authentification "
                 "(`AuthN`)**, qui établit l'identité de l'appelant par jeton Bearer ou clé "
                 "`X-API-Key` (échec sanctionné par `401 Unauthorized`), de l'**Autorisation "
                 "(`AuthZ`)**, qui évalue ses droits d'accès sur l'opération demandée (échec "
                 'sanctionné par `403 Forbidden`).\n'
                 '\n'
                 "En production, le contrôle d'autorisation combine trois garde-fous "
                 'complémentaires : le modèle **RBAC** distinguant les profils macroscopiques '
                 '(`stagiaire` face à `admin`), les **Scopes OAuth2** validant les permissions '
                 'granulaires portées par le jeton (`formations:read`, `audit:admin`), et la '
                 "vérification systématique de **propriété de l'objet** (`dossier.proprietaire == "
                 'user.sub`) indispensable pour parer la faille critique **BOLA** (*OWASP API '
                 'Security #1*).',
  'code_example': 'if not token_valide:\n'
                  '    return jsonify({"etape": "AuthN", "erreur": "Non authentifié"}), 401\n'
                  'if user["role"] != "admin" or "audit:admin" not in user["scopes"]:\n'
                  '    return jsonify({"etape": "AuthZ", "erreur": "Droits insuffisants"}), 403'},
 {'id': 'secret_env',
  'term': "Secrets & Variables d'Environnement (.env / os.environ)",
  'category': 'Sécurité & Architecture API',
  'level': "Cœur d'API",
  'short': 'Pratique fondamentale consistant à stocker les mots de passe, clés de signature et '
           "clés d'API hors du code source Python.",
  'analogy': 'Vous ne gravez jamais le code de votre coffre-fort sur la façade extérieure de votre '
             "maison. Vous le gardez dans une enveloppe scellée à l'intérieur du coffre de la "
             "direction (les variables d'environnement du serveur).",
  'explanation': 'La règle cardinale de la gestion des secrets applicatifs interdit formellement '
                 "d'inscrire une clé cryptographique, un mot de passe SQL ou un jeton partenaire "
                 'en clair dans un fichier source Python tel que `app.py`, sous peine de '
                 'divulgation irréversible dès le premier partage du dépôt Git.\n'
                 '\n'
                 'Conformément à la méthodologie industrielle *Twelve-Factor App*, tous les '
                 "secrets résident exclusivement dans les variables d'environnement du système "
                 'hôte (ou un gestionnaire de coffre-fort) et sont lus dynamiquement au démarrage '
                 "du worker Flask au moyen de `os.environ.get('API_SECRET_KEY')`.",
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
  'explanation': "La signature **HMAC-SHA256** constitue la pierre angulaire de l'intégrité des "
                 "messages dans un écosystème Web : elle scelle aussi bien les jetons d'accès émis "
                 "par le serveur que les notifications **Webhooks** entrantes accompagnées d'un "
                 'en-tête `X-Webhook-Signature: sha256=...`.\n'
                 '\n'
                 "Lors de la vérification côté Flask, l'opérateur d'égalité standard `==` est "
                 "banni car il s'arrête dès le premier octet divergent, offrant un canal "
                 'auxiliaire mesurable ; on emploie exclusivement `hmac.compare_digest(recue, '
                 "calculee)` qui s'exécute en temps constant afin de neutraliser les attaques "
                 'temporelles (*Timing Attacks*).',
  'code_example': 'import hmac, hashlib\n'
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
             '(tout script XSS peut les voler). Un Cookie `HttpOnly; Secure; SameSite=Strict` '
             'place les clés dans un coffre blindé du navigateur que seul le serveur peut ouvrir.',
  'explanation': "Le cycle de vie d'un cookie HTTP s'articule entre l'en-tête serveur `Set-Cookie` "
                 '(`response.set_cookie(...)`), la retransmission automatique par le navigateur '
                 'dans `Cookie` (`request.cookies.get(...)`) et sa révocation explicite par '
                 '`response.delete_cookie(...)` qui force `Max-Age=0`.\n'
                 '\n'
                 "Tout cookie véhiculant un identifiant de session ou un jeton d'authentification "
                 'doit impérativement cumuler trois attributs défensifs : **`HttpOnly`** '
                 '(`httponly=True`) qui le dissimule à `document.cookie` pour parer le vol par '
                 'faille XSS, **`Secure`** (`secure=True`) qui restreint son transport aux seuls '
                 'canaux chiffrés HTTPS/TLS, et **`SameSite=Strict` ou `Lax`** qui bloque son '
                 'envoi lors de requêtes inter-sites forgées afin de neutraliser les attaques '
                 'CSRF.',
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
  'analogy': "Un cookie ordinaire (`set_cookie('theme', 'sombre')`) est écrit au crayon à papier : "
             'le client peut le gommer et le modifier. Le cookie `session` est scellé par '
             "l'empreinte mathématique `HMAC` de `app.secret_key` : la moindre retouche brise le "
             'sceau.',
  'explanation': 'Dans Flask, un cookie ordinaire manipulé via `request.cookies` demeure dépourvu '
                 'de signature cryptographique et doit par conséquent être réservé aux préférences '
                 "ergonomiques sans enjeu de sécurité, telles que la langue d'affichage ou le "
                 'choix du thème visuel.\n'
                 '\n'
                 "À l'inverse, le dictionnaire **`flask.session`** sérialise son contenu en JSON, "
                 'le compresse en Base64URL et y appose une signature HMAC calculée avec '
                 '`app.secret_key` via la bibliothèque `itsdangerous`. La moindre falsification '
                 "d'un octet dans l'inspecteur du navigateur invalide instantanément la signature "
                 'et entraîne le rejet pur et simple de la session.',
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
  'short': 'Mécanisme de sécurité des navigateurs Web contrôlant quels domaines externes sont '
           'autorisés à lire les réponses de votre API.',
  'analogy': "Une liste d'invités accrochée à l'entrée d'un salon privé : si une application React "
             "hébergée sur un domaine inconnu tente d'interroger l'API depuis le navigateur d'un "
             "client, le navigateur vérifie d'abord si ce domaine figure sur la liste blanche "
             '(`Access-Control-Allow-Origin`).',
  'explanation': "Un outil en ligne de commande comme `curl` ou un script Python backend n'est "
                 "jamais affecté par **CORS**, car la politique d'isolation *Same-Origin* est un "
                 'mécanisme de protection mis en œuvre exclusivement par les navigateurs Web pour '
                 "empêcher un site tiers malveillant d'interroger silencieusement une API au nom "
                 "de l'utilisateur.\n"
                 '\n'
                 "Dès qu'une application frontale JavaScript hébergée sur une autre origine tente "
                 "d'émettre une requête `POST`, `PUT` ou `DELETE` assortie d'un corps "
                 "`application/json` ou d'un en-tête `Authorization`, le navigateur expédie au "
                 'préalable une requête de contrôle **`OPTIONS` (*Preflight*)** afin de vérifier '
                 "que le serveur Flask l'y autorise explicitement via "
                 '`Access-Control-Allow-Origin`, `Access-Control-Allow-Methods` et '
                 '`Access-Control-Allow-Headers`.',
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
  'short': "Propriété mathématique d'une opération qui produit le même état sur le serveur qu'elle "
           'soit exécutée 1 fois ou 10 fois.',
  'analogy': "Appuyer 5 fois sur le bouton d'appel d'un ascenseur au 3ème étage est **idempotent** "
             "(l'ascenseur vient une seule fois au 3ème). Appuyer 5 fois sur « Débiter 10 000 DZD "
             "» ne l'est pas !",
  'explanation': "La maîtrise de l'idempotence gouverne la fiabilité des systèmes distribués face "
                 "aux aléas réseau. Les méthodes `GET`, `PUT` (écrasement intégral d'une ressource "
                 'identifiée) et `DELETE` sont **idempotentes** par construction : les exécuter '
                 'une ou plusieurs fois laisse la base de données dans le même état cible, tandis '
                 'que `PATCH` applique une modification partielle limitée aux seuls champs '
                 'transmis.\n'
                 '\n'
                 "En revanche, la méthode `POST` n'est **pas idempotente** nativement. Pour éviter "
                 "qu'une relance automatique consécutive à une coupure mobile ne crée une double "
                 "inscription ou un double débit, le client accompagne sa requête d'un identifiant "
                 'unique `Idempotency-Key: <uuid>` permettant au serveur de rejouer la réponse '
                 "mémorisée sans dupliquer l'écriture.",
  'code_example': '# En-tête envoyé sur un POST critique :\n'
                  '# Idempotency-Key: tx-2026-0001\n'
                  'cle = request.headers.get("Idempotency-Key")'},
 {'id': 'pagination_filtering',
  'term': 'Pagination (page/limit), Filtrage & Tri',
  'category': 'Architecture Web',
  'level': 'Fondamental',
  'short': "Découpage d'une grande collection en tranches via les paramètres d'URL "
           '`?page=1&limit=20&tri=duree_jours`.',
  'analogy': 'Consulter un catalogue de 50 000 articles par pages de 20 résultats au lieu '
             "d'imprimer les 50 000 lignes d'un seul bloc.",
  'explanation': "Le découpage arithmétique d'une collection selon le modèle *Offset Pagination* "
                 "repose sur l'équation `offset = (page - 1) * limit`, qui se traduit directement "
                 'par un indiçage de tranche `resultats[offset : offset + limit]` en Python ou par '
                 'la clause paramétrée `LIMIT ? OFFSET ?` dans une requête SQL.\n'
                 '\n'
                 "Afin de piloter proprement les composants de navigation de l'interface cliente, "
                 'la route Flask restitue systématiquement une enveloppe structurée associant le '
                 'tableau `data` à un objet `meta` renseignant `total_items`, `total_pages` et les '
                 'indicateurs de continuité.',
  'code_example': 'page = max(1, request.args.get("page", 1, type=int))\n'
                  'limit = min(100, request.args.get("limit", 10, type=int))\n'
                  'offset = (page - 1) * limit'},
 {'id': 'jinja2_forms_request_form',
  'term': 'Templates Jinja2 (render_template) & Formulaires HTML (request.form / request.files)',
  'category': 'Flask',
  'level': "Cœur d'API",
  'short': 'Séparation propre du HTML dans le dossier templates/ avec Jinja2 et traitement des '
           'formulaires Web envoyés en application/x-www-form-urlencoded ou multipart/form-data.',
  'analogy': "Jinja2 est le moule d'imprimerie (`.html`) dans lequel Flask injecte les variables "
             'Python (`{{ titre }}`) sans jamais mélanger le HTML dans le code Python. '
             '`request.form` est le guichet qui lit les bordereaux papier (`<form '
             "method='POST'>`), tandis que `request.get_json()` lit les colis électroniques JSON.",
  'explanation': 'Une architecture Flask rigoureuse proscrit toute concaténation de chaînes HTML à '
                 "l'intérieur des vues Python : les gabarits résident dans le sous-dossier "
                 "`templates/` et sont rendus par `render_template('page.html', "
                 "formations=liste)`. Le moteur **Jinja2** assure l'échappement automatique des "
                 'expressions `{{ variable }}` contre les injections XSS tout en structurant '
                 "l'affichage par boucles `{% for %}` et blocs conditionnels `{% if %}`.\n"
                 '\n'
                 "Lors de la soumission d'un formulaire `<form method='POST'>`, le navigateur "
                 "encode les champs munis d'un attribut `name` en "
                 '`application/x-www-form-urlencoded` : `request.get_json()` vaut alors `None` et '
                 "l'extraction s'effectue via **`request.form.get('titre')`**. Pour le "
                 "téléversement de pièces jointes (`enctype='multipart/form-data'`), les fichiers "
                 'binaires sont récupérés dans **`request.files`** et leur nom est '
                 'systématiquement assaini par `secure_filename()`.',
  'code_example': '@app.route("/formations", methods=["GET", "POST"])\n'
                  'def page_formations():\n'
                  '    if request.method == "POST":\n'
                  '        titre = request.form.get("titre", "").strip()  # Lecture du <input '
                  'name="titre">\n'
                  '        duree = request.form.get("duree_jours", type=int)\n'
                  '    return render_template("formations.html", formations=FORMATIONS)'},
 {'id': 'path_variables_syntax',
  'term': "Variables d'URL : <variable> (Flask) vs :variable (Postman/Node) vs {variable} "
          '(OpenAPI)',
  'category': 'Flask',
  'level': 'Fondamental',
  'short': 'Les trois notations différentes utilisées selon les frameworks et outils pour '
           "représenter un paramètre dynamique dans le chemin d'une URL.",
  'analogy': "Trois façons d'écrire un champ à remplir sur un formulaire administratif selon le "
             'pays : `« Votre Nom : <___> »` (Flask), `« Votre Nom : :nom »` (Postman/Express), ou '
             '`« Votre Nom : {nom} »` (OpenAPI/FastAPI). Le principe est identique, seule la '
             "ponctuation change selon l'outil.",
  'explanation': "Quatre conventions syntaxiques coexistent dans l'écosystème des APIs pour "
                 "désigner un segment d'URI variable, et les confondre constitue une source "
                 "fréquente d'erreurs. La notation à chevrons **`<variable>` et `<int:id>`** est "
                 'la **seule syntaxe reconnue par `@app.route(...)` dans Flask** (et Django), '
                 'offrant en prime une validation et conversion automatiques du type par Werkzeug '
                 '(`int`, `float`, `uuid`, `path`).\n'
                 '\n'
                 'La notation préfixée par deux-points **`:id`** appartient à Postman (où elle '
                 "active la grille *Path Variables*) ainsi qu'aux routeurs Express.js et Gin : "
                 "l'écrire dans Flask reviendrait à chercher littéralement la chaîne `':id'`. "
                 'Quant aux accolades **`{id}`** (RFC 6570), elles sont la norme des contrats '
                 "OpenAPI 3.0/Swagger, de FastAPI et des *f-strings* Python, tandis qu'un appel "
                 'réel dans `curl` ou le navigateur substitue toujours la valeur concrète '
                 '(`/api/formations/42`).',
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
  'short': 'Fonctions exécutées automatiquement avant et après chaque route pour la '
           'journalisation, le chronométrage et la corrélation.',
  'analogy': "Le portique de sécurité à l'entrée d'un bâtiment qui enregistre l'heure d'arrivée de "
             "chaque visiteur (`before_request`) et l'heure de sortie (`after_request`).",
  'explanation': 'Les crochets de cycle de vie `@app.before_request` et `@app.after_request` '
                 "permettent d'instrumenter transversalement l'ensemble des routes Flask sans "
                 'jamais dupliquer de code dans les fonctions de vue métier.\n'
                 '\n'
                 'Ils servent notamment à générer ou propager un identifiant de corrélation '
                 "`X-Request-ID` dans l'espace éphémère `flask.g`, à chronométrer la durée exacte "
                 'de traitement en millisecondes (`X-Response-Time-Ms`) et à greffer uniformément '
                 'les en-têtes de durcissement sécuritaire et CORS sur chaque réponse sortante.',
  'code_example': '@app.before_request\n'
                  'def debut():\n'
                  '    g.start = time.perf_counter()\n'
                  '\n'
                  '@app.after_request\n'
                  'def fin(reponse):\n'
                  '    reponse.headers["X-Response-Time-Ms"] = '
                  'str(round((time.perf_counter()-g.start)*1000, 2))\n'
                  '    return reponse'},
 {'id': 'wsgi_blueprints',
  'term': 'Blueprints, Application Factory & Serveur WSGI (Gunicorn)',
  'category': 'Flask',
  'level': "Cœur d'API",
  'short': "Organisation modulaire d'une API Flask (`Blueprint`) et déploiement multi-processus en "
           'production (`Gunicorn`).',
  'analogy': "Les `Blueprints` sont les départements spécialisés d'une entreprise, et `Gunicorn` "
             "est l'équipe de guichetiers parallèles (Workers) remplaçant le guichet unique "
             "d'entraînement (`app.run()`).",
  'explanation': "Dès qu'un projet dépasse quelques routes, l'objet **`Blueprint`** permet de "
                 "découper l'application Flask en modules fonctionnels autonomes "
                 '(`/api/v1/formations`, `/api/health`, portail Web) assemblés proprement au sein '
                 "d'une fabrique `create_app()`.\n"
                 '\n'
                 "Cette structuration facilite l'exécution instantanée de suites d'intégration en "
                 'mémoire via **`app.test_client()`** sans ouvrir de socket réseau, puis le '
                 'passage en production sous **`Gunicorn`**, serveur WSGI pré-forkant plusieurs '
                 'workers Python parallèles derrière un proxy inverse Nginx.',
  'code_example': '# Commande de lancement en production (4 workers) :\n'
                  '# gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"'},
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
                 'un serveur partenaire ou à un automate backend pour authentifier des échanges '
                 'machine-à-machine sur un périmètre bien circonscrit.\n'
                 '\n'
                 "À l'inverse, un jeton **`Authorization: Bearer <token>`** est émis dynamiquement "
                 "à l'issue d'une authentification réussie (`/api/auth/token`), possède une "
                 'fenêtre de validité brève (quelques minutes) et embarque directement dans sa '
                 "charge signée l'identité et le rôle de l'opérateur humain.",
  'code_example': '# Cas 1 : Clé machine-à-machine\n'
                  'cle = request.headers.get("X-API-Key")\n'
                  '\n'
                  '# Cas 2 : Jeton temporaire utilisateur\n'
                  'auth = request.headers.get("Authorization") # "Bearer <token>"'},
 {'id': 'variable',
  'term': 'Variable (Python)',
  'category': 'Bases Python',
  'level': 'Débutant Absolu',
  'short': "Emplacement nommé dans la mémoire de l'ordinateur permettant de conserver une valeur "
           'typée.',
  'analogy': 'Un dossier suspendu dans une armoire sur lequel vous collez une étiquette « '
             'Budget_2026 ». Vous pouvez consulter son contenu ou le mettre à jour à tout moment.',
  'explanation': 'En Python, une variable associe un identifiant symbolique placé à gauche de '
                 "l'opérateur d'affectation `=` à une valeur typée résidant en mémoire.\n"
                 '\n'
                 "Dans le cadre d'une API Web, quatre types scalaires fondamentaux se sérialisent "
                 'nativement vers le standard JSON : les chaînes de caractères `str`, les nombres '
                 'entiers ou flottants `int` et `float`, les booléens `bool` (`True`/`False` '
                 "convertis en `true`/`false`) et la valeur d'absence `None` (convertie en "
                 '`null`).',
  'code_example': 'nom_stagiaire = "Amine"\n'
                  'age = 25\n'
                  '# Utiliser nom_stagiaire renvoie désormais "Amine"'},
 {'id': 'dictionnaire',
  'term': 'Dictionnaire (dict)',
  'category': 'Bases Python',
  'level': 'Débutant Absolu',
  'short': 'Structure de données Python associant des clés uniques à des valeurs (`{clé: '
           'valeur}`).',
  'analogy': 'Une fiche signalétique structurée où chaque champ possède un intitulé précis (« Nom '
             '», « Prénom », « Ville ») associé à sa valeur.',
  'explanation': 'Délimité par des accolades `{ }`, le dictionnaire Python associe des clés '
                 'uniques à des valeurs arbitraires en temps constant par table de hachage. Il '
                 "constitue la brique centrale du développement d'APIs REST car `jsonify()` le "
                 'transforme directement en objet JSON.\n'
                 '\n'
                 "Lors de l'inspection d'une charge utile reçue d'un client externe, la méthode "
                 "défensive `corps.get('cle', valeur_par_defaut)` est toujours préférée à "
                 "l'indexation directe `corps['cle']` afin d'éviter toute interruption brutale par "
                 'exception `KeyError`.',
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
  'explanation': 'Délimitée par des crochets `[ ]`, la liste Python représente une séquence '
                 "ordonnée et mutable d'éléments accessibles par leur indice numérique.\n"
                 '\n'
                 "Lorsqu'un endpoint de collection restitue un ensemble d'entités métier — par "
                 'exemple le catalogue paginé des formations ISGP —, le champ `data` de '
                 "l'enveloppe JSON contient précisément une liste de dictionnaires homogènes.",
  'code_example': 'formations = ["Python", "API REST", "Flask"]\n'
                  'print(formations[0])  # Affiche le 1er élément : Python'},
 {'id': 'fonction',
  'term': 'Fonction (def) & Décorateur (@)',
  'category': 'Bases Python',
  'level': 'Débutant Absolu',
  'short': "Bloc d'instructions réutilisable prenant des paramètres en entrée et retournant un "
           'résultat via `return`.',
  'analogy': 'Une unité de traitement : vous lui fournissez des matières premières (paramètres), '
             'elle applique une procédure interne, et restitue le produit fini (`return`).',
  'explanation': 'Déclarée par le mot-clé `def`, une fonction encapsule une séquence '
                 "d'instructions réutilisable recevant des paramètres d'entrée et produisant une "
                 'valeur via `return`.\n'
                 '\n'
                 "Flask exploite intensivement les **décorateurs (`@`)**, fonctions d'ordre "
                 "supérieur qui enveloppent une vue Python afin d'enregistrer son URI dans la "
                 'table de routage Werkzeug (`@app.route`) ou de contrôler les habilitations de '
                 "l'appelant avant son exécution (`@exiger_role`).",
  'code_example': '@app.route("/bonjour")\n'
                  'def dire_bonjour():\n'
                  '    return jsonify({"message": "Service opérationnel"}), 200'},
 {'id': 'api',
  'term': 'API REST & Modèle de Maturité de Richardson',
  'category': 'Architecture Web',
  'level': 'Fondamental',
  'short': 'Architecture normalisée où chaque URL identifie une ressource (nom au pluriel) '
           'manipulée par les verbes et statuts HTTP.',
  'analogy': "Un guichet de liaison standardisé : l'application cliente dépose un bordereau de "
             'demande normé (Requête HTTP) et reçoit un colis de données structuré (Réponse JSON) '
             'sans dépendre du langage interne du serveur.',
  'explanation': 'Le modèle de maturité de Leonard Richardson évalue la conformité architecturale '
                 "d'une API Web selon quatre paliers progressifs. Le niveau 0 regroupe tous les "
                 'appels RPC ou SOAP sur une URL unique, tandis que le niveau 1 attribue une '
                 'adresse distincte à chaque ressource métier (`/api/formations/1`).\n'
                 '\n'
                 "Le **niveau 2**, référence de l'industrie REST contemporaine, marie ces URIs de "
                 'ressources avec la sémantique exacte des verbes HTTP (`GET`, `POST`, `PUT`, '
                 '`PATCH`, `DELETE`) et des codes de statut normalisés (`200`, `201`, `401`, '
                 '`403`, `422`, `429`), avant un éventuel niveau 3 (*HATEOAS*) enrichissant les '
                 'réponses de liens hypermédias autodocumentés.',
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
  'explanation': 'Tout code de statut HTTP à trois chiffres renseigne immédiatement le client sur '
                 "l'issue du traitement sans l'obliger à analyser le texte du message. La famille "
                 "**2xx** atteste du succès de l'opération (`200 OK`, `201 Created` après "
                 'insertion, `204 No Content` après suppression silencieuse).\n'
                 '\n'
                 "La famille **4xx** impute l'anomalie à la requête cliente : `400 Bad Request` "
                 'sanctionne un JSON malformé, `401 Unauthorized` signale un défaut '
                 "d'authentification, `403 Forbidden` oppose un refus d'autorisation RBAC, `404 "
                 "Not Found` constate l'absence de la cible, `405 Method Not Allowed` rejette le "
                 'verbe HTTP, `413` bloque une charge excessive, `422 Unprocessable Entity` '
                 'détaille les erreurs de validation métier et `429 Too Many Requests` impose une '
                 'limitation de débit. Enfin, la famille **5xx** (`500`, `502`, `503`, `504`) '
                 'caractérise une défaillance interne du serveur ou de sa passerelle amont.',
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
  'short': 'Moteur de base de données relationnelle SQL transactionnel intégré à Python '
           '(`sqlite3`).',
  'analogy': 'Un registre comptable permanent écrit sur disque dur, protégé par des transactions '
             'atomiques (tout réussit avec `commit` ou tout est annulé avec `rollback`).',
  'explanation': 'Moteur relationnel transactionnel ACID embarqué dans un simple fichier disque '
                 "sans démon séparé, SQLite s'intègre nativement à la bibliothèque standard Python "
                 'via le module `sqlite3`.\n'
                 '\n'
                 'La règle de sécurité absolue gouvernant toute interaction SQL interdit '
                 'formellement de construire une requête par concaténation `+` ou *f-string* avec '
                 "une variable externe, sous peine d'**Injection SQL** critique : les valeurs "
                 'dynamiques sont systématiquement transmises dans un tuple séparé associé à des '
                 'marqueurs paramétrés `?`.',
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
  'explanation': "Par défaut, SQLite utilise un journal d'annulation classique qui verrouille la "
                 'base entière lors des écritures et désactive la vérification des clés '
                 'étrangères. Trois directives `PRAGMA` transforment radicalement son comportement '
                 "pour un serveur d'API multi-workers.\n"
                 '\n'
                 "L'activation de **`PRAGMA journal_mode = WAL;`** consigne les écritures "
                 'séquentiellement dans un fichier `.db-wal` annexe afin que les lectures ne '
                 'bloquent jamais les écritures. Parallèlement, **`PRAGMA foreign_keys = ON;`** '
                 "restaure l'intégrité référentielle sur chaque nouvelle connexion ouverte, et "
                 "**`PRAGMA busy_timeout = 5000;`** ordonne d'attendre jusqu'à cinq secondes la "
                 "libération d'un verrou concurrent avant de lever `OperationalError: database is "
                 'locked`.',
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
  'explanation': 'Une subtilité fréquente du module standard `sqlite3` tient au comportement de '
                 'son gestionnaire de contexte : écrire `with conn:` valide automatiquement la '
                 "transaction par `COMMIT` (ou l'annule par `ROLLBACK` en cas d'exception), mais "
                 '**ne referme ni le curseur actif ni la connexion au fichier disque**.\n'
                 '\n'
                 'Dans une application Flask soumise à un fort trafic, on libère proprement les '
                 'ressources mémoire en enveloppant les curseurs ponctuels dans `with '
                 'contextlib.closing(conn.cursor()) as cur:` et en fermant systématiquement la '
                 'connexion rattachée à `flask.g` dans `@app.teardown_appcontext`.',
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
  'explanation': 'Le module **`sqlite3`** inclus dans la bibliothèque standard Python couvre '
                 "l'essentiel des besoins métier sans aucune dépendance externe, respecte la norme "
                 "`DB-API 2.0` (`PEP 249`) et s'intègre nativement à l'ORM SQLAlchemy.\n"
                 '\n'
                 'Pour les charges système spécialisées, la bibliothèque alternative **`apsw`** '
                 "(*Another Python SQLite Wrapper*) expose l'intégralité de l'API C native de "
                 'SQLite : absence de `BEGIN` implicite caché, lecture/écriture en flux continu de '
                 'gros objets binaires (*Streaming Blob I/O*), sauvegarde transactionnelle à chaud '
                 "(*Backup API*) et remontée granulaire des codes d'erreur étendus tels que "
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
  'explanation': 'Le standard **Server-Sent Events (SSE)** établit un flux unidirectionnel léger '
                 'du serveur Flask vers le navigateur sur une simple connexion HTTP persistante '
                 '`text/event-stream`. Chaque notification est formatée en texte clair au moyen '
                 'des champs `id:`, `event:` et `data:` clos par une **double fin de ligne '
                 'obligatoire `\\n\\n`**.\n'
                 '\n'
                 "Côté client, l'interface native `EventSource` gère d'elle-même la reconnexion "
                 "automatique après une coupure réseau en renvoyant l'en-tête `Last-Event-ID`, ce "
                 "qui fait de SSE l'outil privilégié pour les barres de progression, les tableaux "
                 'de bord temps réel et la diffusion jeton par jeton de modèles de langage.',
  'code_example': 'from flask import Response, stream_with_context\n'
                  '\n'
                  '@app.get("/api/sse")\n'
                  'def flux_sse():\n'
                  '    def generateur():\n'
                  '        yield "id: 1\\nevent: progression\\ndata: {\\"pct\\": 50}\\n\\n"\n'
                  '    return Response(stream_with_context(generateur()), '
                  'mimetype="text/event-stream")'},
 {'id': 'websocket_rfc6455',
  'term': 'WebSocket (RFC 6455 & HTTP 101 Switching Protocols)',
  'category': 'Temps Réel & Streaming',
  'level': 'Avancé',
  'short': 'Protocole de communication bidirectionnelle (Full-Duplex) persistante sur un unique '
           'socket TCP après une mise à niveau HTTP 101.',
  'analogy': 'Un appel téléphonique ouvert en continu : contrairement au courrier postal (HTTP '
             'requête/réponse) ou à la radio unidirectionnelle (SSE), les deux interlocuteurs '
             'peuvent parler et écouter simultanément à la milliseconde près.',
  'explanation': 'Défini par la norme **RFC 6455**, le protocole **WebSocket** démarre par une '
                 'poignée de main HTTP classique comportant les en-têtes `Upgrade: websocket`, '
                 '`Connection: Upgrade` et `Sec-WebSocket-Key`, à laquelle le serveur répond par '
                 '`HTTP/1.1 101 Switching Protocols` pour convertir la socket TCP en canal binaire '
                 'ou textuel *full-duplex*.\n'
                 '\n'
                 'Alors que SSE suffit amplement lorsque seul le serveur pousse des mises à jour, '
                 "WebSocket s'impose dès que l'application exige des échanges bidirectionnels à "
                 'très basse latence, tels que la messagerie collaborative instantanée, le partage '
                 'de curseurs multi-opérateurs ou la télémétrie industrielle haute fréquence.',
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
  'explanation': "Encoder un document PDF ou une image en Base64 à l'intérieur d'un objet JSON "
                 'gonfle artificiellement le volume réseau de `+33 %` et contraint le worker '
                 "Python à charger l'intégralité de la chaîne en mémoire vive avant décodage : le "
                 'transport binaire natif **`multipart/form-data`** demeure donc la seule approche '
                 'performante.\n'
                 '\n'
                 "La réception sécurisée d'un fichier téléversé impose trois verrous cumulatifs : "
                 'plafonner strictement la taille maximale acceptée (`413 Content Too Large`), '
                 'inspecter les premiers octets réels du flux (*Magic Bytes*, tels `25 50 44 46 '
                 "2D` pour `%PDF-` ou `89 50 4E 47` pour PNG) sans jamais se fier à l'extension "
                 'déclarée, et substituer au nom fourni par le client un identifiant interne '
                 "`uuid4().hex` afin d'éliminer toute traversée d'arborescence (*Path Traversal*).",
  'code_example': 'app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # Plafond 5 Mo -> 413\n'
                  'f = request.files["document"]\n'
                  'entete = f.stream.read(5); f.stream.seek(0)\n'
                  'if not entete.startswith(b"%PDF-"): abort(415)'},
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
  'explanation': 'Exécuter directement une génération de rapport lourd ou un traitement de trente '
                 "secondes à l'intérieur d'une route HTTP synchrone immobilise le worker Gunicorn "
                 "et expose l'appelant aux coupures `504 Gateway Timeout` imposées par les proxys "
                 'inverses Nginx ou Cloudflare.\n'
                 '\n'
                 "Le patron d'architecture asynchrone résout ce blocage en dissociant la "
                 "soumission de l'exécution : `POST /api/exports` enregistre immédiatement une "
                 "tâche à l'état `EN_ATTENTE`, répond en quelques millisecondes **`202 Accepted`** "
                 "avec l'en-tête `Location: /api/jobs/job-8a2f`, puis laisse le client interroger "
                 "périodiquement cette ressource d'état jusqu'à sa complétion.",
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
  'explanation': "La politique de mise en cache HTTP obéit d'abord à un impératif de "
                 'confidentialité : toute route restituant un profil personnel ou des jetons '
                 'sensibles doit impérativement émettre **`Cache-Control: no-store`** afin '
                 "d'interdire toute persistance sur les proxys partagés.\n"
                 '\n'
                 'Sur les ressources publiques ou semi-statiques consultées en `GET`, le couple '
                 '**`ETag`** et **`If-None-Match`** optimise drastiquement les performances : si '
                 "l'empreinte SHA-256 de l'entité n'a pas évolué depuis la dernière lecture du "
                 'client, Flask retourne instantanément **`304 Not Modified`** avec un corps vide '
                 'de zéro octet, économisant la bande passante mobile.',
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
  'explanation': 'Lorsque deux administrateurs ouvrent simultanément la même fiche de formation et '
                 "soumettent chacun une modification `PUT`, l'absence de contrôle de concurrence "
                 'conduit au syndrome de la mise à jour perdue (*Lost Update*), où le second '
                 'enregistrement écrase silencieusement le travail du premier.\n'
                 '\n'
                 'Le **verrouillage optimiste** prévient cette perte sans bloquer la base : le '
                 'client renvoie la version lue dans l\'en-tête `If-Match: "v1"`, et le serveur '
                 'exécute atomiquement `UPDATE formations SET ..., version = version + 1 WHERE id '
                 "= ? AND version = ?`. Si aucune ligne n'est affectée (`rowcount == 0`), l'API "
                 "rejette l'écriture avec **`412 Precondition Failed`**.",
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
  'explanation': 'Dans une infrastructure de production où chaque transaction traverse un '
                 'répartiteur de charge, un proxy inverse Nginx et un pool de workers Gunicorn, '
                 "retrouver la cause racine d'une erreur sans identifiant commun relève de la "
                 'gageure.\n'
                 '\n'
                 "Le middleware de corrélation vérifie dès l'entrée de la requête si la passerelle "
                 'amont a fourni un en-tête **`X-Request-ID`** conforme, ou engendre à défaut un '
                 '`uuid4` neuf. Associé au chronomètre `time.perf_counter()`, cet identifiant est '
                 'injecté à la fois dans les journaux structurés du serveur et dans les en-têtes '
                 'de réponse aux côtés de `X-Response-Time-Ms`.',
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
  'explanation': 'En configuration par défaut, Nginx rejette tout corps HTTP excédant **1 Mo** '
                 '(`client_max_body_size 1m`) : la bonne pratique consiste à conserver cette '
                 "limite stricte sur les routes JSON générales et à n'ouvrir un plafond supérieur "
                 '(`25M`) que sur le bloc `location` dédié aux téléversements.\n'
                 '\n'
                 'Pour soulager complètement les workers Python des transferts binaires '
                 'volumineux, Nginx peut écrire le flux entrant directement sur disque '
                 '(`client_body_in_file_only clean`) et ne transmettre à Flask que le chemin local '
                 'dans `X-Uploaded-File-Path`. Symétriquement en lecture privée, Flask vérifie les '
                 "droits de l'utilisateur puis délègue l'émission noyau haute performance "
                 "(`sendfile on`) à Nginx via l'en-tête interne **`X-Accel-Redirect`**.",
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
  'explanation': "Si le langage courant associe spontanément le terme d'API aux services Web, "
                 "l'informatique industrielle distingue en réalité quatre grandes familles "
                 "d'interfaces de programmation selon la frontière qu'elles gouvernent. Au plus "
                 'près du matériel, les **appels système POSIX** (`open()`, `epoll()`) encadrent '
                 'le dialogue avec le noyau, tandis que les **interfaces de bibliothèques en '
                 "mémoire** — à l'image de la norme Python **`PEP 249` (`DB-API 2.0`)** unifiant "
                 "`sqlite3` et `psycopg` — isolent les composants d'un même processus.\n"
                 '\n'
                 "À l'échelle locale ou matérielle opèrent les **mécanismes IPC** (sockets UNIX, "
                 "pilotes d'accélérateurs), et à l'échelle distribuée s'épanouissent enfin les "
                 '**APIs réseau**, dominées par **REST** sur HTTP, **GraphQL** pour le requêtage '
                 'déclaratif, **gRPC** sur flux binaires HTTP/2, les **Webhooks** événementiels et '
                 'les **WebSockets**.',
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
  'explanation': "Un **contrat d'API** constitue un engagement formel et exécutable par machine — "
                 'matérialisé par un fichier OpenAPI 3.1 ou JSON Schema — qui fige les types de '
                 'données, les attributs obligatoires, les bornes numériques, les statuts HTTP, la '
                 "structure d'erreur RFC 7807 et les exigences de sécurité, permettant aux "
                 'pipelines CI/CD de bloquer automatiquement tout *Breaking Change*.\n'
                 '\n'
                 "La **documentation d'API** désigne quant à elle l'expérience pédagogique "
                 'destinée aux développeurs humains : guides de démarrage rapide, scénarios '
                 "d'intégration et portails interactifs tels que Swagger UI ou ReDoc. Dériver "
                 'automatiquement cette documentation depuis le contrat machine élimine tout '
                 'risque de dérive documentaire (*Documentation Drift*).',
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
  'explanation': 'Au sens mathématique repris par la norme **RFC 9110**, les verbes HTTP `GET`, '
                 '`HEAD`, `OPTIONS`, `PUT` (remplacement complet) et `DELETE` sont nativement '
                 '**idempotents** : soumettre dix fois la même requête produit exactement le même '
                 "état serveur qu'une exécution unique.\n"
                 '\n'
                 "À l'opposé, la méthode `POST` n'est **pas idempotente** par défaut, de sorte "
                 "qu'une relance automatique après une perte de signal Wi-Fi risque d'engendrer "
                 "une double facturation. L'industrie résout ce problème en exigeant du client un "
                 "identifiant unique dans l'en-tête **`Idempotency-Key`**, mis en cache côté "
                 "serveur pendant vingt-quatre heures afin de restituer à l'identique le résultat "
                 'initial sans réexécuter la transaction métier.',
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
  'explanation': "Deux méthodologies majeures structurent le cycle de conception d'une API "
                 "industrielle. Dans l'approche **Contract-First**, les architectes rédigent et "
                 "valident d'abord le schéma `openapi.yaml` (vérifié par un analyseur tel que "
                 'Spectral), ce qui permet aux équipes frontales, mobiles et backend de développer '
                 'simultanément grâce à des serveurs simulés (*Mock Servers*).\n'
                 '\n'
                 "Dans l'approche **Code-First**, les schémas de validation écrits en Python "
                 "génèrent dynamiquement `/openapi.json` à l'exécution, garantissant l'absence "
                 "d'écart entre l'implémentation et sa spécification. Dans les deux cas, les "
                 'évolutions privilégient les ajouts optionnels rétrocompatibles et encadrent '
                 'toute fin de vie par les en-têtes `Deprecation` et `Sunset` (**RFC 8594**).',
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
  'explanation': "La topologie réseau d'une plateforme moderne distingue deux axes de circulation "
                 'aux contraintes radicalement différentes. Le trafic **Nord-Sud** désigne les '
                 'flux verticaux franchissant la frontière publique depuis Internet (navigateurs, '
                 'applications mobiles, partenaires) sur un réseau étendu hostile à latence élevée '
                 ': il est filtré en bordure par le DNS, un CDN, un pare-feu applicatif WAF, la '
                 'terminaison TLS publique, le Rate Limiting et une **API Gateway**.\n'
                 '\n'
                 'Le trafic **Est-Ouest** regroupe quant à lui les communications horizontales '
                 'internes de microservice à microservice au sein du centre de données, où une '
                 'seule requête entrante peut déclencher dix appels internes en éventail '
                 '(*fan-out*). Cet axe exige des budgets de latence milliseconde, des délais '
                 "d'expiration stricts et un chiffrement mutuel **mTLS** sous doctrine "
                 '**Zero-Trust**.',
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
  'explanation': "Le patron d'architecture **Phantom Token** concilie l'opacité sécuritaire sur "
                 "Internet avec l'efficacité cryptographique interne. Côté externe (Nord-Sud), le "
                 "client ne détient qu'un jeton opaque aléatoire dépourvu de toute signification "
                 'lisible, évitant ainsi de divulguer la nomenclature des rôles ou la topologie '
                 'interne par simple décodage Base64URL.\n'
                 '\n'
                 "À la traversée de l'**API Gateway**, ce jeton opaque est immédiatement vérifié, "
                 'révocable à la seconde près, puis échangé à la volée contre un jeton JWT interne '
                 'signé que les microservices aval (Est-Ouest) valident de manière autonome et '
                 "ultrarapide à l'aide des clés publiques JWKS.",
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
  'explanation': "L'architecture de sécurité contemporaine abandonne définitivement l'ancien "
                 'postulat du « château-fort entouré de douves » selon lequel tout paquet '
                 'circulant sur le réseau privé interne serait digne de confiance : la moindre '
                 "compromission d'un conteneur périphérique livrerait alors sans entrave "
                 "l'ensemble des bases de données et services métiers.\n"
                 '\n'
                 "Sous un modèle **Zero-Trust**, chaque appel Est-Ouest s'établit sur **mTLS "
                 '(*Mutual TLS*)** : lors de la poignée de main cryptographique, non seulement le '
                 'serveur prouve son identité, mais il exige et valide également le certificat '
                 "X.509 du microservice appelant, porteur d'une identité logicielle normalisée "
                 "telle qu'une URI **SPIFFE** "
                 '(`spiffe://isgp.mesh/ns/prod/sa/service-inscriptions`).',
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
  'explanation': "Le cadre d'autorisation déléguée **OAuth 2.0 (RFC 6749)** répartit les "
                 'responsabilités entre quatre acteurs canoniques strictement découplés. Le '
                 "**Resource Owner** est l'utilisateur humain titulaire des données, tandis que le "
                 "**Client** désigne l'application frontale, mobile ou tierce sollicitant un accès "
                 'limité en son nom.\n'
                 '\n'
                 "L'**Authorization Server (IdP)** se charge d'authentifier l'utilisateur, de "
                 "recueillir son consentement et d'émettre les jetons signés, alors que le "
                 '**Resource Server** — rôle tenu par votre API Python Flask — vérifie à chaque '
                 "appel la signature cryptographique, l'échéance `exp`, l'audience `aud` et les "
                 'permissions `scope` avant de servir la donnée.',
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
  'explanation': "L'extension **PKCE (*Proof Key for Code Exchange*, RFC 7636)** protège le flux "
                 "d'autorisation OAuth 2.0 contre l'interception du code de redirection sur les "
                 'terminaux mobiles et les applications Web monopages. Avant toute redirection, le '
                 'client engendre un secret aléatoire éphémère `code_verifier` et ne transmet sur '
                 '`/authorize` que son condensat irréversible `code_challenge = '
                 'BASE64URL(SHA256(code_verifier))`.\n'
                 '\n'
                 "Une fois le `code` à usage unique reçu, le client l'échange sur `/token` en "
                 "présentant simultanément le `code_verifier` original : le serveur d'autorisation "
                 "recalcule le SHA-256 pour s'assurer qu'il s'agit bien de l'initiateur légitime "
                 "avant de délivrer l'`access_token`, remplaçant ainsi définitivement l'ancien "
                 'flux *Implicit* déprécié.',
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
  'explanation': "La couche d'identité **OpenID Connect (OIDC)** superposée à OAuth 2.0 distingue "
                 "rigoureusement deux jetons aux audiences incompatibles. L'**`ID Token`** atteste "
                 "de l'événement d'authentification à l'intention exclusive de l'application "
                 "cliente frontale, tandis que l'**`Access Token`** transporte les autorisations "
                 'destinées au backend API.\n'
                 '\n'
                 'La règle cardinale commande de ne **jamais** transmettre un `ID Token` dans '
                 "`Authorization: Bearer` pour invoquer une API métier, et à l'inverse de ne "
                 'jamais amener le code frontal à décoder un `Access Token` destiné au serveur de '
                 "ressources. Lorsque l'échange s'effectue entre deux serveurs sans intervention "
                 'humaine (tâche planifiée, démon), on recourt directement au flux '
                 '**`client_credentials`**.',
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
  'explanation': "Dans une chaîne d'appels inter-services, propager aveuglément le jeton d'accès "
                 "initial reçu d'Internet d'un microservice A vers un microservice B (*Blind Token "
                 'Passthrough*) crée une vulnérabilité majeure de type *Confused Deputy* : un '
                 'service intermédiaire compromis pourrait rejouer ce jeton à large portée contre '
                 "n'importe quelle autre brique du système.\n"
                 '\n'
                 'Le standard **Token Exchange (RFC 8693, flux *On-Behalf-Of*)** élimine ce risque '
                 ": le service A présente le jeton entrant au serveur d'autorisation pour obtenir "
                 'en retour un jeton dérivé à très courte durée de vie (`120s`), restreint à la '
                 "seule audience `aud: service-paiement`, doté d'un `scope` minimal et traçant "
                 "l'identité de l'intermédiaire dans la déclaration d'audit **`act` (*Actor*)**.",
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
  'explanation': "Né en 2010 sous l'appellation *Swagger Specification* à l'initiative de Tony "
                 "Tam, ce format de description d'APIs REST a été confié en novembre 2015 à la "
                 "**Linux Foundation** au sein de l'OpenAPI Initiative et rebaptisé **OpenAPI "
                 'Specification** (`OAS 3.0`, puis `OAS 3.1` aligné à 100 % sur le standard JSON '
                 'Schema Draft 2020-12).\n'
                 '\n'
                 'Depuis cette distinction, **OpenAPI** désigne exclusivement la norme ouverte du '
                 'contrat JSON/YAML, tandis que **Swagger** regroupe la suite logicielle '
                 "développée par SmartBear (**Swagger Editor** pour l'édition assistée, **Swagger "
                 "UI** pour l'exploration interactive *Try it out*, **Swagger Codegen** pour la "
                 "génération de clients), aux côtés d'outils modernes comme **ReDoc**, **Scalar** "
                 'et **Schemathesis**.',
  'code_example': '# Flask + APIFlask : contrat OpenAPI 3.1 + Swagger UI sur /docs\n'
                  'from apiflask import APIFlask\n'
                  "app = APIFlask(__name__, title='API ISGP', version='2.1.0')"}]
