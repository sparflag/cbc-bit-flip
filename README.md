# CBC Bit Flip (`cbc-bit-flip`)

**Category:** cryptography · **Difficulty:** hard · **Points:** 400

Flip ciphertext bits to tamper the decrypted plaintext and unlock the seed.

## Run it

```bash
docker build -t sparflag/cbc-bit-flip .
# `deca-ai start cbc-bit-flip` (or the web UI) prints the docker run line with your
# SPARFLAG_SERVER + SPARFLAG_INSTANCE_TOKEN
```

## Recover the flag

The delivery blob is Fernet ciphertext. Discover the key seed, derive the Fernet key, then decrypt.

The plaintext flag is never written to disk or served — only the encoded delivery blob
is. When you have it:

```bash
deca-ai submit cbc-bit-flip 'sparflag{...}'
```

## Hints

- A bit flipped in block N alters block N+1 predictably.
- Turn role=user into role=admin by editing the previous block.
