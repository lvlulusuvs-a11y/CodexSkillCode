# API Evolution: Change Without Breaking Clients

APIs are contracts. Breaking a contract erodes trust.

## Additive Changes (Safe)

These never break clients:
1. Adding new optional fields to requests
2. Adding new fields to responses
3. Adding new endpoints
4. Adding new HTTP methods to existing endpoints
5. Making previously required fields optional

## Breaking Changes (Need Version)

These require a new version:
1. Removing a field from requests or responses
2. Changing a fields type
3. Making optional fields required
4. Renaming a field
5. Changing the URL structure
6. Changing error format
7. Changing authentication method

## Best Practices for API Evolution

1. Always add, never remove (within a version)
2. Document all fields with deprecation dates
3. Return old fields alongside new ones during migration
4. Test that old clients work with new versions
5. Version your API from day one (even v1)

## Backward Compatibility Testing

Run tests that verify old clients still work:

async def test_v1_backward_compatibility():
    # Use old client format
    response = await client.get("/v1/users/123")
    assert response.status_code == 200
    assert "name" in response.json()  # old field still present

async def test_v2_has_new_fields():
    response = await client.get("/v2/users/123")
    assert response.status_code == 200
    assert "name" in response.json()
    assert "email" in response.json()  # new field in v2

## Deprecation Strategy

1. Add Deprecation header to old endpoints
2. Document migration guide
3. Contact known clients
4. Keep old version running for 6 months minimum
5. Monitor old version usage
6. Sunset when usage drops below 1%


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.
