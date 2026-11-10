#!/usr/bin/env bash
# ==============================================================================
# FICHIER : deploy_nginx_cluster/start_4_instances.sh
# OBJECTIF : Démarrer ou arrêter les 4 instances Flask/Gunicorn (ports 8001 à 8004)
#            derrière le répartiteur de charge Nginx.
# USAGE :
#   bash deploy_nginx_cluster/start_4_instances.sh start
#   bash deploy_nginx_cluster/start_4_instances.sh status
#   bash deploy_nginx_cluster/start_4_instances.sh stop
# ==============================================================================

set -euo pipefail

ACTION="${1:-status}"
PORTS=(8001 8002 8003 8004)
PYTHON_BIN=".venv/bin/python"

case "$ACTION" in
  start)
    echo "=== Démarrage des 4 instances Flask ISGP (Ports 8001 à 8004) ==="
    for idx in "${!PORTS[@]}"; do
      PORT="${PORTS[$idx]}"
      NODE_ID="flask-node-$((idx + 1))"
      PORT="$PORT" INSTANCE_ID="$NODE_ID" nohup "$PYTHON_BIN" deploy_nginx_cluster/instance_flask.py \
        > "/tmp/${NODE_ID}.log" 2>&1 &
      echo "  [OK] Instance $NODE_ID démarrée sur 127.0.0.1:$PORT (PID: $!)"
    done
    sleep 1
    echo "=== Vérification des sondes /api/health ==="
    for PORT in "${PORTS[@]}"; do
      curl -s "http://127.0.0.1:${PORT}/api/health" || true
      echo ""
    done
    ;;

  status)
    echo "=== État des 4 instances du Cluster Flask (8001..8004) ==="
    for PORT in "${PORTS[@]}"; do
      if curl -s --max-time 1 "http://127.0.0.1:${PORT}/api/health" > /dev/null; then
        echo "  [UP]   127.0.0.1:$PORT -> $(curl -s "http://127.0.0.1:${PORT}/api/health")"
      else
        echo "  [DOWN] 127.0.0.1:$PORT (Aucune réponse)"
      fi
    done
    ;;

  stop)
    echo "=== Arrêt propre (SIGTERM) des 4 instances Flask ==="
    pkill -f "deploy_nginx_cluster/instance_flask.py" || echo "Aucune instance active."
    ;;

  *)
    echo "Usage : $0 {start|status|stop}"
    exit 1
    ;;
esac
