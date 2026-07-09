import os
import time
import json
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import registry
import layer1_authenticity as l1
import layer2_detection as l2

app = FastAPI(title="SatyaCheck API", version="1.0.0")

# Enable CORS for frontend and browser extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock Metrics Store
METRICS_DATA = {
    "total_scans": 128,
    "layer1_verified": 42,
    "layer2_flagged": 76,
    "false_positives": 1,
    "false_negatives": 2,
    "latencies_ms": [120, 180, 240, 95, 110, 150],
}

class TextVerifyRequest(BaseModel):
    text: str
    envelope: Optional[Dict[str, Any]] = None

@app.get("/api/health")
def health():
    return {"status": "healthy"}

@app.get("/api/registry")
def get_registry():
    """Retrieve SEBI intermediary registry."""
    return registry.INTERMEDIARIES_DB

@app.post("/api/sign")
def sign_data(
    content: str = Form(...),
    signer_id: str = Form("SEBI"),
    is_file: bool = Form(False)
):
    """
    Utility endpoint to sign text or create a signed file bytes block for testing.
    Uses the mock private keys.
    """
    if signer_id == "SEBI":
        private_key = l1.SEBI_PRIVATE_KEY_HEX
    elif signer_id in l1.INTERMEDIARY_PRIVATE_KEYS:
        private_key = l1.INTERMEDIARY_PRIVATE_KEYS[signer_id]
    else:
        raise HTTPException(status_code=400, detail="Invalid or unregistered signer ID")

    if is_file:
        # Generate a signed dummy file (representing a signed circular)
        content_bytes = content.encode("utf-8")
        signed_bytes = l1.sign_file_c2pa(content_bytes, signer_id, private_key)
        
        # Return as hex so it's easy to transmit/manipulate on the frontend
        return {
            "signer": signer_id,
            "signed_hex": signed_bytes.hex(),
            "filename": f"signed_circular_{signer_id.lower()}.txt"
        }
    else:
        # Return a signed JSON-LD text envelope
        envelope = l1.sign_text_envelope(content, signer_id, private_key)
        return envelope

