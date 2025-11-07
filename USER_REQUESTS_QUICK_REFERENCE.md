# ⚡ User Requests System - Quick Reference Card

## 🔐 Required Header (All Requests)

```
X-User-ID: your_user_id
```

---

## 📝 Create Article Request

```bash
curl -X POST http://localhost:8000/api/v1/article-requests/request \
  -H "Content-Type: application/json" \
  -H "X-User-ID: analyst_001" \
  -d '{
    "title": "Article Title",
    "topic": "main_topic",
    "article_type": "analysis",
    "priority": 3
  }'
```

**Response:**
```json
{
  "status": "success",
  "request_id": "req_abc123"
}
```

---

## 🔍 Get Your Requests

```bash
curl http://localhost:8000/api/v1/article-requests/my-requests \
  -H "X-User-ID: analyst_001"

# Filter by status
curl "http://localhost:8000/api/v1/article-requests/my-requests?status=pending" \
  -H "X-User-ID: analyst_001"
```

**Status Values:** `pending`, `assigned`, `in_progress`, `completed`, `rejected`

---

## 💭 Add Thinking to Request

```bash
curl -X POST http://localhost:8000/api/v1/article-requests/req_abc123/thinking \
  -H "Content-Type: application/json" \
  -H "X-User-ID: analyst_001" \
  -d '{
    "thinking_content": "Your suggestion or perspective",
    "stage": "pre_generation",
    "thinking_type": "suggestion",
    "adoption_priority": 8
  }'
```

**Stages:** `pre_generation`, `draft_review`, `refinement`, `final`

**Types:** `suggestion`, `perspective`, `fact_check`, `improvement`, `analysis`

**Priority:** 0-10 (higher = more important)

---

## 📊 Get Request Summary

```bash
curl http://localhost:8000/api/v1/article-requests/req_abc123/orchestration \
  -H "X-User-ID: analyst_001"
```

Returns: Request details + all thinking + statistics

---

## ▶️ Generate Article

```bash
curl -X POST http://localhost:8000/api/v1/article-requests/req_abc123/generate \
  -H "X-User-ID: analyst_001"
```

**Response:**
```json
{
  "status": "success",
  "article_id": "article_xyz789",
  "user_thinking_incorporated": 3
}
```

---

## 💬 Get Thinking for Request

```bash
curl http://localhost:8000/api/v1/article-requests/req_abc123/thinking \
  -H "X-User-ID: analyst_001"
```

Returns: All thinking contributions for this request

---

## 👤 Get Your Thinking

```bash
curl http://localhost:8000/api/v1/article-requests/user/analyst_001/thinking \
  -H "X-User-ID: analyst_001"
```

Returns: All your contributions across all requests

---

## 🎯 Get Request Details

```bash
curl http://localhost:8000/api/v1/article-requests/request/req_abc123 \
  -H "X-User-ID: analyst_001"
```

Returns: Full request details including status

---

## 👑 Admin: Get Pending Requests

```bash
curl http://localhost:8000/api/v1/article-requests/pending \
  -H "X-User-ID: reviewer_001"
```

Returns: All pending requests (highest priority first)

---

## 👑 Admin: Update Request Status

```bash
# Mark as in progress
curl -X POST http://localhost:8000/api/v1/article-requests/req_abc123/status/in_progress \
  -H "X-User-ID: reviewer_001"

# Reject with reason
curl -X POST "http://localhost:8000/api/v1/article-requests/req_abc123/status/rejected?rejection_reason=Already%20covered" \
  -H "X-User-ID: reviewer_001"
```

**Valid Statuses:** `pending`, `assigned`, `in_progress`, `completed`, `rejected`

---

## 📋 Request Body Reference

### Complete Request Format

```json
{
  "title": "Article Title (required)",
  "topic": "Main topic (required)",
  "article_type": "analysis",
  "desired_angle": "Specific perspective",
  "key_points": [
    "Point 1",
    "Point 2",
    "Point 3"
  ],
  "required_sources": [
    "http://source1.com",
    "http://source2.com"
  ],
  "exclude_sources": [
    "http://source3.com"
  ],
  "background_context": "Why this article is needed",
  "estimated_length": "medium",
  "target_audience": "investors",
  "priority": 3,
  "deadline": "2024-02-15T10:00:00"
}
```

### Article Type Options
- `historical` - Past events
- `present` - Current situation
- `future` - Predictions/forecasts
- `analysis` - Deep analysis
- `opinion` - Opinion piece

