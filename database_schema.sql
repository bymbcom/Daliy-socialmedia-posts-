-- ============================================================================
-- Social Media Content Visual Pipeline - Database Schema
-- ============================================================================
-- PostgreSQL Schema for Content Generation and Management System
-- Optimized for high-volume content generation with brand compliance
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Users and Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('admin', 'manager', 'user', 'viewer')),
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Organizations/Clients
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    industry VARCHAR(100),
    website_url VARCHAR(500),
    logo_url VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    settings JSONB DEFAULT '{}'::jsonb
);

-- User-Organization relationships
CREATE TABLE user_organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'manager', 'member')),
    is_active BOOLEAN DEFAULT true,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, organization_id)
);

-- ============================================================================
-- BRAND MANAGEMENT
-- ============================================================================

-- Brand Profiles
CREATE TABLE brand_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Brand Colors
    primary_color VARCHAR(7), -- HEX color
    secondary_color VARCHAR(7),
    accent_color VARCHAR(7),
    color_palette JSONB DEFAULT '[]'::jsonb,
    
    -- Typography
    primary_font VARCHAR(100),
    secondary_font VARCHAR(100),
    font_config JSONB DEFAULT '{}'::jsonb,
    
    -- Logo and Assets
    logo_primary_url VARCHAR(500),
    logo_secondary_url VARCHAR(500),
    logo_variants JSONB DEFAULT '[]'::jsonb,
    
    -- Brand Guidelines
    brand_voice_tone TEXT,
    messaging_guidelines TEXT,
    visual_guidelines TEXT,
    usage_restrictions TEXT,
    
    -- Compliance Settings
    enforcement_level VARCHAR(20) DEFAULT 'moderate' CHECK (enforcement_level IN ('strict', 'moderate', 'flexible', 'advisory')),
    minimum_compliance_score DECIMAL(3,2) DEFAULT 0.80,
    
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(organization_id, name)
);

-- Brand Assets Library
CREATE TABLE brand_assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_profile_id UUID NOT NULL REFERENCES brand_profiles(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    asset_type VARCHAR(50) NOT NULL CHECK (asset_type IN ('logo', 'icon', 'image', 'pattern', 'texture', 'graphic')),
    file_path VARCHAR(500) NOT NULL,
    file_url VARCHAR(500),
    file_size_bytes INTEGER,
    mime_type VARCHAR(100),
    dimensions JSONB, -- {"width": 1200, "height": 800}
    
    -- Asset Metadata
    usage_context TEXT[], -- ['social_media', 'website', 'print']
    platform_variants JSONB DEFAULT '{}'::jsonb, -- Platform-specific versions
    color_variants JSONB DEFAULT '{}'::jsonb,
    
    -- Usage Tracking
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,
    
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tags TEXT[] DEFAULT '{}'::text[],
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Content Templates
CREATE TABLE content_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_profile_id UUID NOT NULL REFERENCES brand_profiles(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template_type VARCHAR(50) NOT NULL CHECK (template_type IN ('post', 'story', 'cover', 'ad', 'infographic')),
    
    -- Platform Configuration
    platform VARCHAR(50) NOT NULL CHECK (platform IN ('instagram', 'facebook', 'linkedin', 'twitter', 'tiktok', 'youtube', 'generic')),
    format_specifications JSONB NOT NULL, -- Dimensions, aspect ratios, etc.
    
    -- Template Structure
    layout_config JSONB NOT NULL, -- Layout elements and positioning
    text_zones JSONB DEFAULT '[]'::jsonb, -- Editable text areas
    image_zones JSONB DEFAULT '[]'::jsonb, -- Image placement areas
    brand_elements JSONB DEFAULT '[]'::jsonb, -- Required brand elements
    
    -- Design Elements
    background_config JSONB DEFAULT '{}'::jsonb,
    color_scheme JSONB DEFAULT '{}'::jsonb,
    typography_config JSONB DEFAULT '{}'::jsonb,
    
    -- Usage and Performance
    usage_count INTEGER DEFAULT 0,
    average_engagement_score DECIMAL(5,4),
    performance_metrics JSONB DEFAULT '{}'::jsonb,
    
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tags TEXT[] DEFAULT '{}'::text[],
    
    UNIQUE(brand_profile_id, name, platform)
);

-- ============================================================================
-- CONTENT GENERATION
-- ============================================================================

-- Content Generation Requests
CREATE TABLE content_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    brand_profile_id UUID NOT NULL REFERENCES brand_profiles(id) ON DELETE CASCADE,
    requested_by UUID NOT NULL REFERENCES users(id),
    
    -- Request Details
    title VARCHAR(255) NOT NULL,
    description TEXT,
    content_brief TEXT NOT NULL, -- Business insight/content requirements
    target_platforms TEXT[] NOT NULL, -- ['instagram', 'linkedin']
    content_type VARCHAR(50) NOT NULL CHECK (content_type IN ('post', 'story', 'cover', 'ad', 'infographic', 'carousel')),
    
    -- Generation Parameters
    template_id UUID REFERENCES content_templates(id),
    style_preferences JSONB DEFAULT '{}'::jsonb,
    text_content TEXT,
    keywords TEXT[] DEFAULT '{}'::text[],
    target_audience TEXT,
    call_to_action TEXT,
    
    -- Freepik Integration
    freepik_search_terms TEXT[] DEFAULT '{}'::text[],
    freepik_filters JSONB DEFAULT '{}'::jsonb,
    
    -- Status and Workflow
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'generated', 'review', 'approved', 'rejected', 'published', 'archived')),
    priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
    due_date TIMESTAMP WITH TIME ZONE,
    
    -- Processing Information
    processing_started_at TIMESTAMP WITH TIME ZONE,
    processing_completed_at TIMESTAMP WITH TIME ZONE,
    processing_duration_seconds INTEGER,
    error_message TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Generated Content Assets
