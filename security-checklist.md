# Security Checklist and Configuration
## Social Media Content Visual Pipeline - Security Implementation

## 🔒 Security Checklist Overview

This comprehensive security checklist ensures BYMB Consultancy's Social Media Content Visual Pipeline meets enterprise security standards while protecting sensitive brand data and user information.

## ✅ Pre-Deployment Security Checklist

### Infrastructure Security
- [ ] **Network Segmentation**: Isolated networks for frontend, backend, and database
- [ ] **Firewall Rules**: Restrictive ingress/egress rules configured
- [ ] **Load Balancer Security**: SSL termination and security headers configured
- [ ] **Container Security**: Non-root users, minimal base images, security scanning
- [ ] **Secrets Management**: No hardcoded secrets, secure secret storage
- [ ] **SSL/TLS Configuration**: TLS 1.2+ only, strong cipher suites
- [ ] **Domain Security**: HTTPS enforcement, HSTS headers, secure cookies

### Application Security
- [ ] **Input Validation**: All user inputs validated and sanitized
- [ ] **SQL Injection Prevention**: Parameterized queries, ORM usage
- [ ] **XSS Protection**: Content Security Policy, input encoding
- [ ] **CSRF Protection**: CSRF tokens implemented
- [ ] **Authentication**: Strong password policy, MFA available
- [ ] **Authorization**: Role-based access control implemented
- [ ] **Session Management**: Secure session handling, proper timeout
- [ ] **API Security**: Rate limiting, API key management, request validation

### Data Security
- [ ] **Data Encryption**: Encryption at rest and in transit
- [ ] **Database Security**: Connection encryption, access controls
- [ ] **File Upload Security**: File type validation, malware scanning
- [ ] **Backup Security**: Encrypted backups, secure storage
- [ ] **PII Protection**: Data classification, privacy controls
- [ ] **Data Retention**: Automated data purging policies

### Monitoring & Logging
- [ ] **Security Logging**: Comprehensive audit trails
- [ ] **Intrusion Detection**: Anomaly detection configured
- [ ] **Vulnerability Scanning**: Regular security assessments
- [ ] **Security Monitoring**: Real-time threat detection
- [ ] **Incident Response**: Security incident procedures defined
- [ ] **Log Protection**: Tamper-proof log storage

### Compliance & Governance
- [ ] **Privacy Policy**: GDPR/CCPA compliance documented
- [ ] **Terms of Service**: Legal protections in place
- [ ] **Data Processing Agreements**: Third-party security reviewed
- [ ] **Security Policies**: Company security policies documented
- [ ] **Access Reviews**: Regular access audits scheduled
- [ ] **Security Training**: Team security awareness training

## 🔐 Security Configuration Files

### 1. Nginx Security Configuration

#### Main Nginx Configuration (`config/nginx/nginx.conf`)
```nginx
# Security-hardened Nginx configuration
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    # Basic Settings
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Security Headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
    
    # Hide Nginx version
    server_tokens off;
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;
    limit_conn_zone $binary_remote_addr zone=conn_limit_per_ip:10m;
    
    # Request size limits
    client_max_body_size 50M;
    client_body_buffer_size 1K;
    client_header_buffer_size 1k;
    large_client_header_buffers 2 1k;
    
    # Timeouts
    client_body_timeout 10;
    client_header_timeout 10;
    keepalive_timeout 5 5;
    send_timeout 10;
    
    # Gzip Settings
    gzip on;
    gzip_vary on;
    gzip_min_length 10240;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml application/json application/javascript application/xml+rss application/atom+xml image/svg+xml;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # Include virtual hosts
    include /etc/nginx/sites-available/*.conf;
}
```

