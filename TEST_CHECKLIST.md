# RAG AI Chat - Test Checklist

## Backend Unit Tests (pytest)

Run tests:
```bash
cd back
pip install pytest pytest-cov
python -m pytest tests/ -v
```

### Data Service Tests
- [ ] `test_data_service.py` - All 50+ tests pass
  - [ ] get_all_products returns sorted list
  - [ ] get_product_summary returns valid data
  - [ ] get_category_stats handles case-insensitive input
  - [ ] get_region_stats for all regions
  - [ ] compare_products works with 2+ products
  - [ ] compare_regions identifies best region
  - [ ] get_top_performers by demand/growth/stability
  - [ ] get_dataset_overview returns all fields

### Intent Classifier Tests
- [ ] `test_intent_classifier.py` - All 60+ tests pass
  - [ ] Extracts product IDs (P0001 format)
  - [ ] Extracts days from various formats
  - [ ] Classifies FORECAST intent
  - [ ] Classifies COMPARISON with multiple products
  - [ ] Classifies TRENDS intent
  - [ ] Classifies RECOMMENDATIONS intent
  - [ ] Supports Russian language
  - [ ] Returns suggestions

### Chat Memory Tests
- [ ] `test_chat_memory.py` - All 30+ tests pass
  - [ ] User isolation works
  - [ ] Max messages limit enforced
  - [ ] Context window formatting
  - [ ] Clear history works
  - [ ] LLM message formatting
  - [ ] Thread safety

### AI Chat Service Tests
- [ ] `test_ai_chat_service.py` - All 25+ tests pass
  - [ ] handle_ai_chat returns all fields
  - [ ] build_rag_context for all intents
  - [ ] Chart data returned for forecast
  - [ ] User history isolation
  - [ ] Error handling for LLM failures

### API Integration Tests
- [ ] `test_api_chat.py` - All 35+ tests pass
  - [ ] POST /chat requires auth
  - [ ] POST /chat with forecast intent
  - [ ] POST /chat with comparison
  - [ ] GET /chat/history returns messages
  - [ ] DELETE /chat/history clears messages
  - [ ] GET /analytics/summary
  - [ ] GET /analytics/trends

---

## Manual API Testing

### Prerequisites
```bash
cd back
python backend.py
```

### 1. Authentication
```bash
# Register user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Login and get token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Save token: TOKEN=<your_token>
```

### 2. Chat Tests
```bash
# Test forecast
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Forecast for P0001 for 7 days"}'

# Test comparison
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Compare P0001 and P0002"}'

# Test trends
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the trends?"}'

# Test recommendations
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "What do you recommend?"}'

# Test top products
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me top 5 products"}'

# Test Russian
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Прогноз для P0001 на 14 дней"}'
```

### 3. History Tests
```bash
# Get history
curl http://localhost:8000/chat/history \
  -H "Authorization: Bearer $TOKEN"

# Get limited history
curl "http://localhost:8000/chat/history?limit=5" \
  -H "Authorization: Bearer $TOKEN"

# Clear history
curl -X DELETE http://localhost:8000/chat/history \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Analytics Tests
```bash
# Get summary
curl http://localhost:8000/analytics/summary \
  -H "Authorization: Bearer $TOKEN"

# Get trends
curl http://localhost:8000/analytics/trends \
  -H "Authorization: Bearer $TOKEN"
