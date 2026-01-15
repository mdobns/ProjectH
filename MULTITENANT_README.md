# Multi-Tenant SaaS Chatbot Platform - Implementation Summary

## 🎉 What's New!

Your chatbot system has been upgraded to a **multi-tenant SaaS platform** where multiple companies can:

1. ✅ **Register their own accounts**
2. ✅ **Upload knowledge base resources** (PDFs, Websites, Facebook pages)
3. ✅ **Get AI responses tailored to their company data**
4. ✅ **Manage human agents assigned to their company**
5. ✅ **Super admin can manage all companies**

---

## 📋 Database Changes

### New Tables

1. **companies** - Stores company profiles
   - Company name, slug, email, subscription plan
   - Logo, description, active status

2. **resources** - Knowledge base resources
   - Resource type (PDF, WEBSITE, FACEBOOK, TEXT)
   - Source URL or file path
   - Extracted content
   - Processing status (PENDING, PROCESSING, COMPLETED, FAILED)

3. **super_admins** - Platform administrators
   - Super admin credentials
   - Platform-wide access

### Updated Tables

1. **admin_users** 
   - Added `company_id` (links agent to their company)
   - Added `role` (AGENT or COMPANY_ADMIN)

2. **client_info**
   - Added `company_id` (links client to company)

3. **chat_sessions**
   - Added `company_id` (multi-tenant isolation)

---

## 🚀 New API Endpoints

### Company Management (`/api/companies/`)

- `POST /api/companies/register` - Register new company
- `GET /api/companies/{company_id}` - Get company details
- `GET /api/companies/slug/{slug}` - Get company by slug
- `PUT /api/companies/{company_id}` - Update company
- `GET /api/companies/{company_id}/stats` - Get company statistics
- `DELETE /api/companies/{company_id}` - Deactivate company

### Resource Management (`/api/resources/`)

- `POST /api/resources/upload-pdf` - Upload PDF file
- `POST /api/resources/add-website` - Add website URL
- `POST /api/resources/add-facebook` - Add Facebook page URL
- `POST /api/resources/add-text` - Add custom text content
- `GET /api/resources?company_id={id}` - List resources (paginated)
- `GET /api/resources/{resource_id}` - Get resource details
- `GET /api/resources/{resource_id}/content` - Preview resource content
- `PUT /api/resources/{resource_id}` - Update resource (activate/deactivate)
- `POST /api/resources/{resource_id}/reprocess` - Reprocess failed resource
- `DELETE /api/resources/{resource_id}` - Delete resource

### Updated Endpoints

- `POST /api/auth/register` - Now requires `company_id` and `role`

---

## 🔧 Installation

### 1. Install New Dependencies

```bash
pip install -r requirements.txt
```

New packages added:
- `PyPDF2` - PDF text extraction
- `pdfplumber` - Advanced PDF processing
- `beautifulsoup4` - Web scraping
- `requests` - HTTP requests
- `lxml` - HTML parsing
- `aiofiles` - Async file handling

### 2. Initialize Database

The database will automatically create new tables on first run. If you have existing data:

```bash
# Backup your current database first!
cp chatbot.db chatbot.db.backup

# Run the application - it will create new tables
python main.py
```

**Note:** Existing data may need manual migration. You'll need to:
- Manually create at least one company record
- Update existing `admin_users` with a `company_id`
- Update existing `client_info` with a `company_id`
- Update existing `chat_sessions` with a `company_id`

---

## 📖 How It Works

### Company Registration Flow

1. Company registers via `POST /api/companies/register`
   ```json
   {
     "name": "Acme Corp",
     "slug": "acme-corp",
     "email": "contact@acme.com",
     "phone": "+1234567890",
     "website": "https://acme.com",
     "description": "Best products ever",
     "password": "secure_password"
   }
   ```

2. Company gets assigned an ID and default FREE subscription plan

3. Agents can be registered for this company:
   ```json
   {
     "company_id": 1,
     "username": "agent1",
     "email": "agent1@acme.com",
     "password": "password123",
     "full_name": "John the Agent",
     "role": "AGENT"
   }
   ```

### Knowledge Base Management

