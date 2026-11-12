# 🛡️ HerShield – Women’s Safety & SOS Web Application

**HerShield** is a women-focused safety web application designed to help women respond to emergency situations and stay connected with trusted contacts.

The main idea behind HerShield is simple: *every woman should have access to tools that can help her feel more informed, connected, and supported while travelling or moving around.*

The application brings together SOS alerts, live location tracking, emergency contacts, and a Safe Journey feature in one platform.

🔗 **Live Website:** https://hershield-i2am.onrender.com

💻 **GitHub Repository:** https://github.com/adyasingh8/HerShield

---

## ✨ Key Features

### 🚨 1. SOS Emergency Alert
- Trigger an SOS alert during an emergency.
- Send emergency notifications to registered emergency contacts.
- Share the user's location with the alert.
- Stop an active SOS alert when assistance is no longer needed.

### 📍 2. Live Location Tracking
- Uses the browser's Geolocation API to access the user's location with permission.
- Updates location coordinates while tracking is active.
- Displays the location on an interactive map.

### 👥 3. Emergency Contact Management
- Add and manage trusted emergency contacts.
- Save contact information for emergency notifications.
- Use registered contacts when an SOS alert is triggered.

### 🗺️ 4. Safe Journey
- Start and end a journey through the application.
- Share a journey tracking link with trusted people.
- Track journey progress using live location updates.
- View journey routes on an interactive map.

### 📜 5. SOS History
- View previously triggered SOS alerts.
- Check recorded alert information and status.
- Access location information associated with previous alerts.

### 🔐 6. User Authentication
- User registration and login.
- Individual user sessions.
- Access to personal dashboard and safety features.

---

## 🧰 Technology Stack

| Category | Technologies |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, Flask |
| Database | MySQL / TiDB Cloud |
| Database Integration | Flask-SQLAlchemy, PyMySQL |
| Maps | Leaflet.js |
| Map Data | OpenStreetMap |
| Geolocation | Browser Geolocation API |
| Geocoding | Photon API |
| Route Calculation | OSRM API |
| Email Notifications | Gmail SMTP |
| Deployment | Render |
| Version Control | Git and GitHub |

---

## 🔌 APIs and Services Used

HerShield uses different APIs and services to provide its location-based features.

| API / Service | Purpose |
|---|---|
| Browser Geolocation API | Retrieves the user's location with permission. |
| Photon API | Converts location coordinates or place names into readable locations. |
| OSRM API | Calculates routes between locations. |
| OpenStreetMap | Provides map data and map tiles. |
| Flask REST APIs | Handles SOS alerts, location updates, and journey operations. |

**Note:** Leaflet.js is a JavaScript mapping library used to display interactive maps.

---

## ⚙️ How HerShield Works

1. A user registers and logs into the application.
2. The user adds trusted emergency contacts.
3. In an emergency, the user can trigger the SOS feature.
4. The application records the alert and location information.
5. The emergency notification is sent to configured contacts.
6. The user can also start a Safe Journey and share its tracking link.
7. Location updates help trusted people follow the journey.

---

## 🖥️ Running the Project Locally

Follow these steps to run HerShield on your computer.

### 1. Clone the Repository

```bash
git clone https://github.com/adyasingh8/HerShield.git
```

### 2. Open the Project Folder

```bash
cd HerShield
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root and add your own configuration:

```env
SECRET_KEY=your_secret_key

DB_HOST=your_database_host
DB_USER=your_database_username
DB_PASSWORD=your_database_password
DB_NAME=your_database_name
DB_PORT=3306

EMAIL_ADDRESS=your_email_address
EMAIL_APP_PASSWORD=your_email_app_password
```

Add any additional database SSL configuration required by your database provider.

**Important:** Never upload your `.env` file or actual credentials to GitHub.

### 6. Set Up the Database

Create the required MySQL database and configure its tables using the project's database schema or backup.

Make sure the database connection details in your `.env` file are correct.

### 7. Run the Application

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

---

## ☁️ Deployment

HerShield is deployed using **Render**, with **TiDB Cloud** providing a MySQL-compatible cloud database.

- Hosting: Render
- Cloud Database: TiDB Cloud
- Source Code: GitHub

The deployed application can be accessed here:

**https://hershield-i2am.onrender.com**

*Note: The free hosting service may take some time to respond when accessed after a period of inactivity.*

---

## 🎯 Project Objectives

- To develop a technology-based solution focused on women's safety.
- To provide a simple way to trigger emergency alerts.
- To make location sharing and journey tracking easier.
- To connect users with trusted emergency contacts.
- To gain practical experience in full-stack web development and database integration.

---

## 🚀 Future Improvements

Some features that could be added in future versions include:

- Integration with more emergency response services.
- SMS-based emergency notifications.
- Improved mobile responsiveness and user experience.
- More advanced location-sharing options.
- Additional security and privacy improvements.
- Performance testing and scalability improvements.

---

## 🎓 Learning Outcomes

Building HerShield helped me gain practical experience in:

- Full-stack web development.
- Connecting frontend interfaces with Flask backend routes.
- Designing and integrating a MySQL database.
- Working with REST APIs.
- Implementing browser-based GPS tracking.
- Displaying interactive maps and routes.
- Deploying a web application using cloud services.
- Managing project code using Git and GitHub.

---

## ⚠️ Disclaimer

HerShield is an academic and demonstration project developed to explore technology-based approaches to women's safety.

It is not a certified emergency response system and does not guarantee emergency assistance. Users should continue to contact official emergency services when required.

---

## 👩‍💻 Developed By

**Adya Singh**

B.Tech Student | Full-Stack Web Development Project

**Project:** HerShield – Women’s Safety & SOS Web Application

*Built with the aim of using technology to create a more connected and safety-conscious environment for women.*
