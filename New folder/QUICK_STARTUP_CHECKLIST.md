# 🎯 STARTUP CHECKLIST - Quick Reference

## 🔴 CRITICAL (Week 1-2)
- [ ] **Database**: Migrate from SQLite to PostgreSQL
  - Time: 2 days
  - Tool: `scripts/migrate_to_postgres.py`
  - Impact: Can't scale without this
  
- [ ] **Security**: Rate limiting + CSRF protection
  - Time: 1 day
  - Tools: `flask-limiter`, `flask-wtf`
  - Impact: Prevents brute force attacks

- [ ] **Error Tracking**: Setup Sentry integration
  - Time: 2 hours
  - Sign up at: sentry.io
  - Impact: Know when things break

- [ ] **Validation**: Input validation on all APIs
  - Time: 1 day
  - Tool: `pydantic`
  - Impact: Prevent SQL injection

- [ ] **Health Check**: Add `/health` endpoint
  - Time: 2 hours
  - Impact: Monitor system status

**Total time: 4-5 days**
**Don't skip any of these**

---

## 🟠 HIGH PRIORITY (Week 3)
- [ ] **Data**: Import real road segments from OSM/government sources
  - Time: 2-3 days
  - Scripts: `scripts/import_road_data.py`
  - Impact: Mock data looks unprofessional

- [ ] **Mobile**: Responsive design optimization
  - Time: 1-2 days
  - Update: `static/style.css`, service worker
  - Impact: Field staff need mobile access

- [ ] **Performance**: Add caching (Redis)
  - Time: 1 day
  - Setup: Redis + `functools.lru_cache`
  - Impact: 10x faster API responses

- [ ] **Testing**: Setup pytest framework
  - Time: 1 day
  - Write basic tests for auth, alerts
  - Impact: Catch bugs before users find them

**Total time: 5-7 days**

---

## 🟡 MEDIUM PRIORITY (Week 4)
- [ ] **Notifications**: Full SMS/Email integration testing
  - Time: 1 day
  - Test with real Twilio account
  - Impact: Users stay informed

- [ ] **Roles**: Refine RBAC, add audit trail
  - Time: 1-2 days
  - Update: `auth.py`, database schema
  - Impact: Better compliance

- [ ] **Deployment**: Setup Nginx + SSL
  - Time: 1 day
  - Use Let's Encrypt (free)
  - Impact: HTTPS everywhere

- [ ] **Monitoring**: Setup application monitoring
  - Time: 1 day
  - Options: Datadog, New Relic, or open-source
  - Impact: Know performance bottlenecks

**Total time: 4-5 days**

---

## 📊 Timeline View

```
WEEK 1        WEEK 2          WEEK 3          WEEK 4        LAUNCH
|-------|-------|-------|-------|-------|-------|-------|-------|
D1  D2  D3  D4  D5  D6  D7  D8  D9  D10 D11 D12 D13 D14 D15 D16
│   │   │   │   │   │   │   │   │   │   │   │   │   │   │   │   │
├─DB─┤  └─SEC─┘ └──VALID──┘     REAL DATA──┤ MOBILE──┤  TEST   │
    └─SENTRY─┤  └─CACHE────┘                           └─RBAC─┤
                                                            └─DEPLOY
```

---

## 🧪 Testing Priorities

### Critical to test:
1. **Login/Authentication**
   - Valid credentials → success
   - Invalid credentials → fail
   - Token expiry → redirect to login

2. **Alert Creation**
   - Create alert → saved to DB
   - Wrong severity → rejected
   - Missing fields → error

3. **Work Orders**
   - Create → status pending
   - Update status → lifecycle works
   - Delete → handled correctly

4. **Load Test**
   - 100 concurrent users → no errors
   - Response time <500ms
   - Database doesn't lock

### Run tests:
```bash
pytest tests/ -v --cov
# Target: >60% code coverage
```

---

## 🔒 Security Checklist

- [ ] All passwords hashed with bcrypt
- [ ] JWT tokens have expiry (24 hours)
- [ ] Rate limiting on login (5 attempts/minute)
- [ ] SQL injection protection (parameterized queries)
- [ ] CORS restricted to known domains
- [ ] API keys not in version control
- [ ] HTTPS everywhere (SSL certificate)
- [ ] Database backups encrypted
- [ ] User sessions logged & monitored
- [ ] Sensitive data not in logs

---

## ⚡ Performance Checklist