#### Site Configuration (`config/nginx/sites-available/smcp.conf`)
```nginx
# SMCP Production Site Configuration
upstream backend {
    server backend:8000 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

upstream frontend {
    server frontend:3000 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

# Main HTTPS server
server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_dhparam /etc/nginx/ssl/dhparam.pem;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self'; frame-ancestors 'none';" always;
    
    # API Routes with rate limiting
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        limit_conn conn_limit_per_ip 10;
        
        # Proxy settings
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Authentication endpoints with stricter rate limiting
    location /api/auth/ {
        limit_req zone=login burst=5 nodelay;
        limit_conn conn_limit_per_ip 3;
        
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Frontend application
    location / {
        limit_req zone=api burst=50 nodelay;
        
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    # Static assets with caching
    location /generated/ {
        alias /var/www/generated/;
        expires 1d;
        add_header Cache-Control "public, no-transform";
        
        # Security for file access
        location ~* \.(php|pl|py|jsp|asp|sh|cgi)$ {
            deny all;
        }
    }
    
    location /uploads/ {
        alias /var/www/uploads/;
        expires 7d;
        add_header Cache-Control "public, no-transform";
        
        # Restrict file types
        location ~* \.(jpg|jpeg|png|gif|webp|svg)$ {
            expires 30d;
        }
        
        location ~* \.(php|pl|py|jsp|asp|sh|cgi)$ {
            deny all;
        }
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
    }
    
    # Block common attack patterns
    location ~* \.(env|git|svn|htaccess|htpasswd|ini|log|sh|sql|conf)$ {
        deny all;
    }
    
    # Block bad bots and scrapers
    if ($http_user_agent ~* (bot|crawler|spider|scraper)) {
        return 403;
    }
}
```

### 2. Application Security Configuration