CREATE TABLE generated_assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_request_id UUID NOT NULL REFERENCES content_requests(id) ON DELETE CASCADE,
    brand_profile_id UUID NOT NULL REFERENCES brand_profiles(id) ON DELETE CASCADE,
    
    -- Asset Information
    asset_name VARCHAR(255) NOT NULL,
    asset_type VARCHAR(50) NOT NULL CHECK (asset_type IN ('image', 'video', 'graphic', 'animation')),
    platform VARCHAR(50) NOT NULL,
    variant_type VARCHAR(50) DEFAULT 'primary', -- primary, variation_1, variation_2, etc.
    
    -- File Information
    file_path VARCHAR(500) NOT NULL,
    file_url VARCHAR(500),
    file_size_bytes INTEGER,
    mime_type VARCHAR(100),
    dimensions JSONB, -- {"width": 1200, "height": 1200}
    
    -- Generation Details
    freepik_image_id VARCHAR(100), -- Original Freepik image ID
    freepik_image_url VARCHAR(500), -- Original Freepik image URL
    generation_parameters JSONB DEFAULT '{}'::jsonb,
    applied_transformations JSONB DEFAULT '[]'::jsonb,
    
    -- Brand Compliance
    compliance_score DECIMAL(3,2),
    compliance_details JSONB DEFAULT '{}'::jsonb,
    brand_elements_applied JSONB DEFAULT '[]'::jsonb,
    validation_status VARCHAR(50) DEFAULT 'pending' CHECK (validation_status IN ('pending', 'passed', 'failed', 'manual_review')),
    validation_notes TEXT,
    
    -- Performance Tracking
    download_count INTEGER DEFAULT 0,
    usage_count INTEGER DEFAULT 0,
    engagement_metrics JSONB DEFAULT '{}'::jsonb,
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Platform-Specific Asset Variants
CREATE TABLE asset_variants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parent_asset_id UUID NOT NULL REFERENCES generated_assets(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    format_type VARCHAR(50) NOT NULL, -- post, story, cover, etc.
    
    -- Variant Specifications
    dimensions JSONB NOT NULL, -- {"width": 1080, "height": 1080}
    aspect_ratio VARCHAR(20), -- "1:1", "9:16", "16:9"
    file_path VARCHAR(500) NOT NULL,
    file_url VARCHAR(500),
    file_size_bytes INTEGER,
    
    -- Optimization Details
    optimization_applied JSONB DEFAULT '[]'::jsonb,
    compression_level VARCHAR(20),
    quality_score DECIMAL(3,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb,
    
    UNIQUE(parent_asset_id, platform, format_type)
);

-- ============================================================================
-- WORKFLOW AND APPROVALS
-- ============================================================================

-- Content Approval Workflows
CREATE TABLE approval_workflows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Workflow Configuration
    steps JSONB NOT NULL, -- Array of workflow steps with approvers
    auto_approval_rules JSONB DEFAULT '{}'::jsonb,
    escalation_rules JSONB DEFAULT '{}'::jsonb,
    
    -- Conditions
    applies_to_content_types TEXT[] DEFAULT '{}'::text[],
    applies_to_platforms TEXT[] DEFAULT '{}'::text[],
    minimum_compliance_score DECIMAL(3,2),
    
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Content Approvals
CREATE TABLE content_approvals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_request_id UUID NOT NULL REFERENCES content_requests(id) ON DELETE CASCADE,
    workflow_id UUID REFERENCES approval_workflows(id),
    
    -- Approval Details
    approver_id UUID NOT NULL REFERENCES users(id),
    step_number INTEGER NOT NULL,
    step_name VARCHAR(255),
    
    -- Decision
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'delegated')),
    decision_date TIMESTAMP WITH TIME ZONE,
    comments TEXT,
    feedback JSONB DEFAULT '{}'::jsonb,
    
    -- Delegation
    delegated_to UUID REFERENCES users(id),
    delegation_reason TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- API USAGE AND COST TRACKING
