# RoadSense AI - Enhanced Version

## Overview
RoadSense AI is a comprehensive road condition monitoring and management system with AI-powered analytics, real-time alerts, and citizen crowdsourcing capabilities.

## New Features Implemented

### 1. **Authentication & User Management**
- User registration and login with JWT tokens
- Role-based access control (Admin, Engineer, Viewer)
- User profiles with email, phone, and city tracking
- Default admin account: `admin` / `admin123`

### 2. **Real-time Alerts & Notifications**
- Create severity-based alerts (GREEN, YELLOW, RED)
- Email and SMS notifications for engineers
- Alert history with status tracking (open/resolved)
- Automatic alert assignment to teams

### 3. **Maintenance Work Order Management**
- Create and track repair work orders
- Assign contractors and track costs
- Multiple work types (Pothole Repair, Resurfacing, Drainage, etc.)
- Work order lifecycle management (pending → in_progress → completed)
- Cost tracking and budget integration

### 4. **Historical Analytics & Trending**
- Track road condition changes over time
- Historical data storage for trend analysis
- Days since repair calculations
- Predictive degradation based on material and age
- Time-series data for forecasting

### 5. **Advanced Dashboard KPIs**
- Total roads monitoring
- Green/Yellow/Red road distribution
- Open alerts count
- Pending work orders
- Average days since repair
- Oldest road tracking

### 6. **Crowdsourced Citizen Reporting**
- Public API for citizens to report road issues
- GPS location-based reporting
- Issue verification system with voting
- Photo upload support (prepared)
- Multiple issue types: potholes, cracks, flooding, debris

### 7. **Budget Tracking & Analytics**
- City-level budget allocation
- Spent vs. remaining budget tracking
- Year-based budget management
- Cost-benefit analysis for repairs

### 8. **Export & Reporting**
- Excel report generation
- PDF export capability (ready)
- Comprehensive road status reports
- Summary sheets with KPIs
- Filterable reports by state/city

### 9. **Database Features**
- SQLite backend with migration support
- User accounts table
- Alerts management table
- Work orders table
- Road history (for analytics)
- Citizen reports table
- Budget tracking table

### 10. **API Endpoints**
All endpoints support JWT authentication where required.

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/user` - Get current user info

#### Roads & Status
- `GET /api/roads/status` - Get all roads with condition status
- `GET /api/locations` - Get states and cities
- `GET /api/analytics/kpis` - Get key performance indicators

#### Alerts
- `GET /api/alerts` - Get all alerts
- `POST /api/alerts` - Create new alert
- `PUT /api/alerts/<id>/resolve` - Resolve an alert

#### Work Orders
- `GET /api/work-orders` - Get all work orders
- `POST /api/work-orders` - Create new work order
- `PUT /api/work-orders/<id>` - Update work order status

#### Analytics
- `GET /api/analytics/trending/<road_id>` - Get road trending data
- `GET /api/dashboard/summary` - Get full dashboard summary

#### Citizen Reports
- `POST /api/reports/citizen` - Submit citizen report (public)
- `GET /api/reports/citizen` - Get all reports (requires auth)
- `PUT /api/reports/citizen/<id>/verify` - Verify report

#### Budget
- `GET /api/budget/<city>` - Get city budget
- `POST /api/budget/<city>` - Set city budget

#### Exports
- `GET /api/export/report` - Download Excel report

## File Structure

```
roadsense_webapp/
├── app.py                    # Original Flask app
├── app_enhanced.py           # New enhanced backend
├── database.py               # Database models and manager
├── auth.py                   # Authentication and JWT
├── notifications.py          # Email/SMS notifications
├── train.py                  # ML model training
├── simulated_data.py         # Sample data
├── requirements.txt          # Python dependencies
├── roadsense.db             # SQLite database (created on first run)
├── templates/
│   ├── index.html           # Original frontend
│   └── index_enhanced.html  # New enhanced frontend
└── static/
    ├── style.css            # Original styles
    ├── style_enhanced.css   # New enhanced styles
    ├── app.js               # Original JS
    └── app_enhanced.js      # New enhanced JS
```

## Installation & Setup

### 1. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python -c "from database import init_database; init_database()"
```

