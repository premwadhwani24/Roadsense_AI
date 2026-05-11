# RoadSense AI - Migration Guide from Original to Enhanced Version

## What's New

The enhanced version includes:
1. **Authentication System** - User login with JWT tokens
2. **Role-Based Access** - Admin, Engineer, Viewer roles
3. **Alert Management** - Real-time alerts with notifications
4. **Work Order System** - Track and manage repairs
5. **Database Backend** - SQLite with multiple tables
6. **Citizen Reporting** - Crowdsourced road issue reports
7. **Analytics** - Historical trending and KPIs
8. **Budget Tracking** - Cost management per city
9. **Enhanced UI** - New dashboard with multiple tabs

## Migration Steps

### Step 1: Backup Original Files
```bash
# Optional but recommended
cp -r . ../roadsense_backup
```

### Step 2: Update Requirements
```bash
pip install -r requirements.txt
```

### Step 3: Initialize Database
```bash
python setup.py
```

This will:
- Create `roadsense.db` SQLite database
- Initialize all tables
- Create default admin user

### Step 4: Choose Your Frontend

#### Option A: Use New Enhanced Frontend (Recommended)
```bash
# In index.html, change script source from:
<script src="/static/app.js"></script>
# to:
<script src="/static/app_enhanced.js"></script>
<link rel="stylesheet" href="/static/style_enhanced.css">
```

#### Option B: Continue with Original Frontend
The original `app.py` still works but has limited features.

### Step 5: Run Application
```bash
# Using enhanced version:
python app_enhanced.py

# OR using original version:
python app.py
```

## API Migration

### Original Endpoints Still Available
- `/health` - Health check
- `/api/locations` - Get states/cities
- `/api/roads` - Get road segments

### New Required Endpoints
- `POST /api/auth/login` - Must login first
- `GET /api/roads/status` - Enhanced road status
- `GET /api/alerts` - New alerts system
- `GET /api/work-orders` - New work orders

## Database Changes

### New Tables Added
```
users           - User accounts and roles
alerts          - Road condition alerts
work_orders     - Maintenance work orders
road_history    - Historical condition tracking
citizen_reports - Crowdsourced reports
budget_tracking - Budget management
```

### Sample Data
Existing `ROAD_SEGMENTS` data will work but needs to be migrated to database:

```python
from database import DatabaseManager
# Road data is loaded from ROAD_SEGMENTS in app_enhanced.py
# Historical data automatically created for analytics
```

## Breaking Changes

### Authentication Required
All new endpoints except citizen reporting require JWT token:
```bash
# Get token
curl -X POST http://localhost:5000/api/auth/login \
  -d '{"username":"admin","password":"admin123"}'

# Use token in requests
curl -H "Authorization: Bearer <token>" http://localhost:5000/api/roads/status
```

### URL Changes
Some endpoints have changed:
- Old: `/api/roads`
- New: `/api/roads/status`

## Configuration

### Environment Variables (Optional)
Create `.env` file or set in system:

```bash
# Admin credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# API Keys
GOOGLE_MAPS_KEY=your_key
OPENWEATHER_KEY=your_key
TOMTOM_KEY=your_key

# Email/Notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production

# SMS (Optional - Twilio)
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=+1234567890
```

## Testing the New Features

### Test 1: Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### Test 2: Get Roads Status
```bash
curl -X GET http://localhost:5000/api/roads/status \
  -H "Authorization: Bearer <your_token>"
```

### Test 3: Create Alert
```bash
curl -X POST http://localhost:5000/api/alerts \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "road_id":"R001",
    "road_name":"NH-52 Segment A",
    "severity":"RED",
    "description":"Severe pothole"
  }'
```

### Test 4: Create Work Order
```bash
curl -X POST http://localhost:5000/api/work-orders \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "road_id":"R001",
    "road_name":"NH-52 Segment A",
    "work_type":"Pothole Repair",
    "contractor":"ABC Contractors",
    "estimated_cost":50000
  }'
```

## Troubleshooting

### Database File Already Exists
```bash
# Backup and delete old database
mv roadsense.db roadsense_old.db
python setup.py
```

### Import Errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Permission Denied (Windows)
```powershell
# Run in PowerShell as Administrator
python setup.py
```

## Rollback to Original

If you want to revert to the original version:

```bash
# Stop the application
# Switch back to original files
python app.py

# The database won't interfere with original app
```

## Data Preservation

- Original `ROAD_SEGMENTS` data is preserved in `simulated_data.py`
- New features use SQLite database (`roadsense.db`)
- You can use both systems simultaneously
- Data from new features won't be used by original app

## Performance Considerations

### Database Queries
- Road status queries are fast (< 100ms for 100 roads)
- Alert queries are optimized with indexes
- Consider adding pagination for large reports

### Scalability
For production deployment:
1. Migrate to PostgreSQL from SQLite
2. Add Redis for caching
3. Use connection pooling
4. Add database indexes on frequently queried columns

## Next Steps

1. ✓ Run setup.py
2. ✓ Create additional users for your team
3. ✓ Configure email notifications
4. ✓ Set up budget allocations
5. ✓ Add your road data or use sample data
6. ✓ Train ML model (optional - use train.py)
7. ✓ Deploy to production

## Support

For issues or questions:
1. Check README_ENHANCED.md
2. Review API documentation
3. Check logs for error messages
4. Ensure all dependencies are installed

## Version Info
- Enhanced Version: 2.0
- Original Version: 1.0
- Database: SQLite 3
- Python: 3.8+