-- ============================================================================

-- API Usage Tracking
CREATE TABLE api_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    content_request_id UUID REFERENCES content_requests(id),
    
    -- API Details
    api_provider VARCHAR(50) NOT NULL, -- 'freepik', 'openai', etc.
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    
    -- Request Information
    request_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    request_parameters JSONB DEFAULT '{}'::jsonb,
    response_status INTEGER,
    response_time_ms INTEGER,
    
    -- Cost Information
    cost_per_request DECIMAL(10,4),
    currency VARCHAR(3) DEFAULT 'USD',
    billing_category VARCHAR(50),
    
    -- Resource Usage
    tokens_used INTEGER,
    images_generated INTEGER,
    data_transferred_bytes BIGINT,
    
    -- Rate Limiting
    rate_limit_remaining INTEGER,
    rate_limit_reset_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Daily Usage Summaries (for performance and reporting)
CREATE TABLE daily_usage_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    usage_date DATE NOT NULL,
    api_provider VARCHAR(50) NOT NULL,
    
    -- Summary Metrics
    total_requests INTEGER DEFAULT 0,
    successful_requests INTEGER DEFAULT 0,
    failed_requests INTEGER DEFAULT 0,
    total_cost DECIMAL(10,2) DEFAULT 0.00,
    
    -- Resource Consumption
    total_tokens INTEGER DEFAULT 0,
    total_images_generated INTEGER DEFAULT 0,
    total_data_transferred_bytes BIGINT DEFAULT 0,
    
    -- Performance Metrics
    average_response_time_ms INTEGER,
    p95_response_time_ms INTEGER,
    error_rate DECIMAL(5,4),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(organization_id, usage_date, api_provider)
);

-- ============================================================================
-- ANALYTICS AND PERFORMANCE
-- ============================================================================

-- Content Performance Analytics
CREATE TABLE content_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    generated_asset_id UUID NOT NULL REFERENCES generated_assets(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    
    -- Engagement Metrics
    impressions BIGINT DEFAULT 0,
    views BIGINT DEFAULT 0,
    likes BIGINT DEFAULT 0,
    shares BIGINT DEFAULT 0,
    comments BIGINT DEFAULT 0,
    saves BIGINT DEFAULT 0,
    clicks BIGINT DEFAULT 0,
    
    -- Calculated Metrics
    engagement_rate DECIMAL(5,4),
    click_through_rate DECIMAL(5,4),
    conversion_rate DECIMAL(5,4),
    reach BIGINT DEFAULT 0,
    
    -- Time-based Performance
    performance_date DATE NOT NULL,
    measurement_period VARCHAR(20) DEFAULT 'daily', -- daily, weekly, monthly
    
    -- External Data
    external_post_id VARCHAR(255), -- Platform-specific post ID
    post_url VARCHAR(500),
    published_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb,
    
    UNIQUE(generated_asset_id, platform, performance_date, measurement_period)
);

