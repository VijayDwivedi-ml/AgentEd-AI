# 🎓 ShikshaAI – Intent-Driven Multi-Agent Educational Assistant

🚀 **Live Demo:** https://vijay-demo-633570604567.us-central1.run.app/

🚀 **Video Link:** https://drive.google.com/file/d/1Yt20vBqtLEA0ZZiYjyiwRcteCs7F-9Kq/view

---

## 🌟 Overview

**ShikshaAI** is an **intent-driven, multi-agent AI system** designed to assist educators with lesson planning, task management, scheduling, and real-time data-driven teaching insights.

Built using **Google ADK + Gemini + Firestore**, this system demonstrates how multiple AI agents can collaborate to solve real-world productivity and education challenges.

---

## 🧠 Key Idea

Instead of a single AI assistant, ShikshaAI uses a **Primary Orchestrator Agent** that intelligently routes user requests to specialized sub-agents:

* 📚 Teaching Agent → Assignments & grading
* 📅 Calendar Agent → Scheduling & meetings
* ✅ Task Agent → Tasks, notes & reminders
* 🎓 ShikshaAI Agent → Lesson generation + education intelligence

---

## ⚡ Core Features

### 🎓 1. AI Lesson Generation (Multi-Language)

* Generate structured lesson plans (Explanation, Activities, Homework)
* Supports multiple languages (Hindi, English, etc.)
* Saves lessons to database for reuse

---

### 📊 2. Real-Time Education Insights (MCP Integration)

* India education statistics (World Bank data)
* Trending education topics (Google Trends)
* Comparative country analysis
* Data-driven teaching insights

---

### 📋 3. Assignment Management

* Create, list, and delete assignments
* Auto-grade student submissions with feedback

---

### 📅 4. Smart Scheduling

* Schedule office hours
* Manage meetings with attendees
* Check availability

---

### ✅ 5. Task & Productivity System

* Add / complete / delete tasks
* Priority-based tracking
* Notes management with search

---

### 💾 6. Persistent Cloud Storage

* Powered by **Google Cloud Firestore**
* Stores:

  * Tasks
  * Assignments
  * Notes
  * Lesson Plans

---

## 🧩 Architecture Diagram

<img width="1295" height="648" alt="image" src="https://github.com/VijayDwivedi-ml/AgentEd-AI/blob/main/img/arch_dia.PNG" />

---

## 🎯 How to Test the System

👉 Use the **live deployed link**:
https://vijay-demo-633570604567.us-central1.run.app/

### 🧪 Try These Prompts

#### 📚 Lessons

* `Generate lesson for Science, Grade 5, Topic Photosynthesis, Language Hindi`
* `List my lessons`
* `Search lessons for photosynthesis`

#### 📊 Data Insights (🔥 Highlight Feature)

* `Show me India's education statistics`
* `What’s trending in education?`
* `Compare India vs US education`

#### 📋 Assignments

* `Create assignment for CS101: Python Quiz, due 2026-04-10, 50 points`
* `List assignments`

#### ✅ Tasks

* `Add high priority task: Grade papers tomorrow`
* `List my tasks`
* `Clear all tasks`

#### 📅 Scheduling

* `Schedule office hours for Math on 2026-04-10 from 10:00 to 12:00`
* `Check availability for 2026-04-10`

---

## 💡 What Makes This Project Special?

### ✨ 1. True Multi-Agent System

* Not a single chatbot — **multiple specialized agents collaborating**

### ✨ 2. Data + AI Fusion

* Combines **LLMs + real-world datasets**
* Enables **data-driven teaching decisions**

### ✨ 3. Real-World Use Case

* Built for **teachers, educators, and institutions**

### ✨ 4. Cloud-Native Architecture

* Fully deployed using **Google Cloud**
* Scalable and production-ready design

---

## 🛠️ Tech Stack

* **LLM:** Google Gemini (gemini-2.5-flash)
* **Framework:** Google ADK (Agent Development Kit)
* **Backend:** Python
* **Database:** Google Cloud Firestore
* **APIs (MCP):**

  * World Bank Data
  * Google Trends

---

## ⚙️ Setup Instructions (Local)

```bash
# Clone repo
git clone https://github.com/VijayDwivedi-ml/AgentEd-AI.git


# Install dependencies
pip install -r requirements.txt

```

---
## 📌 Problem Statement Alignment

This project fulfills all requirements of a **Multi-Agent Productivity Assistant**:

* ✅ Multi-agent coordination
* ✅ Tool integration (MCP services)
* ✅ Database persistence (Firestore)
* ✅ Multi-step workflows
* ✅ API-based deployment

---

## 🚀 Future Improvements

* Ecosystem Integrations: 
    - Google Workspace Sync
    - Google Calendar integration for real-time scheduling of lessons and assignments
    - Google Drive/Docs export for generated lesson plans

* LMS Connectivity: 
    - Google Classroom API to push assignments and pull student rosters
    - Canvas API integration for cross-platform assignment management

* Advanced AI & RAG: 
    - AlloyDB AI vector database for semantic search (replacing basic Firestore)
    - Concept-based lesson retrieval instead of keyword-only search

* Syllabus Ingestion:
   - PDF syllabus and textbook upload support
   - Curriculum-grounded lesson generation based on school-specific materials

* Frontend : 
    - Telegram/WhatsApp Bot

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit PRs.

---

## 📜 License

MIT License

---

## 👨‍💻 Author

Built with ❤️ by Vijay, Dhyan, Abhijith

