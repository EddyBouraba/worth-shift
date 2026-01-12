#!/usr/bin/env python3
"""
Lanceur pour l'interface web du comparateur de shifts.

Usage:
    python3 web.py [port] [host]

Exemples:
    python3 web.py              # Démarre sur localhost:8080
    python3 web.py 3000         # Démarre sur localhost:3000
    python3 web.py 8080 0.0.0.0 # Accessible depuis le réseau local
"""
import sys

if __name__ == "__main__":
    from shift_comparator.web import run_server

    # Paramètres par défaut
    port = 8080
    host = 'localhost'

    # Arguments en ligne de commande
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Erreur: '{sys.argv[1]}' n'est pas un port valide")
            sys.exit(1)

    if len(sys.argv) > 2:
        host = sys.argv[2]

    # Lancer le serveur
    run_server(port=port, host=host)