### Length Options
- `short` - 500-1000 words
- `medium` - 1000-2000 words
- `long` - 2000+ words

### Audience Options
- `policymakers`
- `general_public`
- `investors`
- `academics`
- `media`

### Priority Scale
- `1` - Low priority
- `2` - Normal priority
- `3` - Medium priority
- `4` - High priority
- `5` - Critical/Urgent

---

## 🔄 Thinking Contribution Quick Examples

### Suggestion (Pre-Generation)

```bash
curl -X POST http://localhost:8000/api/v1/article-requests/req_123/thinking \
  -H "Content-Type: application/json" \
  -H "X-User-ID: analyst_001" \
  -d '{
    "thinking_content": "Include recent RBZ monetary policy statements",
    "stage": "pre_generation",
    "thinking_type": "suggestion",
    "adoption_priority": 8
  }'
```

### Perspective (Pre-Generation)

```bash
curl -X POST http://localhost:8000/api/v1/article-requests/req_123/thinking \
  -H "Content-Type: application/json" \
  -H "X-User-ID: analyst_002" \
  -d '{
    "thinking_content": "Political factors heavily influence economic outcomes - should emphasize policy environment",
    "stage": "pre_generation",
    "thinking_type": "perspective",
    "adoption_priority": 7
  }'
```

### Fact Check (Draft Review)

```bash
curl -X POST http://localhost:8000/api/v1/article-requests/req_123/thinking \
  -H "Content-Type: application/json" \
  -H "X-User-ID: reviewer_001" \
  -d '{
    "thinking_content": "2024 inflation figure appears incorrect - should be 24.3% not 23.8%",
    "stage": "draft_review",
    "thinking_type": "fact_check",
    "adoption_priority": 9
  }'
```

### Improvement (Refinement)

```bash
curl -X POST http://localhost:8000/api/v1/article-requests/req_123/thinking \
  -H "Content-Type: application/json" \
  -H "X-User-ID: editor_001" \
  -d '{
    "thinking_content": "The historical section is too long - condense pre-2020 context to one paragraph",
    "stage": "refinement",
    "thinking_type": "improvement",
    "adoption_priority": 6
  }'
```

---

## 🔥 Most Used Workflows

### Workflow 1: Quick Request

```bash
# Create
REQ_ID=$(curl -s -X POST http://localhost:8000/api/v1/article-requests/request \
  -H "Content-Type: application/json" \
  -H "X-User-ID: analyst_001" \
  -d '{"title":"Economy","topic":"economy","priority":2}' | grep -o '"request_id":"[^"]*' | cut -d'"' -f4)

# Generate
curl -X POST http://localhost:8000/api/v1/article-requests/$REQ_ID/generate \
  -H "X-User-ID: analyst_001"
```

### Workflow 2: Collaborative

```bash
# Create
REQ_ID="req_123"

# Add thinking (multiple contributors)
curl -X POST http://localhost:8000/api/v1/article-requests/$REQ_ID/thinking \
  -H "Content-Type: application/json" \
  -H "X-User-ID: analyst_1" \
  -d '{"thinking_content":"Focus on economy","stage":"pre_generation","thinking_type":"suggestion","adoption_priority":8}'

curl -X POST http://localhost:8000/api/v1/article-requests/$REQ_ID/thinking \
  -H "Content-Type: application/json" \
  -H "X-User-ID: analyst_2" \
  -d '{"thinking_content":"Include politics angle","stage":"pre_generation","thinking_type":"perspective","adoption_priority":7}'

# Check summary
curl http://localhost:8000/api/v1/article-requests/$REQ_ID/orchestration \
  -H "X-User-ID: analyst_1"

# Generate
curl -X POST http://localhost:8000/api/v1/article-requests/$REQ_ID/generate \
  -H "X-User-ID: analyst_1"
```

---

## ❌ Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `User ID required` | Missing X-User-ID | Add `-H "X-User-ID: username"` |
| `Invalid stage` | Wrong stage name | Use: pre_generation, draft_review, refinement, final |
| `Request not found` | Wrong request_id | Copy request_id from create response |
| `Status not found` | Wrong request status | Use valid status from current state |
| `Permission denied` | Wrong user role | Ask admin to upgrade your role |
| `Too many requests` | Rate limit exceeded | Wait before making more requests |

---

## 📊 Configuration Toggles

**Enable/Disable in `zimbabwe.yaml`:**

