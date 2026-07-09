import json
import base64
from typing import Tuple, Dict, Optional
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature

# Hardcoded SEBI Mock Authority Keys for demonstration
SEBI_PRIVATE_KEY_HEX = "6528ab2b958be883abc89c0e232682b16c4075fbb964314796da6097efe1a0ce"
# Public key corresponding to the private key above:
SEBI_PUBLIC_KEY_HEX = "32b5769ffa29f4824bd2f4d2c45ac8c905feb0455afbc6a849b555b39ea0241e"

# In production, keys would be generated and mapped to DIDs or registration numbers.
# We will hold private keys for our mock intermediaries here to allow demo-signing.
INTERMEDIARY_PRIVATE_KEYS: Dict[str, str] = {
    "INZ000123456": "05fda31a842c7a70c4e65c92f7e14049111dca37bf3f4686ed4c6db902dd2ee9", # Zerodha Private Key
    "INZ000987654": "0f2a62befc91f78355775c0a98f7ce3b75fcb929859197251ba9f34575206f9b", # Groww Private Key
    "INA000011111": "af8d6317597265b1a96070802707d06dab0b282079f98343b22b0c15cc2fc16d"  # NiftyWealth Private Key
}

SIGNATURE_TAG = b"\n--SATYA-CHECK-SIGNATURE--\n"

def get_sebi_public_key() -> str:
    return SEBI_PUBLIC_KEY_HEX

def generate_keypair() -> Tuple[str, str]:
    """Helper to generate new Ed25519 keypair as hex strings."""
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    
    private_hex = private_key.private_bytes_raw().hex()
    public_hex = public_key.public_bytes_raw().hex()
    return private_hex, public_hex

def sign_text_envelope(text: str, signer_id: str, private_key_hex: str) -> Dict:
    """Sign text content and return a verifiable JSON-LD envelope."""
    try:
        private_bytes = bytes.fromhex(private_key_hex)
        private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_bytes)
        
        payload_bytes = text.encode("utf-8")
        signature = private_key.sign(payload_bytes)
        
        return {
            "content": text,
            "signer": signer_id,
            "signature": signature.hex()
        }
    except Exception as e:
        raise ValueError(f"Signing failed: {str(e)}")

def verify_text_envelope(envelope: Dict, public_key_hex: str) -> bool:
    """Verify a JSON-LD style envelope signature."""
    try:
        content = envelope.get("content", "")
        signature_hex = envelope.get("signature", "")
        
        public_bytes = bytes.fromhex(public_key_hex)
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_bytes)
        
        payload_bytes = content.encode("utf-8")
        sig_bytes = bytes.fromhex(signature_hex)
        
        public_key.verify(sig_bytes, payload_bytes)
        return True
    except InvalidSignature:
        return False
    except Exception:
        return False

def sign_file_c2pa(file_bytes: bytes, signer_id: str, private_key_hex: str) -> bytes:
    """
    Simulates C2PA provenance injection.
    Signs the original file bytes and appends a structured signature block at the end of the file.
    """
    private_bytes = bytes.fromhex(private_key_hex)
    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_bytes)
    
    # Sign the file bytes
    signature = private_key.sign(file_bytes)
    
    metadata = {
        "signer": signer_id,
        "signature": signature.hex(),
        "algorithm": "Ed25519",
        "standard": "C2PA-Lite"
    }
    
    metadata_json_bytes = json.dumps(metadata).encode("utf-8")
    
    # Append the tag and metadata to the end of the file bytes
    signed_file = file_bytes + SIGNATURE_TAG + metadata_json_bytes
    return signed_file

def verify_file_c2pa(signed_file_bytes: bytes, public_key_hex: str) -> Tuple[bool, Optional[bytes], Optional[Dict]]:
    """
    Verify the signature embedded in the file bytes.
    Returns: (is_valid, original_file_bytes, metadata)
    """
    if SIGNATURE_TAG not in signed_file_bytes:
        return False, None, None
        
    try:
        parts = signed_file_bytes.rsplit(SIGNATURE_TAG, 1)
        original_bytes = parts[0]
        metadata_json_bytes = parts[1]
        
        metadata = json.loads(metadata_json_bytes.decode("utf-8"))
        signature_hex = metadata.get("signature", "")
        
        public_bytes = bytes.fromhex(public_key_hex)
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_bytes)
        
        sig_bytes = bytes.fromhex(signature_hex)
        public_key.verify(sig_bytes, original_bytes)
        
        return True, original_bytes, metadata
    except InvalidSignature:
        return False, None, None
    except Exception:
        return False, None, None
