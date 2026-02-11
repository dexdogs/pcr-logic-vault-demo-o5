# pcr-logic-vault-demo-o5
### dexdogs | The Immutable Carbon Ledger for Insulation

**A high-fidelity proof-of-concept for the 2026 "Buy Clean" construction market.**

This repository demonstrates the **dexdogs AWS Pipeline**, which automates the **UL 10010-1 PCR** (Product Category Rule) for building insulation. By encoding physics-based auditing directly into the cloud, we eliminate greenwashing and provide "Scalable Trust" for federal and corporate buyers.

---

## The Hook: Physics-Based Trust
Traditional EPDs (Environmental Product Declarations) are static PDF promises. **dexdogs** turns them into live, audited receipts.

1. **PCR Logic as Code**: Every material batch is audited by an AWS Lambda function against density and R-value tolerances.
2. **Immutable Ledger**: Verified audits are locked in an **Amazon S3 bucket** with **Object Lock** enabled—making the data tamper-proof for 10+ years.
3. **Full-Stack Accountability**: We report the "Meta-Footprint" of the cloud infrastructure itself via the AWS Carbon Tool.

---

## Technical Architecture

* **Frontend**: Streamlit (Python)
* **Compute**: AWS Lambda (Automated Auditor)
* **Storage**: Amazon S3 (Object-Locked Carbon Ledger)
* **Standard**: UL 10010-1 (Building Envelope Thermal Insulation)

---

## Security & Transparency
This is a **Public Repository** used to demonstrate our open-source PCR logic. 
* **Zero Hardcoded Keys**: All AWS credentials are managed via **GitHub Actions Secrets** and **Streamlit Secrets**.
* **Audit-Proof**: The underlying S3 ledger is private and protected by IAM policies, ensuring that only verified pipeline data is entered.

---

## Stakeholders
This demo is designed for:
* **Manufacturers** (e.g., TimberHP, Rmax) to defend high-performance carbon claims.
* **PCR Writers/Auditors** (e.g., UL Solutions, Thomas Gloria) to automate manual math checks.
* **Big Buyers** (e.g., GSA, Google) to secure "Scope 3" supply chain data.

---

© 2026 dexdogs. Solving the environment's data problem.
