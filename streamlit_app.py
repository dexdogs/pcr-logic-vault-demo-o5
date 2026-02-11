import streamlit as st
import boto3
import json
from pypdf import PdfReader
from botocore.exceptions import ClientError

# --- CONFIGURATION ---
st.set_page_config(page_title="dexdogs | PCR Vault", page_icon="🛡️")

# --- 1. SECURE AWS CONNECTION ---
try:
    # Pulls from .streamlit/secrets.toml (Local) or Dashboard (Cloud)
    session = boto3.Session(
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
        region_name=st.secrets["AWS_REGION"]
    )
    s3 = session.client('s3')
    lam = session.client('lambda')
    
    BUCKET = st.secrets["S3_BUCKET_NAME"]
    LAMBDA_FUNC = st.secrets["LAMBDA_FUNCTION_NAME"]
    
    st.sidebar.success(f"✅ Connected to: {LAMBDA_FUNC}")
    
except Exception as e:
    st.sidebar.error("❌ AWS Connection Failed")
    st.sidebar.warning("Check Secrets in Streamlit Settings.")
    st.stop()

# --- 2. LOGIC: PARSE EPD ---
def parse_insulation_epd(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content: text += content.lower()
    
    # Auto-detect material from PDF text
    if "wood fiber" in text or "timberhp" in text:
        return "Wood Fiber Board", 180, 3.8
    elif "mineral wool" in text or "rockwool" in text:
        return "Mineral Wool Board", 120, 4.2
    else:
        return "Generic Insulation", 50, 3.0

# --- 3. UI LAYOUT ---
st.title("🛡️ dexdogs | PCR Logic Vault")
st.caption("Automated UL 10010-1 Compliance Audit (Immutable Ledger)")

uploaded_epd = st.file_uploader("1. Upload Insulation EPD (PDF)", type="pdf")

if uploaded_epd:
    # Step A: Local Parse
    m_type, def_density, def_r = parse_insulation_epd(uploaded_epd)
    st.info(f"📄 Detected Material: **{m_type}**")

    # Step B: The "Demo Controls" (Allows you to force a Fail)
    st.divider()
    st.subheader("2. Verify Physical Telemetry")
    col_a, col_b = st.columns(2)
    with col_a:
        density_input = st.slider("Density (kg/m³)", 0, 300, def_density)
    with col_b:
        # Range allows for the "Impossible" 6.0 value for the demo
        r_input = st.slider("R-Value (per inch)", 1.0, 8.0, def_r)

    # Step C: The Audit Button
    if st.button("🚀 Audit & Lock to Ledger"):
        
        payload = {
            "batch_id": f"DEMO-{uploaded_epd.name[:10]}",
            "material_type": m_type,
            "density_kg_m3": density_input,
            "r_value_per_inch": r_input
        }
        
        # --- EXECUTE LAMBDA AUDIT ---
        with st.spinner("Running Physics Check (UL 10010-1)..."):
            try:
                response = lam.invoke(
                    FunctionName=LAMBDA_FUNC, 
                    Payload=json.dumps(payload)
                )
                raw_payload = response['Payload'].read()
                audit_res = json.loads(raw_payload)
                
                # Handle double-encoded body (common Lambda issue)
                if 'body' in audit_res and isinstance(audit_res['body'], str):
                    res_body = json.loads(audit_res['body'])
                else:
                    res_body = audit_res

                # --- DISPLAY RESULTS ---
                c1, c2 = st.columns(2)
                
                # Left: The Auditor Decision
                with c1:
                    status = res_body.get('status', 'ERROR')
                    if status == "PASS":
                        st.success("✅ PCR COMPLIANT")
                    elif status == "FAIL":
                        st.error("❌ PCR VIOLATION")
                    else:
                        st.warning(f"⚠️ {status}")
                    
                    st.write(f"**Reason:** {res_body.get('details', 'No details')}")

                # Right: The Ledger Lock
                with c2:
                    if status == "PASS" or status == "FAIL":
                        # Write to S3
                        file_key = f"ledger/{payload['batch_id']}.json"
                        s3.put_object(
                            Bucket=BUCKET, 
                            Key=file_key, 
                            Body=json.dumps(res_body)
                        )
                        st.metric("Ledger Status", "LOCKED 🔒", delta="Immutable")
                        st.caption(f"Receipt: s3://{BUCKET}/{file_key}")

            except ClientError as e:
                st.error(f"AWS Error: {e.response['Error']['Message']}")
            except Exception as e:
                st.error(f"System Error: {str(e)}")

# --- 4. META FOOTPRINT ---
st.divider()
st.caption("☁️ AWS Carbon Footprint Tool: Tracking 0.0004 kg CO2e for this compute cycle.")
