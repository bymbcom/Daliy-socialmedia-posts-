# Data Flow Documentation
## Social Media Content Visual Pipeline

### Overview

This document outlines the complete data flow patterns within the Social Media Content Visual Pipeline, detailing how data moves through the system from initial user requests to final analytics collection.

### Core Data Flow Patterns

#### 1. User Onboarding and Organization Setup

```mermaid
flowchart TD
    A[New User Registration] --> B[User Account Creation]
    B --> C[Email Verification]
    C --> D[Organization Creation/Join]
    D --> E[Role Assignment]
    E --> F[Brand Profile Setup]
    F --> G[Brand Asset Upload]
    G --> H[Template Creation]
    
    subgraph "Database Operations"
        B --> B1[INSERT users]
        D --> D1[INSERT organizations]
        D --> D2[INSERT user_organizations]
        F --> F1[INSERT brand_profiles]
        G --> G1[INSERT brand_assets]
        H --> H1[INSERT content_templates]
    end
    
    subgraph "Validation Layer"
        B --> V1[User Data Validation]
        D --> V2[Organization Uniqueness]
        F --> V3[Brand Guidelines Validation]
        G --> V4[Asset Format Validation]
        H --> V5[Template Compliance Check]
    end
```

#### 2. Content Generation Request Flow

```mermaid
flowchart TD
    A[User Content Request] --> B[Request Validation]
    B --> C[Brand Profile Lookup]
    C --> D[Template Selection]
    D --> E[Freepik API Integration]
    E --> F[Asset Generation]
    F --> G[Brand Compliance Check]
    G --> H[Multi-Platform Variants]
    H --> I[Approval Workflow]
    I --> J[Final Asset Storage]
    J --> K[Notification & Analytics]
    
    subgraph "Database Writes"
        A --> A1[INSERT content_requests]
        E --> E1[INSERT api_usage]
        F --> F1[INSERT generated_assets]
        G --> G1[UPDATE compliance_score]
        H --> H1[INSERT asset_variants]
        I --> I1[INSERT content_approvals]
        K --> K1[INSERT user_activity_logs]
    end
    
    subgraph "External APIs"
        E --> EA1[Freepik Search API]
        E --> EA2[Freepik Download API]
        EA1 --> EA3[Image Selection]
        EA2 --> EA4[Asset Retrieval]
    end
    
    subgraph "Background Processing"
        F --> BP1[Image Processing]
        G --> BP2[Brand Validation]
        H --> BP3[Platform Optimization]
        BP1 --> BP4[Queue: background_jobs]
    end
```

#### 3. Brand Compliance Validation Flow

```mermaid
flowchart TD
    A[Generated Asset] --> B[Brand Profile Rules]
    B --> C[Color Analysis]
    C --> D[Logo Placement Check]
    D --> E[Typography Validation]
    E --> F[Layout Compliance]
    F --> G[Scoring Algorithm]
    G --> H{Compliance Score}
    
    H -->|Score >= Threshold| I[Auto-Approve]
    H -->|Score < Threshold| J[Manual Review Required]
    
    I --> K[UPDATE validation_status = 'passed']
    J --> L[UPDATE validation_status = 'manual_review']
    
    subgraph "Scoring Components"
        C --> C1[Color Palette Match: 25%]
        D --> D1[Logo Requirements: 30%]
        E --> E1[Typography Rules: 20%]
        F --> F1[Layout Guidelines: 25%]
    end
    
    subgraph "Analytics Capture"
        G --> GA1[Brand Compliance Analytics]
        GA1 --> GA2[Daily Aggregation]
        GA2 --> GA3[UPDATE brand_compliance_analytics]
    end
```

#### 4. Approval Workflow Data Flow

