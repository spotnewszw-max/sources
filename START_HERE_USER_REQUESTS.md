# 📝 User-Driven Article System - Quick Start Guide

## Overview

The Think Tank now supports **user-driven article generation** where analysts can:

1. **Request specific articles** to be written on topics they care about
2. **Contribute their thinking** at multiple stages during article construction
3. **Influence article direction** with specific angles and key points
4. **Track adoption** of their contributions

---

## 🎯 Quick Start (5 minutes)

### 1. **Request an Article**

```bash
# Submit an article request
curl -X POST http://localhost:8000/api/v1/article-requests/request \
  -H "Content-Type: application/json" \
  -H "X-User-ID: analyst_001" \
  -d '{
    "title": "Zimbabwe Economic Recovery Analysis",
    "topic": "Zimbabwe economy",
    "article_type": "analysis",
    "desired_angle": "Focus on fiscal policy and foreign reserves",
    "key_points": [
      "Currency stability measures",
      "Inflation control strategies",
      "GDP growth targets"
    ],
    "background_context": "Needed for investor briefing next week",
    "priority": 3,
    "estimated_length": "long",
    "target_audience": "investors"
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "Article request 'Zimbabwe Economic Recovery Analysis' created successfully",
  "request_id": "req_123456",
  "topic": "Zimbabwe economy",
  "priority": 3
}
```

### 2. **View Your Requests**

```bash
curl http://localhost:8000/api/v1/article-requests/my-requests \
  -H "X-User-ID: analyst_001"
```

### 3. **Contribute Your Thinking**

```bash
# Add thinking before article is generated
curl -X POST http://localhost:8000/api/v1/article-requests/req_123456/thinking \
  -H "Content-Type: application/json" \
  -H "X-User-ID: analyst_001" \
  -d '{
    "thinking_content": "Be sure to include recent RBZ monetary policy statements from Jan 2024",
    "stage": "pre_generation",
    "thinking_type": "suggestion",
    "adoption_priority": 9
  }'
```

### 4. **Generate Article from Request**

```bash
# Trigger generation incorporating all user thinking
curl -X POST http://localhost:8000/api/v1/article-requests/req_123456/generate \
  -H "X-User-ID: analyst_001"
```

**Response:**
```json
{
  "status": "success",
  "message": "Article generated successfully",
  "article_id": "article_xyz789",
  "request_id": "req_123456",
  "user_thinking_incorporated": 3
}
```

---

## 📚 Features in Depth

### **A. Article Requests**

Submit requests with complete specifications:

```json
{
  "title": "Article title",
  "topic": "Main topic",
  "article_type": "analysis",           // historical, present, future, analysis
  "desired_angle": "Specific perspective to take",
  "key_points": ["Point 1", "Point 2"],  // Must include these
  "required_sources": ["url1", "url2"],  // Sources to use
  "exclude_sources": ["url3"],           // Sources to avoid
  "background_context": "Why this article",
  "estimated_length": "medium",          // short, medium, long
  "target_audience": "investors",        // policymakers, general_public, etc.
  "priority": 3,                         // 1-5 scale
  "deadline": "2024-02-15T10:00:00"
}
```

**Request Status Flow:**
```
pending → assigned → in_progress → completed
                  ↓
            rejected (with reason)
```

### **B. User Thinking Contributions**

Contribute at **4 stages**:

| Stage | When | Purpose |
|-------|------|---------|
| **pre_generation** | Before article written | Initial ideas & suggestions |
| **draft_review** | After draft created | Feedback on draft |
| **refinement** | During improvement | Refinement suggestions |
| **final** | Before publication | Final recommendations |

**Thinking Types:**
- `suggestion` - Content suggestions
- `perspective` - Different viewpoint
- `fact_check` - Verify facts
- `improvement` - Improve wording/flow
- `analysis` - Additional analysis

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/article-requests/req_123456/thinking \
  -H "Content-Type: application/json" \
  -H "X-User-ID: analyst_001" \
  -d '{
    "thinking_content": "The article should emphasize the 2023 currency revaluation and its impact on small businesses",
    "stage": "pre_generation",
    "thinking_type": "suggestion",
    "adoption_priority": 8
  }'
```

### **C. Orchestration Overview**

Get complete summary of request + thinking:

```bash
curl http://localhost:8000/api/v1/article-requests/req_123456/orchestration \
  -H "X-User-ID: analyst_001"
