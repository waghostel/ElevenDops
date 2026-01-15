# Troubleshooting

## Common Issues

### Connection Refused

**Error**: `httpx.ConnectError: Connection refused`

**Solution**:

1. Ensure backend is running: `.\start-servers-gcp-firestore.ps1`
2. Check port 8000 is not blocked
3. Verify `BASE_URL` in test configuration

### ReadTimeout

**Error**: `httpx.ReadTimeout`

**Solution**:

1. Increase timeout in test configuration
2. Check backend performance
3. Run fewer parallel tests

### Port Already in Use

**Error**: `Address already in use`

**Solution**:

```powershell
.\stop_server.ps1 -Force
.\start-servers-gcp-firestore.ps1
```

### Pydantic Validation Error

**Error**: `pydantic.ValidationError`

**Solution**:

1. Check schema matches between tests and backend
2. Verify response fields are present
3. Update test assertions if API changed

## Debugging Tips

1. **Verbose output**: `pytest -v`
2. **Single test**: `pytest tests/postman/test_health_endpoints.py::TestHealthEndpoint::test_health_status_200 -v`
3. **Print statements**: Use `pytest -s` to see print output
4. **Stop on first failure**: `pytest -x`

## FAQ

**Q: Why are tests slow?**
A: Property tests run 100 iterations by default. Reduce with `@settings(max_examples=10)`.

**Q: How to skip specific tests?**
A: Use `pytest -k "not slow_test_name"` or decorate with `@pytest.mark.skip`.