```mermaid
flowchart TD
    A[Content Request] --> B[Workflow Lookup]
    B --> C[Step Configuration]
    C --> D[Approver Assignment]
    D --> E[Notification Dispatch]
    E --> F[Approver Action]
    F --> G{Decision}
    
    G -->|Approved| H[Next Step Check]
    G -->|Rejected| I[Request Rejection]
    G -->|Delegated| J[Reassignment]
    
    H -->|More Steps| K[Next Approver]
    H -->|Final Step| L[Final Approval]
    
    K --> D
    L --> M[Asset Publishing]
    I --> N[Rejection Notification]
    J --> O[Delegation Process]
    
    subgraph "Database Updates"
        F --> F1[INSERT content_approvals]
        G --> G1[UPDATE approval status]
        L --> L1[UPDATE content_requests.status = 'approved']
        I --> I1[UPDATE content_requests.status = 'rejected']
    end
    
    subgraph "Workflow Rules"
        B --> B1[approval_workflows.steps]
        B1 --> B2[Auto-approval conditions]
        B1 --> B3[Escalation rules]
        B1 --> B4[Minimum compliance scores]
    end
```

#### 5. API Usage and Cost Tracking Flow

```mermaid
flowchart TD
    A[API Request Initiated] --> B[Rate Limit Check]
    B --> C[Cost Calculation]
    C --> D[API Call Execution]
    D --> E[Response Processing]
    E --> F[Usage Logging]
    F --> G[Daily Aggregation]
    G --> H[Cost Analysis]
    
    subgraph "Real-time Tracking"
        F --> F1[INSERT api_usage]
        F1 --> F2[Track: request_timestamp]
        F2 --> F3[Track: response_time_ms]
        F3 --> F4[Track: cost_per_request]
        F4 --> F5[Track: tokens_used]
    end
    
    subgraph "Batch Processing"
        G --> G1[Background Job: Daily Aggregation]
        G1 --> G2[GROUP BY organization_id, api_provider, date]
        G2 --> G3[UPSERT daily_usage_summaries]
        G3 --> G4[Calculate: total_cost, avg_response_time]
    end
    
    subgraph "Rate Limiting"
        B --> B1[Check: Current Request Count]
        B1 --> B2[Check: Time Window]
        B2 --> B3[Update: rate_limit_remaining]
    end
```

#### 6. Analytics Data Collection Flow

```mermaid
flowchart TD
    A[Published Content] --> B[Platform Integration]
    B --> C[Performance Data Fetch]
    C --> D[Data Normalization]
    D --> E[Metrics Calculation]
    E --> F[Analytics Storage]
    F --> G[Reporting Aggregation]
    
    subgraph "Performance Metrics"
        C --> C1[Impressions Data]
        C --> C2[Engagement Data]
        C --> C3[Click Data]
        C --> C4[Conversion Data]
    end
    
    subgraph "Calculated Analytics"
        E --> E1[Engagement Rate = (likes + shares + comments) / impressions]
        E --> E2[Click-through Rate = clicks / impressions]
        E --> E3[Conversion Rate = conversions / clicks]
    end
    
    subgraph "Database Operations"
        F --> F1[INSERT content_analytics]
        F1 --> F2[Platform-specific metrics]
        F2 --> F3[Time-series data points]
        G --> G1[Brand performance summaries]
        G1 --> G2[Template effectiveness metrics]
    end
    
    subgraph "External Integrations"
        B --> B1[Instagram API]
        B --> B2[Facebook API]
        B --> B3[LinkedIn API]
        B --> B4[Twitter API]
    end
```

### Data Processing Patterns

#### Batch Processing Jobs

1. **Daily Usage Aggregation**
   ```sql
   -- Executed nightly via background_jobs
   INSERT INTO daily_usage_summaries (
       organization_id, usage_date, api_provider,
       total_requests, successful_requests, total_cost
   )
   SELECT 
       organization_id,
       DATE(request_timestamp),
       api_provider,
       COUNT(*),
       COUNT(CASE WHEN response_status BETWEEN 200 AND 299 THEN 1 END),
       SUM(cost_per_request)
   FROM api_usage
   WHERE DATE(request_timestamp) = CURRENT_DATE - INTERVAL '1 day'
   GROUP BY organization_id, DATE(request_timestamp), api_provider;
   ```