#### FastAPI Security Settings (`backend/api/security.py`)
```python
"""
Security configuration and utilities for SMCP Backend
"""
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis

# Security constants
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# JWT Security
security = HTTPBearer()

# Redis connection for rate limiting
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)

class SecurityConfig:
    """Security configuration settings"""
    
    # Password policy
    MIN_PASSWORD_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True  
    REQUIRE_NUMBERS = True
    REQUIRE_SYMBOLS = True
    
    # Session settings
    SESSION_TIMEOUT_MINUTES = 30
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15
    
    # API rate limits
    API_RATE_LIMIT = "100/minute"
    AUTH_RATE_LIMIT = "10/minute"
    UPLOAD_RATE_LIMIT = "20/minute"
    
    # File upload security
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}
    ALLOWED_MIME_TYPES = {
        'image/jpeg', 'image/png', 'image/gif', 
        'image/webp', 'image/svg+xml'
    }

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def validate_password_strength(password: str) -> Dict[str, Any]:
    """Validate password meets security requirements"""
    errors = []
    
    if len(password) < SecurityConfig.MIN_PASSWORD_LENGTH:
        errors.append(f"Password must be at least {SecurityConfig.MIN_PASSWORD_LENGTH} characters")
    
    if SecurityConfig.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
        errors.append("Password must contain uppercase letters")
    
    if SecurityConfig.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
        errors.append("Password must contain lowercase letters")
    
    if SecurityConfig.REQUIRE_NUMBERS and not any(c.isdigit() for c in password):
        errors.append("Password must contain numbers")
    
    if SecurityConfig.REQUIRE_SYMBOLS and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("Password must contain symbols")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            return None
        return payload
    except JWTError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise credentials_exception
    
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Get user from database (implement based on your user model)
    # user = await get_user_by_id(user_id)
    # if user is None:
    #     raise credentials_exception
    
    return {"user_id": user_id, "email": payload.get("email")}

def check_user_permissions(required_role: str):
    """Decorator to check user role permissions"""
    def permission_checker(current_user: dict = Depends(get_current_user)):
        # Implement role-based access control
        user_role = current_user.get("role", "user")
        role_hierarchy = {"admin": 3, "manager": 2, "user": 1, "viewer": 0}
        
        if role_hierarchy.get(user_role, 0) < role_hierarchy.get(required_role, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return permission_checker

def sanitize_input(input_string: str, max_length: int = 1000) -> str:
    """Sanitize user input to prevent XSS and injection attacks"""
    import html
    import re
    
    # HTML encode
    sanitized = html.escape(input_string)
    
    # Remove potential script tags and javascript
    sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'on\w+\s*=', '', sanitized, flags=re.IGNORECASE)
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()

def validate_file_upload(file) -> Dict[str, Any]:
    """Validate uploaded file for security"""
    import magic
    from pathlib import Path
    
    errors = []
    
    # Check file size
    if hasattr(file, 'size') and file.size > SecurityConfig.MAX_FILE_SIZE:
        errors.append(f"File size exceeds {SecurityConfig.MAX_FILE_SIZE} bytes")
    
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in SecurityConfig.ALLOWED_EXTENSIONS:
        errors.append(f"File type {file_ext} not allowed")
    
    # Check MIME type
    mime_type = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)  # Reset file pointer
    
    if mime_type not in SecurityConfig.ALLOWED_MIME_TYPES:
        errors.append(f"MIME type {mime_type} not allowed")
    
    # Additional security checks for images
    if mime_type.startswith('image/'):
        try:
            from PIL import Image
            img = Image.open(file)
            img.verify()
            file.seek(0)  # Reset after verification
        except Exception as e:
            errors.append("Invalid or corrupted image file")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "mime_type": mime_type,
        "file_ext": file_ext
    }

# Login attempt tracking
async def track_login_attempt(ip_address: str, success: bool) -> Dict[str, Any]:
    """Track login attempts for brute force protection"""
    key = f"login_attempts:{ip_address}"
    
    if success:
        # Clear failed attempts on successful login
        await redis_client.delete(key)
        return {"blocked": False}
    
    # Increment failed attempts
    attempts = await redis_client.incr(key)
    if attempts == 1:
        # Set expiration on first attempt
        await redis_client.expire(key, SecurityConfig.LOCKOUT_DURATION_MINUTES * 60)
    
    # Check if account should be locked
    if attempts >= SecurityConfig.MAX_LOGIN_ATTEMPTS:
        # Extend lockout period
        await redis_client.expire(key, SecurityConfig.LOCKOUT_DURATION_MINUTES * 60)
        return {
            "blocked": True,
            "attempts": attempts,
            "lockout_expires": SecurityConfig.LOCKOUT_DURATION_MINUTES
        }
    
    return {
        "blocked": False,
        "attempts": attempts,
        "remaining": SecurityConfig.MAX_LOGIN_ATTEMPTS - attempts
    }

async def is_ip_blocked(ip_address: str) -> bool:
    """Check if IP is currently blocked due to failed login attempts"""
    key = f"login_attempts:{ip_address}"
    attempts = await redis_client.get(key)
    
    if attempts and int(attempts) >= SecurityConfig.MAX_LOGIN_ATTEMPTS:
        return True
    
    return False

# Security middleware
class SecurityMiddleware:
    """Custom security middleware for additional protections"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Check for common attack patterns
            suspicious_patterns = [
                r'\.\./', r'\.\.\%2f', r'\.\.\%5c',  # Directory traversal
                r'<script', r'javascript:', r'vbscript:',  # XSS attempts
                r'union.*select', r'or.*1.*=.*1',  # SQL injection
                r'cmd.*=', r'exec.*\(',  # Command injection
            ]
            
            query_string = request.url.query.lower()
            user_agent = request.headers.get("user-agent", "").lower()
            
            for pattern in suspicious_patterns:
                if re.search(pattern, query_string) or re.search(pattern, user_agent):
                    # Log security event
                    logger.warning(
                        f"Suspicious request blocked from {request.client.host}",
                        extra={
                            "ip": request.client.host,
                            "url": str(request.url),
                            "user_agent": request.headers.get("user-agent"),
                            "pattern": pattern
                        }
                    )
                    
                    # Return 403 Forbidden
                    response = Response(
                        content="Forbidden",
                        status_code=403
                    )
                    await response(scope, receive, send)
                    return
        
        await self.app(scope, receive, send)
```