### 3. Set Environment Variables (Optional)
```bash
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD=yourpassword
export GOOGLE_MAPS_KEY=your_key
export OPENWEATHER_KEY=your_key
export SMTP_SERVER=smtp.gmail.com
export EMAIL_SENDER=your_email@gmail.com
export EMAIL_PASSWORD=your_app_password
```

### 4. Run the Application
```bash
python app_enhanced.py
```

Open `http://localhost:5000` in your browser.

## Default Credentials
- **Username:** admin
- **Password:** admin123
- **Role:** admin

## Quick Start

### 1. Login
Visit the app and login with default credentials

### 2. View Dashboard
- See all roads with their condition status
- View KPIs: total roads, green/yellow/red counts
- Check open alerts and pending work orders

### 3. Create Work Order
- Click a road in the table
- Click "Create WO" button
- Fill in work type, contractor, and cost
- Submit to track repair

### 4. Create Alert
- Click "Create Alert" button
- Select severity level
- Add description
- Notifications sent to team

### 5. Manage Reports
- Switch to "Citizen Reports" tab
- View crowdsourced road issues
- Verify and respond to reports

## Role-Based Permissions

### Admin
- All permissions
- User management
- Budget management
- Report export
- System configuration

### Engineer
- Create/manage work orders
- Create/resolve alerts
- Verify citizen reports
- View analytics

### Viewer
- View-only access
- Can see roads and alerts
- Cannot create or modify

## Notification Configuration

### Email Setup
Use Gmail with App Passwords:
1. Enable 2-Factor Authentication on Gmail
2. Generate App Password
3. Set environment variables:
   ```bash
   EMAIL_SENDER=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   ```

### SMS Setup
Requires Twilio account:
```bash
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=+1234567890
```

## API Usage Examples

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### Get Roads Status
```bash
curl -X GET http://localhost:5000/api/roads/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create Work Order
```bash
curl -X POST http://localhost:5000/api/work-orders \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "road_id":"R001",
    "road_name":"NH-52 Segment A",
    "work_type":"Pothole Repair",
    "contractor":"ABC Contractors",
    "estimated_cost":50000,
    "notes":"Emergency repair needed"
  }'
```

### Submit Citizen Report
```bash
curl -X POST http://localhost:5000/api/reports/citizen \
  -H "Content-Type: application/json" \
  -d '{
    "latitude":28.6139,
    "longitude":77.2090,
    "issue_type":"pothole",
    "description":"Large pothole on Ring Road"
  }'
```

## Database Schema

### Users Table
- id, username, email, password_hash, role, city, phone, created_at, last_login

### Alerts Table
- id, road_id, road_name, severity, status, description, created_at, resolved_at, assigned_to

### Work Orders Table
- id, road_id, road_name, work_type, contractor, estimated_cost, actual_cost, status, start_date, end_date, created_by, created_at

### Road History Table
- id, road_id, road_name, condition_status, traffic_level, weather_condition, recorded_at

### Citizen Reports Table
- id, latitude, longitude, issue_type, description, image_path, verified, verification_count, status, created_at

### Budget Tracking Table
- id, city, year, allocated_budget, spent, remaining, updated_at

## Future Enhancements

1. **Mobile App** - React Native or Flutter app
2. **Real-time Map** - Google Maps integration
3. **Weather Integration** - Real-time weather data
4. **Traffic Analysis** - Real-time traffic impact
5. **ML Predictions** - Predictive maintenance scheduling
6. **Image Processing** - AI-based road damage detection
7. **Offline Mode** - Work offline and sync
8. **Multi-language** - Support for multiple languages
9. **Advanced Analytics** - Statistical analysis and reporting
10. **Integration APIs** - Connect to government systems

## Troubleshooting

### Database Error
```bash
python -c "from database import init_database; init_database()"
```

### JWT Token Error
- Tokens expire after 24 hours
- Login again to get a new token

### Email Not Sending
- Check SMTP configuration
- Verify email credentials
- Enable "Less Secure Apps" on Gmail (if applicable)

## Support & Contribution
For issues or suggestions, contact the development team or create an issue in the repository.

## License
RoadSense AI © 2024. All rights reserved.