```yaml
# Disable entire system
article_requests:
  enabled: false

# Disable approval requirement
workflow:
  require_approval: false

# Auto-incorporate high-priority thinking
thinking:
  auto_incorporate_priority: 8

# Disable user tracking
notifications:
  notify_on_adoption: false
```

---

## 🎯 One-Liners

### Check if system is running
```bash
curl -s http://localhost:8000/api/v1/article-requests/pending \
  -H "X-User-ID: test" | head -c 50
```

### Count your requests
```bash
curl -s http://localhost:8000/api/v1/article-requests/my-requests \
  -H "X-User-ID: analyst_001" | grep -o '"count":[0-9]*'
```

### Get latest request
```bash
curl -s http://localhost:8000/api/v1/article-requests/my-requests \
  -H "X-User-ID: analyst_001" | jq '.data[0].id'
```

### Check pending approval
```bash
curl -s http://localhost:8000/api/v1/article-requests/pending \
  -H "X-User-ID: reviewer_001" | jq '.count'
```

---

## 🚨 Rate Limits

| Operation | Limit | Window |
|-----------|-------|--------|
| Create requests | 10 | per hour |
| Add thinking | 30 | per hour |
| Generate articles | 5 | per hour |
| API calls (total) | 60 | per hour |
| Request size | 100 KB | max |

---

## 📚 Documentation Links

- **Quick Start:** `START_HERE_USER_REQUESTS.md`
- **Full API:** `USER_REQUESTS_API_REFERENCE.md`
- **Technical:** `USER_REQUESTS_INTEGRATION_GUIDE.md`
- **Overview:** `USER_REQUESTS_DELIVERY_SUMMARY.md`

---

## 🎓 Learning by Example

### Example 1: Zimbabwe Politics Request

```bash
curl -X POST http://localhost:8000/api/v1/article-requests/request \
  -H "Content-Type: application/json" \
  -H "X-User-ID: analyst_john" \
  -d '{
    "title": "2024 Zimbabwe Political Dynamics",
    "topic": "politics",
    "article_type": "analysis",
    "desired_angle": "Election preparations and opposition movements",
    "key_points": ["ZANU-PF positioning", "Opposition strategies", "Electoral preparations"],
    "background_context": "For stakeholder briefing",
    "priority": 4,
    "target_audience": "policymakers"
  }'
```

### Example 2: Economy Request with Thinking

```bash
# Create
REQ_ID="req_economy_2024"

curl -X POST http://localhost:8000/api/v1/article-requests/request \
  -H "Content-Type: application/json" \
  -H "X-User-ID: analyst_sarah" \
  -d '{
    "title": "Zimbabwe Economic Recovery Analysis",
    "topic": "economy",
    "article_type": "analysis",
    "priority": 3
  }'

# Add thinking
curl -X POST http://localhost:8000/api/v1/article-requests/$REQ_ID/thinking \
  -H "Content-Type: application/json" \
  -H "X-User-ID: analyst_sarah" \
  -d '{
    "thinking_content": "Focus on currency stability measures and foreign reserves",
    "stage": "pre_generation",
    "thinking_type": "suggestion",
    "adoption_priority": 8
  }'
```

---

## ✅ Checklist for Perfect Request

- [ ] **Title:** Clear, descriptive
- [ ] **Topic:** One main topic
- [ ] **Priority:** Realistic (1-5)
- [ ] **Context:** Explained why needed
- [ ] **Angle:** Specific perspective
- [ ] **Key Points:** 3-5 must-includes
- [ ] **Audience:** Clearly defined
- [ ] **Sources:** If known, specify

---

## 🆘 Troubleshooting Commands

```bash
# Test authentication
curl -H "X-User-ID: test" \
  http://localhost:8000/api/v1/article-requests/my-requests

# Check system status
curl http://localhost:8000/api/v1/article-requests/pending \
  -H "X-User-ID: admin_001"

# Get detailed error
curl -v http://localhost:8000/api/v1/article-requests/invalid_id \
  -H "X-User-ID: analyst_001"

# Check logs
tail -f logs/zimbabwe.log | grep "article_request"
```

---

## 🔗 API Base URL

```
http://localhost:8000/api/v1/article-requests
```

All endpoints append to this base URL.

---

## 📱 Mobile-Friendly Format

For quick mobile access, bookmark:
```
http://localhost:8000/api/v1/article-requests/my-requests?format=json
```

---

**💡 Tip:** Save this file as a bookmark or reference!

**Version:** 1.0  
**Last Updated:** January 2024