#### Frontend Security Configuration (`frontend/src/lib/security.ts`)
```typescript
/**
 * Frontend security utilities and configuration
 */

export class SecurityConfig {
  static readonly CSP_POLICY = {
    'default-src': ["'self'"],
    'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
    'style-src': ["'self'", "'unsafe-inline'"],
    'img-src': ["'self'", "data:", "https:"],
    'font-src': ["'self'", "data:"],
    'connect-src': ["'self'"],
    'frame-ancestors': ["'none'"]
  }

  static readonly SECURE_HEADERS = {
    'X-Frame-Options': 'DENY',
    'X-Content-Type-Options': 'nosniff',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'strict-origin-when-cross-origin'
  }

  static readonly API_CONFIG = {
    timeout: 30000, // 30 seconds
    maxRetries: 3,
    retryDelay: 1000
  }
}

/**
 * Sanitize user input to prevent XSS attacks
 */
export function sanitizeInput(input: string, maxLength: number = 1000): string {
  if (!input) return '';
  
  // HTML encode special characters
  const htmlEscapes: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;'
  };
  
  let sanitized = input.replace(/[&<>"'\/]/g, (match) => htmlEscapes[match]);
  
  // Remove potential script content
  sanitized = sanitized.replace(/<script[^>]*>.*?<\/script>/gi, '');
  sanitized = sanitized.replace(/javascript:/gi, '');
  sanitized = sanitized.replace(/on\w+\s*=/gi, '');
  
  // Truncate to max length
  if (sanitized.length > maxLength) {
    sanitized = sanitized.substring(0, maxLength);
  }
  
  return sanitized.trim();
}

/**
 * Validate file uploads on client side
 */
export function validateFileUpload(file: File): { valid: boolean; errors: string[] } {
  const errors: string[] = [];
  
  // File size limit (50MB)
  const MAX_FILE_SIZE = 50 * 1024 * 1024;
  if (file.size > MAX_FILE_SIZE) {
    errors.push(`File size must be less than ${MAX_FILE_SIZE / (1024 * 1024)}MB`);
  }
  
  // Allowed file types
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml'];
  if (!allowedTypes.includes(file.type)) {
    errors.push('File type not allowed. Please upload JPG, PNG, GIF, WebP, or SVG files only.');
  }
  
  // File name validation
  const allowedExtensions = /\.(jpg|jpeg|png|gif|webp|svg)$/i;
  if (!allowedExtensions.test(file.name)) {
    errors.push('Invalid file extension');
  }
  
  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * Secure API client with authentication and error handling
 */
export class SecureApiClient {
  private baseUrl: string;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.loadTokensFromStorage();
  }

  private loadTokensFromStorage(): void {
    if (typeof window !== 'undefined') {
      this.accessToken = localStorage.getItem('access_token');
      this.refreshToken = localStorage.getItem('refresh_token');
    }
  }

  private saveTokensToStorage(accessToken: string, refreshToken: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
      this.accessToken = accessToken;
      this.refreshToken = refreshToken;
    }
  }

  private clearTokensFromStorage(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      this.accessToken = null;
      this.refreshToken = null;
    }
  }

  private async refreshAccessToken(): Promise<boolean> {
    if (!this.refreshToken) return false;

    try {
      const response = await fetch(`${this.baseUrl}/api/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: this.refreshToken }),
      });

      if (response.ok) {
        const data = await response.json();
        this.saveTokensToStorage(data.access_token, data.refresh_token);
        return true;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
    }

    this.clearTokensFromStorage();
    return false;
  }

  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<{ data: T | null; error: string | null }> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = new Headers(options.headers);

    // Add security headers
    Object.entries(SecurityConfig.SECURE_HEADERS).forEach(([key, value]) => {
      headers.set(key, value);
    });

    // Add authentication if available
    if (this.accessToken) {
      headers.set('Authorization', `Bearer ${this.accessToken}`);
    }

    const requestOptions: RequestInit = {
      ...options,
      headers,
      credentials: 'include',
    };

    try {
      let response = await fetch(url, requestOptions);

      // Handle token expiration
      if (response.status === 401 && this.refreshToken) {
        const refreshed = await this.refreshAccessToken();
        if (refreshed) {
          // Retry request with new token
          headers.set('Authorization', `Bearer ${this.accessToken}`);
          response = await fetch(url, { ...requestOptions, headers });
        } else {
          // Redirect to login
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
          return { data: null, error: 'Authentication required' };
        }
      }

      if (response.ok) {
        const data = await response.json();
        return { data, error: null };
      } else {
        const errorData = await response.json().catch(() => ({ message: 'Unknown error' }));
        return { data: null, error: errorData.message || 'Request failed' };
      }
    } catch (error) {
      console.error('API request failed:', error);
      return { data: null, error: 'Network error' };
    }
  }

  async login(email: string, password: string): Promise<{ success: boolean; error?: string }> {
    const { data, error } = await this.request<{ access_token: string; refresh_token: string }>('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email: sanitizeInput(email), password }),
    });

    if (data) {
      this.saveTokensToStorage(data.access_token, data.refresh_token);
      return { success: true };
    }

    return { success: false, error: error || 'Login failed' };
  }

  logout(): void {
    this.clearTokensFromStorage();
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  }

  isAuthenticated(): boolean {
    return !!this.accessToken;
  }
}

