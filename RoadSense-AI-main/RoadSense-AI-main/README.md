# 🚧 RoadSense AI  
### AI-Powered Pothole-Aware Navigation & Road Safety Platform  
*Advanced extension of iWatchRoadv2*
 
---

## 📌 What is RoadSense AI?
RoadSense AI is a smart road safety system that **detects potholes using AI**, **warns drivers in real time**, and **helps authorities repair roads efficiently**.

It combines **computer vision, GPS, and web technologies** to improve driver safety and road maintenance.

---

## ❓ Why This Project?
- Potholes cause accidents and vehicle damage  
- Road inspections are mostly manual and slow  
- Drivers get **no advance warning**  
- Authorities lack **real-time road condition data**  

---

## 💡 What Does RoadSense AI Do?
- Detects potholes automatically from dashcam videos  
- Maps potholes using GPS  
- Alerts drivers before they reach a pothole  
- Provides dashboards for authorities to manage repairs  

---

## ⭐ Core Features

### 🧠 AI Pothole Detection
- YOLOv8 deep learning model  
- Works on dashcam video  
- Classifies severity: **Low / Medium / High**  

### 🧭 Smart Navigation Alerts
- Live GPS tracking  
- Real-time voice alerts  
- Example: *“Pothole ahead in 50 meters. Slow down.”*  

### 🎨 Road Condition Map
- Color-coded roads based on damage level  
- Interactive map using Leaflet  

### 👥 Crowdsourced Verification
- Users confirm or mark potholes as fixed  
- System improves accuracy over time  

### 🏛️ Authority Dashboard
- Track pothole repair status  
- Assign contractors  
- Make data-driven decisions  

### 🔮 Predictive Risk Analysis
- Identifies pothole-prone areas  
- Helps prevent future road damage  

---

## 🧠 System Flow (Simple)
Dashcam → AI Detection → GPS Mapping → Database → Route Check → Driver Alerts → Analytics

---

## 🛠️ Tech Stack

**Backend:** Django, Django REST Framework, PostgreSQL  
**Frontend:** React, TypeScript, Leaflet, Web Speech API  
**AI / ML:** YOLOv8, OpenCV, Scikit-learn  
**DevOps:** Docker, GitHub Actions, AWS / Render / Vercel  

---

## ▶️ How It Works (Step-by-Step)
1. Dashcam video is uploaded  
2. AI detects potholes and records GPS location  
3. Driver starts navigation  
4. System checks nearby potholes continuously  
5. Voice alert warns the driver in advance  
6. Authorities monitor and manage repairs  

---

## 🎥 Demo
A demo video showing **real GPS-based alerts** is available in the `demo` folder.

---

## 🌍 Real-World Usage
- Works on mobile phones and browsers  
- Can scale city by city  
- Suitable for smart city and government use  

---

## 🧾 One-Line Interview Explanation
**“RoadSense AI detects potholes using AI, alerts drivers in real time, and helps authorities manage road repairs efficiently.”**

---


## 🔮 Future Improvements
- Android & iOS mobile app  
- Offline navigation support  
- Google Maps integration  
- Advanced analytics dashboards  

---

## 📜 License
Open-source under Apache-2.0  
Suitable for academic and non-commercial use.
