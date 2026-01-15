---
description: Multi-Tenant SaaS Implementation Plan
---

# Multi-Tenant Chatbot SaaS Platform Implementation Plan

## Overview
Transform the chatbot service into a multi-tenant SaaS platform where companies can:
- Register and manage their accounts
- Upload knowledge base resources (PDFs, websites, Facebook pages)
- Have AI responses tailored to their specific data
- Manage human agents assigned to their company
- Super admin can manage all companies and resources

## Implementation Phases

### Phase 1: Database Schema Updates

**1.1 Create Company Model**
- `id`: Primary key
- `name`: Company name
- `slug`: URL-friendly identifier
- `email`: Company contact email
- `phone`: Company phone
- `website`: Company website
- `logo_url`: Company logo
- `subscription_plan`: Plan type (free, basic, premium, enterprise)
- `is_active`: Active status
- `created_at`: Registration date
- `updated_at`: Last update

**1.2 Create Resource Model** (Knowledge Base)
- `id`: Primary key
- `company_id`: Foreign key to companies
- `resource_type`: ENUM ('pdf', 'website', 'facebook', 'text')
- `source_url`: Original URL (for web/FB resources)
- `file_path`: Local path (for PDFs)
- `file_name`: Original filename
- `extracted_content`: Text content extracted
- `metadata`: JSON field for additional info
- `status`: ENUM ('pending', 'processing', 'completed', 'failed')
- `is_active`: Active status
- `created_at`: Upload date
- `updated_at`: Last update

**1.3 Create SuperAdmin Model**
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email
- `hashed_password`: Password hash
- `full_name`: Full name
- `is_super_admin`: Boolean (always True)
- `is_active`: Active status
- `created_at`: Creation date

**1.4 Update AdminUser Model**
- Add `company_id`: Foreign key to companies
- Add `role`: ENUM ('agent', 'company_admin')
- Update relationships

**1.5 Update ClientInfo Model**
- Add `company_id`: Foreign key to companies

**1.6 Update ChatSession Model**
- Add `company_id`: Foreign key to companies
- Ensure multi-tenant isolation

### Phase 2: Resource Processing System

**2.1 PDF Processing**
- Install dependencies: `PyPDF2`, `pdfplumber`, or `pypdf`
- Create PDF extraction service
- Extract text content from uploaded PDFs
- Store content in database
- Handle OCR for scanned PDFs (optional: `pytesseract`)

**2.2 Website Scraping**
- Install dependencies: `beautifulsoup4`, `requests`, `selenium` (optional)
- Create web scraping service
- Extract text from HTML pages
- Handle JavaScript-rendered content
- Respect robots.txt
- Store extracted content

**2.3 Facebook Page Scraping**
- Create Facebook scraper
- Extract public posts and page info
- Handle API limitations
- Store extracted content

**2.4 Background Task System**
- Install: `celery` + `redis` OR use `FastAPI BackgroundTasks`
- Process resources asynchronously
- Update resource status
- Send notifications on completion

### Phase 3: AI Context Enhancement

**3.1 Create Knowledge Base Service**
- Retrieve company-specific resources
- Format resources for AI context
- Implement RAG (Retrieval-Augmented Generation) approach
- Use vector embeddings for better retrieval (optional: `chromadb`, `faiss`)

**3.2 Update AI Service**
- Inject company knowledge base into prompts
- Add company context to conversations
- Implement context window management
- Add fallback mechanisms

### Phase 4: API Endpoints

**4.1 Company Management**
- `POST /api/companies/register` - Company registration
- `GET /api/companies/me` - Get company profile
- `PUT /api/companies/me` - Update company profile
- `DELETE /api/companies/me` - Deactivate company

**4.2 Resource Management**
- `POST /api/resources/upload-pdf` - Upload PDF
- `POST /api/resources/add-website` - Add website URL
- `POST /api/resources/add-facebook` - Add Facebook page
- `GET /api/resources` - List all resources
- `GET /api/resources/{id}` - Get resource details
- `PUT /api/resources/{id}` - Update resource
- `DELETE /api/resources/{id}` - Delete resource
- `POST /api/resources/{id}/reprocess` - Reprocess resource

**4.3 Admin/Agent Management**
- Update `POST /api/auth/register` - Add company assignment
- `GET /api/agents` - List company agents
- `PUT /api/agents/{id}` - Update agent info
- `DELETE /api/agents/{id}` - Remove agent

**4.4 Super Admin Endpoints**
- `POST /api/superadmin/auth/login` - Super admin login
- `GET /api/superadmin/companies` - List all companies
- `GET /api/superadmin/companies/{id}` - Company details
- `PUT /api/superadmin/companies/{id}` - Update company
- `DELETE /api/superadmin/companies/{id}` - Delete company
- `GET /api/superadmin/resources` - All resources across companies
- `GET /api/superadmin/agents` - All agents
- `GET /api/superadmin/analytics` - Platform analytics

### Phase 5: Frontend Updates

**5.1 Company Registration Page**
- Create company registration form
- Handle logo upload
- Select subscription plan

**5.2 Company Dashboard**
- View company profile
- Manage resources
- View agents
- Analytics and statistics

**5.3 Resource Management UI**
- Upload PDF files
- Add website URLs
- Add Facebook pages
- View resource list with status
- Delete/reprocess resources

**5.4 Agent Management UI**
- List agents
- Assign agents to company
- Update agent details

**5.5 Super Admin Dashboard**
- Overview of all companies
- Manage companies
- View all resources
- Platform-wide analytics
- System settings

**5.6 Widget Updates**
- Add company identifier to widget
- Load company-specific branding
- Route to correct company context

### Phase 6: Authentication & Authorization

**6.1 Multi-tenant Auth**
- Update JWT tokens with company_id
- Add role-based access control (RBAC)
- Implement permissions system

**6.2 Middleware**
- Create company isolation middleware
- Ensure users only access their company data
- Super admin bypass for all companies

### Phase 7: Testing & Deployment

**7.1 Testing**
- Unit tests for new models
- Integration tests for resource processing
- E2E tests for multi-tenant isolation
- Load testing

**7.2 Migration**
- Create database migration scripts
- Migrate existing data
- Backup strategy

**7.3 Documentation**
- API documentation updates
- Company onboarding guide
- Admin user guide
- Super admin guide

## Dependencies to Install

```txt
# PDF Processing
PyPDF2==3.0.1
pdfplumber==0.10.3

# Web Scraping
beautifulsoup4==4.12.2
requests==2.31.0
lxml==4.9.3

# Optional: For advanced features
selenium==4.15.2  # JavaScript rendering
pytesseract==0.3.10  # OCR for scanned PDFs
chromadb==0.4.18  # Vector database for RAG
sentence-transformers==2.2.2  # Embeddings

# Background tasks (choose one)
# celery==5.3.4
# redis==5.0.1

# File uploads
python-multipart==0.0.6
aiofiles==23.2.1
```

## Implementation Order

1. **Database Models** (Phase 1)
2. **Basic Company Registration** (Phase 4.1, Phase 5.1)
3. **Resource Upload Endpoints** (Phase 4.2)
4. **Resource Processing** (Phase 2)
5. **AI Context Enhancement** (Phase 3)
6. **Super Admin System** (Phase 4.4, Phase 5.5)
7. **Frontend Dashboards** (Phase 5)
8. **Testing & Refinement** (Phase 7)

## Security Considerations

- Multi-tenant data isolation
- Row-level security
- Company-specific API keys
- Rate limiting per company
- File upload validation
- XSS/CSRF protection
- Data encryption at rest