/**
 * Content Security Policy implementation
 */
export function setContentSecurityPolicy(): void {
  if (typeof document !== 'undefined') {
    const meta = document.createElement('meta');
    meta.httpEquiv = 'Content-Security-Policy';
    
    const policy = Object.entries(SecurityConfig.CSP_POLICY)
      .map(([key, values]) => `${key} ${values.join(' ')}`)
      .join('; ');
    
    meta.content = policy;
    document.head.appendChild(meta);
  }
}

/**
 * Secure local storage wrapper
 */
export class SecureStorage {
  private static encrypt(data: string): string {
    // Simple XOR encryption for client-side storage
    // In production, use a proper encryption library
    const key = 'SMCP_SECURE_KEY'; // Should be dynamic/random
    let encrypted = '';
    for (let i = 0; i < data.length; i++) {
      encrypted += String.fromCharCode(data.charCodeAt(i) ^ key.charCodeAt(i % key.length));
    }
    return btoa(encrypted);
  }

  private static decrypt(encryptedData: string): string {
    try {
      const key = 'SMCP_SECURE_KEY'; // Should match encryption key
      const data = atob(encryptedData);
      let decrypted = '';
      for (let i = 0; i < data.length; i++) {
        decrypted += String.fromCharCode(data.charCodeAt(i) ^ key.charCodeAt(i % key.length));
      }
      return decrypted;
    } catch (error) {
      console.error('Decryption failed:', error);
      return '';
    }
  }

  static setItem(key: string, value: string): void {
    if (typeof window !== 'undefined') {
      const encrypted = this.encrypt(value);
      localStorage.setItem(key, encrypted);
    }
  }

  static getItem(key: string): string | null {
    if (typeof window !== 'undefined') {
      const encrypted = localStorage.getItem(key);
      if (encrypted) {
        return this.decrypt(encrypted);
      }
    }
    return null;
  }

  static removeItem(key: string): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(key);
    }
  }
}
```

### 3. Docker Security Configuration

#### Security-Hardened Dockerfile (`backend/Dockerfile.secure`)
```dockerfile
# Multi-stage security-hardened Dockerfile
FROM python:3.12-slim as builder

# Security: Create non-root user early
RUN groupadd -r appuser && \
    useradd -r -g appuser -m -d /app -s /bin/bash appuser

WORKDIR /app

# Install security tools and dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gnupg2 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency files
COPY --chown=appuser:appuser pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync --frozen --no-dev

# Production stage
FROM python:3.12-slim

# Security: Install security updates only
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Security: Create non-root user
RUN groupadd -r appuser && \
    useradd -r -g appuser -m -d /app -s /bin/bash appuser

WORKDIR /app

# Copy Python environment from builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY --chown=appuser:appuser . .

