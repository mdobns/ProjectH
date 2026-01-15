# Quick Start Guide - Multi-Tenant System

## Step 1: Start the Server

```bash
python main.py
```

The server will automatically create all new database tables on startup.

## Step 2: Register a Company

```bash
curl -X POST "http://localhost:8000/api/companies/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corporation",
    "slug": "acme",
    "email": "contact@acme-corp.com", 
    "phone": "+1234567890",
    "website": "https://acme-corp.com",
    "description": "Leading provider of innovative solutions",
    "password": "SecurePass123!"
  }'
```

Response will include the company details with an `id`. Note this ID (e.g., `company_id: 1`).

## Step 3: Register an Agent for the Company

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": 1,
    "username": "agent_john",
    "email": "john@acme-corp.com",
    "password": "AgentPass123!",
    "full_name": "John Smith",
    "role": "AGENT"
  }'
```

Response includes `access_token` and `refresh_token`.

## Step 4: Upload Knowledge Base Resources

### Upload a PDF

```bash
curl -X POST "http://localhost:8000/api/resources/upload-pdf?company_id=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/your/document.pdf"
```

### Add a Website

```bash
curl -X POST "http://localhost:8000/api/resources/add-website?company_id=1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "resource_type": "WEBSITE",
    "source_url": "https://acme-corp.com/faq"
  }'
```

### Add Custom Text

```bash
curl -X POST "http://localhost:8000/api/resources/add-text?company_id=1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "resource_type": "TEXT",
    "text_content": "We offer 24/7 customer support. Our return policy is 30 days..."
  }'
```

## Step 5: Check Resource Status

```bash
curl "http://localhost:8000/api/resources?company_id=1&page=1&page_size=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Wait for resources to process (status: PENDING → PROCESSING → COMPLETED).

## Step 6: View Company Stats

```bash
curl "http://localhost:8000/api/companies/1/stats" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Step 7: Test the Chatbot

Now when clients chat with your bot, the AI will use the company's knowledge base to answer questions!

The chat widget automatically uses the company context based on which site it's embedded on (using the `company_id` or `slug`).

---

## Testing Locally

### Using Swagger UI

1. Visit `http://localhost:8000/docs`
2. Try out the endpoints interactively
3. Use the "Authorize" button to add your token

### Using the Admin Dashboard

Visit `http://localhost:8000/admin` to access the admin interface (if frontend is built).

---

## Next: Build the Frontend

Create frontends for:
1. Company registration page
2. Company dashboard with resource management
3. Agent login and chat interface
4. Super admin panel

See `MULTITENANT_README.md` for full details!
