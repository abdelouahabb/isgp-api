"""
Référentiel des Concepts Fondamentaux & Addendum Technique — Édition TORNADO (69 fiches).
Chaque concept ou outil est expliqué sans aucun prérequis, avec une analogie fonctionnelle
et des commandes / exemples prêts pour la production.
"""

GLOSSARY_TERMS = [{'id': 'openssl_rand_secrets',
  'term': 'Génération de Secrets Cryptographiques (openssl rand & secrets)',
  'category': 'Cryptographie & OpenSSL',
  'level': 'Addendum Sécurité',
  'short': 'Commandes permettant de générer des clés secrètes (cookie_secret, SECRET_KEY, API '
           'Keys) à haute entropie impossibles à deviner.',
  'analogy': 'Un générateur mécanique de combinaisons de coffre-fort à 256 bits : contrairement à '
             'un mot de passe inventé par un humain, aucun dictionnaire ni supercalculateur ne '
             'peut deviner une clé aléatoire cryptographique de 32 octets.',
  'explanation': "Un secret d'infrastructure tel qu'un `cookie_secret` Tornado ou une clé "
                 '`SECRET_KEY` ne doit jamais être inventé manuellement au clavier, car une chaîne '
                 "choisie par un opérateur humain présente une entropie faible qui l'expose aux "
                 'attaques par dictionnaire hors ligne.\n'
                 '\n'
                 'En administration système Linux, la commande `openssl rand` puise directement '
                 "dans le générateur d'aléa cryptographique du noyau (`/dev/urandom`) pour "
                 'produire des séquences imprévisibles encodées en hexadécimal (`-hex 32`, soit 64 '
                 "caractères pour 256 bits) ou en Base64 (`-base64 32`). Au sein d'une application "
                 'Python, le module pseudo-aléatoire `random` est proscrit en matière de sécurité '
                 'au profit exclusif du module standard `secrets` (`secrets.token_hex(32)`).',
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
  'explanation': "Lors du calcul d'une empreinte cryptographique en ligne de commande Linux, "
                 'l\'usage de `echo "secret"` constitue un piège fréquent car `echo` ajoute '
                 'implicitement un saut de ligne final `\\n` qui modifie radicalement le condensat '
                 "SHA-256 par rapport au calcul effectué en Python. Il convient donc d'utiliser "
                 'systématiquement `printf \'%s\' "secret"` (ou `echo -n`).\n'
                 '\n'
                 "Pour attester l'intégrité d'archives de déploiement ou de binaires, les "
                 'utilitaires `sha256sum archive.tar.gz` et `openssl dgst -sha256 archive.tar.gz` '
                 'calculent une empreinte déterministe permettant de détecter immédiatement toute '
                 'corruption réseau ou altération malveillante.',
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
             'Tornado.',
  'explanation': "Contrairement à un condensat SHA-256 ordinaire que n'importe quel tiers peut "
                 'recalculer sur un message intercepté, le mécanisme **HMAC (`Hash-based Message '
                 'Authentication Code`)** mêle mathématiquement les octets utiles du message à une '
                 'clé secrète partagée (`-hmac "cle"`).\n'
                 '\n'
                 "En phase d'intégration et de recette, `openssl dgst -sha256 -hmac` constitue "
                 "l'outil de référence en terminal pour forger une signature valide dans l'en-tête "
                 "`X-Webhook-Signature` avant d'éprouver un contrôleur Tornado avec `curl`.",
  'code_example': "# 1. Calculer la signature HMAC-SHA256 d'un corps JSON avec OpenSSL :\n"
                  'printf \'%s\' \'{"id":101,"statut":"paye"}\' | openssl dgst -sha256 -hmac '
                  '"whsec_isgp_2026"\n'
                  '\n'
                  "# 2. Stocker la signature dans une variable Bash et appeler l'API Tornado avec "
                  'curl :\n'
                  'BODY=\'{"id":101,"statut":"paye"}\'\n'
                  'SIG=$(printf \'%s\' "$BODY" | openssl dgst -sha256 -hmac "whsec_isgp_2026" | '
                  "awk '{print $2}')\n"
                  'curl -i -X POST http://127.0.0.1:8888/api/webhooks -H "X-Webhook-Signature: '
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
  'explanation': 'Il est essentiel de distinguer rigoureusement le hachage irréversible du '
                 'chiffrement réversible : on hache les mots de passe utilisateurs car le serveur '
                 "n'a jamais besoin de les relire en clair, tandis qu'on chiffre en **AES-256** "
                 "les sauvegardes SQLite, les fichiers `.env` d'archivage ou les identifiants "
                 'bancaires qui devront être restitués ultérieurement.\n'
                 '\n'
                 "Lors d'un chiffrement symétrique avec OpenSSL (`openssl enc -aes-256-cbc`), la "
                 "sécurité opérationnelle impose d'activer conjointement un sel aléatoire "
                 "(`-salt`), la dérivation standardisée `-pbkdf2` et un nombre élevé d'itérations "
                 '(`-iter 600000`) afin de neutraliser le cassage par force brute.',
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
  'explanation': 'Dans un écosystème distribué comptant vingt microservices appelés à valider des '
                 "jetons d'accès, la signature symétrique HMAC (`HS256`) oblige chaque service à "
                 "détenir la même clé `SECRET_KEY`, de sorte que la compromission d'un seul nœud "
                 "secondaire permettrait à l'attaquant de forger des jetons `admin` arbitraires.\n"
                 '\n'
                 'La cryptographie asymétrique **RSA** ou **Ed25519** (`openssl genpkey`) résout '
                 "structurellement ce risque : seul le serveur d'authentification central conserve "
                 'jalousement la clé privée `private.pem` pour signer les jetons émis, tandis que '
                 "l'ensemble des microservices Tornado ne reçoivent que la clé publique "
                 '`public.pem`, strictement limitée à la vérification en lecture seule.',
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
  'explanation': 'Sur un environnement exposé sur Internet, la terminaison HTTPS repose sur un '
                 'certificat X.509 délivré par une Autorité de Certification reconnue telle que '
                 "Let's Encrypt automatisée par Certbot sur le frontal Nginx.\n"
                 '\n'
                 'En qualification locale ou sur un bus interne isolé, la commande `openssl req '
                 '-x509` engendre en une seule opération la biclé (`key.pem`) et le certificat '
                 'auto-signé (`cert.pem`) directement exploitables par '
                 "`tornado.httpserver.HTTPServer(app, ssl_options=...)`. En cas d'échec de "
                 'négociation TLS vers un partenaire distant, `openssl s_client -connect` inspecte '
                 "en direct la chaîne de certification et sa date d'expiration.",
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
           'HTTP (Basic Auth, Payload JWT, Cookies signés Tornado).',
  'analogy': "Traduire un document en alphabet morse pour qu'il passe sur une ligne télégraphique "
             ": cela permet le transport sans erreur d'encodage, mais ce n'est absolument pas un "
             'chiffrement secret.',
  'explanation': "L'encodage **Base64** assure le transport sûr d'octets arbitraires au sein "
                 "d'en-têtes HTTP textuels ASCII : il structure l'authentification `Authorization: "
                 "Basic <base64(user:pass)>`, l'en-tête et la charge utile des jetons **JWT "
                 "(`Header.Payload.Signature`)**, ainsi que l'enveloppe interne des cookies signés "
                 '`set_secure_cookie` de Tornado.\n'
                 '\n'
                 "Sous Linux, l'option `base64 -w 0` produit une chaîne continue dépourvue de "
                 'retour à la ligne parasite pour les en-têtes HTTP, tandis que `base64 -d` '
                 'restitue instantanément le contenu original sans jamais constituer un mécanisme '
                 'de chiffrement.',
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
  'explanation': 'Les fonctions de hachage généralistes comme SHA-256 sont spécifiquement '
                 'optimisées pour la vitesse matérielle, autorisant un attaquant équipé de '
                 'processeurs graphiques (GPU) à tester plusieurs milliards de candidats par '
                 'seconde sur une table de comptes divulguée.\n'
                 '\n'
                 'Le stockage sécurisé de mots de passe impose par conséquent le recours exclusif '
                 'à une fonction de dérivation de clé (**KDF**, *Key Derivation Function*) '
                 'volontairement coûteuse en temps CPU et en mémoire, systématiquement associée à '
                 'un sel aléatoire unique par utilisateur, telle que `hashlib.pbkdf2_hmac`, '
                 '`hashlib.scrypt`, Argon2id ou `openssl passwd -6`.',
  'code_example': '# 1. Générer un hash de mot de passe salé SHA-512 sous Linux :\n'
                  'openssl passwd -6 "MotDePasseStagiaire2026!"\n'
                  '\n'
                  '# 2. Générer un hash PBKDF2-HMAC-SHA256 (600 000 itérations) en Python standard '
                  ':\n'
                  'python3 -c "import hashlib, secrets; sel = secrets.token_hex(16); \\\n'
                  "h = hashlib.pbkdf2_hmac('sha256', b'Secret2026!', sel.encode(), 600000).hex(); "
                  'print(f\'pbkdf2:sha256:600000${sel}${h}\')"'},
 {'id': 'linux_ports_ss_lsof',
  'term': 'Inspection des Ports & Processus Linux (ss -tulpn, lsof -i, kill)',
  'category': 'Linux & Réseau Prod',
  'level': 'Addendum Linux',
  'short': "Commandes système permettant d'identifier quel programme écoute sur un port TCP (ex. "
           ':8888) et de libérer un port bloqué.',
  'analogy': 'Le tableau de contrôle de la capitainerie du port : permet de voir instantanément '
             'quel navire (processus `PID`) est amarré au quai n°8888 lorsque Tornado affiche '
             "l'erreur `Address already in use`.",
  'explanation': "L'utilitaire moderne **`ss -tulpn`** (*Socket Statistics*, successeur direct de "
                 "`netstat`) dresse l'inventaire instantané des sockets TCP (`-t`) et UDP (`-u`) "
                 'en écoute (`-l`) avec résolution numérique des ports (`-n`) et identification du '
                 'processus propriétaire (`-p`), tandis que **`lsof -i :8888`** cible '
                 'chirurgicalement le démon occupant un port précis.\n'
                 '\n'
                 "Lors de l'arrêt d'une instance en production, l'envoi préalable du signal "
                 'gracieux `kill -15 <PID>` (`SIGTERM`) permet à la boucle `IOLoop` de Tornado '
                 "d'achever les requêtes en vol et de refermer proprement ses descripteurs SQLite, "
                 'réservant `kill -9 <PID>` (`SIGKILL`) aux seuls processus totalement figés.',
  'code_example': '# 1. Lister tous les serveurs en écoute sur la machine Linux :\n'
                  'sudo ss -tulpn | grep -E "8888|8001|80|443"\n'
                  '\n'
                  '# 2. Trouver le PID exact qui bloque le port 8888 :\n'
                  'lsof -i :8888\n'
                  '# ou :\n'
                  'fuser 8888/tcp\n'
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
  'explanation': "Le diagnostic méthodique d'une connectivité API s'opère couche par couche : `ip "
                 '-br a` synthétise les interfaces et adresses IP locales du serveur Linux, puis '
                 '`dig +short domaine.dz` interroge la résolution DNS afin de valider '
                 "l'enregistrement A ou AAAA associé au nom d'hôte.\n"
                 '\n'
                 "Une fois l'adresse IP confirmée, la commande **`nc -zv HOTE PORT`** (Netcat) "
                 'éprouve isolément la poignée de main TCP (*3-way handshake*) sur le port cible, '
                 'permettant de vérifier en une fraction de seconde si une base relationnelle '
                 '(`:5432`) ou un démon Tornado (`:8889`) traverse effectivement les règles de '
                 'pare-feu.',
  'code_example': '# 1. Afficher les adresses IP locales du serveur de manière lisible :\n'
                  'ip -br addr show\n'
                  '\n'
                  '# 2. Tester si le port TCP 8888 est ouvert en local ou à distance :\n'
                  'nc -zv 127.0.0.1 8888\n'
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
  'explanation': "Présent nativement sur tout serveur disposant d'un interpréteur Python sans "
                 'nécessiter de paquet tiers, le module **`python3 -m json.tool`** valide la '
                 "syntaxe d'une réponse brute issue de `curl` et l'indente proprement sur la "
                 'sortie standard.\n'
                 '\n'
                 "Pour l'exploration interactive et les scripts d'exploitation avancés, le "
                 "processeur **`jq`** offre un langage de requêtage algébrique capable d'extraire "
                 'une métadonnée imbriquée (`.meta.total_items`), de projeter un tableau '
                 '(`.data[]`) ou de filtrer dynamiquement les enregistrements selon un prédicat '
                 'métier (`select(.duree_jours >= 5)`).',
  'code_example': '# 1. Indenter une réponse curl avec Python (sans installer jq) :\n'
                  'curl -s http://127.0.0.1:8888/api/sandbox/formations | python3 -m json.tool\n'
                  '\n'
                  '# 2. Extraire uniquement les titres des formations avec jq :\n'
                  "curl -s http://127.0.0.1:8888/api/sandbox/formations | jq '.data[].titre'\n"
                  '\n'
                  '# 3. Filtrer les formations de 5 jours ou plus avec jq :\n'
                  "curl -s http://127.0.0.1:8888/api/sandbox/formations | jq '.data[] | "
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
  'explanation': 'En supervision opérationnelle, `tail -f fichier.log` (ou `journalctl -u service '
                 '-f` sous systemd) diffuse en continu chaque événement inscrit par les instances '
                 'Tornado, tandis que `grep` isole instantanément une anomalie HTTP (`" 500 "`, `" '
                 '401 "`) ou reconstitue le parcours complet d\'un identifiant de corrélation '
                 '`X-Request-ID`.\n'
                 '\n'
                 'Pour quantifier une anomalie de trafic ou détecter un abus automatisé, le '
                 'chaînage Unix `awk`, `sort` et `uniq -c | sort -nr` agrège des centaines de '
                 "milliers de lignes de journaux Nginx ou Tornado afin d'établir en quelques "
                 'secondes le palmarès des adresses IP les plus consommatrices.',
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
  'explanation': 'Appliquer le masque octal **`chmod 600` (`-rw-------`)** restreint strictement '
                 "la lecture et l'écriture d'un fichier à son seul compte propriétaire Linux en "
                 'retirant tout privilège aux autres utilisateurs locaux du système : ce '
                 'verrouillage est impératif sur les fichiers `.env`, les clés privées TLS '
                 '`private.pem` et les identités SSH.\n'
                 '\n'
                 'En complément, la directive shell `export` (ou la directive `EnvironmentFile=` '
                 "d'une unité `systemd`) injecte ces paramètres sensibles directement dans "
                 "l'espace mémoire du processus Tornado, qui les consulte proprement via "
                 '`os.environ.get(...)` sans jamais les exposer dans le dépôt de code source.',
  'code_example': '# 1. Restreindre la lecture du fichier .env et de la clé privée au seul '
                  'propriétaire :\n'
                  'chmod 600 .env private_key.pem\n'
                  'ls -l .env  # Affiche : -rw------- 1 abdelouahab abdelouahab ...\n'
                  '\n'
                  "# 2. Exporter une variable d'environnement et lancer l'API Tornado :\n"
                  'export TORNADO_COOKIE_SECRET="$(openssl rand -hex 32)"\n'
                  '.venv/bin/python app.py'},
 {'id': 'linux_systemd_nginx',
  'term': 'Déploiement Linux : Service systemd, Cluster Tornado (HTTPServer xheaders=True) & '
          'Reverse Proxy Nginx',
  'category': 'Linux & Réseau Prod',
  'level': 'Addendum Linux',
  'short': "Architecture standard permettant de faire tourner un cluster d'instances Tornado "
           '24h/24 en tâche de fond avec redémarrage automatique et HTTPS.',
  'analogy': 'Transformer un moteur posé sur un établi (`python app.py`) en une centrale '
             'électrique multi-turbines (`systemd` + 4 instances `HTTPServer` sur les ports '
             '`8001..8004`) protégée par un poste de garde blindé (`Nginx`).',
  'explanation': 'En production Linux, le gestionnaire de services **`systemd`** '
                 "(`/etc/systemd/system/isgp-tornado@.service`) supervise le cycle de vie d'une "
                 "flotte d'instances Tornado indépendantes, assurant leur démarrage au boot, la "
                 'collecte centralisée de leurs journaux et leur relance automatique en cas de '
                 'défaillance (`Restart=always`).\n'
                 '\n'
                 'Placé en coupure frontale sur les ports publics `80` et `443`, le répartiteur '
                 '**`Nginx`** absorbe la négociation cryptographique TLS, filtre les requêtes '
                 'malformées et distribue la charge applicative vers le bloc `upstream` local en '
                 "propageant l'adresse IP réelle aux serveurs `HTTPServer(app, xheaders=True)`.",
  'code_example': "# Commandes d'exploitation du service systemd en production :\n"
                  'sudo systemctl daemon-reload\n'
                  'sudo systemctl enable --now isgp-tornado@8001 isgp-tornado@8002\n'
                  'sudo systemctl status isgp-tornado@8001\n'
                  '\n'
                  '# Consulter les journaux du service en temps réel :\n'
                  'sudo journalctl -u "isgp-tornado@*" -f'},
 {'id': 'mime_content_type_accept_415',
  'term': 'Types MIME (Content-Type vs Accept), self.request.headers & Code 415',
  'category': 'Types MIME & Tornado',
  'level': 'Fondamental',
  'short': "Identifiant normalisé IANA (type/sous-type) décrivant le format exact d'un flux "
           "d'octets HTTP et pilotant la négociation de contenu dans Tornado.",
  'analogy': "L'étiquette réglementaire collée sur un conteneur maritime : 'Liquide', 'Poudre' ou "
             "'Gaz'. Sans cette étiquette (Content-Type), le destinataire ne sait pas avec quel "
             'outil ouvrir le conteneur.',
  'explanation': "La négociation documentaire HTTP repose sur une paire d'en-têtes complémentaires "
                 'inspectés dans Tornado via `self.request.headers` : **`Content-Type`** déclare '
                 'la nature exacte des octets actuellement véhiculés dans le corps du message (par '
                 "exemple `application/json; charset=utf-8`), tandis qu'**`Accept`** exprime les "
                 "représentations que le client appelant est capable d'interpréter en retour.\n"
                 '\n'
                 "Lorsqu'un client transmet en `POST` ou `PUT` une charge utile dont le type MIME "
                 "n'est pas pris en charge par le contrôleur, la sémantique HTTP impose de rejeter "
                 'immédiatement la requête avec le statut normatif **`415 Unsupported Media '
                 'Type`** via `self.set_status(415)`.',
  'code_example': '# Inspecter le type MIME entrant et rejeter proprement en 415 dans un '
                  'RequestHandler :\n'
                  'ctype = self.request.headers.get("Content-Type", "").split(";")[0].strip()\n'
                  'if ctype not in ("application/json", "application/x-www-form-urlencoded"):\n'
                  '    self.set_status(415)\n'
                  '    self.write({"erreur": f"Type MIME {ctype} non supporté"})\n'
                  '    return'},
 {'id': 'mime_json_vs_form_vs_multipart',
  'term': "Types MIME d'Entrée (POST) : application/json vs x-www-form-urlencoded vs "
          'multipart/form-data',
  'category': 'Types MIME & Tornado',
  'level': "Cœur d'API",
  'short': 'Les trois grands types MIME utilisés pour envoyer des données à un serveur Tornado '
           "lors d'une requête POST ou PUT.",
  'analogy': "Trois façons de transmettre un dossier à l'administration : un fichier informatique "
             'structuré (`application/json`), un coupon-réponse papier '
             '(`application/x-www-form-urlencoded`), ou une pochette cartonnée contenant à la fois '
             'le coupon papier et des pièces jointes PDF (`multipart/form-data`).',
  'explanation': "Dans un `RequestHandler` Tornado, le mode d'extraction des données entrantes "
                 'dépend directement du `Content-Type` reçu : un flux **`application/json`** émis '
                 'par `fetch()`, une application mobile ou `curl` se désérialise depuis les octets '
                 'bruts via **`tornado.escape.json_decode(self.request.body)`**.\n'
                 '\n'
                 "À l'inverse, un formulaire Web classique `<form method='POST'>` encodé en "
                 "**`application/x-www-form-urlencoded`** s'extrait champ par champ au moyen de "
                 "**`self.get_body_argument('champ')`**, tandis qu'un envoi mixte "
                 '**`multipart/form-data`** répartit ses champs textuels dans '
                 '`self.get_body_argument(...)` et ses pièces jointes binaires dans le '
                 'dictionnaire **`self.request.files`**.',
  'code_example': 'ctype = self.request.headers.get("Content-Type", "")\n'
                  'if "application/json" in ctype:\n'
                  '    data = tornado.escape.json_decode(self.request.body)\n'
                  'else:\n'
                  '    titre = self.get_body_argument("titre", "")\n'
                  '    fichiers = self.request.files.get("document_pdf", [])'},
 {'id': 'mime_response_csv_xml_sse',
  'term': "Émettre des Types MIME Personnalisés (self.set_header('Content-Type', ...) : CSV, XML, "
          'Problem+JSON, SSE)',
  'category': 'Types MIME & Tornado',
  'level': "Cœur d'API",
  'short': "Utilisation de self.set_header('Content-Type', ...) et self.write(...) dans Tornado "
           'pour retourner tout format autre que HTML ou JSON standard.',
  'analogy': "Si `self.render()` est l'imprimante de brochures HTML et `self.write(dict)` "
             "l'emballeur automatique de colis JSON, `self.set_header('Content-Type', ...)` suivi "
             "de `self.write(bytes)` est l'atelier sur mesure capable d'expédier des feuilles "
             'Excel CSV, des actes XML ou un flux continu.',
  'explanation': 'Un même serveur Tornado peut projeter ses données métier sous de multiples types '
                 "MIME normalisés en configurant `self.set_header('Content-Type', ...)` : "
                 '**`text/csv`** couplé à `Content-Disposition: attachment` génère des exports '
                 "tabulaires pour tableurs, tandis qu'**`application/xml`** assure "
                 "l'interopérabilité avec les bus SOAP patrimoniaux.\n"
                 '\n'
                 'Pour la gouvernance moderne des erreurs, **`application/problem+json`** véhicule '
                 'les diagnostics structurés conformes au standard **RFC 7807**, alors que '
                 "**`text/event-stream`** maintient une connexion HTTP ouverte sur l'`IOLoop` pour "
                 "diffuser des événements temps réel (**SSE**) au fil d'appels successifs à `await "
                 'self.flush()`.',
  'code_example': 'class ExportCSVHandler(tornado.web.RequestHandler):\n'
                  '    def get(self):\n'
                  '        csv_data = "id,titre,duree\\n1,API REST,5\\n"\n'
                  '        self.set_header("Content-Type", "text/csv; charset=utf-8")\n'
                  '        self.set_header("Content-Disposition", \'attachment; '
                  'filename="formations.csv"\')\n'
                  '        self.write(csv_data)'},
 {'id': 'mime_send_file_disposition_nosniff',
  'term': 'Fichiers Binaires (application/pdf, image/png, Content-Disposition) & '
          'X-Content-Type-Options: nosniff',
  'category': 'Types MIME & Tornado',
  'level': 'Intermédiaire',
  'short': 'Transmission de fichiers binaires dans Tornado avec self.write(bytes), contrôle de '
           "l'ouverture navigateur (inline vs attachment) et protection contre le MIME Sniffing.",
  'analogy': 'Envoyer un document PDF soit sous verre pour être lu sur place dans le navigateur '
             '(`inline`), soit dans une enveloppe scellée que le navigateur enregistre directement '
             'dans le dossier Téléchargements (`attachment`).',
  'explanation': "Lors de la restitution d'un document binaire tel qu'une attestation PDF ou un "
                 "graphique vectoriel, l'en-tête **`Content-Disposition: inline; "
                 'filename="facture.pdf"`** invite le navigateur à prévisualiser directement le '
                 "média dans l'onglet actif, tandis que la directive **`attachment`** déclenche "
                 "systématiquement la boîte de dialogue d'enregistrement sur disque.\n"
                 '\n'
                 'Pour prévenir toute exécution accidentelle de code malveillant dissimulé dans un '
                 "fichier téléversé par un tiers, l'ajout systématique de "
                 '**`X-Content-Type-Options: nosniff`** interdit au navigateur de deviner le '
                 "format par inspection heuristique et l'oblige à respecter strictement le type "
                 'MIME déclaré par le serveur.',
  'code_example': 'class FacturePDFHandler(tornado.web.RequestHandler):\n'
                  '    def get(self):\n'
                  '        self.set_header("Content-Type", "application/pdf")\n'
                  '        self.set_header("Content-Disposition", \'attachment; '
                  'filename="facture.pdf"\')\n'
                  '        self.set_header("X-Content-Type-Options", "nosniff")\n'
                  '        self.write(b"%PDF-1.4 ...")'},
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
  'explanation': 'En vertu du principe de robustesse (*Tolerant Reader* ou loi de Postel), '
                 "enrichir une réponse JSON d'un nouvel attribut, ouvrir une route inédite ou "
                 'accepter un paramètre de requête facultatif ne brise aucun consommateur '
                 "existant, ce qui permet à une branche majeure `/api/v1` d'évoluer sereinement "
                 'durant cinq à dix ans.\n'
                 '\n'
                 'Inscrire explicitement le préfixe **`/api/v1`** dès la publication initiale '
                 'demeure néanmoins indispensable : si des milliers de terminaux mobiles compilés '
                 'pointent vers une racine dépourvue de numéro de version (`/api/formations`), '
                 "l'introduction ultérieure d'une refonte incompatible deviendrait impossible sans "
                 'rompre brutalement le parc installé.',
  'code_example': '# Coexistence de /api/v1 et /api/v2 dans la table de routage Tornado :\n'
                  'app = tornado.web.Application([\n'
                  '    (r"/api/v1/formations", FormationsV1Handler),\n'
                  '    (r"/api/v2/formations", FormationsV2Handler),\n'
                  '])'},
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
  'explanation': 'Une évolution est qualifiée de **rétrocompatible (*Non-Breaking*)** et demeure '
                 "au sein de `/api/v1` lorsqu'elle se limite à ajouter une clé informative en "
                 'sortie, à exposer un point de terminaison supplémentaire (`GET '
                 "/api/v1/certificats`) ou à introduire un filtre optionnel doté d'une valeur par "
                 'défaut.\n'
                 '\n'
                 'Constitue en revanche une **rupture de contrat (*Breaking Change*)** exigeant '
                 "l'ouverture parallèle d'une branche `/api/v2` tout renommage ou suppression "
                 "d'attribut existant (`intitule` remplacé par `titre`), toute mutation du type "
                 'structurel d\'un champ (`"duree": 5` devenant un objet imbriqué) ou le passage '
                 "d'un champ facultatif à obligatoire en entrée.",
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
  'explanation': "L'extinction civilisée d'une version d'API obéit au protocole **IETF RFC 8594** "
                 ": le contrôleur Tornado maintient temporairement l'ancienne branche active tout "
                 "en émettant l'en-tête **`Deprecation: true`**, l'échéance formelle d'arrêt "
                 '**`Sunset: Thu, 31 Dec 2026 23:59:59 GMT`** ainsi que le pointeur de migration '
                 '**`Link: </api/v2/formations>; rel="successor-version"`**.\n'
                 '\n'
                 'Une fois la date `Sunset` échue et la migration des partenaires achevée, la '
                 'route décommissionnée ne doit pas renvoyer un simple `404` ambigu, mais le '
                 'statut explicite **`410 Gone`** attestant que la ressource a bien existé par le '
                 "passé avant d'être définitivement retirée du catalogue.",
  'code_example': 'class FormationsV1Handler(tornado.web.RequestHandler):\n'
                  '    def set_default_headers(self):\n'
                  '        self.set_header("Deprecation", "true")\n'
                  '        self.set_header("Sunset", "Thu, 31 Dec 2026 23:59:59 GMT")\n'
                  '        self.set_header("Link", \'</api/v2/formations>; '
                  'rel="successor-version"\')'},
 {'id': 'api_envelope_pagination_cursor_offset',
  'term': 'Enveloppe JSON (meta / data / links) & Pagination (Offset/Limit vs Cursor)',
  'category': 'Architecture Web',
  'level': 'Intermédiaire',
  'short': "Structuration racine d'une réponse JSON de collection pour permettre l'évolution sans "
           'Breaking Change et la pagination haute performance.',
  'analogy': "Ne jamais expédier des feuilles volantes sans chemise cartonnée : l'objet enveloppe "
             '`{"meta": ..., "data": [...]}` est la chemise sur laquelle on peut inscrire le '
             'numéro de page et le total sans toucher aux feuilles `data`.',
  'explanation': "Retourner un tableau JSON nu `[...]` à la racine d'une réponse fige "
                 "définitivement le contrat en interdisant l'ajout ultérieur de métadonnées ; "
                 "Tornado bloque d'ailleurs nativement `self.write([1, 2])` par un `TypeError` "
                 "historique de sécurité, encourageant l'emploi systématique d'une enveloppe "
                 'dictionnaire `{"meta": {...}, "data": [...]}`.\n'
                 '\n'
                 "À l'intérieur de cette enveloppe, la pagination **`Offset/Limit`** "
                 '(`?page=2&per_page=20`) convient aux grilles administratives numérotées sur '
                 'volumes modérés, tandis que la pagination par **curseur (`Keyset`, '
                 "`?after_id=1042&limit=20`)** exploite directement l'index primaire SQL (`WHERE "
                 'id > ?`) pour garantir un temps constant sur plusieurs millions de lignes.',
  'code_example': 'self.write({\n'
                  '    "meta": {"version": "v2", "page": 1, "per_page": 20, "total_items": 145},\n'
                  '    "data": formations,\n'
                  '    "links": {"self": "/api/v2/formations?page=1", "next": '
                  '"/api/v2/formations?page=2"}\n'
                  '})'},
 {'id': 'swagger_openapi_3',
  'term': 'Swagger UI (/api/docs), Swagger Editor & Spécification OpenAPI 3.0 (OAS)',
  'category': 'Architecture Web',
  'level': "Cœur d'API",
  'short': "Norme mondiale de contrat d'API (OpenAPI 3.0 JSON/YAML) et portail Web interactif "
           '(Swagger UI) permettant de documenter et tester une API dans le navigateur.',
  'analogy': "OpenAPI 3.0 est le plan d'architecte coté et normalisé de l'immeuble "
             '(`openapi.json`), tandis que Swagger UI est la visite virtuelle interactive générée '
             'automatiquement à partir de ce plan (boutons « Authorize » et « Try it out »).',
  'explanation': "Gouvernée par l'OpenAPI Initiative au sein de la Linux Foundation, l'**OpenAPI "
                 "Specification (`OAS 3.0` / `3.1`)** formalise l'intégralité d'une API REST dans "
                 "un document déclaratif décrivant les métadonnées `info`, les `servers`, l'arbre "
                 '`paths` à variables entre accolades `{id}`, les modèles réutilisables '
                 "`components.schemas` (`$ref`) et les mécanismes d'authentification "
                 '`securitySchemes`.\n'
                 '\n'
                 'Exposé sur `/api/openapi.json`, ce contrat machine alimente simultanément le '
                 'portail visuel **Swagger UI (`/api/docs`)** — doté du cadenas **Authorize** et '
                 "du mode d'essai direct **Try it out** — ainsi que l'importation automatisée dans "
                 'Postman, Insomnia ou les générateurs de SDK clients.',
  'code_example': '# Handler Tornado exposant le contrat OpenAPI 3.0.3 :\n'
                  'class OpenAPIHandler(tornado.web.RequestHandler):\n'
                  '    def get(self):\n'
                  '        self.write({"openapi": "3.0.3", "info": {"title": "API ISGP Tornado", '
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
  'explanation': "Trois familles de clients complémentaires rythment l'ingénierie quotidienne "
                 "d'une API Tornado : omniprésent sur tout serveur Unix ou conteneur minimaliste, "
                 "**`curl`** permet d'inspecter les en-têtes (`-i`), la négociation réseau (`-v`), "
                 'le verbe (`-X`) et le corps (`-d`) directement en terminal ou dans un pipeline '
                 'CI/CD.\n'
                 '\n'
                 'Pour la conception collaborative et la recette fonctionnelle, les ateliers '
                 'graphiques **Postman, Bruno et Insomnia** organisent des collections versionnées '
                 "enrichies de variables d'environnement, tandis qu'**HTTPie (`http`)** et "
                 "l'extension **REST Client (`.http`)** offrent une syntaxe concise directement "
                 "intégrée à l'éditeur de code.",
  'code_example': 'curl -i -X POST "http://127.0.0.1:8888/api/sandbox/formations" \\\n'
                  '  -H "Content-Type: application/json" \\\n'
                  '  -H "X-API-Key: isgp-secret-2026" \\\n'
                  '  -d \'{"titre": "API Tornado", "duree_jours": 5}\''},
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
  'explanation': "En l'absence de limitation de débit, une simple boucle infinie accidentelle chez "
                 'un client partenaire ou une attaque par force brute suffirait à monopoliser les '
                 'descripteurs réseau et le processeur de votre serveur Tornado.\n'
                 '\n'
                 'En comptabilisant les requêtes par adresse IP (`self.request.remote_ip`) ou par '
                 'identité cliente dès le hook `prepare()`, le contrôleur intercepte tout '
                 'dépassement de seuil en retournant le statut normatif **`429 Too Many '
                 'Requests`** assorti des en-têtes `X-RateLimit-Remaining: 0` et `Retry-After`, '
                 "avant d'interrompre immédiatement le cycle par `self.finish()`.",
  'code_example': '# Si le client dépasse 3 requêtes en 20 secondes dans prepare(self) :\n'
                  'self.set_status(429)\n'
                  'self.set_header("Retry-After", "20")\n'
                  'self.finish({"erreur": "Quota dépassé (Rate Limit)", "reessayer_dans_secondes": '
                  '20})'},
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
  'explanation': 'Un jeton porteur (**Bearer Token** ou **JWT**) repose sur une distinction '
                 'cryptographique essentielle : sa charge utile (`Payload`) est simplement encodée '
                 "en Base64url afin d'être lisible sans déchiffrement, mais son intégrité est "
                 'scellée par une signature mathématique calculée avec la `SECRET_KEY` du '
                 'serveur.\n'
                 '\n'
                 "Parce que n'importe quel intermédiaire ayant accès au jeton peut décoder ses "
                 "revendications en clair, on n'y inscrit jamais de secret ni de mot de passe, "
                 "mais uniquement l'identifiant du sujet (`sub`), son rôle et son horodatage "
                 "d'expiration (`exp`).",
  'code_example': '# En-tête HTTP envoyé par le client :\n'
                  '# Authorization: Bearer eyJhbGciOi...\n'
                  '\n'
                  'auth = self.request.headers.get("Authorization", "")\n'
                  'if auth.startswith("Bearer "):\n'
                  '    token = auth.split(" ", 1)[1]'},
 {'id': 'refresh_token_rbac',
  'term': 'Authentification (AuthN / 401) vs Autorisation (AuthZ / 403, RBAC, Scopes & BOLA)',
  'category': 'Sécurité & Architecture API',
  'level': "Cœur d'API",
  'short': 'AuthN vérifie QUI vous êtes (échec = 401 Unauthorized) ; AuthZ vérifie QUELS sont vos '
           'droits sur la ressource (échec = 403 Forbidden).',
  'analogy': "Le passeport contrôlé à l'entrée de l'aéroport est l'Authentification (`AuthN` -> "
             "`401` si absent). La carte d'accès réservée aux pilotes pour entrer dans le cockpit "
             "est l'Autorisation (`AuthZ` -> `403` si vous êtes un simple passager).",
  'explanation': "Une gouvernance d'accès complète sépare nettement l'**Authentification "
                 "(`AuthN`)**, qui établit l'identité de l'appelant par jeton Bearer ou clé "
                 "`X-API-Key` sous peine de rejet `401`, de l'**Autorisation (`AuthZ`)**, qui "
                 'évalue ses prérogatives effectives sous peine de rejet `403`.\n'
                 '\n'
                 "En ingénierie d'API, cette autorisation combine trois verrous complémentaires : "
                 'le contrôle par rôle métier (**RBAC**, `stagiaire` face à `admin`), la '
                 'vérification des permissions déléguées au jeton (**Scopes OAuth2** tels que '
                 "`formations:read`) et le contrôle strict de propriété de l'enregistrement "
                 "(`dossier.proprietaire == self.current_user['sub']`) neutralisant la faille "
                 '**OWASP BOLA**.',
  'code_example': 'if not token_valide:\n'
                  '    self.set_status(401)\n'
                  '    self.write({"etape": "AuthN", "erreur": "Non authentifié"})\n'
                  '    return\n'
                  'if user["role"] != "admin" or "audit:admin" not in user["scopes"]:\n'
                  '    self.set_status(403)\n'
                  '    self.write({"etape": "AuthZ", "erreur": "Droits insuffisants"})'},
 {'id': 'secret_env',
  'term': "Secrets & Variables d'Environnement (.env / os.environ)",
  'category': 'Sécurité & Architecture API',
  'level': "Cœur d'API",
  'short': 'Pratique fondamentale consistant à stocker les mots de passe, clés de signature et '
           "clés d'API hors du code source Python.",
  'analogy': 'Vous ne gravez jamais le code de votre coffre-fort sur la façade extérieure de votre '
             "maison. Vous le gardez dans une enveloppe scellée à l'intérieur du coffre de la "
             "direction (les variables d'environnement du serveur).",
  'explanation': "Une règle d'hygiène cardinale en génie logiciel interdit d'inscrire en clair une "
                 'clé de signature, un mot de passe de base de données ou un jeton partenaire '
                 'directement dans un fichier Python versionné sous Git, où il demeurerait exposé '
                 "dans l'historique des commits.\n"
                 '\n'
                 'Conformément à la méthodologie *Twelve-Factor App*, tous les secrets résident '
                 "exclusivement dans les variables d'environnement du système hôte ou d'un "
                 'coffre-fort dédié, et sont lus dynamiquement au démarrage du processus Tornado '
                 "via `os.environ.get('API_SECRET_KEY')`.",
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
  'explanation': "Le code d'authentification **HMAC-SHA256** constitue la brique cryptographique "
                 "polyvalente des architectures Tornado : il scelle aussi bien les jetons d'accès "
                 'légers et les cookies sécurisés que les notifications asynchrones **Webhooks** '
                 'entrantes vérifiées sur les octets exacts de `self.request.body` via '
                 '`X-Webhook-Signature`.\n'
                 '\n'
                 "Lors de la vérification côté serveur, l'opérateur standard `==` doit être "
                 'systématiquement écarté au profit de **`hmac.compare_digest(a, b)`**, dont le '
                 "temps d'exécution constant empêche un attaquant de déduire la signature octet "
                 'par octet en mesurant les micro-variations de latence réseau (*Timing Attack*).',
  'code_example': 'import hmac, hashlib\n'
                  'sig = hmac.new(SECRET.encode(), self.request.body, hashlib.sha256).hexdigest()\n'
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
  'explanation': "Le cycle de session Web s'articule entre l'en-tête serveur `Set-Cookie` émis "
                 "dans Tornado par `self.set_secure_cookie(...)` et l'en-tête client `Cookie` relu "
                 "via `self.get_secure_cookie(...)` jusqu'à sa révocation explicite par "
                 '`self.clear_cookie(...)`.\n'
                 '\n'
                 'Pour blinder ce transport navigateur, trois attributs défensifs doivent être '
                 'combinés : **`HttpOnly`** (`httponly=True`) occulte le cookie vis-à-vis de '
                 '`document.cookie` contre le vol par injection JavaScript **XSS**, **`Secure`** '
                 '(`secure=True`) exige un tunnel chiffré **HTTPS/TLS**, et **`SameSite=Strict` ou '
                 "`Lax`** bloque l'envoi automatique depuis un domaine tiers pour déjouer les "
                 'attaques **CSRF**.',
  'code_example': 'self.set_secure_cookie(\n'
                  '    "isgp_session",\n'
                  '    json.dumps({"sub": "yasmine", "role": "admin"}),\n'
                  '    httponly=True,     # Invisible pour document.cookie (Anti-XSS)\n'
                  '    secure=True,       # HTTPS uniquement\n'
                  '    samesite="Strict"  # Anti-CSRF\n'
                  ')'},
 {'id': 'signed_session_cookie_hmac',
  'term': 'Cookie Signé Horodaté Tornado (set_secure_cookie / get_secure_cookie) vs Cookie '
          'Standard (set_cookie)',
  'category': 'Sécurité & Architecture API',
  'level': "Cœur d'API",
  'short': "Différence fondamentale entre un cookie ordinaire modifiable par l'utilisateur et un "
           'cookie signé cryptographiquement avec cookie_secret dans Tornado.',
  'analogy': "Un cookie ordinaire (`self.set_cookie('theme', 'sombre')`) est écrit au crayon à "
             'papier : le client peut le gommer et le modifier. Un cookie signé '
             "(`self.set_secure_cookie`) est scellé par l'empreinte mathématique `HMAC-SHA256` de "
             '`cookie_secret` avec un horodatage anti-rejeu : la moindre retouche brise le sceau.',
  'explanation': 'Tornado opère une séparation stricte entre `self.set_cookie` / '
                 '`self.get_cookie`, dépourvus de signature et réservés aux seules préférences '
                 'visuelles non sensibles (`theme=sombre`, `lang=fr`), et son mécanisme '
                 'cryptographique natif **`self.set_secure_cookie` / `self.get_secure_cookie`**.\n'
                 '\n'
                 'Appuyé sur le paramètre `cookie_secret` déclaré dans `tornado.web.Application`, '
                 'un cookie sécurisé Tornado encode la charge utile en Base64, lui adjoint un '
                 "horodatage Unix et scelle l'ensemble par HMAC-SHA256 : la moindre falsification "
                 'opérée dans les outils de développement du navigateur conduit immédiatement '
                 '`self.get_secure_cookie()` à retourner `None`.',
  'code_example': 'app = tornado.web.Application(routes, '
                  'cookie_secret=os.environ["COOKIE_SECRET"])\n'
                  '\n'
                  '# Écriture signée par HMAC-SHA256 :\n'
                  'self.set_secure_cookie("isgp_session", "yasmine.merabet", httponly=True)\n'
                  '\n'
                  '# Lecture et vérification cryptographique (retourne bytes ou None) :\n'
                  'val = self.get_secure_cookie("isgp_session", max_age_days=1)'},
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
  'explanation': 'Un outil en ligne de commande tel que `curl` ou un client Python '
                 "`AsyncHTTPClient` n'est jamais affecté par **CORS**, car la politique de même "
                 'origine (*Same-Origin Policy*) est un mécanisme de confinement exécuté '
                 "exclusivement par les navigateurs Web pour protéger l'utilisateur connecté.\n"
                 '\n'
                 "Lorsqu'une application frontale hébergée sur un autre domaine s'apprête à "
                 "émettre un `POST`, `PUT` ou `DELETE` assorti d'un corps JSON ou d'un en-tête "
                 '`Authorization`, le navigateur expédie au préalable une sonde **`OPTIONS` '
                 '(*Preflight*)** que Tornado acquitte dans `def options(self)` par un statut `204 '
                 'No Content` accompagné des en-têtes `Access-Control-Allow-Origin`, '
                 '`Allow-Methods` et `Allow-Headers`.',
  'code_example': 'class BaseCORSHandler(tornado.web.RequestHandler):\n'
                  '    def set_default_headers(self):\n'
                  '        origine = self.request.headers.get("Origin")\n'
                  '        if origine in {"https://portail.isgp.dz", "http://localhost:3000"}:\n'
                  '            self.set_header("Access-Control-Allow-Origin", origine)\n'
                  '    def options(self, *args):\n'
                  '        self.set_status(204)\n'
                  '        self.finish()'},
 {'id': 'idempotence_put_patch',
  'term': 'Idempotence, PUT vs PATCH & Idempotency-Key',
  'category': 'Architecture Web',
  'level': "Cœur d'API",
  'short': "Propriété mathématique d'une opération qui produit le même état sur le serveur qu'elle "
           'soit exécutée 1 fois ou 10 fois.',
  'analogy': "Appuyer 5 fois sur le bouton d'appel d'un ascenseur au 3ème étage est **idempotent** "
             "(l'ascenseur vient une seule fois au 3ème). Appuyer 5 fois sur « Débiter 10 000 DZD "
             "» ne l'est pas !",
  'explanation': 'Au sens mathématique de la norme HTTP, les méthodes `GET`, `PUT` (remplacement '
                 "intégral d'un enregistrement) et `DELETE` sont **idempotentes** : soumettre une "
                 "ou dix fois la même requête laisse l'état final du serveur rigoureusement "
                 'identique, tandis que `PATCH` applique une modification ciblée sur un '
                 'sous-ensemble de champs.\n'
                 '\n'
                 "À l'inverse, `POST` n'est pas idempotent par défaut ; pour prévenir toute double "
                 "facturation ou création en doublon lorsqu'un terminal mobile répète sa requête "
                 'après une micro-coupure réseau, le client joint un identifiant unique '
                 '**`Idempotency-Key: <uuid>`** mémorisé côté serveur.',
  'code_example': '# En-tête envoyé sur un POST critique :\n'
                  '# Idempotency-Key: tx-2026-0001\n'
                  'cle = self.request.headers.get("Idempotency-Key")'},
 {'id': 'pagination_filtering',
  'term': 'Pagination (page/limit), Filtrage & Tri',
  'category': 'Architecture Web',
  'level': 'Fondamental',
  'short': "Découpage d'une grande collection en tranches via les paramètres d'URL "
           '`?page=1&limit=20&tri=duree_jours`.',
  'analogy': 'Consulter un catalogue de 50 000 articles par pages de 20 résultats au lieu '
             "d'imprimer les 50 000 lignes d'un seul bloc.",
  'explanation': 'Le découpage par décalage (*Offset Pagination*) repose sur la relation '
                 'arithmétique `offset = (page - 1) * limit`, traduite par un tranchage '
                 '`resultats[offset : offset + limit]` en mémoire Python ou par une clause '
                 'paramétrée `LIMIT ? OFFSET ?` en SQL.\n'
                 '\n'
                 "Afin de guider l'interface cliente sans ambiguïté, le contrôleur Tornado "
                 'restitue les enregistrements dans une enveloppe structurée associant le tableau '
                 '`data` à un bloc `meta` détaillant `total_items`, `total_pages` et les '
                 'indicateurs de navigation.',
  'code_example': 'page = max(1, int(self.get_query_argument("page", "1")))\n'
                  'limit = min(100, int(self.get_query_argument("limit", "10")))\n'
                  'offset = (page - 1) * limit'},
 {'id': 'jinja2_forms_request_form',
  'term': 'Templates Tornado (tornado.template / self.render) & Formulaires HTML '
          '(get_body_argument / request.files)',
  'category': 'Tornado',
  'level': "Cœur d'API",
  'short': 'Séparation propre du HTML dans le dossier templates/ avec tornado.template et '
           'traitement des formulaires Web envoyés en application/x-www-form-urlencoded ou '
           'multipart/form-data.',
  'analogy': "Le moteur `tornado.template` est le moule d'imprimerie (`.html`) dans lequel Tornado "
             'injecte les variables Python (`{{ titre }}`) sans jamais mélanger le HTML dans le '
             'code Python. `self.get_body_argument()` est le guichet qui lit les bordereaux papier '
             "(`<form method='POST'>`), tandis que `tornado.escape.json_decode(self.request.body)` "
             'lit les colis électroniques JSON.',
  'explanation': 'Une architecture Tornado propre bannit toute concaténation HTML dans le code '
                 'Python en déclarant `template_path` sur `tornado.web.Application` et en '
                 "invoquant `self.render('page.html', formations=liste)`, qui échappe "
                 'automatiquement les expressions `{{ variable }}` contre les failles XSS et '
                 'structure ses blocs `{% for ... %}` et `{% if ... %}` fermés par `{% end %}`.\n'
                 '\n'
                 "À la soumission d'un formulaire `<form method='POST'>`, les champs encodés en "
                 '`application/x-www-form-urlencoded` sont extraits par '
                 "**`self.get_body_argument('titre')`**, tandis que les documents transmis via "
                 "`enctype='multipart/form-data'` sont réceptionnés sous forme de dictionnaires "
                 '(`filename`, `body`, `content_type`) dans **`self.request.files`**.',
  'code_example': 'class FormationsPageHandler(tornado.web.RequestHandler):\n'
                  '    def get(self):\n'
                  '        self.render("formations.html", formations=FORMATIONS)\n'
                  '    def post(self):\n'
                  '        titre = self.get_body_argument("titre", "").strip()\n'
                  '        duree = int(self.get_body_argument("duree_jours", "1"))\n'
                  '        self.render("formations.html", formations=FORMATIONS)'},
 {'id': 'path_variables_syntax',
  'term': "Variables d'URL : Groupes Regex ([0-9]+) (Tornado) vs :variable (Postman/Node) vs "
          '{variable} (OpenAPI)',
  'category': 'Tornado',
  'level': 'Fondamental',
  'short': 'Les trois notations différentes utilisées selon les frameworks et outils pour '
           "représenter un paramètre dynamique dans le chemin d'une URL.",
  'analogy': "Trois façons d'écrire un champ à remplir sur un formulaire administratif selon "
             "l'outil : une expression régulière `([0-9]+)` (Tornado), `:nom` (Postman/Express), "
             'ou `{nom}` (OpenAPI/FastAPI). Le principe est identique, seule la syntaxe change '
             "selon l'outil.",
  'explanation': "Chaque écosystème Web possède sa notation propre pour exprimer un segment d'URI "
                 'variable : dans `tornado.web.Application`, le routage repose sur des **groupes '
                 "capturants d'expressions régulières** tels que `r'/api/formations/([0-9]+)'` (ou "
                 '`(?P<id>[0-9]+)`), qui injectent la sous-chaîne capturée directement en '
                 'paramètre de `def get(self, id):`.\n'
                 '\n'
                 'En parallèle, Postman et Express adoptent le préfixe à deux-points '
                 '`/api/formations/:id`, tandis que la spécification **OpenAPI 3.0 (RFC 6570)** et '
                 'FastAPI normalisent la notation entre accolades `/api/formations/{id}`. Lors de '
                 "l'appel effectif dans `curl` ou un navigateur, ce marqueur abstrait cède "
                 'toujours la place à la valeur concrète (`/api/formations/42`).',
  'code_example': '# 1. Dans le code serveur Python Tornado (Regex) :\n'
                  'class FormationDetailHandler(tornado.web.RequestHandler):\n'
                  '    def get(self, formation_id: str):\n'
                  '        self.write({"id": int(formation_id)})\n'
                  '# Route : (r"/api/v1/formations/([0-9]+)", FormationDetailHandler)\n'
                  '\n'
                  '# 2. Dans Postman (Deux-points :variable) :\n'
                  '# GET http://127.0.0.1:8888/api/v1/formations/:id\n'
                  '\n'
                  '# 3. Dans OpenAPI 3.0 / Swagger (Accolades {variable}) :\n'
                  '# GET /api/v1/formations/{id}\n'
                  '\n'
                  '# 4. Dans curl (Valeur réelle) :\n'
                  '# curl -i http://127.0.0.1:8888/api/v1/formations/42'},
 {'id': 'middlewares_hooks',
  'term': 'Hooks de Cycle de Vie Tornado (set_default_headers, prepare, on_finish) & X-Request-ID',
  'category': 'Tornado',
  'level': 'Intermédiaire',
  'short': "Méthodes d'un BaseHandler exécutées automatiquement avant et après chaque requête pour "
           'la journalisation, le chronométrage et la corrélation.',
  'analogy': "Le portique de sécurité à l'entrée d'un bâtiment qui enregistre l'heure d'arrivée de "
             "chaque visiteur (`prepare`) et l'heure de sortie (`on_finish`) sur sa fiche "
             'individuelle (`self`).',
  'explanation': 'Parce que Tornado instancie un objet `RequestHandler` neuf et dédié pour chaque '
                 "requête HTTP entrante, l'instance `self` offre un espace mémoire naturellement "
                 "isolé d'un client à l'autre tout au long du traitement asynchrone.\n"
                 '\n'
                 'Une classe de base transversale exploite ce cycle en initialisant '
                 '`self.request_id` et le chronomètre haute résolution `time.perf_counter()` dans '
                 'le hook amont **`prepare(self)`**, puis en calculant la latence exacte pour '
                 "inscrire la trace d'audit finale dans le hook aval **`on_finish(self)`**.",
  'code_example': 'class BaseHandler(tornado.web.RequestHandler):\n'
                  '    def prepare(self):\n'
                  '        self.start = time.perf_counter()\n'
                  '        self.request_id = f"req-{uuid.uuid4().hex[:8]}"\n'
                  '        self.set_header("X-Request-ID", self.request_id)\n'
                  '\n'
                  '    def on_finish(self):\n'
                  '        ms = round((time.perf_counter() - self.start) * 1000, 2)\n'
                  '        print(f"[AUDIT] {self.request_id} {self.request.method} '
                  '{self.request.path} ({ms} ms)")'},
 {'id': 'wsgi_blueprints',
  'term': 'Sous-tables de Routage Modulaires, Application Factory & HTTPServer(xheaders=True)',
  'category': 'Tornado',
  'level': "Cœur d'API",
  'short': "Organisation modulaire d'une API Tornado (listes de routes par domaine) et déploiement "
           'multi-instances non bloquant derrière Nginx.',
  'analogy': "Les listes de routes par module sont les départements spécialisés d'une entreprise, "
             "et les 4 instances `HTTPServer` sur l'Event-Loop `IOLoop` sont l'équipe de "
             'guichetiers asynchrones haute vitesse derrière le répartiteur Nginx.',
  'explanation': "Sur une application d'envergure, l'architecture Tornado découpe ses points de "
                 'terminaison en sous-listes de routage modulaires par domaine métier '
                 '(`WEB_ROUTES`, `API_V1_ROUTES`, `API_V2_ROUTES`, `HEALTH_ROUTES`) fédérées au '
                 "sein d'une fabrique `make_app()` ou `create_app()`.\n"
                 '\n'
                 "Cette fabrique alimente à la fois la suite de tests d'intégration rapides "
                 '**`tornado.testing.AsyncHTTPTestCase`** (`self.fetch()`) en intégration continue '
                 'et le serveur non bloquant **`tornado.httpserver.HTTPServer(app, '
                 "xheaders=True)`** chargé d'interpréter `X-Forwarded-For` derrière un répartiteur "
                 'Nginx en production.',
  'code_example': "# Lancement d'une instance Tornado de production derrière Nginx :\n"
                  'server = tornado.httpserver.HTTPServer(create_app(), xheaders=True)\n'
                  'server.listen(8001, address="127.0.0.1")\n'
                  'tornado.ioloop.IOLoop.current().start()'},
 {'id': 'apikey_vs_token',
  'term': 'Clé API (X-API-Key) vs Jeton Bearer (Token)',
  'category': 'Sécurité & Architecture API',
  'level': "Cœur d'API",
  'short': 'La Clé API identifie une application/machine (longue durée), tandis que le Bearer '
           'Token identifie un utilisateur connecté (courte durée).',
  'analogy': "La **Clé API** est comme le badge d'accès permanent d'une société de livraison "
             "partenaire. Le **Bearer Token** est le ticket nominatif temporaire d'un visiteur "
             'valable uniquement pour la séance.',
  'explanation': "Bien que tous deux voyagent dans les en-têtes HTTP, clé d'API et jeton Bearer "
                 "répondent à deux modèles de confiance distincts : l'en-tête **`X-API-Key`** "
                 'transporte un secret statique à longue durée de vie alloué à un serveur '
                 'partenaire pour des échanges automatisés machine-à-machine.\n'
                 '\n'
                 "À l'inverse, l'en-tête **`Authorization: Bearer <token>`** présente un jeton "
                 "temporaire émis dynamiquement à l'issue d'une authentification "
                 "(`/api/auth/token`), doté d'une échéance courte automatique et porteur de "
                 "l'identité ainsi que du rôle précis de l'opérateur connecté.",
  'code_example': '# Cas 1 : Clé machine-à-machine\n'
                  'cle = self.request.headers.get("X-API-Key")\n'
                  '\n'
                  '# Cas 2 : Jeton temporaire utilisateur\n'
                  'auth = self.request.headers.get("Authorization") # "Bearer <token>"'},
 {'id': 'variable',
  'term': 'Variable (Python)',
  'category': 'Bases Python',
  'level': 'Débutant Absolu',
  'short': "Emplacement nommé dans la mémoire de l'ordinateur permettant de conserver une valeur "
           'typée.',
  'analogy': 'Un dossier suspendu dans une armoire sur lequel vous collez une étiquette « '
             'Budget_2026 ». Vous pouvez consulter son contenu ou le mettre à jour à tout moment.',
  'explanation': "En Python, l'opérateur d'affectation `=` lie un identifiant symbolique à un "
                 "objet typé en mémoire. Le développement d'APIs REST s'appuie directement sur la "
                 'correspondance native entre les quatre types scalaires fondamentaux de Python — '
                 '`str`, `int` ou `float`, `bool` (`True` / `False`) et `None` — et les types '
                 'primitifs universels du format JSON.',
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
                 'uniques à des valeurs arbitraires et constitue la pierre angulaire de Tornado : '
                 'transmettre un dictionnaire à `self.write(d)` déclenche automatiquement sa '
                 "sérialisation JSON UTF-8 accompagnée de l'en-tête `Content-Type: "
                 "application/json; charset=UTF-8`. Lors de la lecture d'une charge utile "
                 "entrante, la méthode `.get('cle', defaut)` prévient toute interruption par "
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
                 "ordonnée et dynamique d'éléments. Lorsqu'un point de terminaison REST restitue "
                 "une collection d'enregistrements métier, il encapsule cette liste de "
                 'dictionnaires au sein d\'un objet enveloppe (`{"meta": {...}, "data": [...]}`) '
                 "afin de préserver l'extensibilité du contrat et de respecter les garde-fous "
                 'natifs de `self.write()`.',
  'code_example': 'formations = ["Python", "API REST", "Tornado"]\n'
                  'print(formations[0])  # Affiche le 1er élément : Python'},
 {'id': 'fonction',
  'term': 'Fonction (def), Classe (RequestHandler) & Décorateur (@)',
  'category': 'Bases Python',
  'level': 'Débutant Absolu',
  'short': "Bloc d'instructions réutilisable prenant des paramètres en entrée, ou méthode d'une "
           'classe RequestHandler traitant un verbe HTTP.',
  'analogy': 'Une unité de traitement : vous lui fournissez des matières premières (paramètres), '
             'elle applique une procédure interne, et restitue le produit fini (`return` ou '
             '`self.write()`).',
  'explanation': 'Introduite par le mot-clé `def`, une fonction isole un traitement réutilisable '
                 'et paramétré. Dans le paradigme orienté objet de Tornado, chaque route est '
                 'gouvernée par une classe dérivée de `tornado.web.RequestHandler` dont les '
                 'méthodes `def get(self):` ou `def post(self):` répondent aux verbes HTTP '
                 "correspondants, éventuellement enrichies d'un **décorateur (`@exiger_role`)** "
                 'factorisant les contrôles transversaux.',
  'code_example': 'class BonjourHandler(tornado.web.RequestHandler):\n'
                  '    def get(self):\n'
                  '        self.write({"message": "Service Tornado opérationnel"})'},
 {'id': 'api',
  'term': 'API REST & Modèle de Maturité de Richardson',
  'category': 'Architecture Web',
  'level': 'Fondamental',
  'short': 'Architecture normalisée où chaque URL identifie une ressource (nom au pluriel) '
           'manipulée par les verbes et statuts HTTP.',
  'analogy': "Un guichet de liaison standardisé : l'application cliente dépose un bordereau de "
             'demande normé (Requête HTTP) et reçoit un colis de données structuré (Réponse JSON) '
             'sans dépendre du langage interne du serveur.',
  'explanation': "Le **Modèle de Maturité de Richardson** évalue la conformité architecturale d'un "
                 'service Web en quatre paliers progressifs : le Niveau 0 achemine des commandes '
                 'RPC ou SOAP sur une URL unique, tandis que le Niveau 1 attribue une URI '
                 'distincte à chaque ressource métier (`/api/formations/1`).\n'
                 '\n'
                 'Le **Niveau 2**, standard opérationnel des APIs REST modernes sous Tornado, '
                 'combine ces URIs nominales avec la sémantique exacte des verbes HTTP (`GET`, '
                 '`POST`, `PUT`, `PATCH`, `DELETE`) et des codes de statut (`200`, `201`, `401`, '
                 '`403`, `422`, `429`), avant le Niveau 3 (**HATEOAS**) qui embarque des liens '
                 "hypermédias de transition d'état.",
  'code_example': '# Anti-pattern RPC : POST /api/creerFormation\n'
                  '# Standard REST    : POST /api/formations  -> 201 Created'},
 {'id': 'status_code',
  'term': 'Codes de Statut HTTP (self.set_status) & RFC 7807 (Problem Details)',
  'category': 'Architecture Web',
  'level': 'Fondamental',
  'short': "Code numérique à 3 chiffres normalisé indiquant le résultat d'une requête, complété en "
           "cas d'erreur par un JSON RFC 7807.",
  'analogy': "Un code d'état standardisé sur un terminal bancaire : transaction acceptée (200), "
             'création validée (201), erreur de saisie (422), carte non reconnue (401), droits '
             'insuffisants (403), plafond dépassé (429).',
  'explanation': 'Les codes de statut HTTP normalisés (RFC 9110) se répartissent en trois classes '
                 "décisives pour une API : la plage **2xx** confirme le succès de l'opération "
                 '(`200 OK`, `201 Created` après création, `204 No Content` après suppression).\n'
                 '\n'
                 'La plage **4xx** impute le rejet à la requête cliente — `400` pour une syntaxe '
                 "JSON invalide, `401` pour un défaut d'authentification, `403` pour une "
                 'habilitation insuffisante, `404` et `405` pour le routage, `413` pour un '
                 'dépassement de taille, `422` pour une règle métier violée et `429` pour un '
                 'dépassement de quota — tandis que la plage **5xx** (`500`, `502`, `503`, `504`) '
                 "signale une défaillance interne du serveur ou d'une dépendance amont.",
  'code_example': 'self.set_status(422)\n'
                  'self.set_header("Content-Type", "application/problem+json; charset=utf-8")\n'
                  'self.write({\n'
                  '    "type": "https://api.isgp.dz/erreurs/validation",\n'
                  '    "title": "Erreur de validation",\n'
                  '    "status": 422,\n'
                  '    "errors": [{"champ": "duree_jours", "message": "Doit être >= 1"}]\n'
                  '})'},
 {'id': 'sqlite',
  'term': 'SQLite, Transactions ACID & Requêtes Paramétrées (?)',
  'category': 'Données',
  'level': 'Intermédiaire',
  'short': 'Moteur de base de données relationnelle SQL transactionnel intégré à Python '
           '(`sqlite3`).',
  'analogy': 'Un registre comptable permanent écrit sur disque dur, protégé par des transactions '
             'atomiques (tout réussit avec `commit` ou tout est annulé avec `rollback`).',
  'explanation': 'Moteur relationnel transactionnel ACID embarqué directement dans la bibliothèque '
                 'standard Python (`sqlite3`), SQLite exige une discipline absolue lors de la '
                 'construction des requêtes : assembler une instruction SQL par concaténation `+` '
                 'ou interpolation `f"..."` ouvre une brèche critique d\'**Injection SQL**, tandis '
                 "que l'usage systématique de marqueurs positionnels paramétrés `?` sépare "
                 "hermétiquement la grammaire SQL des données fournies par l'appelant.",
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
  'explanation': "Exploiter SQLite sous charge concurrente au sein d'un serveur Web impose "
                 "d'appliquer trois directives dès l'ouverture de chaque connexion : **`PRAGMA "
                 'journal_mode = WAL;`** consigne les écritures séquentiellement dans un journal '
                 '`.db-wal` dédié afin que les lecteurs ne soient plus jamais bloqués par un '
                 'écrivain.\n'
                 '\n'
                 "Conjointement, **`PRAGMA foreign_keys = ON;`** réactive le contrôle d'intégrité "
                 'référentielle (désactivé par défaut par rétrocompatibilité historique dans '
                 "SQLite), tandis que **`PRAGMA busy_timeout = 5000;`** autorise jusqu'à cinq "
                 "secondes d'attente coopérative lors d'écritures simultanées avant de lever "
                 '`OperationalError`.',
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
  'explanation': 'En Python standard, le gestionnaire de contexte `with conn:` du module `sqlite3` '
                 'pilote uniquement les frontières transactionnelles (`COMMIT` automatique en cas '
                 "de succès ou `ROLLBACK` en cas d'exception), sans fermer ni le curseur "
                 'sous-jacent ni le descripteur de connexion.\n'
                 '\n'
                 'Pour libérer déterministement les verrous de lecture et les tampons mémoire C '
                 "dès la fin d'une requête — y compris lorsqu'une erreur survient — il est "
                 "recommandé d'encapsuler l'exécution dans `with contextlib.closing(conn.cursor()) "
                 "as cur:` et de déporter l'appel synchrone dans un `ThreadPoolExecutor` hors de "
                 "l'`IOLoop`.",
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
  'explanation': "Le module standard **`sqlite3`** offre l'avantage décisif d'une disponibilité "
                 "immédiate sans dépendance tierce et d'une conformité complète au contrat "
                 "**DB-API 2.0 (PEP 249)** attendu par les outils de l'écosystème Python.\n"
                 '\n'
                 "Pour les architectures spécialisées exigeant un contrôle bas niveau de l'API C "
                 'de SQLite, la bibliothèque **`apsw`** (*Another Python SQLite Wrapper*) supprime '
                 'les transactions `BEGIN` implicites cachées et expose le streaming incrémental '
                 "de binaires (`zeroblob` / `blobopen`), l'API de sauvegarde à chaud ainsi que les "
                 "codes d'erreur étendus (`SQLITE_BUSY_SNAPSHOT`).",
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
  'explanation': 'Le standard W3C **Server-Sent Events (SSE)** diffuse des notifications '
                 'unidirectionnelles du serveur Tornado vers le navigateur sur une simple '
                 'connexion HTTP maintenue ouverte (`Content-Type: text/event-stream`), où chaque '
                 'événement textuel rassemble des champs `id:`, `event:` et `data:` clos par une '
                 'double fin de ligne `\\n\\n`.\n'
                 '\n'
                 'Particulièrement adapté aux barres de progression, aux journaux temps réel et au '
                 "streaming de jetons d'IA générative, le client natif navigateur `EventSource` "
                 'gère de lui-même la reconnexion automatique après une coupure réseau en '
                 "transmettant le dernier jalon reçu dans l'en-tête `Last-Event-ID`.",
  'code_example': 'class SseHandler(tornado.web.RequestHandler):\n'
                  '    async def get(self):\n'
                  '        self.set_header("Content-Type", "text/event-stream")\n'
                  '        self.write("id: 1\\nevent: progression\\ndata: {\\"pct\\": 50}\\n\\n")\n'
                  '        await self.flush()'},
 {'id': 'websocket_rfc6455',
  'term': 'WebSocket (RFC 6455 & HTTP 101 Switching Protocols)',
  'category': 'Temps Réel & Streaming',
  'level': 'Avancé',
  'short': 'Protocole de communication bidirectionnelle (Full-Duplex) persistante sur un unique '
           'socket TCP après une mise à niveau HTTP 101.',
  'analogy': 'Un appel téléphonique ouvert en continu : contrairement au courrier postal (HTTP '
             'requête/réponse) ou à la radio unidirectionnelle (SSE), les deux interlocuteurs '
             'peuvent parler et écouter simultanément à la milliseconde près.',
  'explanation': "Normalisé par l'**IETF RFC 6455**, le protocole **WebSocket** débute par une "
                 'requête HTTP classique sollicitant une bascule de protocole (`Upgrade: '
                 'websocket`, `Connection: Upgrade`, `Sec-WebSocket-Key`) à laquelle '
                 '`tornado.websocket.WebSocketHandler` répond par `HTTP/1.1 101 Switching '
                 'Protocols`.\n'
                 '\n'
                 "Une fois ce canal TCP full-duplex établi sans surcharge d'en-têtes HTTP répétés, "
                 'serveur et navigateur échangent instantanément des trames dans les deux sens, ce '
                 "qui en fait l'architecture privilégiée pour la messagerie collaborative, les "
                 'curseurs partagés multi-utilisateurs et la télémétrie industrielle à haute '
                 'fréquence.',
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
  'explanation': "Véhiculer des documents volumineux encodés en Base64 à l'intérieur d'un objet "
                 'JSON gonfle artificiellement la charge réseau de `+33 %` et contraint le parseur '
                 "à allouer l'intégralité du bloc en mémoire vive ; l'encodage binaire natif "
                 "`multipart/form-data` s'impose donc pour tout téléversement.\n"
                 '\n'
                 "La réception sécurisée d'un fichier repose sur trois garde-fous cumulatifs : "
                 'plafonner strictement `max_body_size` sur `HTTPServer` (`413 Content Too '
                 'Large`), inspecter la signature binaire réelle en tête de flux (*Magic Bytes*, '
                 'telle que `25 50 44 46 2D` pour `%PDF-` ou `89 50 4E 47` pour PNG) et substituer '
                 'un identifiant interne `uuid4().hex` au nom fourni par le client afin '
                 "d'éradiquer toute traversée d'arborescence (*Path Traversal*).",
  'code_example': '@tornado.web.stream_request_body\n'
                  'class StreamUploadHandler(tornado.web.RequestHandler):\n'
                  '    def data_received(self, chunk: bytes):\n'
                  '        self.octets_recus += len(chunk)  # Streaming C10K sans RAM !'},
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
  'explanation': "Exécuter de manière synchrone la génération lourde d'une archive comptable ou un "
                 "traitement analytique prolongé au cours d'une requête HTTP ordinaire immobilise "
                 "les ressources serveur et expose l'appelant aux coupures **`504 Gateway "
                 'Timeout`** imposées par les proxys frontaux Nginx ou Cloudflare.\n'
                 '\n'
                 "Le patron d'architecture asynchrone résout cette contrainte en enregistrant "
                 "immédiatement une tâche à l'état `EN_ATTENTE`, puis en répondant sans délai "
                 "**`202 Accepted`** accompagné de l'en-tête `Location: /api/jobs/job-8a2f` que le "
                 "client sonde périodiquement jusqu'à l'état final `TERMINE`.",
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
  'explanation': 'Si les routes manipulant des données personnelles ou des jetons doivent '
                 'impérativement interdire toute mise en cache partagée via **`Cache-Control: '
                 'no-store`**, les ressources de référence fréquemment consultées gagnent '
                 'considérablement à exploiter la validation conditionnelle HTTP.\n'
                 '\n'
                 "En associant une empreinte SHA-256 dans l'en-tête **`ETag`** de la réponse "
                 '`GET`, le contrôleur Tornado permet au client de représenter cette valeur dans '
                 "`If-None-Match` lors des appels suivants : si l'enregistrement demeure inchangé, "
                 'le serveur répond **`304 Not Modified`** avec zéro octet de corps, économisant à '
                 'la fois bande passante mobile et sérialisation JSON.',
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
  'explanation': 'Lorsque deux administrateurs éditent simultanément la même fiche formation sans '
                 'mécanisme de coordination, la sauvegarde la plus tardive écrase silencieusement '
                 'les modifications de la première (*Lost Update*).\n'
                 '\n'
                 'Le **verrouillage optimiste HTTP** élimine cette anomalie sans bloquer la base '
                 'de données : le client soumet sa mise à jour `PUT` assortie de la précondition '
                 '**`If-Match: "v1-..."`**, et le serveur exécute une clause atomique `UPDATE ... '
                 'WHERE id = ? AND version = ?`, renvoyant **`412 Precondition Failed`** dès '
                 "qu'une écriture concurrente a déjà fait progresser la version.",
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
  'explanation': 'Dans une architecture en couches traversant un répartiteur Nginx, un démon '
                 'Tornado et un pool SQLite, diagnostiquer un incident de production exige un fil '
                 "d'Ariane unique reliant chaque ligne de journal.\n"
                 '\n'
                 "Dès l'entrée dans `prepare(self)`, le serveur conserve l'en-tête "
                 "**`X-Request-ID`** s'il a déjà été émis et validé par la passerelle amont, ou "
                 'engendre à défaut un identifiant `uuid4` neuf ; combiné à `time.perf_counter()`, '
                 'cet identifiant ainsi que la durée `X-Response-Time-Ms` sont restitués à la fois '
                 'dans les en-têtes HTTP et dans les journaux structurés.',
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
  'explanation': 'En configuration standard, Nginx rejette tout corps de requête excédant **1 Mo** '
                 '(`client_max_body_size 1m`) : une architecture durcie maintient ce seuil strict '
                 "de `1M` sur les routes JSON classiques et n'ouvre une limite supérieure (`25M`) "
                 'que sur la `location` dédiée au téléversement.\n'
                 '\n'
                 'Pour préserver intégralement la boucle `IOLoop` de Tornado lors des transferts '
                 'lourds, Nginx peut écrire directement le flux entrant sur disque '
                 '(`client_body_in_file_only clean`) et ne transmettre que le chemin local à '
                 'Python, puis assurer symétriquement les téléchargements privés à vitesse noyau '
                 "(`sendfile on`) dès que Tornado valide les droits et émet l'en-tête interne "
                 '**`X-Accel-Redirect`**.',
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
  'explanation': 'Une interface de programmation (**API**) définit une frontière contractuelle '
                 "stable qui abstrait l'implémentation interne d'un sous-système et se décline en "
                 'quatre strates complémentaires en informatique.\n'
                 '\n'
                 'Au plus près du matériel opèrent les **appels système POSIX** du noyau '
                 '(`open()`, `epoll()`), les interfaces **IPC / pilotes matériels** (sockets UNIX '
                 'locaux, GPU) et les **contrats de bibliothèques en mémoire** tels que **PEP 249 '
                 '(`DB-API 2.0`)** unifiant `sqlite3` et `psycopg`, tandis que les **APIs Web '
                 'réseau** orchestrent les systèmes distribués au moyen de **REST**, **GraphQL**, '
                 '**gRPC**, **Webhooks** et **WebSockets**.',
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
  'explanation': "Il convient de ne pas confondre le **contrat d'API**, pacte formel et exécutable "
                 'vérifié automatiquement en intégration continue (types stricts, champs requis, '
                 'bornes numériques, codes HTTP, erreurs RFC 7807 et scopes de sécurité où tout '
                 "retrait constitue un *Breaking Change*), avec la **documentation d'API**.\n"
                 '\n'
                 "Cette dernière englobe l'expérience pédagogique offerte aux intégrateurs — "
                 "guides de démarrage rapide, scénarios d'authentification et portails interactifs "
                 'Swagger UI ou ReDoc — qui doit être générée directement depuis le contrat source '
                 "afin d'éliminer tout risque de dérive documentaire (*Documentation Drift*).",
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
  'explanation': "La spécification **HTTP (RFC 9110)** garantit l'idempotence native des verbes "
                 '`GET`, `HEAD`, `OPTIONS`, `PUT` et `DELETE`, mais exclut volontairement `POST`, '
                 "de sorte que la répétition automatique d'un `POST /paiements` après une perte de "
                 "signal Wi-Fi risquerait d'exécuter deux débits successifs.\n"
                 '\n'
                 'La parade industrielle adoptée par les passerelles bancaires consiste à exiger '
                 'du client un identifiant unique **`Idempotency-Key`** (UUID v4) : le serveur '
                 'associe cette clé à la réponse initiale durant vingt-quatre heures et restitue '
                 'exactement le même résultat en cas de rejeu sans ré-exécuter la transaction '
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
  'explanation': "Deux méthodologies gouvernent le cycle de vie OpenAPI : l'approche "
                 "**Contract-First** rédige et valide d'abord le fichier `openapi.yaml` (via des "
                 'linters comme Spectral), autorisant les équipes frontales sur serveur simulé '
                 '(*Mock*) et les équipes Tornado backend à développer simultanément sans attente '
                 'mutuelle.\n'
                 '\n'
                 "À l'inverse, l'approche **Code-First** synthétise `/openapi.json` directement "
                 "depuis les structures du code applicatif pour garantir l'absence d'écart avec "
                 "l'implémentation, les deux démarches s'appuyant sur les en-têtes `Deprecation` "
                 'et `Sunset` (RFC 8594) pour piloter les transitions de versions sans rupture.',
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
  'explanation': "L'architecture réseau d'une plateforme distingue le trafic **Nord-Sud "
                 '(vertical)**, qui relie les terminaux externes au cluster à travers un réseau '
                 'WAN non maîtrisé et franchit en bordure DNS, CDN, pare-feu applicatif WAF, '
                 'terminaison TLS, limitation de débit et passerelle API.\n'
                 '\n'
                 'Une fois cette frontière franchie, une seule requête entrante déclenche '
                 'fréquemment plusieurs appels **Est-Ouest (horizontaux)** entre microservices '
                 'internes (*fan-out*), lesquels exigent des budgets de latence resserrés, des '
                 "délais d'expiration courts, un chiffrement mutuel **mTLS** et une politique "
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
  'explanation': "Le patron d'architecture **Phantom Token** concilie confidentialité externe et "
                 "performance interne : le client public ne détient sur Internet qu'un jeton "
                 'opaque aléatoire dépourvu de toute information métier lisible par simple '
                 'décodage Base64url.\n'
                 '\n'
                 "À chaque franchissement Nord-Sud, la passerelle d'entrée vérifie instantanément "
                 "que ce jeton opaque n'a pas été révoqué, puis l'échange à la volée contre un "
                 '**JWT interne signé** transmis aux microservices Tornado Est-Ouest, qui valident '
                 'alors les habilitations de façon autonome par clé publique JWKS.',
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
  'explanation': "L'architecture **Zero-Trust** met fin au postulat obsolète du réseau interne de "
                 "confiance (« château-fort et douves ») dans lequel la compromission d'un seul "
                 "conteneur périphérique offrait un accès libre à l'ensemble des bases et services "
                 'internes.\n'
                 '\n'
                 'Grâce à **mTLS (*Mutual TLS*)**, chaque poignée de main Est-Ouest impose une '
                 'authentification cryptographique réciproque où le serveur et le microservice '
                 'appelant valident mutuellement leurs certificats X.509 à courte durée de vie, '
                 "fréquemment porteurs d'une identité de charge normalisée **SPIFFE** "
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
  'explanation': "Le cadre d'autorisation déléguée **OAuth 2.0 (RFC 6749)** orchestre quatre "
                 "acteurs distincts : le **Resource Owner** (l'utilisateur humain titulaire des "
                 "données) et le **Client** (l'application Web, mobile ou tierce sollicitant un "
                 'accès limité en son nom).\n'
                 '\n'
                 "Face à eux, l'**Authorization Server (IdP)** vérifie l'identité de "
                 "l'utilisateur, recueille son consentement et délivre les jetons signés, tandis "
                 'que le **Resource Server** (votre API Python Tornado) contrôle systématiquement '
                 'la signature cryptographique ainsi que les revendications `exp`, `aud` et '
                 "`scope` avant d'exécuter l'opération.",
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
  'explanation': "L'extension **PKCE (*Proof Key for Code Exchange*, RFC 7636)** sécurise le flux "
                 "d'autorisation des applications publiques (SPA et mobiles) contre l'interception "
                 'du code de redirection : au départ, le client engendre un secret éphémère '
                 'aléatoire `code_verifier` et ne transmet sur `/authorize` que son condensat '
                 '`code_challenge = BASE64URL(SHA256(code_verifier))`.\n'
                 '\n'
                 'Après authentification et réception du `code` à usage unique, le client présente '
                 'conjointement `code` et `code_verifier` sur `/token`, permettant au serveur '
                 "d'identité de vérifier mathématiquement le condensat SHA-256 avant de délivrer "
                 "l'`access_token`, remplaçant ainsi définitivement l'ancien flux *Implicit* "
                 'déprécié.',
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
  'explanation': "La couche d'identité **OpenID Connect (OIDC)** superpose deux jetons aux usages "
                 "strictement disjoints : une règle de sécurité impérative interdit d'envoyer un "
                 '**`ID Token`** dans `Authorization: Bearer` pour consommer une API métier, tout '
                 'comme une interface frontale ne doit jamais décoder un **`Access Token`** '
                 "destiné au backend pour en déduire l'identité affichée.\n"
                 '\n'
                 "Lorsqu'aucun opérateur humain n'intervient dans la boucle — cas d'un démon "
                 "planifié ou d'une synchronisation inter-serveurs —, l'architecture bascule sur "
                 'le flux **`Client Credentials` (`grant_type=client_credentials`)** dédié aux '
                 'échanges machine-à-machine.',
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
  'explanation': "Relayer aveuglément le jeton utilisateur Nord-Sud initial d'un microservice à "
                 "l'autre (*Blind Token Passthrough*) expose l'infrastructure au problème du "
                 '**député confus (*Confused Deputy*)** : tout service intermédiaire compromis '
                 "pourrait rejouer ce jeton à large portée auprès d'autres briques internes.\n"
                 '\n'
                 'Le standard **OAuth 2.0 Token Exchange (RFC 8693, `On-Behalf-Of`)** élimine ce '
                 "risque en ordonnant au Service A d'échanger le jeton entrant auprès de l'IdP "
                 "contre un jeton dérivé à vie brève (`120s`), restreint à l'audience exacte `aud: "
                 "service-paiement`, doté d'un `scope` minimal et enrichi de la revendication "
                 "d'audit **`act` (*Actor*)** identifiant formellement l'intermédiaire.",
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
  'explanation': "Conçue en 2010 par Tony Tam sous l'appellation initiale *Swagger Specification*, "
                 'la norme a été confiée en novembre 2015 à la **Linux Foundation** (OpenAPI '
                 'Initiative) et rebaptisée **OpenAPI Specification** (`OAS 3.0`, puis `OAS 3.1` '
                 'alignée à 100 % sur JSON Schema Draft 2020-12).\n'
                 '\n'
                 "Aujourd'hui, *OpenAPI* désigne exclusivement le standard ouvert du contrat, "
                 "tandis que *Swagger* (SmartBear) et son écosystème désignent l'outillage "
                 "logiciel qui l'exploite au quotidien : **Swagger Editor** pour la rédaction, "
                 "**Swagger UI** pour l'exploration interactive (*Try it out*), **OpenAPI "
                 'Generator** pour les SDK clients, **ReDoc / Scalar** pour les portails '
                 'documentaires et **Schemathesis** pour les tests de conformité automatisés.',
  'code_example': '# Tornado Contract-First : exposition du contrat openapi.yaml validé en CI\n'
                  'class OpenAPIHandler(tornado.web.RequestHandler):\n'
                  '    def get(self): self.write(OPENAPI_3_1_SPEC)'}]