```

---

## Flutter Tests

Run tests:
```bash
cd prodbot_ai
flutter test
```

### Unit Tests
- [ ] `chat_models_test.dart`
  - [ ] ChatResponse parsing
  - [ ] ChatData parsing
  - [ ] HistoryPoint parsing
  - [ ] ForecastPoint parsing
  - [ ] ChatMessage parsing

### Service Tests
- [ ] `chat_service_test.dart`
  - [ ] sendMessage returns ChatResponse
  - [ ] getHistory returns List<ChatMessage>
  - [ ] clearHistory works
  - [ ] getAnalyticsSummary works
  - [ ] getAnalyticsTrends works

### Manual Flutter Testing
1. [ ] Open app and navigate to Chat screen
2. [ ] Verify initial welcome message
3. [ ] Send "Forecast for P0001 for 7 days"
4. [ ] Verify chart appears with history and forecast
5. [ ] Verify suggestions appear
6. [ ] Tap a suggestion
7. [ ] Send "Compare P0001 and P0002"
8. [ ] Verify comparison response
9. [ ] Test clear history button
10. [ ] Verify history cleared
11. [ ] Close and reopen app
12. [ ] Verify history loads from server

---

## React Admin Tests

Run tests:
```bash
cd frontend-admin
npm test
```

### API Tests
- [ ] `chatApi.test.js`
  - [ ] sendChatMessage sends POST request
  - [ ] sendChatMessage includes auth header
  - [ ] getChatHistory fetches messages
  - [ ] getChatHistory respects limit
  - [ ] clearChatHistory sends DELETE
  - [ ] getAnalyticsSummary works
  - [ ] getAnalyticsTrends works

### Manual React Testing
1. [ ] Navigate to /chat page
2. [ ] Verify chat interface loads
3. [ ] Send "Forecast for P0001"
4. [ ] Verify response appears
5. [ ] Verify chart appears (if data)
6. [ ] Verify suggestions appear
7. [ ] Click a suggestion
8. [ ] Test Clear History button
9. [ ] Refresh page
10. [ ] Verify history loads

---

## Integration Test Scenarios

### Scenario 1: Full Conversation Flow
1. [ ] User asks "What products do you have?"
2. [ ] AI responds with dataset overview
3. [ ] User asks "Forecast for P0001 for 14 days"
4. [ ] AI responds with forecast + chart data
5. [ ] User asks "Compare it with P0002"
6. [ ] AI compares the two products
7. [ ] User asks "What do you recommend?"
8. [ ] AI gives recommendations

### Scenario 2: Multi-User Isolation
1. [ ] User A sends messages
2. [ ] User B sends different messages
3. [ ] User A's history only shows their messages
4. [ ] User B's history only shows their messages
5. [ ] Clearing User A's history doesn't affect User B

### Scenario 3: Error Handling
1. [ ] Send request without auth - should get 401
2. [ ] Send invalid product ID - should handle gracefully
3. [ ] Simulate LLM failure - should show error message
4. [ ] Send very long message - should handle

### Scenario 4: Persistence
1. [ ] Send several messages
2. [ ] Restart backend
3. [ ] Messages should be in memory (cleared on restart)
4. [ ] For persistent storage, DB integration needed

---

## Performance Tests

### Response Time
- [ ] Chat response < 5 seconds (with LLM)
- [ ] History load < 500ms
- [ ] Analytics endpoints < 1 second

### Concurrent Users
- [ ] Test with 10 concurrent users
- [ ] Verify no memory leaks
- [ ] Verify user isolation maintained

---

## Expected Response Examples

### Forecast Response
```json
{
  "reply": "Based on the data, P0001 (Electronics) shows:\n- Average demand: 151 units/day\n- Trend: +2% growth\n- Forecast suggests stable demand over the next 7 days.\n\nRecommendation: Current inventory levels appear adequate.",
  "intent": "forecast",
  "entities": {"product_ids": ["P0001"], "days": 7},
  "suggestions": ["Seasonality P0001", "Weather impact on P0001", "Compare with P0002"],
  "data": {
    "product_id": "P0001",
    "history": [...],
    "forecast": [...]
  }
}
```

### Comparison Response
```json
{
  "reply": "Comparison of P0001 vs P0002:\n\nP0001 (Electronics):\n- Avg Demand: 151 units/day\n- Trend: +2%\n\nP0002 (Clothing):\n- Avg Demand: 143 units/day\n- Trend: -1%\n\nP0001 outperforms P0002 by 5.6% in average demand.",
  "intent": "comparison",
  "entities": {"product_ids": ["P0001", "P0002"]},
  "suggestions": ["Forecast P0001", "Forecast P0002", "Top 5 products"]
}
```

---

## Sign-off

- [ ] All automated tests pass
- [ ] Manual API tests pass
- [ ] Flutter app works correctly
- [ ] React admin works correctly
- [ ] Integration scenarios pass
- [ ] Performance acceptable

Date: _______________
Tester: _______________