```

**Response shows:**
- Request details
- All thinking contributions
- Thinking organized by stage & type
- Average priority score
- Adoption status

---

## 🔌 Complete API Reference

### Article Request Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| **POST** | `/article-requests/request` | Create new request |
| **GET** | `/article-requests/request/{id}` | Get request details |
| **GET** | `/article-requests/my-requests` | Get your requests |
| **GET** | `/article-requests/pending` | Get pending requests (admin) |
| **GET** | `/article-requests/{id}/orchestration` | Get full summary |
| **POST** | `/article-requests/{id}/generate` | Generate from request |
| **POST** | `/article-requests/{id}/status/{status}` | Update status (admin) |

### User Thinking Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| **POST** | `/article-requests/{id}/thinking` | Add thinking contribution |
| **GET** | `/article-requests/{id}/thinking` | Get thinking for request |
| **GET** | `/user/{user_id}/thinking` | Get your thinking |

---

## 📊 Usage Examples

### **Example 1: Political Trend Analysis Request**

```bash
curl -X POST http://localhost:8000/api/v1/article-requests/request \
  -H "Content-Type: application/json" \
  -H "X-User-ID: analyst_john" \
  -d '{
    "title": "2024 Zimbabwe Political Dynamics Analysis",
    "topic": "Zimbabwe politics",
    "article_type": "analysis",
    "desired_angle": "Focus on election preparations and opposition movements",
    "key_points": [
      "ZANU-PF positioning",
      "Opposition strategies",
      "International observation plans",
      "Electoral commission preparations"
    ],
    "background_context": "Stakeholder presentation on political outlook",
    "priority": 4,
    "target_audience": "policymakers",
    "estimated_length": "long"
  }'
```

Then add thinking:

```bash
# Suggestion from another analyst
curl -X POST http://localhost:8000/api/v1/article-requests/req_abc123/thinking \
  -H "Content-Type: application/json" \
  -H "X-User-ID: analyst_jane" \
  -d '{
    "thinking_content": "Include the recent statements from the election observer organizations",
    "stage": "pre_generation",
    "thinking_type": "suggestion",
    "adoption_priority": 7
  }'

# Perspective from economic analyst
curl -X POST http://localhost:8000/api/v1/article-requests/req_abc123/thinking \
  -H "Content-Type: application/json" \
  -H "X-User-ID: economist_bob" \
  -d '{
    "thinking_content": "Political stability concerns are directly impacting foreign investment - worth highlighting the economic dimension",
    "stage": "pre_generation",
    "thinking_type": "perspective",
    "adoption_priority": 8
  }'
```

### **Example 2: Technology Sector Deep Dive**

```bash
# Create request for tech sector analysis
curl -X POST http://localhost:8000/api/v1/article-requests/request \
  -H "Content-Type: application/json" \
  -H "X-User-ID: tech_analyst" \
  -d '{
    "title": "Zimbabwe Tech Sector Growth Report",
    "topic": "technology",
    "article_type": "present",
    "desired_angle": "Current state and growth opportunities",
    "key_points": [
      "Fintech innovations",
      "Mobile money penetration",
      "Tech startups landscape",
      "Skills gap challenges"
    ],
    "required_sources": ["techzim.co.zw"],
    "background_context": "Quarterly tech sector review",
    "priority": 2
  }'
```

### **Example 3: Multi-Stage Article Refinement**

**Stage 1 - Pre-Generation Thinking:**
```bash
curl -X POST http://localhost:8000/api/v1/article-requests/req_xyz/thinking \
  -H "Content-Type: application/json" \
  -H "X-User-ID: analyst_1" \
  -d '{
    "thinking_content": "Should emphasize agricultural productivity statistics",
    "stage": "pre_generation",
    "thinking_type": "suggestion",
    "adoption_priority": 8
  }'
```

**Stage 2 - Draft Review (after article is generated):**
```bash
curl -X POST http://localhost:8000/api/v1/article-requests/req_xyz/thinking \
  -H "Content-Type: application/json" \
  -H "X-User-ID: reviewer_1" \
  -d '{
    "thinking_content": "The historical section is too lengthy - suggest condensing pre-2020 context",
    "stage": "draft_review",
    "thinking_type": "improvement",
    "adoption_priority": 6
  }'
```

**Stage 3 - Final Review:**
```bash
curl -X POST http://localhost:8000/api/v1/article-requests/req_xyz/thinking \
  -H "Content-Type: application/json" \
  -H "X-User-ID: editor_1" \
  -d '{
    "thinking_content": "Ready for publication - excellent analysis",
    "stage": "final",
    "thinking_type": "analysis",
    "adoption_priority": 5
  }'
```

---

## 🔐 Authentication & Permissions

### **Required Header**
```
X-User-ID: your_user_id
```

### **User Roles**
- **analyst** - Can request articles, contribute thinking
- **reviewer** - Can approve requests, contribute thinking
- **admin** - Full access

### **Permissions**
```yaml
can_submit_request:
  - analyst
  - reviewer
  - admin

can_contribute_thinking:
  - analyst
  - reviewer
  - admin

can_approve:
  - reviewer
  - admin
