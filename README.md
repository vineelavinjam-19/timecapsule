# ⏳ TimeCapsule

### Secure Digital Time Capsule Platform with Blockchain-Based Integrity Verification, Automated Future Delivery, and AI-Powered Security

<p align="center">

**Store today. Unlock tomorrow. Preserve memories forever.**

*A secure web platform that enables users to schedule encrypted digital memories—including messages, images, videos, and documents—for automatic delivery at a future date while ensuring authenticity, integrity, and secure access.*

</p>

---

## 📖 Overview

**TimeCapsule** is a full-stack web application designed to preserve digital memories by allowing users to create time capsules that remain inaccessible until a specified future date.

Unlike traditional cloud storage, TimeCapsule focuses on **future-based digital communication**, combining automated scheduling, blockchain-inspired integrity verification, machine learning-based spam detection, secure authentication, and comprehensive audit logging to provide a trustworthy and tamper-resistant digital preservation platform.

The system is designed around modern software engineering principles including modular architecture, RESTful APIs, secure authentication, automated workflows, and data integrity verification.

---

# ✨ Key Features

### ⏰ Future Scheduling

* Schedule digital capsules for any future date
* Automatic release when unlock conditions are met
* Time-based delivery automation

### 📧 Automated Email Delivery

* Automatic email notifications
* Scheduled capsule delivery
* SMTP integration

### 📁 Multimedia Support

Upload and preserve

* Text Messages
* Images
* Videos
* PDF Documents
* Office Files

---

### 🔐 Security & Integrity

* Blockchain-inspired integrity verification
* SHA-256 cryptographic hashing
* Tamper detection
* Secure authentication
* Protected access workflow
* File validation
* Secure API endpoints

---

### 🤖 Intelligent Security

Integrated Machine Learning module for

* Spam detection
* Malicious content filtering
* Suspicious upload detection

---

### 📜 Audit & Transparency

* Activity logging
* User audit trail
* Capsule history
* Access request logs
* Administrative monitoring

---

## 🏗️ System Architecture

```text
                        User
                          │
                          ▼
                 Web Frontend (HTML/CSS/JS)
                          │
                          ▼
                  Flask REST API Server
                          │
     ┌────────────────────┼────────────────────┐
     ▼                    ▼                    ▼
 MongoDB Database   ML Spam Detection   Email Scheduler
     │                    │                    │
     └────────────────────┼────────────────────┘
                          │
                          ▼
          Blockchain Integrity Verification
                          │
                          ▼
                 Scheduled Future Delivery
```

---

# ⚙️ Technology Stack

## Frontend

* HTML5
* CSS3
* JavaScript

## Backend

* Python
* Flask
* Flask-CORS

## Database

* MongoDB

## Security

* SHA-256 Hashing
* Authentication
* Audit Logging
* Secure File Validation

## Artificial Intelligence

* Scikit-learn
* Joblib
* Machine Learning Spam Detection

## Email Services

* Gmail SMTP

## Development Tools

* Git
* GitHub
* VS Code
* Postman

---

# 🔐 Security Architecture

TimeCapsule prioritizes data security throughout the application lifecycle.

Implemented security mechanisms include:

* Secure Authentication
* Password Protection
* SHA-256 Integrity Verification
* Blockchain-Based Hash Validation
* Machine Learning Spam Detection
* Access Request Authorization
* Activity Audit Logs
* Secure File Upload Validation

---

# 🤖 Machine Learning Module

The platform integrates a supervised Machine Learning model for spam detection before storing user-generated content.

### Workflow

```text
Training Dataset
        │
        ▼
Feature Extraction
        │
        ▼
Model Training
        │
        ▼
Saved ML Model
        │
        ▼
Real-Time Spam Prediction
        │
        ▼
Accept / Reject Capsule
```

---

# ⛓️ Blockchain Integrity Verification

To protect digital memories from unauthorized modifications, every capsule is associated with a cryptographic hash.

The blockchain-inspired verification layer provides:

* Tamper detection
* Integrity verification
* Immutable record validation
* Secure hash comparison before unlocking
* Trustworthy digital preservation

---

# 📂 Project Structure

```text
TimeCapsule/

├── backend/
│   ├── app.py
│   ├── models/
│   ├── blockchain/
│   ├── ml/
│   ├── uploads/
│   └── services/
│
├── frontend/
│   ├── html/
│   ├── css/
│   ├── js/
│   └── assets/
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/vineelavinjam-19/timecapsule.git
```

Move into the project directory

```bash
cd timecapsule
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the environment

**Windows**

```bash
venv\Scripts\activate
```

**macOS/Linux**

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Configure environment variables

```env
EMAIL_USER=your_email
EMAIL_PASS=your_app_password

MONGO_URI=mongodb://localhost:27017
```

Start MongoDB

```bash
mongod
```

Run the Flask application

```bash
python app.py
```

---

# 📡 API Modules

* User Authentication
* Capsule Management
* Future Scheduling
* File Upload
* Spam Detection
* Blockchain Verification
* Audit Logs
* Email Delivery

---

# 📸 Screenshots

Add screenshots of:

* Login Page
* Dashboard
* Create Capsule
* Unlock Capsule
* Audit Dashboard
* Blockchain Verification
* Spam Detection
* Email Delivery

---

# 🎯 Future Enhancements

* End-to-End Encryption
* IPFS Distributed Storage
* Smart Contract Integration
* Multi-Factor Authentication
* Cloud Deployment
* Mobile Application
* AI Memory Summarization
* Voice Capsules
* Video Capsules
* Digital Legacy Management

---

# 📈 Highlights

* Full-Stack Web Application
* RESTful Architecture
* Machine Learning Integration
* Blockchain-Based Integrity Verification
* Automated Future Scheduling
* Secure Authentication
* MongoDB Database
* Email Automation
* Audit Logging
* Modular & Scalable Design

---

# 👩‍💻 Author

**Vineela Vinjam**

Computer Science Engineering Student

Passionate about

* Artificial Intelligence
* Full-Stack Development
* Cybersecurity
* Blockchain Applications
* Backend Engineering
* Cloud Technologies

GitHub:
https://github.com/vineelavinjam-19

---

# 📄 License

Licensed under the **MIT License**.

---

# ⭐ Support

If you found this project useful or inspiring, consider giving it a **⭐ Star** on GitHub. Contributions, suggestions, and feedback are always welcome.