-- Brand Compliance Analytics
CREATE TABLE brand_compliance_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_profile_id UUID NOT NULL REFERENCES brand_profiles(id) ON DELETE CASCADE,
    analysis_date DATE NOT NULL,
    
    -- Compliance Metrics
    total_assets_generated INTEGER DEFAULT 0,
    assets_passed_compliance INTEGER DEFAULT 0,
    assets_failed_compliance INTEGER DEFAULT 0,
    average_compliance_score DECIMAL(5,4),
    
    -- Brand Element Usage
    logo_usage_count INTEGER DEFAULT 0,
    color_compliance_rate DECIMAL(5,4),
    font_compliance_rate DECIMAL(5,4),
    layout_compliance_rate DECIMAL(5,4),
    
    -- Violation Tracking
    common_violations JSONB DEFAULT '[]'::jsonb,
    violation_categories JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(brand_profile_id, analysis_date)
);

-- User Activity Tracking
CREATE TABLE user_activity_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Activity Details
    action VARCHAR(100) NOT NULL, -- 'create_request', 'approve_content', 'download_asset', etc.
    resource_type VARCHAR(50), -- 'content_request', 'brand_profile', 'template', etc.
    resource_id UUID,
    
    -- Context Information
    session_id VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    referrer VARCHAR(500),
    
    -- Activity Metadata
    activity_details JSONB DEFAULT '{}'::jsonb,
    duration_seconds INTEGER,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- SYSTEM CONFIGURATION
-- ============================================================================

-- System Settings and Configuration
CREATE TABLE system_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category VARCHAR(100) NOT NULL,
    setting_key VARCHAR(255) NOT NULL,
    setting_value JSONB NOT NULL,
    description TEXT,
    data_type VARCHAR(50) NOT NULL CHECK (data_type IN ('string', 'number', 'boolean', 'json', 'array')),
    is_encrypted BOOLEAN DEFAULT false,
    is_readonly BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(category, setting_key)
);

-- Background Jobs and Task Queue
CREATE TABLE background_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_type VARCHAR(100) NOT NULL,
    job_name VARCHAR(255),
    
    -- Job Parameters
    parameters JSONB DEFAULT '{}'::jsonb,
    priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
    
    -- Execution Details
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    processing_duration_seconds INTEGER,
    
    -- Results and Errors
    result JSONB DEFAULT '{}'::jsonb,
    error_message TEXT,
    error_details JSONB DEFAULT '{}'::jsonb,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    
    -- Scheduling
    scheduled_for TIMESTAMP WITH TIME ZONE,
    next_retry_at TIMESTAMP WITH TIME ZONE,
    
    -- Relations
    organization_id UUID REFERENCES organizations(id),
    user_id UUID REFERENCES users(id),
    content_request_id UUID REFERENCES content_requests(id),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- ============================================================================

-- User and Authentication Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = true;
CREATE INDEX idx_users_last_login ON users(last_login_at DESC);

-- Organization Indexes
CREATE INDEX idx_organizations_active ON organizations(is_active) WHERE is_active = true;
CREATE INDEX idx_organizations_created_by ON organizations(created_by);
CREATE INDEX idx_user_orgs_user_id ON user_organizations(user_id);
CREATE INDEX idx_user_orgs_org_id ON user_organizations(organization_id);

-- Brand Profile Indexes
CREATE INDEX idx_brand_profiles_org ON brand_profiles(organization_id);
CREATE INDEX idx_brand_profiles_active ON brand_profiles(is_active) WHERE is_active = true;
CREATE INDEX idx_brand_assets_brand_profile ON brand_assets(brand_profile_id);
CREATE INDEX idx_brand_assets_type ON brand_assets(asset_type);
CREATE INDEX idx_brand_assets_usage ON brand_assets(usage_count DESC);

-- Content Template Indexes
CREATE INDEX idx_templates_brand_profile ON content_templates(brand_profile_id);
CREATE INDEX idx_templates_platform ON content_templates(platform);
CREATE INDEX idx_templates_type ON content_templates(template_type);
CREATE INDEX idx_templates_active ON content_templates(is_active) WHERE is_active = true;