```

---

## 📈 Tracking & Analytics

### **View Request Summary**

```bash
curl http://localhost:8000/api/v1/article-requests/req_123/orchestration \
  -H "X-User-ID: analyst_001"
```

Returns:
```json
{
  "status": "success",
  "request": {
    "id": "req_123",
    "title": "Zimbabwe Economic Analysis",
    "topic": "economy",
    "status": "in_progress",
    "priority": 3,
    "created_date": "2024-01-15T10:00:00"
  },
  "thinking_contributions": [
    {
      "id": "think_001",
      "thinking_type": "suggestion",
      "stage": "pre_generation",
      "adoption_priority": 8,
      "was_used": true
    },
    {
      "id": "think_002",
      "thinking_type": "perspective",
      "stage": "pre_generation",
      "adoption_priority": 7,
      "was_used": true
    }
  ],
  "thinking_count": 2,
  "thinking_by_type": {
    "suggestion": 1,
    "perspective": 1
  },
  "thinking_by_stage": {
    "pre_generation": 2
  },
  "avg_priority": 7.5
}
```

---

## 📝 Configuration

### **Enable/Disable Feature**

In `configs/zimbabwe.yaml`:

```yaml
article_requests:
  enabled: true                    # Set to false to disable

  workflow:
    require_approval: true         # Require approval before generation
    default_priority: 2            # Default priority level
    request_expiration_days: 90    # Request expires after 90 days

  thinking:
    track_adoption: true           # Track which thinking was used
    auto_incorporate_priority: 8   # Auto-use thinking with priority >= 8

  generation:
    include_user_thinking: true    # Include thinking in generation
```

---

## 🚀 Best Practices

### **For Requesters**

1. **Be Specific**
   - ✅ DO: "Include recent monetary policy changes and foreign reserve impacts"
   - ❌ DON'T: "Write about economy"

2. **Provide Context**
   - Always include `background_context` explaining why the article is needed
   - Specify `target_audience` to guide tone and depth

3. **Set Realistic Deadlines**
   - Complex analyses need time for research
   - Factor in review cycles

4. **Use Priorities Wisely**
   - Priority 5 = Urgent, needed ASAP
   - Priority 1 = Can wait, no urgency

### **For Thinkers (Contributors)**

1. **Contribute Early**
   - Best impact at `pre_generation` stage
   - Later stages are refinements, not direction-setting

2. **Be Specific**
   - ✅ DO: Cite sources: "According to RBZ 2024 report..."
   - ❌ DON'T: Vague suggestions like "make it better"

3. **Set Priority Appropriately**
   - 8-10 = Must include
   - 5-7 = Should consider
   - 1-4 = Nice to have

4. **Track Your Impact**
   - System records which contributions are adopted
   - Use this to improve over time

---

## ⚠️ Limitations & Considerations

1. **User Thinking as Suggestions**
   - System incorporates thinking as **guidance**, not requirements
   - Final article generation still uses all available data sources
   - Conflicting thinking is noted but doesn't prevent generation

2. **Privacy & Transparency**
   - User tracking is internal only (not exposed in public API)
   - Contributions not attributed publicly
   - Maintains author anonymity if desired

3. **Rate Limiting**
   - Max 60 requests per hour per user
   - Max thinking contributions: 10 per user per request, 50 total per request

4. **Performance**
   - Multiple thinking contributions increase generation time
   - System optimizes by parallel processing

---

## 🔧 Troubleshooting

### **"User ID not found"**
```
Error: User not found
```
**Fix:** Ensure user is registered. Pass valid `X-User-ID` header.

### **"Invalid stage"**
```
Error: Invalid stage. Must be one of: pre_generation, draft_review, refinement, final
```
**Fix:** Use valid stage names exactly as listed.

### **"Request already completed"**
```
Error: Cannot add thinking to completed request
```
**Fix:** Thinking can only be added to pending/assigned requests.

### **"Permission denied"**
```
Error: Your role does not have permission to submit requests
```
**Fix:** Contact admin to upgrade your role to analyst/reviewer/admin.

---

## 📞 Support & Questions

### Common Questions

**Q: Can I edit a request after submitting?**
A: Not currently - create a new request if needed.

**Q: How long does article generation take?**
A: Typically 5-15 minutes depending on complexity and user thinking.

**Q: Can I see which of my thinking was used?**
A: Yes - check the orchestration endpoint or wait for email notification.

**Q: What happens if my requested article conflicts with existing content?**
A: System flags it for review. You'll be notified if it's rejected.

---

## 📊 Next Steps

1. **Try submitting your first request** - Use example #1 above
2. **Add thinking to a request** - Collaborate with team members
3. **Generate an article** - Trigger generation to see your influence
4. **Check analytics** - View adoption rate of your contributions
5. **Refine and improve** - Learn from experience to make better requests

---

**Ready to drive article creation?** Start by submitting your first request! 🚀