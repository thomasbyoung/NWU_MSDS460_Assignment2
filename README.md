# **MSDS 460 - Assignment 2: Networking Models - Project Management**

## **Project Repository: Applied Optimization and Recommendation Systems**

This repository contains multiple projects developed as part of **MSDS 460 - Assignment 2: Network Models - Project Management** at **Northwestern University**.

## **Table of Contents**

- [Overview](#overview)
- [Projects](#projects)
  - [Project Schedule Desktop App](#project-schedule-desktop-app)
  - [Project Schedule Solver (Web App)](#project-schedule-solver-web-app)
  - [DineWise: Restaurant Recommendation System](#dinewise-restaurant-recommendation-system)
- [GenAI Tools](#general-ai-and-automation-considerations)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

## **Overview**

This project looks at how network models and linear programming (LP) can improve project scheduling by optimizing resource allocation and reducing completion time. The implementation consists of a PuLP-based optimization model, a directed graph for task relationships, and both a desktop and web-based interface. Beyond the core optimization, I built interactive features to improve usability. A simple Tkinter GUI lets users adjust task durations, while a web-based version provides real-time forecasting using vanilla JavaScript. The assumption is that team members will log their hours, keeping project managers updated via a dashboard. A mock proposal (included in the same folder) outlines system capabilities and possible refinements for a hypothetical client. 

 DineWise is a prototype of the requested application. Although it meets core requirements (Alipine.js, Go, etc), it also currently runs on JSON files rather than a hosted Postgres DB. To fully test, signing up for Yelp Fusion app will be necessary. 

- **Project Schedule Optimization**: Uses **linear programming (LP) models** to optimize project timelines and minimize cost.
- **Restaurant Recommendation System**: Uses **Yelp GraphQL API** and **data analytics** to enhance restaurant discovery.


---

## **Projects**

### **1. Project Schedule Desktop App**

📌 **Description:**  
A **desktop-based application** for project scheduling and optimization. It provides an **interactive UI** that allows users to define tasks, analyze multiple scenarios, and generate **Gantt charts**.

📂 **Location:** [`/DesktopApp`](./ProjectManagement/DesktopApp)

🛠 **Technologies:**

- Python (`tkinter`, `pulp`, `matplotlib`)
- JSON-based task configurations

🚀 **Features:**

- Editable **task list** for dynamic scheduling
- **Three scenario models**: Best-case, Expected, Worst-case
- **Gantt chart visualization** for timeline planning
- **Real-time schedule optimization** using **PuLP solver**

📖 **Detailed Setup & Instructions:**  
Refer to the [Project Schedule Desktop App README](./ProjectManagement/DesktopApp/README.md)

---

### **2. Project Schedule Solver (Web App)**

📌 **Description:**  
A **web-based application** that visualizes project schedules, computes **critical paths**, and provides cost estimates based on **worker allocation**.

📂 **Location:** [`/WebApp`](./ProjectManagement/WebApp)

🛠 **Technologies:**

- **Vanilla JavaScript**
- **Chart.js** for Gantt visualization
- **javascript-lp-solver** for constraint optimization

🚀 **Features:**

- **Interactive project timeline**
- **Scenario-based analysis** (Best/Expected/Worst)
- **Dynamic worker cost calculations**
- **Real-time solving** with `javascript-lp-solver`

📖 **Detailed Setup & Instructions:**  
Refer to the [Project Schedule Solver README](./ProjectManagement/WebApp/README.md)

---

### **3. DineWise: Restaurant Recommendation System**

📌 **Description:**  
A **full-stack web application** that provides **restaurant recommendations** based on user preferences, location, and **Yelp data**.

📂 **Location:** [`/DineWise`](./_DineWise)

🛠 **Technologies:**

- **Frontend**: Alpine.js, Tailwind CSS
- **Backend**: Go, PostgreSQL
- **Data Processing**: Python, Yelp GraphQL API

🚀 **Features:**

- **Restaurant search & filtering**
- **Yelp integration for real-time data**
- **GraphQL API for data retrieval**
- **Review analysis & sentiment tracking** (planned feature)

📖 **Detailed Setup & Instructions:**  
Refer to the [DineWise README](./_DineWise/README.md)

---

## **GenAI Tools**

### 🔹 **Use of Generative AI (GenAI)**

This project leveraged generative AI tools in the development process, particularly in brainstorming and debugging implementation details. In addition, generative AI played a role in drafting and refining project documentation. For example, these tools assisted in formatting this markdown document. The final work remains my own and using AI tools accelurated my productivity and ensured clarity.

AI used: Copilot, Claude, DeepSeekR1 (locally).
AI Logs: ./Logs/aiLogs.txt

## **Future Enhancements**

🚀 **Possible Extensions Across Projects**

1. **Advanced AI for Project Scheduling**:

   - Train **machine learning models** for schedule estimation
   - Implement **Monte Carlo simulations** for uncertainty modeling

2. **DineWise Feature Expansions**:

   - **Personalized recommendations** based on past user interactions
   - **Sentiment analysis** of Yelp reviews

---

## **License**

This repository is licensed under the **MIT License**. See [LICENSE](./LICENSE) for details.