2. **Brand Compliance Analytics**
   ```sql
   -- Weekly brand compliance summary
   INSERT INTO brand_compliance_analytics (
       brand_profile_id, analysis_date,
       total_assets_generated, average_compliance_score
   )
   SELECT 
       brand_profile_id,
       CURRENT_DATE,
       COUNT(*),
       AVG(compliance_score)
   FROM generated_assets
   WHERE DATE(created_at) >= CURRENT_DATE - INTERVAL '7 days'
   GROUP BY brand_profile_id;
   ```

#### Real-time Processing

1. **Content Request Processing**
   - Immediate validation of request parameters
   - Real-time brand profile lookup and rule application
   - Asynchronous Freepik API integration
   - Live compliance scoring

2. **User Activity Tracking**
   - Session-based activity logging
   - Real-time audit trail generation
   - Immediate security event detection

#### Stream Processing Considerations

```mermaid
flowchart LR
    A[User Actions] --> B[Event Queue]
    B --> C[Stream Processor]
    C --> D[Real-time Analytics]
    C --> E[Batch Storage]
    
    subgraph "Event Types"
        A1[Content Requests]
        A2[Asset Downloads]
        A3[Approval Actions]
        A4[API Calls]
    end
    
    subgraph "Processing Logic"
        C --> C1[Event Validation]
        C1 --> C2[Data Enrichment]
        C2 --> C3[Rule Application]
        C3 --> C4[Output Routing]
    end
```

### Data Consistency Patterns

#### Transaction Management

1. **Content Generation Transaction**
   ```sql
   BEGIN;
   
   -- Create content request
   INSERT INTO content_requests (...) VALUES (...);
   
   -- Log API usage
   INSERT INTO api_usage (...) VALUES (...);
   
   -- Create generated assets
   INSERT INTO generated_assets (...) VALUES (...);
   
   -- Create platform variants
   INSERT INTO asset_variants (...) VALUES (...);
   
   -- Update usage statistics
   UPDATE brand_profiles SET usage_count = usage_count + 1 WHERE ...;
   
   COMMIT;
   ```

2. **Approval Workflow Transaction**
   ```sql
   BEGIN;
   
   -- Record approval decision
   INSERT INTO content_approvals (...) VALUES (...);
   
   -- Update content request status
   UPDATE content_requests SET status = 'approved' WHERE ...;
   
   -- Log user activity
   INSERT INTO user_activity_logs (...) VALUES (...);
   
   COMMIT;
   ```

#### Data Validation Rules

1. **Referential Integrity Checks**
   - All foreign keys validated before insertion
   - Cascade deletion rules prevent orphaned records
   - Cross-table consistency maintained through triggers

2. **Business Logic Validation**
   - Brand compliance scores within valid range (0.00-1.00)
   - API usage costs properly calculated and tracked
   - User permissions verified before data access

### Performance Optimization Strategies

#### Query Optimization

1. **Indexed Query Patterns**
   ```sql
   -- Optimized for organization-scoped queries
   SELECT * FROM content_requests 
   WHERE organization_id = ? AND status = 'pending'
   ORDER BY priority DESC, created_at ASC;
   
   -- Uses: idx_content_requests_org + idx_content_requests_status
   ```

2. **Aggregation Queries**
   ```sql
   -- Pre-computed via materialized views
   SELECT organization_name, total_cost, total_requests
   FROM v_daily_api_usage
   WHERE usage_date >= CURRENT_DATE - INTERVAL '30 days';
   ```

#### Caching Strategy

1. **Application-Level Caching**
   - Brand profiles cached for 1 hour
   - Content templates cached for 30 minutes
   - System settings cached for 24 hours

2. **Database-Level Caching**
   - Query result caching for analytics
   - Prepared statement caching
   - Connection pooling optimization

This comprehensive data flow documentation ensures efficient data processing, maintains consistency, and provides clear patterns for system monitoring and optimization.