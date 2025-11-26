"""
client.py
Client pour envoyer trois entiers A, B, C au serveur qui résout l'équation A*x^2 + B*x + C = 0.

Utilisation :
    python3 client.py <server_host> <server_port> A B C

Exemple :
    python3 client.py 127.0.0.1 5000 1 -3 2
"""

import sys
import socket
import json

def main():
    # Vérification du nombre d'arguments
    if len(sys.argv) != 6:
        print("Usage: python3 client.py <server_host> <server_port> A B C")
        sys.exit(1)

    # Récupération des arguments
    host = sys.argv[1]             # Adresse IP du serveur
    port = int(sys.argv[2])        # Port d’écoute du serveur

    # Conversion des coefficients A, B, C en entiers
    try:
        A = int(sys.argv[3])
        B = int(sys.argv[4])
        C = int(sys.argv[5])
    except ValueError:
        print("A, B and C must be integers")
        sys.exit(1)

    # ---------------------------------------------------------
    #  Création du message JSON qui contient les coefficients
    # ---------------------------------------------------------
    payload = json.dumps({"A": A, "B": B, "C": C}).encode("utf-8")

    # Préfixe de longueur : 4 octets big-endian indiquant la taille du message
    length_prefix = len(payload).to_bytes(4, "big")

    # ---------------------------------------------------------
    #  Connexion au serveur et envoi du message
    # ---------------------------------------------------------
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        # Connexion au serveur
        s.connect((host, port))

        # Envoi du préfixe + message JSON
        s.sendall(length_prefix + payload)

        # -----------------------------------------------------
        #  Réception de la réponse du serveur
        # -----------------------------------------------------

        # Lecture des 4 premiers octets contenant la taille
        data_len_bytes = s.recv(4)
        if len(data_len_bytes) < 4:
            print("Server closed connection unexpectedly")
            sys.exit(1)

        # Conversion du préfixe en entier
        resp_len = int.from_bytes(data_len_bytes, "big")

        # Lecture des "resp_len" octets du JSON de réponse
        data = b""
        while len(data) < resp_len:
            chunk = s.recv(resp_len - len(data))
            if not chunk:
                break
            data += chunk

        if not data:
            print("No response from server")
            sys.exit(1)

        # Tentative de décodage du JSON reçu
        try:
            resp = json.loads(data.decode("utf-8"))
        except Exception as e:
            print("Failed to parse server response:", e)
            print("Raw:", data)
            sys.exit(1)

        # -----------------------------------------------------
        #  Affichage propre de la réponse du serveur
        # -----------------------------------------------------
        print("Server response:")
        for k, v in resp.items():
            print(f"  {k}: {v}")

# Lancement du programme client
if __name__ == "__main__":
    main()
