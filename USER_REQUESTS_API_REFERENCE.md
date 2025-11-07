# 🔌 User-Driven Article System - Complete API Reference

## Overview

This document provides comprehensive technical documentation for the User-Driven Article Request and Thinking system API endpoints.

**Base URL:** `http://localhost:8000/api/v1/article-requests`

**Authentication:** All endpoints require `X-User-ID` header

---

## 📋 Table of Contents

1. [Article Request Endpoints](#article-request-endpoints)
2. [User Thinking Endpoints](#user-thinking-endpoints)
3. [Data Models](#data-models)
4. [Response Formats](#response-formats)
5. [Error Handling](#error-handling)
6. [Examples](#examples)

---

## 🔹 Article Request Endpoints

### 1. Create Article Request

**Endpoint:** `POST /request`

**Description:** Create a new article request with complete specifications

**Headers:**
```
Content-Type: application/json
X-User-ID: string (required)
```

**Request Body:**
```json
{
  "title": "string (required)",
  "topic": "string (required)",
  "article_type": "string (optional, default: analysis)",
  "desired_angle": "string (optional)",
  "key_points": ["string"] (optional),
  "required_sources": ["string"] (optional),
  "exclude_sources": ["string"] (optional),
  "background_context": "string (optional)",
  "estimated_length": "string (optional, default: medium)",
  "target_audience": "string (optional, default: general_public)",
  "priority": "integer (optional, default: 1, range: 1-5)",
  "deadline": "ISO8601 datetime (optional)"
}
```

**Valid Values:**

| Field | Valid Values |
|-------|--------------|
| `article_type` | `historical`, `present`, `future`, `analysis`, `opinion` |
| `estimated_length` | `short`, `medium`, `long` |
| `target_audience` | `policymakers`, `general_public`, `investors`, `academics`, `media` |
| `priority` | `1` (low) to `5` (critical) |

**Response:**
```json
{
  "status": "success",
  "message": "Article request 'Title' created successfully",
  "request_id": "req_abc123",
  "topic": "string",
  "priority": 3,
  "deadline": "ISO8601 datetime or null"
}
```

**Status Codes:**
- `200 OK` - Request created successfully
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Missing X-User-ID header
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/article-requests/request \
  -H "Content-Type: application/json" \
  -H "X-User-ID: analyst_001" \
  -d '{
    "title": "Zimbabwe Economic Recovery Strategy",
    "topic": "Zimbabwe economy",
    "article_type": "analysis",
    "desired_angle": "Focus on fiscal policy and forex reserves",
    "key_points": [
      "Currency stability",
      "Inflation control",
      "GDP growth targets"
    ],
    "priority": 3,
    "target_audience": "investors",
    "estimated_length": "long"
  }'
```

---

### 2. Get Article Request

**Endpoint:** `GET /request/{request_id}`

**Description:** Retrieve details of a specific article request

**Parameters:**
- `request_id` (string, required) - The request ID

**Headers:**
```
X-User-ID: string (required)
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "string",
    "title": "string",
    "topic": "string",
    "article_type": "string",
    "desired_angle": "string",
    "key_points": ["string"],
    "required_sources": ["string"],
    "exclude_sources": ["string"],
    "background_context": "string",
    "deadline": "ISO8601 datetime",
    "estimated_length": "string",
    "target_audience": "string",
    "status": "string",
    "priority": "integer",
    "requested_by_id": "string",
    "generated_article_id": "string or null",
    "created_date": "ISO8601 datetime",
    "assigned_date": "ISO8601 datetime or null",
    "completed_date": "ISO8601 datetime or null",
    "rejection_reason": "string or null"
  }
}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/article-requests/request/req_abc123 \
  -H "X-User-ID: analyst_001"
```

---

### 3. Get User's Requests

**Endpoint:** `GET /my-requests`

**Description:** Get all article requests submitted by the current user

**Query Parameters:**
- `status` (string, optional) - Filter by status: `pending`, `assigned`, `in_progress`, `completed`, `rejected`

**Headers:**
```
X-User-ID: string (required)
```

**Response:**
```json
{
  "status": "success",
  "count": 5,
  "data": [
    {
      "id": "string",
      "title": "string",
      "topic": "string",
      "status": "string",
      "priority": "integer",
      "created_date": "ISO8601 datetime",
      ...
    }
  ]
}
```

**Example:**
```bash
# Get all requests
curl http://localhost:8000/api/v1/article-requests/my-requests \
  -H "X-User-ID: analyst_001"

# Get only completed requests
curl "http://localhost:8000/api/v1/article-requests/my-requests?status=completed" \
  -H "X-User-ID: analyst_001"
```

---

### 4. Get Pending Requests

**Endpoint:** `GET /pending`

**Description:** Get all pending article requests (admin/reviewer only)

**Headers:**
```
X-User-ID: string (required)
```

**Response:**
```json
{
  "status": "success",
  "count": 12,
  "data": [
    {
      "id": "string",
      "title": "string",
      "topic": "string",
      "priority": "integer",
      "status": "pending|assigned",
      "created_date": "ISO8601 datetime",
      ...
    }
  ]
}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/article-requests/pending \
  -H "X-User-ID: reviewer_001"
```

---

### 5. Get Orchestration Summary

**Endpoint:** `GET /{request_id}/orchestration`

**Description:** Get comprehensive summary of request with all user thinking contributions

**Parameters:**
- `request_id` (string, required) - The request ID

**Headers:**
```
X-User-ID: string (required)
```

**Response:**
```json
{
  "status": "success",
  "request": {
    "id": "string",
    "title": "string",
    "topic": "string",
    "status": "string",
    "priority": "integer",
    "created_date": "ISO8601 datetime",
    ...
  },
  "thinking_contributions": [
    {
      "id": "string",
      "stage": "pre_generation|draft_review|refinement|final",
      "thinking_type": "string",
      "thinking_content": "string",
      "was_used": "boolean",
      "adoption_priority": "integer",
      "created_date": "ISO8601 datetime"
    }
  ],
  "thinking_count": 5,
  "thinking_by_type": {
    "suggestion": 2,
    "perspective": 1,
    "fact_check": 1,
    "improvement": 1
  },
  "thinking_by_stage": {
    "pre_generation": 3,
    "draft_review": 2
  },
  "avg_priority": 7.4
}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/article-requests/req_abc123/orchestration \
  -H "X-User-ID: analyst_001"
```

---

### 6. Generate Article from Request

**Endpoint:** `POST /{request_id}/generate`

**Description:** Trigger article generation from the request, incorporating user thinking

**Parameters:**
- `request_id` (string, required) - The request ID
- `include_user_thinking` (boolean, optional, default: true) - Whether to include user thinking

**Headers:**
```
X-User-ID: string (required)
```

**Response:**
```json
{
  "status": "success",
  "message": "Article generated successfully",
  "article_id": "string",
  "request_id": "string",
  "user_thinking_incorporated": 3
}
```

**Status Codes:**
- `200 OK` - Generation started successfully
- `400 Bad Request` - Invalid request or generation failed
- `404 Not Found` - Request not found
- `500 Internal Server Error` - Server error

**Example:**
```bash
# Generate with user thinking included (default)
curl -X POST http://localhost:8000/api/v1/article-requests/req_abc123/generate \
  -H "X-User-ID: analyst_001"

# Generate without user thinking
curl -X POST "http://localhost:8000/api/v1/article-requests/req_abc123/generate?include_user_thinking=false" \
  -H "X-User-ID: analyst_001"
```

---

### 7. Update Request Status

**Endpoint:** `POST /{request_id}/status/{new_status}`

**Description:** Update the status of an article request (admin/reviewer only)

**Parameters:**
- `request_id` (string, required) - The request ID
- `new_status` (string, required) - New status: `pending`, `assigned`, `in_progress`, `completed`, `rejected`
- `rejection_reason` (string, optional, query parameter) - Reason if rejecting

**Headers:**
```
X-User-ID: string (required)
```

**Response:**
```json
{
  "status": "success",
  "message": "Request status updated to completed"
}
```

**Example:**
```bash
# Mark as in progress
curl -X POST http://localhost:8000/api/v1/article-requests/req_abc123/status/in_progress \
  -H "X-User-ID: reviewer_001"

# Reject with reason
curl -X POST "http://localhost:8000/api/v1/article-requests/req_abc123/status/rejected?rejection_reason=Topic%20already%20covered" \
  -H "X-User-ID: reviewer_001"
```

---

## 🔹 User Thinking Endpoints

### 1. Add User Thinking

**Endpoint:** `POST /{request_id}/thinking`

**Description:** Add user thinking/contribution to an article request

**Parameters:**
- `request_id` (string, required) - The request ID

**Headers:**
```
Content-Type: application/json
X-User-ID: string (required)
```

**Request Body:**
```json
{
  "thinking_content": "string (required)",
  "stage": "string (required)",
  "thinking_type": "string (required)",
  "adoption_priority": "integer (optional, default: 5, range: 0-10)"
}
```

**Valid Values:**

| Field | Valid Values |
|-------|--------------|
| `stage` | `pre_generation`, `draft_review`, `refinement`, `final` |
| `thinking_type` | `suggestion`, `perspective`, `fact_check`, `improvement`, `analysis` |
| `adoption_priority` | `0-10` (0=low, 10=high) |

**Response:**
```json
{
  "status": "success",
  "message": "Your thinking has been recorded",
  "thinking_id": "think_xyz789",
  "stage": "pre_generation",
  "thinking_type": "suggestion"
}
```

**Status Codes:**
- `200 OK` - Thinking added successfully
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Missing X-User-ID header
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/article-requests/req_abc123/thinking \
  -H "Content-Type: application/json" \
  -H "X-User-ID: analyst_001" \
  -d '{
    "thinking_content": "Include recent RBZ monetary policy statements from January 2024",
    "stage": "pre_generation",
    "thinking_type": "suggestion",
    "adoption_priority": 8
  }'
```

---

### 2. Get Thinking for Request

**Endpoint:** `GET /{request_id}/thinking`

**Description:** Get all thinking contributions for an article request

**Parameters:**
- `request_id` (string, required) - The request ID

**Headers:**
```
X-User-ID: string (required)
```

**Response:**
```json
{
  "status": "success",
  "count": 3,
  "data": [
    {
      "id": "think_001",
      "article_request_id": "req_abc123",
      "contributed_by_id": "analyst_001",
      "stage": "pre_generation",
      "thinking_content": "string",
      "thinking_type": "suggestion",
      "was_used": true,
      "impact_notes": "string",
      "helpfulness_score": 0.8,
      "adoption_priority": 8,
      "created_date": "ISO8601 datetime",
      "updated_date": "ISO8601 datetime"
    }
  ]
}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/article-requests/req_abc123/thinking \
  -H "X-User-ID: analyst_001"
```

---

### 3. Get User's Thinking

**Endpoint:** `GET /user/{user_id}/thinking`

**Description:** Get all thinking contributions from a specific user

**Parameters:**
- `user_id` (string, required) - The user ID

**Headers:**
```
X-User-ID: string (required)
```

**Response:**
```json
{
  "status": "success",
  "count": 15,
  "data": [
    {
      "id": "think_001",
      "article_request_id": "req_abc123",
      "stage": "pre_generation",
      "thinking_type": "suggestion",
      "was_used": true,
      "created_date": "ISO8601 datetime"
    }
  ]
}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/article-requests/user/analyst_001/thinking \
  -H "X-User-ID: analyst_001"
```

---

## 📊 Data Models

### ArticleRequest Model

```python
{
  "id": "string (UUID)",
  "title": "string",
  "topic": "string",
  "article_type": "string",
  "desired_angle": "string or null",
  "key_points": ["string"],
  "required_sources": ["string"],
  "exclude_sources": ["string"],
  "background_context": "string or null",
  "deadline": "ISO8601 datetime or null",
  "estimated_length": "string",
  "target_audience": "string",
  "status": "pending|assigned|in_progress|completed|rejected",
  "priority": "integer (1-5)",
  "requested_by_id": "string",
  "generated_article_id": "string or null",
  "created_date": "ISO8601 datetime",
  "assigned_date": "ISO8601 datetime or null",
  "completed_date": "ISO8601 datetime or null",
  "rejection_reason": "string or null"
}
```

### UserThinking Model

```python
{
  "id": "string (UUID)",
  "article_request_id": "string or null",
  "generated_article_id": "string or null",
  "contributed_by_id": "string",
  "stage": "pre_generation|draft_review|refinement|final",
  "thinking_content": "string",
  "thinking_type": "suggestion|perspective|fact_check|improvement|analysis",
  "was_used": "boolean",
  "impact_notes": "string or null",
  "helpfulness_score": "float (0.0-1.0) or null",
  "adoption_priority": "integer (0-10)",
  "created_date": "ISO8601 datetime",
  "updated_date": "ISO8601 datetime"
}
```

### User Model

```python
{
  "id": "string (UUID)",
  "username": "string",
  "email": "string",
  "full_name": "string or null",
  "role": "analyst|reviewer|admin",
  "permissions": ["string"],
  "expertise_areas": ["string"],
  "bio": "string or null",
  "articles_requested": "integer",
  "thinking_contributions": "integer",
  "created_date": "ISO8601 datetime",
  "last_login": "ISO8601 datetime or null"
}
```

---

## 📨 Response Formats

### Success Response

```json
{
  "status": "success",
  "message": "Operation completed successfully",
  "data": {}
}
```

### Error Response

```json
{
  "status": "error",
  "message": "Description of what went wrong",
  "error_code": "ERROR_TYPE",
  "details": {}
}
```

### List Response

```json
{
  "status": "success",
  "count": 10,
  "page": 1,
  "page_size": 20,
  "total_pages": 2,
  "data": []
}
```

---

## ⚠️ Error Handling

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `401` | Unauthorized | Missing or invalid X-User-ID header |
| `400` | Bad Request | Invalid input parameters |
| `403` | Forbidden | User doesn't have permission |
| `404` | Not Found | Resource not found |
| `409` | Conflict | Request status invalid for operation |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Server error |

### Error Response Examples

**Missing User ID:**
```json
{
  "status": "error",
  "message": "User ID required in X-User-ID header",
  "error_code": "MISSING_AUTH"
}
```

**Invalid Status:**
```json
{
  "status": "error",
  "message": "Invalid status. Must be one of: pending, assigned, in_progress, completed, rejected",
  "error_code": "INVALID_STATUS"
}
```

**Request Not Found:**
```json
{
  "status": "error",
  "message": "Article request not found",
  "error_code": "NOT_FOUND"
}
```

**Permission Denied:**
```json
{
  "status": "error",
  "message": "Your role does not have permission to submit requests",
  "error_code": "FORBIDDEN"
}
```

---

## 📝 Examples

### Complete Workflow Example

```bash
#!/bin/bash

USER_ID="analyst_001"
BASE_URL="http://localhost:8000/api/v1/article-requests"

# Step 1: Create article request
echo "Step 1: Creating article request..."
REQUEST=$(curl -s -X POST $BASE_URL/request \
  -H "Content-Type: application/json" \
  -H "X-User-ID: $USER_ID" \
  -d '{
    "title": "Zimbabwe Economic Analysis",
    "topic": "economy",
    "article_type": "analysis",
    "priority": 3,
    "target_audience": "investors"
  }')

REQUEST_ID=$(echo $REQUEST | grep -o '"request_id":"[^"]*' | cut -d'"' -f4)
echo "Created request: $REQUEST_ID"

# Step 2: Add pre-generation thinking
echo "Step 2: Adding pre-generation thinking..."
curl -s -X POST $BASE_URL/$REQUEST_ID/thinking \
  -H "Content-Type: application/json" \
  -H "X-User-ID: $USER_ID" \
  -d '{
    "thinking_content": "Focus on currency stability measures",
    "stage": "pre_generation",
    "thinking_type": "suggestion",
    "adoption_priority": 8
  }'

# Step 3: Get orchestration summary
echo "Step 3: Getting orchestration summary..."
curl -s $BASE_URL/$REQUEST_ID/orchestration \
  -H "X-User-ID: $USER_ID" | jq .

# Step 4: Generate article
echo "Step 4: Generating article..."
curl -s -X POST $BASE_URL/$REQUEST_ID/generate \
  -H "X-User-ID: $USER_ID" | jq .

# Step 5: Get updated request
echo "Step 5: Getting updated request..."
curl -s $BASE_URL/request/$REQUEST_ID \
  -H "X-User-ID: $USER_ID" | jq .

echo "Workflow complete!"
```

### Python Client Example

```python
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1/article-requests"
USER_ID = "analyst_001"

def create_request(title, topic, **kwargs):
    """Create an article request"""
    payload = {
        "title": title,
        "topic": topic,
        **kwargs
    }
    
    response = requests.post(
        f"{BASE_URL}/request",
        json=payload,
        headers={"X-User-ID": USER_ID}
    )
    
    return response.json()

def add_thinking(request_id, content, stage, thinking_type, priority=5):
    """Add thinking to a request"""
    payload = {
        "thinking_content": content,
        "stage": stage,
        "thinking_type": thinking_type,
        "adoption_priority": priority
    }
    
    response = requests.post(
        f"{BASE_URL}/{request_id}/thinking",
        json=payload,
        headers={"X-User-ID": USER_ID}
    )
    
    return response.json()

def generate_article(request_id):
    """Trigger article generation"""
    response = requests.post(
        f"{BASE_URL}/{request_id}/generate",
        headers={"X-User-ID": USER_ID}
    )
    
    return response.json()

# Usage
result = create_request(
    title="Zimbabwe Political Analysis",
    topic="politics",
    article_type="analysis",
    priority=3,
    target_audience="policymakers"
)

request_id = result["request_id"]

add_thinking(
    request_id,
    content="Include recent opposition statements",
    stage="pre_generation",
    thinking_type="suggestion",
    priority=8
)

generation_result = generate_article(request_id)
print(f"Generated article: {generation_result['article_id']}")
```

---

## 🔒 Rate Limiting

**Global Limits:**
- 60 requests per hour per user
- Max 100 KB request payload
- 30 requests per minute burst limit

**Endpoint-Specific Limits:**
- `/request` - 10 per hour
- `/thinking` - 30 per hour
- `/generate` - 5 per hour

**Rate Limit Headers:**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1705372800
```

---

## 🔐 Security

1. **Authentication:** All endpoints require valid X-User-ID
2. **Authorization:** Roles determine available operations
3. **Data Privacy:** User contributions tracked internally only
4. **Input Validation:** All inputs validated and sanitized
5. **SQL Injection Protection:** ORM prevents SQL injection

---

## 📞 Support

For issues or questions, contact: `support@thinkank.local`

---

**Last Updated:** January 2024  
**API Version:** 1.0