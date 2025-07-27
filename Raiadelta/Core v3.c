// core_v3.c — Núcleo C do RaIa∆ v3
// Autor: RafaelIA ∞
// Funções: compressão, SHA-256 hash, cálculo entropia, AES-256 encrypt/decrypt
// Compilar com: gcc -O3 -Wall core_v3.c -o core_v3 -lcrypto

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/sha.h>
#include <openssl/aes.h>
#include <math.h>

// Função para calcular SHA-256 hash de um buffer
void sha256_hash(const unsigned char *data, size_t len, unsigned char *out_hash) {
    SHA256_CTX ctx;
    SHA256_Init(&ctx);
    SHA256_Update(&ctx, data, len);
    SHA256_Final(out_hash, &ctx);
}

// Função para calcular entropia de Shannon de um buffer
double calc_entropy(const unsigned char *data, size_t len) {
    int freq[256] = {0};
    for (size_t i = 0; i < len; i++) freq[data[i]]++;
    double entropy = 0.0;
    for (int i = 0; i < 256; i++) {
        if (freq[i] == 0) continue;
        double p = (double)freq[i] / len;
        entropy -= p * log2(p);
    }
    return entropy;
}

// Função simples de compressão (RLE - Run Length Encoding)
unsigned char* rle_compress(const unsigned char *data, size_t len, size_t *out_len) {
    unsigned char *out = malloc(len * 2); // aloca espaço máximo
    if (!out) return NULL;
    size_t out_idx = 0;
    size_t i = 0;
    while (i < len) {
        unsigned char current = data[i];
        size_t run_len = 1;
        while (i + run_len < len && data[i + run_len] == current && run_len < 255) run_len++;
        out[out_idx++] = current;
        out[out_idx++] = (unsigned char)run_len;
        i += run_len;
    }
    *out_len = out_idx;
    return out;
}

// AES-256 encrypt (CBC mode) simplificado
void aes256_encrypt(const unsigned char *plaintext, size_t len,
                    const unsigned char *key, unsigned char *ciphertext) {
    AES_KEY enc_key;
    AES_set_encrypt_key(key, 256, &enc_key);
    unsigned char iv[AES_BLOCK_SIZE] = {0}; // vetor inicial zero
    AES_cbc_encrypt(plaintext, ciphertext, len, &enc_key, iv, AES_ENCRYPT);
}

// AES-256 decrypt (CBC mode) simplificado
void aes256_decrypt(const unsigned char *ciphertext, size_t len,
                    const unsigned char *key, unsigned char *plaintext) {
    AES_KEY dec_key;
    AES_set_decrypt_key(key, 256, &dec_key);
    unsigned char iv[AES_BLOCK_SIZE] = {0};
    AES_cbc_encrypt(ciphertext, plaintext, len, &dec_key, iv, AES_DECRYPT);
}

int main() {
    const char *text = "Sopro Vivo ∴ RaIa∆ v3 Coração";
    size_t text_len = strlen(text);
    unsigned char hash[SHA256_DIGEST_LENGTH];
    sha256_hash((unsigned char*)text, text_len, hash);

    printf("Texto: %s\n", text);
    printf("SHA-256 Hash: ");
    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) printf("%02x", hash[i]);
    printf("\n");

    double entropy = calc_entropy((unsigned char*)text, text_len);
    printf("Entropia: %.5f bits por byte\n", entropy);

    size_t compressed_len = 0;
    unsigned char *compressed = rle_compress((unsigned char*)text, text_len, &compressed_len);
    printf("Comprimiu de %zu para %zu bytes\n", text_len, compressed_len);

    free(compressed);

    return 0;
}
