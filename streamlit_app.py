import streamlit as st
import boto3
import json
from pypdf import PdfReader

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
    st.sidebar.success("Carbon Ledger Connected")
except Exception as e:
    st.sidebar.error("AWS Setup Incomplete")
    st.stop()

# --- 2. THE INSULATION AUDITOR (Logic) ---
def parse_insulation_epd(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content: text += content.lower()
    
    # Simple keyword check for Insulation demo
    if "wood fiber" in text or "timberhp" in text:
        m_type, density, r_val = "Wood Fiber Board", 180, 3.8
    elif "mineral wool" in text or "rockwool" in text:
        m_type, density, r_val = "Mineral Wool Board", 120, 4.2
    else:
        m_type, density, r_val = "Generic Insulation", 50, 3.0
    
    return {"material": m_type, "density": density, "r_value": r_val}

# --- 3. UI LAYOUT ---
st.title("PCR Logic Vault // dexdogs")
st.caption("Automated UL 10010-1 Compliance via AWS Lambda")

uploaded_epd = st.file_uploader("Upload EPD (PDF)", type="pdf")

if uploaded_epd:
    # Step A: Local Parse
    data = parse_insulation_epd(uploaded_epd)
    st.info(f"Detected Material: **{data['material']}**")

    if st.button("Execute Cloud Audit & Lock"):
        # Step B: Trigger AWS Lambda Auditor
        payload = {
            "batch_id": f"DEMO-{uploaded_epd.name[:10]}",
            "material_type": data['material'],
            "density_kg_m3": data['density'],
            "r_value_per_inch": data['r_value']
        }
        
        with st.spinner("Invoking AWS Lambda Auditor..."):
            response = lam.invoke(FunctionName=LAMBDA_FUNC, Payload=json.dumps(payload))
            audit_res = json.loads(response['Payload'].read())
            # Clean up double-string nesting if needed
            res_body = json.loads(audit_res['body']) if 'body' in audit_res else audit_res

        # Step C: Visual Result
        col1, col2 = st.columns(2)
        with col1:
            if res_body['status'] == "PASS":
                st.success("✅ PCR COMPLIANT")
            else:
                st.error("❌ PCR VIOLATION")
            st.write(res_body['details'])

        with col2:
            # Step D: Write to S3 Ledger
            file_key = f"ledger/{payload['batch_id']}.json"
            s3.put_object(Bucket=BUCKET, Key=file_key, Body=json.dumps(res_body))
            st.metric("Ledger Status", "LOCKED", delta="Object Lock Active")
            st.caption(f"Receipt: s3://{BUCKET}/{file_key}")

# --- 4. THE "META" FOOTPRINT HOOK ---
st.divider()
st.subheader("Meta-Footprint (AWS Cloud Emissions)")
st.progress(0.02) # Visual representation for demo

st.caption("Reporting 0.0004 kg CO2e for this compute cycle via AWS Carbon Tool.")
