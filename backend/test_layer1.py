import sys
from layer1_authenticity import sign_file_c2pa, verify_file_c2pa, SEBI_PRIVATE_KEY_HEX, SEBI_PUBLIC_KEY_HEX

def run_tests():
    print("Running Layer 1 Authenticity Backbone tests...")
    
    # 1. Prepare original data
    original_circular = b"SEBI Circular: Mandatory 2FA for trading accounts. Date: 2026-06-15."
    print(f"Original content size: {len(original_circular)} bytes")
    
    # 2. Sign document
    signed_data = sign_file_c2pa(original_circular, "SEBI", SEBI_PRIVATE_KEY_HEX)
    print(f"Signed content size: {len(signed_data)} bytes")
    
    # 3. Verify original signed document
    is_valid, extracted_bytes, metadata = verify_file_c2pa(signed_data, SEBI_PUBLIC_KEY_HEX)
    assert is_valid == True, "Verification failed for original signed document!"
    assert extracted_bytes == original_circular, "Extracted content does not match original!"
    print("SUCCESS: Test 1: Signed document successfully verified.")
    
    # 4. Tamper test: Modify a character in the content (e.g. change '2' to '3' for 3FA)
    tampers = bytearray(signed_data)
    # The word '2FA' starts somewhere near index 30. Let's find '2' and change it.
    idx = tampers.find(b"2FA")
    if idx != -1:
        tampers[idx] = ord("3")  # Change to 3FA
        print(f"Tampered at index {idx} ('2FA' -> '3FA')")
    else:
        # Fallback tamper
        tampers[0] = ord("X")
        print("Tampered at index 0")
        
    tampered_data = bytes(tampers)
    
    # 5. Verify tampered document (should fail!)
    is_valid_tampered, extracted_bytes_tampered, metadata_tampered = verify_file_c2pa(tampered_data, SEBI_PUBLIC_KEY_HEX)
    assert is_valid_tampered == False, "Tampered document was incorrectly verified as valid!"
    print("SUCCESS: Test 2: Tampered document verification failed as expected (tamper-proofing works).")
    
    print("\nAll Layer 1 tests passed successfully!")

if __name__ == "__main__":
    run_tests()
