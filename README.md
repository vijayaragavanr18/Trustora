# 🛡️ Trustora: AI-Powered Deepfake Forensic & Digital Evidence Platform

**Deepfake Detection. Forensic Accountability. Blockchain Immutability.**

Trustora is a comprehensive enterprise-grade platform designed to detect digital manipulations across images, audio, and video while providing a cryptographically secure chain of custody for digital evidence.

---

## 🚀 The Vision

In an era of generative AI, "seeing is no longer believing." Trustora solves the crisis of digital trust by providing dual-layer protection:

1.  **AI Forensics**: Detecting deepfakes and generative AI artifacts.
2.  **Digital Truth**: Sealing evidence on the blockchain to ensure it remains untampered from capture to courtroom.

---

## ✨ Key Features

### 🧠 Advanced AI Detection Engine

- **Multi-Modal Analysis**: Specialized pipelines for Image, Audio, and Video.
- **Forensic Heatmaps**: Visual representation of manipulation hotspots in images using edge-divergence and saturation analysis.
- **Temporal Video Consistency**: Analyzes "flicker" and interpolation artifacts across video frames to detect temporal deepfakes.
- **Wav2Vec2 Audio Analysis**: AI-powered voice cloning detection trained on synthetic speech datasets.
- **Ensemble Scoring**: Combines pre-trained HuggingFace ViT models with classical signal forensics (MFCC, Laplacian variance, Phase analysis).

### 🔗 Blockchain Evidence Sealing

- **Cryptographic Fingerprinting**: Generates unique SHA-256 hashes for every file and its corresponding analysis result.
- **Sepolia Testnet Integration**: "Seals" the evidence fingerprint on the blockchain, creating an immutable, timestamped record of the truth.
- **Visual Proof**: Direct integration with Etherscan, allowing anyone to verify the integrity of a report.

### 📁 Digital Evidence Locker

- **Secure Storage**: Encrypted storage for high-value media assets.
- **Trusted Capture**: Mobile-ready capture interface that signs media at the point of origin.
- **Soft-Delete Ecosystem**: Enterprise-grade recycle bin logic with backend-sync for accidental deletion recovery.

### 📄 Professional Forensic Reporting

- **Automated PDF Generation**: Clean, court-ready PDF reports including risk levels, artifact lists, and blockchain transaction IDs.
- **Batch Export**: Select and export multiple cases as a single compressed forensic archive (Zip).

---

## 🛠️ Tech Stack

### Frontend

- **Framework**: Next.js 15 (App Router)
- **State Management**: React Hooks & Context
- **Animations**: Framer Motion (for high-fidelity status transitions)
- **UI Components**: Tailwind CSS & Lucide React
- **API Client**: Axios with JWT interceptors

### Backend

- **API**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Background Tasks**: Python BackgroundTasks for asynchronous heavy-lifting ML analysis.
- **Security**: JWT (JSON Web Tokens) with Organization-level isolation.

### AI & Forensics

- **Models**:
  - Image: `ViT-Deepfake-Detector` (HuggingFace)
  - Audio: `Wav2Vec2-Deepfake-Audio-V2`
- **Libraries**: OpenCV, Librosa, Scikit-learn, Torch (PyTorch), Transformers (HuggingFace).

---

## 📐 System Architecture

1.  **Ingestion**: Files are uploaded or captured via the Trusted Node.
2.  **Decomposition**: Videos are sampled into frames; audio is processed into MFCC spectrograms.
3.  **Analysis**: Files run through the "Ensemble Analyzer" (Signal Forensics + AI Model Inference).
4.  **Sealing**: The outcome is hashed and sent to the Blockchain Sealer.
5.  **Reporting**: A forensic PDF is generated and made available in the Secure Locker.

---

## 🚦 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (or SQLite for local dev)

### Backend Setup

1.  Navigate to `/Trustora-backend`
2.  Install dependencies: `pip install -r requirements.txt`
3.  Initialize the database: `python main.py`
4.  Run the server: `uvicorn app.main:app --reload`

### Frontend Setup

1.  Navigate to `/Trustora`
2.  Install dependencies: `npm install`
3.  Configure `.env.local`:
    ```bash
    NEXT_PUBLIC_API_URL=http://localhost:8000
    ```
4.  Run the dev server: `npm run dev`

---

## 🔮 Future Roadmap

- [ ] **Real-time Deepfake Stream Interception**: Integrate with browser extensions to detect deepfakes in live meetings.
- [ ] **Chainlink Integration**: Use Decentralized Oracles to feed real-world metadata into the blockchain seal.
- [ ] **Collaborative Forensics**: Allow multiple investigative teams to share and analyze evidence lockers securely.

---

## ⚖️ License & Disclaimer

Trustora is a forensic tool designed to assist in digital investigations. AI analysis results are probabilistic and should be reviewed by qualified human forensic experts.

---

**Built for the Hackathon by [Your Team Name]**