-- Content Request Indexes
CREATE INDEX idx_content_requests_org ON content_requests(organization_id);
CREATE INDEX idx_content_requests_brand ON content_requests(brand_profile_id);
CREATE INDEX idx_content_requests_status ON content_requests(status);
CREATE INDEX idx_content_requests_requested_by ON content_requests(requested_by);
CREATE INDEX idx_content_requests_due_date ON content_requests(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_content_requests_created ON content_requests(created_at DESC);

-- Generated Assets Indexes
CREATE INDEX idx_generated_assets_request ON generated_assets(content_request_id);
CREATE INDEX idx_generated_assets_brand ON generated_assets(brand_profile_id);
CREATE INDEX idx_generated_assets_platform ON generated_assets(platform);
CREATE INDEX idx_generated_assets_compliance ON generated_assets(compliance_score DESC);
CREATE INDEX idx_generated_assets_freepik_id ON generated_assets(freepik_image_id);

-- Asset Variants Indexes
CREATE INDEX idx_asset_variants_parent ON asset_variants(parent_asset_id);
CREATE INDEX idx_asset_variants_platform ON asset_variants(platform);

-- API Usage Indexes
CREATE INDEX idx_api_usage_org ON api_usage(organization_id);
CREATE INDEX idx_api_usage_timestamp ON api_usage(request_timestamp DESC);
CREATE INDEX idx_api_usage_provider ON api_usage(api_provider);
CREATE INDEX idx_api_usage_content_request ON api_usage(content_request_id);

-- Daily Usage Summary Indexes
CREATE INDEX idx_daily_usage_org_date ON daily_usage_summaries(organization_id, usage_date DESC);
CREATE INDEX idx_daily_usage_provider ON daily_usage_summaries(api_provider, usage_date DESC);

-- Analytics Indexes
CREATE INDEX idx_content_analytics_asset ON content_analytics(generated_asset_id);
CREATE INDEX idx_content_analytics_platform ON content_analytics(platform);
CREATE INDEX idx_content_analytics_date ON content_analytics(performance_date DESC);
CREATE INDEX idx_brand_compliance_analytics ON brand_compliance_analytics(brand_profile_id, analysis_date DESC);

-- User Activity Indexes
CREATE INDEX idx_user_activity_user ON user_activity_logs(user_id);
CREATE INDEX idx_user_activity_org ON user_activity_logs(organization_id);
CREATE INDEX idx_user_activity_action ON user_activity_logs(action);
CREATE INDEX idx_user_activity_created ON user_activity_logs(created_at DESC);

-- Background Jobs Indexes
CREATE INDEX idx_background_jobs_status ON background_jobs(status);
CREATE INDEX idx_background_jobs_type ON background_jobs(job_type);
CREATE INDEX idx_background_jobs_scheduled ON background_jobs(scheduled_for) WHERE scheduled_for IS NOT NULL;
CREATE INDEX idx_background_jobs_retry ON background_jobs(next_retry_at) WHERE next_retry_at IS NOT NULL;

-- System Settings Indexes
CREATE UNIQUE INDEX idx_system_settings_key ON system_settings(category, setting_key);

-- ============================================================================
-- FULL-TEXT SEARCH INDEXES
-- ============================================================================

-- Enable full-text search on content descriptions and briefs
CREATE INDEX idx_content_requests_search ON content_requests USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '') || ' ' || content_brief));
CREATE INDEX idx_brand_profiles_search ON brand_profiles USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));
CREATE INDEX idx_templates_search ON content_templates USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));

-- Trigram indexes for fuzzy text search
CREATE INDEX idx_content_requests_title_trgm ON content_requests USING gin(title gin_trgm_ops);
CREATE INDEX idx_brand_assets_name_trgm ON brand_assets USING gin(name gin_trgm_ops);

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC TIMESTAMP UPDATES
-- ============================================================================

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply timestamp triggers to tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_brand_profiles_updated_at BEFORE UPDATE ON brand_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_brand_assets_updated_at BEFORE UPDATE ON brand_assets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_content_templates_updated_at BEFORE UPDATE ON content_templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_content_requests_updated_at BEFORE UPDATE ON content_requests FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_generated_assets_updated_at BEFORE UPDATE ON generated_assets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_daily_usage_summaries_updated_at BEFORE UPDATE ON daily_usage_summaries FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_content_analytics_updated_at BEFORE UPDATE ON content_analytics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_brand_compliance_analytics_updated_at BEFORE UPDATE ON brand_compliance_analytics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_background_jobs_updated_at BEFORE UPDATE ON background_jobs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_system_settings_updated_at BEFORE UPDATE ON system_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- PARTITIONING STRATEGY FOR HIGH-VOLUME TABLES
-- ============================================================================

-- Partition user activity logs by month for better performance
-- Note: This requires manual partition creation and maintenance
-- Consider implementing automated partition management