# Security: Set proper permissions
RUN chown -R appuser:appuser /app && \
    chmod -R 755 /app && \
    chmod -R 644 /app/*.py

# Security: Switch to non-root user
USER appuser

# Security: Use non-privileged port
ARG BACKEND_PORT=8000
ENV BACKEND_PORT=${BACKEND_PORT}

EXPOSE ${BACKEND_PORT}

# Security: Use exec form and specific command
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Security: Add health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${BACKEND_PORT}/health || exit 1
```

### 4. Environment Security

#### Production Environment Template (`.env.production.template`)
```bash
# Production Environment Configuration
# Copy to .env.production and fill in actual values

# Project Configuration
PROJECT_NAME=smcp
BUILD_ID=v1.0.0
ENVIRONMENT=production

# Domain Configuration
DOMAIN_NAME=your-domain.com
CDN_URL=https://cdn.your-domain.com
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Application Ports
BACKEND_PORT=8000
FRONTEND_PORT=3000
BACKEND_HOST=backend

# Database Configuration
POSTGRES_DB=smcp_production
POSTGRES_USER=smcp_user
POSTGRES_PASSWORD=CHANGE_ME_SECURE_PASSWORD
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

# Redis Configuration  
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=CHANGE_ME_SECURE_REDIS_PASSWORD
REDIS_URL=redis://default:${REDIS_PASSWORD}@${REDIS_HOST}:${REDIS_PORT}/0

# Security Configuration
SECRET_KEY=CHANGE_ME_GENERATE_SECURE_SECRET_KEY
JWT_SECRET_KEY=CHANGE_ME_GENERATE_JWT_SECRET
ENCRYPTION_KEY=CHANGE_ME_32_CHAR_ENCRYPTION_KEY

# API Keys
FREEPIK_API_KEY=your_freepik_api_key
OPENAI_API_KEY=your_openai_api_key_if_needed

# Email Configuration
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your_sendgrid_api_key
FROM_EMAIL=noreply@your-domain.com

# AWS Configuration (for S3 storage and backups)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
S3_BUCKET_NAME=smcp-assets-prod
S3_BACKUP_BUCKET=smcp-backups-prod
AWS_REGION=us-east-1

# Monitoring Configuration
GRAFANA_ADMIN_PASSWORD=CHANGE_ME_SECURE_GRAFANA_PASSWORD
PROMETHEUS_RETENTION_DAYS=90

# Security Settings
RATE_LIMIT_PER_MINUTE=100
MAX_LOGIN_ATTEMPTS=5
SESSION_TIMEOUT_MINUTES=30
PASSWORD_MIN_LENGTH=8

# File Upload Settings
MAX_FILE_SIZE_MB=50
ALLOWED_FILE_TYPES=jpg,jpeg,png,gif,webp,svg

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
SENTRY_DSN=your_sentry_dsn_for_error_tracking

# Feature Flags
ENABLE_NEW_BRAND_VALIDATOR=false
ENABLE_ADVANCED_ANALYTICS=true
ENABLE_CONTENT_MODERATION=true
```

### 5. Security Monitoring Scripts

#### Security Audit Script (`scripts/security-audit.sh`)
```bash
#!/bin/bash
# Comprehensive security audit script

set -e

echo "🔒 Starting Security Audit..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check Docker security
echo "📦 Checking Docker Security..."

# Check for running containers as root
ROOT_CONTAINERS=$(docker ps --format "table {{.Names}}" | xargs -I {} docker exec {} whoami 2>/dev/null | grep -c "^root$" || true)
if [ "$ROOT_CONTAINERS" -gt 0 ]; then
    print_warning "$ROOT_CONTAINERS containers running as root user"
else
    print_status 0 "All containers running as non-root users"
fi

# Check for privileged containers
PRIVILEGED_CONTAINERS=$(docker ps --filter "privileged=true" -q | wc -l)
if [ "$PRIVILEGED_CONTAINERS" -gt 0 ]; then
    print_warning "$PRIVILEGED_CONTAINERS privileged containers found"
else
    print_status 0 "No privileged containers running"
fi

# Check image vulnerabilities with Trivy
echo "🔍 Scanning container images for vulnerabilities..."
if command -v trivy &> /dev/null; then
    for image in $(docker images --format "{{.Repository}}:{{.Tag}}" | grep smcp); do
        echo "Scanning $image..."
        trivy image --severity HIGH,CRITICAL --quiet $image
    done
    print_status 0 "Container vulnerability scan completed"
else
    print_warning "Trivy not installed - skipping container vulnerability scan"
fi

# Check SSL/TLS configuration
echo "🔐 Checking SSL/TLS Configuration..."
if command -v testssl.sh &> /dev/null; then
    testssl.sh --quiet --protocols --ciphers --headers https://$DOMAIN_NAME
    print_status 0 "SSL/TLS configuration check completed"
else
    print_warning "testssl.sh not installed - skipping SSL/TLS check"
fi

# Check for exposed secrets
echo "🔑 Checking for exposed secrets..."
SECRET_FILES=(".env.production" "docker-compose.prod.yml" "config/")
for file in "${SECRET_FILES[@]}"; do
    if [ -f "$file" ] || [ -d "$file" ]; then
        # Check for common secret patterns
        SECRETS_FOUND=$(grep -r -i "password\|secret\|key\|token" $file 2>/dev/null | grep -v "CHANGE_ME" | wc -l || true)
        if [ "$SECRETS_FOUND" -gt 0 ]; then
            print_warning "Potential secrets found in $file"
        fi
    fi
done

# Check file permissions
echo "📋 Checking file permissions..."
SECURE_FILES=(".env.production" "config/nginx/ssl/" "scripts/")
for file in "${SECURE_FILES[@]}"; do
    if [ -f "$file" ] || [ -d "$file" ]; then
        PERMS=$(stat -c %a "$file")
        if [[ "$PERMS" =~ ^[67] ]]; then
            print_warning "$file has overly permissive permissions: $PERMS"
        else
            print_status 0 "$file has secure permissions: $PERMS"
        fi
    fi
done

# Check for security updates
echo "🆙 Checking for security updates..."
if command -v apt &> /dev/null; then
    UPDATES=$(apt list --upgradable 2>/dev/null | grep -c "security" || true)
    if [ "$UPDATES" -gt 0 ]; then
        print_warning "$UPDATES security updates available"
    else
        print_status 0 "No security updates pending"
    fi
fi

# Check database security
echo "🗄️ Checking database security..."
if docker exec smcp_postgres_prod pg_isready -U $POSTGRES_USER > /dev/null 2>&1; then
    # Check for default passwords
    if [ "$POSTGRES_PASSWORD" = "password" ] || [ "$POSTGRES_PASSWORD" = "postgres" ]; then
        print_warning "Database using default password"
    else
        print_status 0 "Database using custom password"
    fi
    
    # Check database connections
    CONNECTIONS=$(docker exec smcp_postgres_prod psql -U $POSTGRES_USER -d $POSTGRES_DB -t -c "SELECT count(*) FROM pg_stat_activity;" 2>/dev/null | xargs)
    print_status 0 "Database has $CONNECTIONS active connections"
fi

# Check Redis security
echo "📮 Checking Redis security..."
if docker exec smcp_redis_prod redis-cli ping > /dev/null 2>&1; then
    # Check if Redis requires authentication
    if docker exec smcp_redis_prod redis-cli --raw incr ping 2>/dev/null; then
        print_warning "Redis accessible without authentication"
    else
        print_status 0 "Redis requires authentication"
    fi
fi

# Check log file security
echo "📝 Checking log file security..."
LOG_DIRS=("logs/" "/var/log/")
for dir in "${LOG_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        WORLD_READABLE=$(find "$dir" -type f -perm -004 2>/dev/null | wc -l)
        if [ "$WORLD_READABLE" -gt 0 ]; then
            print_warning "$WORLD_READABLE log files are world-readable"
        else
            print_status 0 "Log files have secure permissions"
        fi
    fi
done

# Check for open ports
echo "🌐 Checking for open ports..."
if command -v nmap &> /dev/null; then
    OPEN_PORTS=$(nmap -sS localhost | grep "open" | wc -l)
    print_status 0 "$OPEN_PORTS open ports found on localhost"
else
    print_warning "nmap not installed - skipping port scan"
fi

# Generate security report
echo "📊 Generating security report..."
cat > security-audit-report.txt << EOF
Security Audit Report
Generated: $(date)
Domain: $DOMAIN_NAME

Container Security:
- Root containers: $ROOT_CONTAINERS
- Privileged containers: $PRIVILEGED_CONTAINERS

Network Security:
- Open ports: ${OPEN_PORTS:-"N/A"}

Database Security:
- Active connections: ${CONNECTIONS:-"N/A"}

File Security:
- World-readable logs: ${WORLD_READABLE:-0}

Recommendations:
- Review all WARNING items above
- Update all CHANGE_ME placeholders
- Schedule regular security scans
- Monitor security logs daily
- Update dependencies regularly

EOF

echo -e "${GREEN}✓${NC} Security audit completed. Report saved to security-audit-report.txt"
echo "📋 Review all warnings and take appropriate action."
```

### 6. Security Incident Response Plan

#### Incident Response Runbook (`docs/security-incident-response.md`)
```markdown
# Security Incident Response Plan

## 🚨 Immediate Response (0-30 minutes)

### 1. Incident Detection
- Monitor alerts from Grafana/Prometheus
- Check security logs in Loki
- Review failed login attempts
- Monitor API rate limiting triggers

### 2. Initial Assessment
```bash
# Quick security assessment
./scripts/security-quick-check.sh

# Check recent access logs
docker logs smcp_nginx_prod | tail -1000 | grep -E "(40[0-9]|50[0-9])"

# Check database connections
docker exec smcp_postgres_prod psql -U $POSTGRES_USER -d $POSTGRES_DB -c "
SELECT pid, usename, application_name, client_addr, backend_start 
FROM pg_stat_activity 
WHERE state = 'active' 
ORDER BY backend_start DESC;"
```

### 3. Containment Actions
```bash
# Block suspicious IP addresses
iptables -A INPUT -s <SUSPICIOUS_IP> -j DROP

# Rate limit specific endpoints
# Update nginx configuration and reload
docker exec smcp_nginx_prod nginx -s reload

# Revoke compromised user sessions
# Update JWT secret key and restart backend
docker-compose restart backend
```

## 🔧 Investigation Phase (30 minutes - 2 hours)

### 1. Evidence Collection
```bash
# Export security logs
docker exec smcp_loki_prod logcli query '{job="smcp_backend"}' \
  --from="2024-01-01T00:00:00Z" --to="2024-01-01T23:59:59Z" \
  --output=jsonl > security-incident-logs.jsonl

# Database audit trail
docker exec smcp_postgres_prod psql -U $POSTGRES_USER -d $POSTGRES_DB -c "
SELECT * FROM user_activity_logs 
WHERE created_at >= NOW() - INTERVAL '24 hours' 
ORDER BY created_at DESC;"

# File system changes
find /app -type f -mtime -1 -ls > recent-file-changes.log
```

### 2. Impact Assessment
- Identify compromised accounts
- Check data access/modification
- Review system integrity
- Assess service availability

## 🛡️ Recovery Phase (2-24 hours)

### 1. System Hardening
```bash
# Force password resets for affected users
python scripts/force_password_reset.py --users="user1,user2"

# Rotate API keys
python scripts/rotate_api_keys.py

# Update SSL certificates if compromised
./scripts/renew-ssl-certificates.sh

# Database security updates
docker exec smcp_postgres_prod psql -U $POSTGRES_USER -d $POSTGRES_DB -c "
UPDATE users SET password_hash = 'FORCE_RESET' 
WHERE last_login_at < NOW() - INTERVAL '30 days';"
```

### 2. Monitoring Enhancement
```bash
# Increase logging verbosity
export LOG_LEVEL=DEBUG
docker-compose up -d backend

# Add additional security monitoring
./scripts/enable_enhanced_monitoring.sh

# Set up temporary alerting
./scripts/setup_incident_alerts.sh
```

## 📊 Post-Incident Analysis (24-72 hours)

### 1. Root Cause Analysis
- Timeline reconstruction
- Vulnerability identification
- Process gap analysis
- Security control effectiveness

### 2. Remediation Plan
- Immediate fixes
- Short-term improvements
- Long-term security enhancements
- Training requirements

### 3. Documentation
- Incident report
- Lessons learned
- Process updates
- Stakeholder communication

## 📞 Contact Information

### Internal Team
- Security Lead: security@bymb.com
- DevOps Team: devops@bymb.com
- Management: management@bymb.com

### External Resources
- Cloud Provider Security: [Provider Contact]
- Legal Counsel: [Legal Contact]
- PR/Communications: [PR Contact]
- Cyber Insurance: [Insurance Contact]
```

This comprehensive security configuration provides BYMB Consultancy with enterprise-grade security controls, monitoring, and incident response capabilities to protect their social media content generation platform and sensitive brand data.