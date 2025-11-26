"""
    Le serveur service.py qui :
        - Initialise le serveur.
        - Attend une connexion.
        - Reçoit les données.
        - Traite : résolution de l'équation.
        - Envoie le résultat au client et ferme la connexion avec le client.
"""
import sys
import socket
import json
import math
 
# ---------------------------------------------------------------
#  Fonction qui résout l'équation A*x^2 + B*x + C = 0
# ---------------------------------------------------------------
def solve_quadratic(A, B, C):
    # Cas dégénéré : si A = 0, l’équation devient linéaire
    if A == 0:
        # Si B = 0 aussi → soit pas de solution, soit infinité
        if B == 0:
            if C == 0:
                return ("infinite", None)  # 0 = 0 → infinité de solutions
            else:
                return ("none", None)  # 0*x + C = 0 impossible
        else:
            # Equation linéaire : B*x + C = 0
            x = -C / B
            return ("linear", [x])

    # Calcul du discriminant Δ = B² - 4AC
    disc = B*B - 4*A*C

    if disc > 0:
        # Deux solutions réelles distinctes
        r1 = (-B + math.sqrt(disc)) / (2*A)
        r2 = (-B - math.sqrt(disc)) / (2*A)
        return ("two", [r1, r2])

    elif disc == 0:
        # Une seule solution réelle
        r = -B / (2*A)
        return ("one", [r])

    else:
        # Racines complexes
        real = -B / (2*A)
        imag = math.sqrt(-disc) / (2*A)
        return ("complex", [complex(real, imag), complex(real, -imag)])


# ---------------------------------------------------------------
#  Fonction qui gère une connexion avec un client
# ---------------------------------------------------------------
def handle_connection(conn, addr):
    try:
        # Réception du préfixe de longueur (4 octets big-endian)
        
        length_bytes = conn.recv(4) # Permet de connaître la taille du message JSON à lire
        if len(length_bytes) < 4:
            return

        # Conversion des 4 octets en un entier (taille du JSON)
        length = int.from_bytes(length_bytes, "big")

        # Lecture du message JSON complet
        data = b""
        while len(data) < length:
            chunk = conn.recv(length - len(data))
            if not chunk:
                break
            data += chunk

        if not data:
            return

        # Décodage du JSON reçu
        try:
            req = json.loads(data.decode("utf-8"))
            A = int(req.get("A"))
            B = int(req.get("B"))
            C = int(req.get("C"))
        except Exception as e:
            # Message d'erreur si format incorrect
            resp = {"status":"error", "message": f"Invalid request: {e}"}
            send_response(conn, resp)
            return

        # Résolution de l’équation
        kind, roots = solve_quadratic(A, B, C)

        # Création d’une réponse adaptée au résultat
        if kind == "infinite":
            resp = {"status":"ok", "type":"infinite_solutions", "message":"Every x is a solution"}

        elif kind == "none":
            resp = {"status":"ok", "type":"no_solution", "message":"No solution"}

        elif kind == "linear":
            resp = {"status":"ok", "type":"linear", "roots": roots}

        elif kind == "two":
            resp = {"status":"ok", "type":"two_real", "roots": roots}

        elif kind == "one":
            resp = {"status":"ok", "type":"one_real", "roots": roots}

        elif kind == "complex":
            # JSON ne supporte pas les nombres complexes → conversion en strings
            resp = {"status":"ok", "type":"complex", "roots":[str(roots[0]), str(roots[1])]}
        
        else:
            resp = {"status":"error", "message":"Unhandled case"}

        # Envoi de la réponse
        send_response(conn, resp)

    finally:
        # Fermeture du canal avec le client
        conn.close()


# ---------------------------------------------------------------
#  Envoi de la réponse JSON avec préfixe de longueur
# ---------------------------------------------------------------

def send_response(conn, resp_obj):
    # Encodage JSON → bytes
    payload = json.dumps(resp_obj).encode("utf-8")
    # Envoi : d'abord la taille (4 octets), ensuite le JSON
    conn.sendall(len(payload).to_bytes(4, "big") + payload)


# ---------------------------------------------------------------
#  Fonction principale : création et gestion du serveur TCP
# ---------------------------------------------------------------
def main():
    # Récupération automatique de l'adresse IP de l'hôte
    host = socket.gethostbyname(socket.gethostname())
    port = 5000  # port par défaut

    # Possibilité de passer host et port en arguments
    # Ex : python3 server.py 0.0.0.0 5000
    if len(sys.argv) >= 2:
        host = sys.argv[1]
    if len(sys.argv) >= 3:
        port = int(sys.argv[2])

    # Création du socket TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        # Autorise le redémarrage rapide du serveur
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Association socket → (IP, port)
        sock.bind((host, port))

        # Le serveur écoute jusqu'à 5 connexions simultanées
        sock.listen(5)
        print(f"Server listening on {host}:{port} (Ctrl-C to stop)")

        try:
            # Boucle infinie : attente de clients
            while True:
                conn, addr = sock.accept()    # Connexion entrante
                print("Connection from", addr)

                # Gestion de la connexion client
                handle_connection(conn, addr)

        except KeyboardInterrupt:
            print("Server stopped by user")


# Lancement du serveur
if __name__ == "__main__":
    main()