-- Example: Partition api_usage by month
-- ALTER TABLE api_usage PARTITION BY RANGE (request_timestamp);
-- CREATE TABLE api_usage_2024_01 PARTITION OF api_usage FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Active content requests with brand and user information
CREATE VIEW v_active_content_requests AS
SELECT 
    cr.id,
    cr.title,
    cr.description,
    cr.status,
    cr.priority,
    cr.due_date,
    cr.created_at,
    bp.name AS brand_name,
    o.name AS organization_name,
    u.username AS requested_by_username,
    u.first_name || ' ' || u.last_name AS requested_by_name
FROM content_requests cr
JOIN brand_profiles bp ON cr.brand_profile_id = bp.id
JOIN organizations o ON cr.organization_id = o.id
JOIN users u ON cr.requested_by = u.id
WHERE cr.status NOT IN ('archived', 'cancelled');

-- Brand compliance summary
CREATE VIEW v_brand_compliance_summary AS
SELECT 
    bp.id AS brand_profile_id,
    bp.name AS brand_name,
    COUNT(ga.id) AS total_assets,
    AVG(ga.compliance_score) AS avg_compliance_score,
    COUNT(CASE WHEN ga.compliance_score >= bp.minimum_compliance_score THEN 1 END) AS compliant_assets,
    COUNT(CASE WHEN ga.compliance_score < bp.minimum_compliance_score THEN 1 END) AS non_compliant_assets
FROM brand_profiles bp
LEFT JOIN generated_assets ga ON bp.id = ga.brand_profile_id
WHERE bp.is_active = true
GROUP BY bp.id, bp.name;

-- Daily API usage summary
CREATE VIEW v_daily_api_usage AS
SELECT 
    o.name AS organization_name,
    au.api_provider,
    DATE(au.request_timestamp) AS usage_date,
    COUNT(*) AS total_requests,
    COUNT(CASE WHEN au.response_status >= 200 AND au.response_status < 300 THEN 1 END) AS successful_requests,
    SUM(au.cost_per_request) AS total_cost,
    AVG(au.response_time_ms) AS avg_response_time
FROM api_usage au
JOIN organizations o ON au.organization_id = o.id
GROUP BY o.name, au.api_provider, DATE(au.request_timestamp);

-- ============================================================================
-- INITIAL SYSTEM CONFIGURATION DATA
-- ============================================================================

-- Insert default system settings
INSERT INTO system_settings (category, setting_key, setting_value, description, data_type) VALUES
('freepik', 'api_base_url', '"https://api.freepik.com/v1"', 'Freepik API base URL', 'string'),
('freepik', 'rate_limit_per_second', '45', 'Freepik requests per second', 'number'),
('freepik', 'daily_quota', '10000', 'Daily API request quota', 'number'),
('freepik', 'cost_per_request', '0.01', 'Cost per API request in USD', 'number'),
('brand', 'default_enforcement_level', '"moderate"', 'Default brand enforcement level', 'string'),
('brand', 'minimum_compliance_score', '0.80', 'Default minimum compliance score', 'number'),
('system', 'max_file_size_mb', '50', 'Maximum file size for uploads in MB', 'number'),
('system', 'supported_image_formats', '["jpg", "jpeg", "png", "webp", "svg"]', 'Supported image formats', 'array'),
('analytics', 'retention_days', '90', 'Days to retain analytics data', 'number'),
('cache', 'search_results_ttl', '3600', 'Search results cache TTL in seconds', 'number'),
('cache', 'image_cache_ttl', '86400', 'Image cache TTL in seconds', 'number');

-- ============================================================================
-- COMMENTS AND DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE users IS 'User accounts and authentication information';
COMMENT ON TABLE organizations IS 'Client organizations and companies';
COMMENT ON TABLE brand_profiles IS 'Brand identity and guidelines configuration';
COMMENT ON TABLE brand_assets IS 'Brand asset library (logos, images, graphics)';
COMMENT ON TABLE content_templates IS 'Reusable content templates with brand compliance';
COMMENT ON TABLE content_requests IS 'Content generation requests and workflow tracking';
COMMENT ON TABLE generated_assets IS 'Generated content assets with compliance tracking';
COMMENT ON TABLE asset_variants IS 'Platform-specific variants of generated assets';
COMMENT ON TABLE api_usage IS 'API usage tracking for cost management and analytics';
COMMENT ON TABLE content_analytics IS 'Content performance and engagement analytics';
COMMENT ON TABLE user_activity_logs IS 'Comprehensive user activity audit trail';
COMMENT ON TABLE background_jobs IS 'Asynchronous job processing queue';

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================