@app.post("/api/verify")
async def verify_artifact(
    text: Optional[str] = Form(None),
    envelope_json: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Main SatyaCheck verification endpoint.
    Handles text, signed envelopes, or raw file uploads (image/audio/video/PDF).
    """
    start_time = time.time()
    METRICS_DATA["total_scans"] += 1
    
    verdict = {
        "status": "UNVERIFIED",
        "layer_applied": 1,
        "signer": None,
        "risk_score": 0,
        "explanation": "No indicators checked yet.",
        "claims_report": None,
        "phishing_report": None,
        "media_report": None,
        "latency_ms": 0
    }
    
    text_content = text or ""
    
    # CASE A: A file is uploaded
    if file:
        file_bytes = await file.read()
        filename = file.filename or "unknown"
        file_size = len(file_bytes)
        
        # 1. Attempt Layer 1 verification (embedded C2PA manifest)
        # Try verifying with SEBI public key
        is_valid, original_bytes, metadata = l1.verify_file_c2pa(file_bytes, l1.SEBI_PUBLIC_KEY_HEX)
        signer_found = "SEBI" if is_valid else None
        
        # If not signed by SEBI, try verifying with registered intermediaries
        if not is_valid:
            for reg_id, intermediary in registry.INTERMEDIARIES_DB.items():
                is_valid, original_bytes, metadata = l1.verify_file_c2pa(file_bytes, intermediary.public_key_hex)
                if is_valid:
                    signer_found = intermediary.name
                    break
        
        # If valid Layer 1 signature is found
        if is_valid and metadata and original_bytes:
            METRICS_DATA["layer1_verified"] += 1
            verdict.update({
                "status": "VERIFIED_GENUINE",
                "layer_applied": 1,
                "signer": signer_found,
                "risk_score": 0,
                "explanation": f"Cryptographically signed by SEBI-authorized issuer: {signer_found}. Ground truth verified.",
                "latency_ms": int((time.time() - start_time) * 1000)
            })
            METRICS_DATA["latencies_ms"].append(verdict["latency_ms"])
            return verdict
            
        # Tampered verification test: Did it have a signature tag, but failed validation?
        elif l1.SIGNATURE_TAG in file_bytes:
            # The file has a signature tag, but it was invalid (indicates tampering!)
            verdict.update({
                "status": "TAMPERED",
                "layer_applied": 1,
                "risk_score": 100,
                "explanation": "WARNING: Cryptographic signature detected but payload validation failed. The content of this document has been modified/altered since publication.",
                "latency_ms": int((time.time() - start_time) * 1000)
            })
            METRICS_DATA["latencies_ms"].append(verdict["latency_ms"])
            return verdict
            
        # 2. Layer 1 failed (No valid signature). Apply Layer 2 Detection Net
        verdict["layer_applied"] = 2
        
        # Treat files with text representation
        if filename.endswith(".txt") or filename.endswith(".pdf"):
            try:
                # OCR/Text extraction mock
                text_content = original_bytes.decode("utf-8") if is_valid else file_bytes.decode("utf-8", errors="ignore")
            except Exception:
                text_content = "Mock PDF Content representing unverified claim."
        else:
            text_content = f"Uploaded media file: {filename}"
            
        # Score media if audio or video
        media_report = None
        is_audio = any(ext in filename.lower() for ext in [".mp3", ".wav", ".m4a", ".aac"])
        is_video = any(ext in filename.lower() for ext in [".mp4", ".mov", ".avi", ".webm"])
        
        if is_audio:
            media_report = l2.score_voice_clone(filename, file_bytes)
            verdict["media_report"] = media_report
        elif is_video:
            media_report = l2.score_deepfake_video(filename, file_bytes)
            verdict["media_report"] = media_report

    # CASE B: JSON-LD Envelope uploaded
    elif envelope_json:
        try:
            envelope = json.loads(envelope_json)
            signer_id = envelope.get("signer", "")
            
            # Retrieve signer public key from database
            public_key = None
            if signer_id == "SEBI":
                public_key = l1.SEBI_PUBLIC_KEY_HEX
            else:
                intermediary = registry.lookup_intermediary(signer_id)
                if intermediary:
                    public_key = intermediary.public_key_hex
                    
            if public_key and l1.verify_text_envelope(envelope, public_key):
                METRICS_DATA["layer1_verified"] += 1
                verdict.update({
                    "status": "VERIFIED_GENUINE",
                    "layer_applied": 1,
                    "signer": signer_id,
                    "risk_score": 0,
                    "explanation": f"Verifiable credential envelope validated successfully. Signed by: {signer_id}.",
                    "latency_ms": int((time.time() - start_time) * 1000)
                })
                METRICS_DATA["latencies_ms"].append(verdict["latency_ms"])
                return verdict
            else:
                verdict.update({
                    "status": "TAMPERED" if signer_id else "UNVERIFIED",
                    "layer_applied": 1,
                    "risk_score": 95 if signer_id else 0,
                    "explanation": "Verification failed. Envelope signature is invalid or signer registry not found.",
                    "latency_ms": int((time.time() - start_time) * 1000)
                })
                METRICS_DATA["latencies_ms"].append(verdict["latency_ms"])
                return verdict
        except Exception as e:
            text_content = text or str(envelope_json)

    # Apply Layer 2 for text
    verdict["layer_applied"] = 2
    claims_report = l2.analyze_claims(text_content)
    phishing_report = l2.analyze_phishing(text_content)
    
    verdict["claims_report"] = claims_report
    verdict["phishing_report"] = phishing_report
    
    # Calculate fused risk score
    c_score = claims_report.get("max_severity_score", 0)
    p_score = phishing_report.get("phishing_risk_score", 0)
    m_score = 0
    if verdict.get("media_report") and verdict["media_report"].get("is_synthetic"):
        m_score = verdict["media_report"]["confidence_score"]
        
    fused_score = max(c_score, p_score, m_score)
    verdict["risk_score"] = int(fused_score)
    
    # Compose explanation
    explanation_parts = []
    if fused_score >= 80:
        verdict["status"] = "SUSPICIOUS"
        explanation_parts.append("HIGH RISK DETECTED.")
    elif fused_score >= 40:
        verdict["status"] = "WARNING"
        explanation_parts.append("POTENTIAL THREAT.")
    else:
        verdict["status"] = "UNVERIFIED"
        explanation_parts.append("Unsigned document.")

    # Add specifics
    if claims_report.get("findings"):
        for f in claims_report["findings"]:
            if f["severity"] in ["HIGH", "CRITICAL"]:
                explanation_parts.append(f"Filing Mismatch: {f['evidence']}")
    if phishing_report.get("indicators"):
        explanation_parts.append(f"Phishing indicators: {'; '.join(phishing_report['indicators'])}")
    if verdict.get("media_report") and verdict["media_report"].get("is_synthetic"):
        explanation_parts.append(f"Media anomaly: {list(verdict['media_report']['details'].values())[0]}")
        
    if len(explanation_parts) <= 1:
        explanation_parts.append("No cryptographic signature found. Information check yields no major regulatory mismatches or scams, but treat as unverified.")
        
    verdict["explanation"] = " ".join(explanation_parts)
    
    if verdict["status"] in ["SUSPICIOUS", "TAMPERED"]:
        METRICS_DATA["layer2_flagged"] += 1
        
    verdict["latency_ms"] = int((time.time() - start_time) * 1000)
    METRICS_DATA["latencies_ms"].append(verdict["latency_ms"])
    return verdict

@app.post("/api/call-guardian")
def call_guardian_chunk(
    chunk_base64: str = Form(...),
    chunk_index: int = Form(...),
    stream_id: str = Form(...)
):
    """
    Call-Guardian endpoint.
    Accepts sequential base64 audio chunks representing streaming voice calls.
    Returns real-time warnings if synthesis metrics spike.
    """
    # Simulate a stream analysis where chunk 3 onwards shows high synthesis artifacts for demo
    is_spoof = False
    confidence = 0.0
    reason = "Voice liveness parameters normal."
    
    if "fake" in stream_id.lower() or "synthesized" in stream_id.lower():
        if chunk_index >= 2:
            is_spoof = True
            confidence = 89.6
            reason = "WARNING: Synthesized audio profile matched. Flat intonation / absence of spectral breathing cues."
            
    return {
        "stream_id": stream_id,
        "chunk_index": chunk_index,
        "is_spoof": is_spoof,
        "confidence": confidence,
        "reason": reason,
        "timestamp": time.time()
    }

@app.get("/api/metrics")
def get_metrics():
    """Retrieve validation metrics for the dashboard."""
    total = METRICS_DATA["total_scans"]
    l1_c = METRICS_DATA["layer1_verified"]
    l2_c = METRICS_DATA["layer2_flagged"]
    fp = METRICS_DATA["false_positives"]
    fn = METRICS_DATA["false_negatives"]
    latencies = METRICS_DATA["latencies_ms"]
    
    # Calculate performance metrics
    # TP = Flagged correctly + Verified genuine correctly
    # FP = 1, FN = 2
    # Mocking standard binary metrics for the evaluation split
    precision = 98.4
    recall = 96.2
    f1 = 97.3
    roc_auc = 0.991
    avg_latency = sum(latencies) / len(latencies) if latencies else 150.0
    
    return {
        "total_scans": total,
        "layer1_verified": l1_c,
        "layer2_flagged": l2_c,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "roc_auc": roc_auc,
        "false_positive_rate": 0.8,
        "avg_latency_ms": round(avg_latency, 1),
        "confusion_matrix": {
            "true_positive": 74,
            "false_positive": 1,
            "true_negative": 51,
            "false_negative": 2
        }
    }

# Mock translation dictionary for Bhashini
TRANSLATIONS = {
    "hindi": {
        "Cryptographically signed by SEBI-authorized issuer: SEBI. Ground truth verified.": 
            "सेबी-अधिकृत जारीकर्ता: सेबी द्वारा प्रमाणित रूप से हस्ताक्षरित। सत्यता सत्यापित।",
        "WARNING: Cryptographic signature detected but payload validation failed. The content of this document has been modified/altered since publication.":
            "चेतावनी: क्रिप्टोग्राफिक हस्ताक्षर का पता चला लेकिन पेलोड सत्यापन विफल रहा। प्रकाशन के बाद से इस दस्तावेज़ की सामग्री को संशोधित/बदला गया है।",
        "HIGH RISK DETECTED. Homoglyph/lookalike domains detected.":
            "उच्च जोखिम का पता चला। नकली डोमेन की पहचान की गई है।",
    },
    "tamil": {
        "Cryptographically signed by SEBI-authorized issuer: SEBI. Ground truth verified.":
            "செபி-அங்கீகரிக்கப்பட்ட வழங்குநரால் கையொப்பமிடப்பட்டது: செபி. உண்மைத்தன்மை சரிபார்க்கப்பட்டது.",
        "WARNING: Cryptographic signature detected but payload validation failed. The content of this document has been modified/altered since publication.":
            "எச்சரிக்கை: கையொப்பம் கண்டறியப்பட்டது ஆனால் சரிபார்ப்பு தோல்வியடைந்தது. இந்த ஆவணத்தின் உள்ளடக்கம் வெளியிடப்பட்டதிலிருந்து மாற்றப்பட்டுள்ளது.",
    }
}

@app.post("/api/translate")
def translate_verdict(text: str = Form(...), language: str = Form(...)):
    """Mock Bhashini translation interface."""
    lang_lower = language.lower()
    if lang_lower in TRANSLATIONS and text in TRANSLATIONS[lang_lower]:
        return {"translated_text": TRANSLATIONS[lang_lower][text]}
        
    # Simple fallback rule-based translator for terms if exact matches aren't present
    if lang_lower == "hindi":
        translated = text.replace("VERIFIED GENUINE", "प्रमाणित रूप से वास्तविक")\
                         .replace("TAMPERED", "छेड़छाड़ की गई")\
                         .replace("SUSPICIOUS", "संदिग्ध")\
                         .replace("UNVERIFIED", "अपुष्ट")
        return {"translated_text": translated}
    elif lang_lower == "tamil":
        translated = text.replace("VERIFIED GENUINE", "உண்மையானது என சரிபார்க்கப்பட்டது")\
                         .replace("TAMPERED", "சேதப்படுத்தப்பட்டது")\
                         .replace("SUSPICIOUS", "சந்தேகத்திற்குரியது")
        return {"translated_text": translated}
        
    return {"translated_text": text}

@app.post("/api/whatsapp/chat")
async def whatsapp_chat(
    message: str = Form(...),
    language: str = Form("english")
):
    """
    Real-time WhatsApp bot emulator powered by Groq AI.
    Analyzes and validates claims against official SEBI registry data.
    """
    import registry
    import httpx
    
    # Format database items cleanly for the model prompt
    registry_context = {
        "intermediaries": [item.dict() for item in registry.INTERMEDIARIES_DB.values()],
        "corporate_filings": [item.dict() for item in registry.CORPORATE_FILINGS],
        "sebi_circulars": {k: v.dict() for k, v in registry.SEBI_CIRCULARS.items()}
    }

    system_prompt = f"""
You are SatyaCheck Bot, an elite AI-driven Securities Market Integrity Guard developed for SEBI (Securities and Exchange Board of India).
Your task is to analyze forwarded messages, circulars, stock tips, or claims sent by retail investors and determine if they are genuine, suspicious, or a scam.

Here is the SEBI Ground Truth Registry Data to cross-reference:
{json.dumps(registry_context, indent=2)}

Rules for Analysis:
1. Verify Signatures / Provenance: If a message claims to be an official SEBI circular, cross-reference the circulars registry.
2. Check Corporate Filings: If a message makes claims about corporate actions (buybacks, dividends, splits) for companies like Reliance, TCS, or Infosys, cross-reference the filings registry. Highlight price mismatches.
3. Identify Common Scams: Look for signs of guaranteed returns, pump-and-dump, unregistered Telegram channel links, or demands for UPI payments under SEBI's name (SEBI never accepts fines via UPI).
4. Response Tone: Keep the reply concise, professional, clear, and formatted as a helpful WhatsApp message with emojis.
5. Language: You must write the entire response in '{language}' (e.g. if 'hindi', write in Hindi; if 'tamil', write in Tamil).
"""

    headers = {
        "Authorization": f"Bearer {os.environ.get('GROQ_API_KEY', 'YOUR_GROQ_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ],
        "temperature": 0.2,
        "max_tokens": 800
    }
    
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=15.0)
            if res.status_code != 200:
                raise HTTPException(status_code=res.status_code, detail=f"Groq API Error: {res.text}")
            
            response_data = res.json()
            reply = response_data["choices"][0]["message"]["content"]
            return {"reply": reply}
    except Exception as e:
        # Fallback to local rule-based verification if Groq API fails
        import layer2_detection
        verdict = layer2_detection.analyze_claims(message)
        
        # Analyze_claims doesn't return an explanation directly, it returns findings
        explanation = "Information check yields no major regulatory mismatches."
        if verdict.get("findings"):
            explanation = " ".join([f["claim"] + " - " + f["evidence"] for f in verdict["findings"]])
            
        return {"reply": f"⚠️ [Local Scanner Fallback] {explanation}"}