- [ ] Database queries indexed
- [ ] API response time <500ms (p95)
- [ ] Static files minified (CSS/JS)
- [ ] Map loading optimized
- [ ] Pagination implemented (don't load all records)
- [ ] Images compressed (< 100KB)
- [ ] Caching working (5min cache for stable data)
- [ ] Load balancing configured (multi-worker)
- [ ] Database connection pooling active
- [ ] CDN used for static assets (optional)

Test with:
```bash
# Load testing
ab -n 1000 -c 100 http://localhost:5000/api/roads

# Response time profiling
python -m cProfile -s cumtime app_enhanced.py
```

---

## 📱 Mobile Checklist

- [ ] Responsive design works on 320px width (phones)
- [ ] Touch targets minimum 48px x 48px
- [ ] Input fields font-size 16px (prevents zoom)
- [ ] Service worker installed (offline support)
- [ ] Maps work on mobile (touch zoom)
- [ ] Forms mobile-optimized
- [ ] Tested on iOS Safari
- [ ] Tested on Android Chrome
- [ ] Lighthouse score >80

Check with:
```bash
# Google PageSpeed
# https://pagespeed.web.dev/

# Chrome DevTools
# F12 → Device Toolbar
```

---

## 📋 Pre-Launch Testing Script

```bash
#!/bin/bash
# test_before_launch.sh

echo "🧪 Running Pre-Launch Tests..."

# 1. Database
echo -n "Database: "
pg_isready -h localhost -p 5432 && echo "✅" || echo "❌"

# 2. API Health
echo -n "API Health: "
curl -s http://localhost:5000/health | grep -q "healthy" && echo "✅" || echo "❌"

# 3. Login Test
echo -n "Login Test: "
curl -s -X POST http://localhost:5000/api/login \
  -d '{"username":"admin","password":"admin123"}' | grep -q "token" && echo "✅" || echo "❌"

# 4. Response Time
echo -n "Response Time: "
TIME=$(curl -s -o /dev/null -w "%{time_total}" http://localhost:5000/api/roads)
if (( $(echo "$TIME < 0.5" | bc -l) )); then echo "✅"; else echo "❌ ($TIME s)"; fi

# 5. Test Coverage
echo -n "Test Coverage: "
pytest --cov=app_enhanced --cov-report=term-missing tests/ > /dev/null 2>&1 && echo "✅" || echo "❌"

# 6. SSL Certificate
echo -n "SSL Certificate: "
[ -f "/path/to/cert.pem" ] && echo "✅" || echo "❌ Missing"

# 7. Backups
echo -n "Database Backup: "
[ -f "backup/roadsense_$(date +%Y%m%d).sql" ] && echo "✅" || echo "❌ Missing"

echo ""
echo "✨ Pre-launch check complete!"
```

---

## 🚀 Go-Live Procedure

### 48 Hours Before:
- [ ] Final database backup
- [ ] Test all critical flows
- [ ] Team on-call roster confirmed
- [ ] Rollback plan documented

### 24 Hours Before:
- [ ] Staging environment matches production
- [ ] Load testing completed successfully
- [ ] Documentation up to date
- [ ] Team briefing conducted

### Launch Day (T-0):
```bash
# 1. Backup production database
pg_dump roadsense > backup/roadsense_$(date +%Y%m%d_%H%M%S).sql

# 2. Stop current service
systemctl stop roadsense

# 3. Deploy code
git pull origin main
pip install -r requirements.txt

# 4. Run database migrations
alembic upgrade head

# 5. Start service
gunicorn -c gunicorn_config.py app_enhanced:app --daemon

# 6. Verify health
curl http://localhost:5000/health

# 7. Monitor logs
tail -f logs/app.log
```

### First Hour:
- [ ] Monitor error logs (should be 0)
- [ ] Check database performance
- [ ] Verify all alerts sending
- [ ] Test first 10 users
- [ ] Check SSL certificate is valid

### First Day:
- [ ] Monitor CPU/memory usage
- [ ] Check database disk space
- [ ] Verify backups running
- [ ] Review user feedback
- [ ] Monitor error rate

---

## 🆘 Troubleshooting Guide

### Issue: High database latency
```bash
# Check indexes
SELECT * FROM pg_stat_user_indexes;

# Check slow queries
SELECT query, calls, mean_time FROM pg_stat_statements ORDER BY mean_time DESC;

# Add missing indexes
CREATE INDEX idx_alerts_status ON alerts(status);
```

### Issue: API rate limiting too strict
```python
# Adjust in flask-limiter config
limiter = Limiter(
    app=app,
    default_limits=["500 per day", "100 per hour"]  # Increase these
)
```

### Issue: Out of memory
```bash
# Check memory usage
top

# Reduce worker count in gunicorn_config.py
workers = 2  # Reduce from 4
```

### Issue: SSL certificate warning
```bash
# Renew Let's Encrypt certificate
certbot renew --force-renewal

# Restart Nginx
nginx -s reload
```

---

## 📞 Emergency Contacts

- **Database Down**: Check PostgreSQL service
  ```bash
  systemctl status postgresql
  ```

- **API Errors**: Check Sentry dashboard

- **Performance Issues**: Check Redis/cache status
  ```bash
  redis-cli ping
  ```

- **SSL Issues**: Check certificate expiry
  ```bash
  openssl x509 -enddate -noout -in /path/to/cert.pem
  ```

---

## ✅ Final Verification

Before declaring launch successful:

```
□ No errors in logs (24 hours)
□ Uptime: 99%+
□ Response time: <500ms (p95)
□ Database: <100ms queries
□ User registration working
□ Alerts triggering correctly
□ Work orders persisting
□ Notifications sending
□ Mobile working
□ Backups running
□ Monitoring active
□ Team trained
□ Documentation complete
```

---

**Status:** Ready for Startup Phase ✨
**Estimated Effort:** 3-4 weeks of full-time development
**Success Metric:** 99%+ uptime, <0.1% error rate, 500+ concurrent users

Good luck! 🚀
