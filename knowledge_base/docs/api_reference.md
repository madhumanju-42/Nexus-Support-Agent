# NexusCloud API Reference

## Authentication

All API requests require authentication using an API key. To get your API key:
1. Log in to the NexusCloud dashboard
2. Navigate to Settings > API
3. Click "Generate API Key"
4. Copy and store your key securely — it will only be shown once

Include your API key in the Authorization header:
```
Authorization: Bearer YOUR_API_KEY
```

## Base URL

All API requests are made to: `https://api.nexuscloud.io/v1/`

## Rate Limits

Rate limits vary by plan:
- **Free**: 100 requests per minute
- **Pro**: 1,000 requests per minute
- **Enterprise**: 10,000 requests per minute

When you exceed your rate limit, the API returns a 429 status code with a `Retry-After` header indicating how many seconds to wait.

## Available SDKs

Official SDKs are available for:
- **Python**: `pip install nexuscloud` — supports Python 3.8+
- **JavaScript/Node.js**: `npm install nexuscloud` — supports Node 16+
- **Go**: `go get github.com/nexuscloud/sdk-go`

## Core Endpoints

### Compute
- `GET /instances` — List all instances
- `POST /instances` — Create a new instance
- `GET /instances/{id}` — Get instance details
- `DELETE /instances/{id}` — Terminate an instance
- `POST /instances/{id}/restart` — Restart an instance

### Storage
- `GET /buckets` — List all storage buckets
- `POST /buckets` — Create a new bucket
- `GET /buckets/{name}/objects` — List objects in a bucket
- `PUT /buckets/{name}/objects/{key}` — Upload an object
- `DELETE /buckets/{name}/objects/{key}` — Delete an object

### Billing
- `GET /billing/usage` — Get current usage summary
- `GET /billing/invoices` — List invoices

## Error Codes

- `400` — Bad request (invalid parameters)
- `401` — Unauthorized (invalid or missing API key)
- `403` — Forbidden (insufficient permissions)
- `404` — Resource not found
- `429` — Rate limit exceeded
- `500` — Internal server error (contact support if persistent)

## Webhooks

Enterprise tier customers can configure webhooks to receive real-time notifications about instance state changes, deployment events, and billing alerts. Configure webhooks in Settings > Integrations > Webhooks.
