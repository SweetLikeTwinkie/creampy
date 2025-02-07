import yaml
import os
import base64
import secrets
import subprocess
import string

BANNER = r"""
   ______                          ______  __
  / ____/_______  ____ _____ ___  / __ \ \/ /
 / /   / ___/ _ \/ __ `/ __ `__ \/ /_/ /\  /
/ /___/ /  /  __/ /_/ / / / / / / ____/ / /
\____/_/_  \___/\__,_/_/ /_/ /_/_/     /_/
  / ____/___  ____ ___  ____ ___  ____ _____  ____/ /
 / /   / __ \/ __ `__ \/ __ `__ \/ __ `/ __ \/ __  /
/ /___/ /_/ / / / / / / / / / / / /_/ / / / / /_/ /
\____/\____/_/ /_/ /_/_/ /_/ /_/\__,_/_/ /_/\__,_/
            By: SweetLikeTwinkie <3
"""


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)


def check_existing_config(filename):
    clear_screen()
    if os.path.exists(filename):
        choice = input(f"[!] {filename} already exists. Do you want to delete and create a new config? (yes/no): ") or "no"
        if choice.lower() != "yes":
            print("[+] Exiting without changes.")
            exit()
        os.remove(filename)
        print(f"[+] {filename} deleted. Creating a new configuration...")


def generate_secret_key():
    clear_screen()
    return base64.b64encode(secrets.token_bytes(32)).decode()


def generate_master_password():
    clear_screen()
    special_chars = "!@#$%^&*()-_=+[]{}|;:'<>,.?/"
    password = ''.join(
        secrets.choice(string.ascii_uppercase + string.digits + special_chars) for _ in range(5)
    ) + ''.join(
        secrets.choice(string.ascii_letters + string.digits + special_chars) for _ in range(27)
    )
    return password


def generate_ssl_certificates():
    clear_screen()
    cert_dir = "certificates"
    os.makedirs(cert_dir, exist_ok=True)
    cert_key_path = os.path.join(cert_dir, "server.key")
    cert_crt_path = os.path.join(cert_dir, "server.crt")

    if not os.path.exists(cert_key_path) or not os.path.exists(cert_crt_path):
        subprocess.run([
            "openssl", "req", "-newkey", "rsa:2048", "-nodes", "-keyout", cert_key_path,
            "-x509", "-days", "365", "-out", cert_crt_path,
            "-subj", "/C=US/ST=ExampleState/L=ExampleCity/O=ExampleOrg/OU=Dev/CN=example.com"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


# Fix Yaml parsing.
class CustomDumper(yaml.Dumper):
    def represent_str(self, data):
        return self.represent_scalar("tag:yaml.org,2002:str", data, style='"')

yaml.add_representer(str, CustomDumper.represent_str)

def ask_questions():

    responses = {
        "server": {},
        "https": {},
        "c2": {}
    }
    # Server IP ---------------------
    clear_screen()
    server_ip = input("Enter server host (default: 0.0.0.0): ") or "0.0.0.0"
    responses["server"]["ip"] = f'{server_ip}'
    print("[+] Server IP address:", server_ip)
    input("[+] Press Enter to continue...")
    # Server Port ---------------------
    clear_screen()
    server_port = int(input("Enter server port (default: 50000): ") or 50000)
    responses["server"]["port"] = server_port
    print("[+] Server port:", server_port)
    input("[+] Press Enter to continue...")
    # Generate secret key ---------------------
    clear_screen()
    generated_secret_key = generate_secret_key()
    responses["server"]["secret_key"] = generated_secret_key
    print(f"[+] Generated secret key: {generated_secret_key}")
    input("[+] Press Enter to continue...")
    # Master Password ---------------------
    clear_screen()
    if input("Do you want to generate a secure master password? (yes/no): ") == "yes":
        generated_master_password = generate_master_password()
        responses["server"]["master_password"] = generated_master_password
        print(f"[+] Generated master password: {generated_master_password}")
        input("[+] Press Enter to continue...")
    else:
        user_master_password = input("Enter master password: ")
        responses["server"]["master_password"] = user_master_password
        print(f"[+] Your master password: {user_master_password}")
        input("[+] Press Enter to continue...")
    # Debug mode ---------------------
    clear_screen()
    debug_mode_state = input("Do you want to debug mode? (true/false): ") in ["true", "1"] or "false"
    responses["server"]["debug_mode"] = debug_mode_state
    print(f"[+] Debug mode: {debug_mode_state}")
    input("[+] Press Enter to continue...")
    # HTTPs ---------------------
    clear_screen()
    use_https = input("Do you want to use https? (true/false): ") in ["true", "1"] or "true"
    if use_https:
        responses["https"]["use_https"] = use_https
        print("[+] Using HTTPS...")
        print("[+] The server will generate the certificate and key files. Press enter to continue...")
        input("[+] Press Enter to continue...")
        generate_ssl_certificates()
    else:
        responses["https"]["use_https"] = False
        print("[-] HTTPS is disabled. The server will run without encryption.")
        print("[-] You can place your certificate and key files into the certificate folder.")
        print("[!] just change their names to server.crt or server.key")
        input("[+] Press Enter to continue...")
    responses["https"]["server_crt"] = "server.crt"
    responses["https"]["server_key"] = "server.key"
    # Base Path length ---------------------
    clear_screen()
    base_length = int(input("Enter base path length (default: 8):") or 8)
    responses["c2"]["base_path_length"] = base_length
    print("[+] Base path length:", base_length)
    input("[+] Press Enter to continue...")
    # db file name ---------------------
    clear_screen()
    db_name = f"{input("Enter database name (default: c2db): ") or "c2db"}.json"
    responses["c2"]["db_name"] = db_name
    print("[+] Database name:", db_name)
    input("[+] Press Enter to continue...")
    # Load other stuff -----------------
    responses["c2"]["logging_file_path"] = "logs/server.log"
    return responses


def write_to_yaml(data, filename="server_config.yaml"):
    clear_screen()
    with open(filename, "w") as file:
        yaml.dump(data, file, Dumper=CustomDumper, sort_keys=False)
    print(f"Data saved to {filename}")


if __name__ == "__main__":
    clear_screen()
    config_filename = "server_config.yaml"
    check_existing_config(config_filename)
    generate_ssl_certificates()
    user_data = ask_questions()
    write_to_yaml(user_data, filename=config_filename)