#### Upload PDF
```bash
POST /api/resources/upload-pdf?company_id=1
Content-Type: multipart/form-data

file: [PDF file]
```

#### Add Website
```bash
POST /api/resources/add-website?company_id=1
Content-Type: application/json

{
  "resource_type": "WEBSITE",
  "source_url": "https://acme.com/faq"
}
```

#### Add Facebook Page
```bash
POST /api/resources/add-facebook?company_id=1
Content-Type: application/json

{
  "resource_type": "FACEBOOK",
  "source_url": "https://facebook.com/acme-corp"
}
```

### AI Context Enhancement

When a client starts a chat, the AI receives:
1. **System prompt** (general behavior)
2. **Company knowledge base** (up to 15,000 characters from all active resources)
3. **Chat history** (conversation context)

The AI prioritizes answers from the knowledge base, providing accurate company-specific information!

---

## 🔐 Multi-Tenant Security

- **Row-level isolation**: All queries filter by `company_id`
- **JWT tokens include company_id**: Ensures users can only access their company data
- **Company verification**: All resource and agent operations verify company exists
- **File isolation**: Uploaded files stored in company-specific directories

---

## 🎨 Resource Processing

Resources are processed in the background:

1. **PDF Processing**
   - Extracts text using both PyPDF2 and pdfplumber
   - Handles tables and complex layouts
   - Stores extracted content in database

2. **Website Scraping**
   - Fetches HTML content
   - Removes navigation, scripts, styles
   - Extracts main content area
   - Cleans and formats text

3. **Facebook Scraping**
   - Limited to public information
   - Recommends using Facebook Graph API for full access
   - Extracts page title and description

4. **Processing Status**
   - PENDING → PROCESSING → COMPLETED ✅
   - or FAILED ❌ (can be reprocessed)

---

## 📊 Company Statistics

GET `/api/companies/{id}/stats` returns:

```json
{
  "total_resources": 10,
  "total_agents": 5,
  "total_sessions": 150,
  "active_sessions": 3,
  "total_messages": 1200
}
```

---

## 🛠️ Next Steps

### 1. Create Frontend Dashboards

- **Company Registration Page** - Let companies sign up
- **Company Dashboard** - Manage profile, view stats
- **Resource Management UI** - Upload and manage knowledge base
- **Agent Management** - Add/remove agents
- **Super Admin Dashboard** - Manage all companies

### 2. Super Admin System

Create routes for super admin:
- View all companies
- Activate/deactivate companies
- View platform-wide analytics
- Manage subscriptions

### 3. Testing with Sample Data

```python
# Create a test company
company_data = {
    "name": "Test Company",
    "slug": "test-company",
    "email": "test@example.com",
    "password": "password123"
}

# Upload a PDF
# Add a website
# Register an agent
# Start a chat and see AI use the knowledge base!
```

### 4. Migration Script (if needed)

If you have existing data, create a migration script to:
- Create a default company
- Assign all existing admins to this company
- Assign all existing clients to this company
- Assign all existing sessions to this company

---

## 🐛 Troubleshooting

### Database Errors
- Make sure to backup before running migrations
- If you see FK constraint errors, manually set company_id values

### Resource Processing Fails
- Check logs for specific errors
- PDF issues: File might be scanned (needs OCR)
- Website issues: Site might block scraping
- Facebook issues: Need API access for full content

### File Upload Errors
- Check `uploads/` directory exists and is writable
- Verify file size limits in your server config
- Ensure proper permissions

---

## 🎯 Key Features Summary

✅ Multi-tenant architecture with company isolation
✅ PDF, Website, and Facebook content extraction  
✅ AI responses enhanced with company knowledge base  
✅ Role-based access control (AGENT, COMPANY_ADMIN, SUPER_ADMIN)  
✅ Background resource processing  
✅ Resource management (activate, reprocess, delete)  
✅ Company statistics and analytics  
✅ RESTful API with comprehensive endpoints  

---

## 📚 API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 🚀 Ready to Go!

Your multi-tenant chatbot SaaS platform is ready. Start by:

1. Running the server: `python main.py`
2. Creating a test company via API
3. Uploading some knowledge base resources
4. Registering an agent
5. Testing the chatbot with company-specific questions!

**Happy coding! 🎉**
