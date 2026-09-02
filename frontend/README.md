# UMLReq Frontend - React Application

AI-Powered UML Diagram Generation Frontend built with React, TypeScript, and Vite.

## 🚀 Features

- Modern React 18 with TypeScript
- Fast development with Vite
- Responsive UI with Tailwind CSS
- State management with Zustand
- Docker containerization with multi-stage builds
- Automated CI/CD deployment to Digital Ocean
- Production-ready Nginx configuration
- SSL/HTTPS support

## 📋 Quick Links

- **[Repository Structure](REPOSITORY-STRUCTURE.md)** - How frontend & backend repos work together
- **[Quick Start Guide](QUICKSTART.md)** - Get up and running in 30 minutes
- **[Full Deployment Guide](DEPLOYMENT.md)** - Complete deployment documentation
- **[Production Docker Compose](docker-compose.production.yml)** - Unified service orchestration
- **[GitHub Actions Workflow](.github/workflows/deploy.yml)** - CI/CD pipeline

## 🏗️ Architecture

### Repository Structure
```
Frontend Repo          Backend Repo
     │                      │
     ├─ Build image        ├─ Build image
     ├─ Push to Hub        ├─ Push to Hub
     └─ Deploy             └─ Deploy
            │                    │
            └────────┬───────────┘
                     ▼
         Digital Ocean Droplet
    ┌─────────────────────────────┐
    │  One unified docker-compose │
    │                             │
    │  ┌────────┐  ┌────────┐   │
    │  │ Nginx  │◄─┤Frontend│   │
    │  │ Proxy  │  │(React) │   │
    │  └───┬────┘  └────────┘   │
    │      │                     │
    │      ├─► /api/* → Backend  │
    │      └─► /*     → Frontend │
    │                             │
    │  ┌────────┐  ┌────────┐   │
    │  │Postgres│  │ Redis  │   │
    │  └────────┘  └────────┘   │
    └─────────────────────────────┘
```

**Key Concept**: Two separate Git repositories deploy to one unified production environment.
See [REPOSITORY-STRUCTURE.md](REPOSITORY-STRUCTURE.md) for details.

## 🛠️ Technology Stack

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Zustand** - State management

### Infrastructure
- **Docker** - Containerization
- **Nginx** - Web server and reverse proxy
- **GitHub Actions** - CI/CD automation
- **Digital Ocean** - Cloud hosting
- **Let's Encrypt** - SSL certificates

## 🚀 Development

### Prerequisites

- Node.js 18+
- npm or yarn
- Docker (for containerization)

### Local Development

```bash
# Navigate to app directory
cd app

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint

# Type check
npm run type-check
```

The development server will start at `http://localhost:5173`

### Environment Variables

For local development, you can create a `.env.local` file in the `app` directory:

```env
# API endpoint (adjust for your local backend)
VITE_API_URL=http://localhost:8000/api
```

## 🐳 Docker

### Build Docker Image

```bash
# Build frontend image
docker build -t umlreq-frontend:latest .

# Run container locally
docker run -p 8080:80 umlreq-frontend:latest

# Access at http://localhost:8080
```

### Docker Compose (Local Testing)

```bash
# Test frontend Docker build locally
docker compose -f docker-compose.dev.yml up

# Access at http://localhost:8080

# Note: This only runs the frontend container
# For full stack, use the unified docker-compose.yml on the droplet
```

## 📦 Deployment

### Quick Deployment (30 minutes)

See [QUICKSTART.md](QUICKSTART.md) for a streamlined setup guide.

### Full Deployment Guide

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive documentation including:

- Digital Ocean droplet setup
- SSL certificate configuration
- GitHub Actions secrets
- CORS configuration
- Troubleshooting
- Maintenance tasks

### Automated Deployment

Every push to the `main` branch automatically:

1. ✅ Builds a new Docker image
2. ✅ Pushes to Docker Hub
3. ✅ Deploys to Digital Ocean
4. ✅ Restarts services
5. ✅ Cleans up old images

## 🔧 Configuration Files

### In This Repository

| File | Purpose | Location |
|------|---------|----------|
| `Dockerfile` | Multi-stage build for React app | Used by CI/CD |
| `docker-compose.production.yml` | **Template** for droplet setup | Copy to droplet |
| `docker-compose.dev.yml` | Local frontend testing | Dev only |
| `nginx/nginx.conf` | Frontend Nginx config (SPA routing) | Inside Docker image |
| `nginx/reverse-proxy.conf` | Main reverse proxy config | Copy to droplet |
| `.github/workflows/deploy.yml` | CI/CD pipeline | GitHub Actions |
| `.env.production.example` | Environment variables template | Copy to droplet |

### On the Droplet (`/opt/umlreq/`)

| File | Purpose |
|------|---------|
| `docker-compose.yml` | **Unified** config for ALL services (frontend + backend) |
| `.env` | Environment variables for ALL services |
| `nginx/reverse-proxy.conf` | Nginx configuration |

### Nginx Configuration

The project includes two Nginx configurations:

1. **Frontend Nginx** (`nginx/nginx.conf`)
   - Serves React SPA
   - Handles client-side routing
   - Gzip compression
   - Static asset caching

2. **Reverse Proxy** (`nginx/reverse-proxy.conf`)
   - Routes `/api/*` to backend
   - Routes `/*` to frontend
   - SSL termination
   - Rate limiting
   - Security headers

## 🔒 Security

- ✅ HTTPS enforced with Let's Encrypt
- ✅ HTTP to HTTPS redirect
- ✅ Security headers (HSTS, X-Frame-Options, etc.)
- ✅ Rate limiting on API and auth endpoints
- ✅ CORS configured for specific origins
- ✅ Non-root user in Docker containers
- ✅ Secrets managed via GitHub Secrets

## 🧪 Testing

```bash
cd app

# Run tests (when test suite is added)
npm test

# Run linter
npm run lint

# Type check
npm run type-check
```

## 📊 Monitoring

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f frontend

# Last 100 lines
docker compose logs --tail=100 frontend
```

### Health Checks

```bash
# Frontend health
curl http://localhost/health

# API health
curl https://umlreq.com/api/health

# Check all services
docker compose ps
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Additional Resources

- [React Documentation](https://react.dev)
- [Vite Documentation](https://vitejs.dev)
- [TypeScript Documentation](https://www.typescriptlang.org)
- [Tailwind CSS Documentation](https://tailwindcss.com)
- [Docker Documentation](https://docs.docker.com)
- [Nginx Documentation](https://nginx.org/en/docs)

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/umlreq-frontend/issues)
- **Deployment Help**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Quick Reference**: See [QUICKSTART.md](QUICKSTART.md)

## 🎯 Roadmap

- [ ] Add comprehensive test suite
- [ ] Implement E2E testing with Playwright
- [ ] Add performance monitoring
- [ ] Implement error tracking (Sentry)
- [ ] Add PWA support
- [ ] Implement analytics

---

**Built with ❤️ using React and TypeScript**
