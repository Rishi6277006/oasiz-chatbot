#!/bin/bash

# 🚀 Oasiz Chatbot Deployment Script
# This script automates the deployment process

echo "🎉 Starting Oasiz Chatbot Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Vercel CLI is installed
check_vercel() {
    if ! command -v vercel &> /dev/null; then
        print_warning "Vercel CLI not found. Installing..."
        npm install -g vercel
    else
        print_success "Vercel CLI found"
    fi
}

# Deploy frontend
deploy_frontend() {
    print_status "Deploying frontend to Vercel..."
    cd frontend
    
    # Build the project
    print_status "Building frontend..."
    npm run build
    
    if [ $? -eq 0 ]; then
        print_success "Frontend build successful"
        
        # Deploy to Vercel
        print_status "Deploying to Vercel..."
        vercel --prod --yes
        
        if [ $? -eq 0 ]; then
            print_success "Frontend deployed successfully!"
            print_status "Get your frontend URL from the Vercel dashboard"
        else
            print_error "Frontend deployment failed"
            exit 1
        fi
    else
        print_error "Frontend build failed"
        exit 1
    fi
    
    cd ..
}

# Deploy backend
deploy_backend() {
    print_status "Preparing backend for deployment..."
    cd backend
    
    # Check if Railway CLI is installed
    if ! command -v railway &> /dev/null; then
        print_warning "Railway CLI not found. Please install it manually:"
        echo "npm install -g @railway/cli"
        print_status "Or deploy manually to Railway/Render"
        return 1
    fi
    
    print_status "Deploying backend to Railway..."
    railway up
    
    if [ $? -eq 0 ]; then
        print_success "Backend deployed successfully!"
        print_status "Get your backend URL from the Railway dashboard"
    else
        print_error "Backend deployment failed"
        print_status "You can deploy manually to Railway or Render"
    fi
    
    cd ..
}

# Main deployment process
main() {
    print_status "🚀 Starting Oasiz Chatbot Deployment..."
    
    # Check prerequisites
    check_vercel
    
    # Deploy frontend
    deploy_frontend
    
    # Deploy backend
    deploy_backend
    
    print_success "🎉 Deployment process completed!"
    print_status "Next steps:"
    echo "1. Set environment variables in Vercel dashboard"
    echo "2. Set environment variables in Railway/Render dashboard"
    echo "3. Update VITE_API_URL in frontend environment"
    echo "4. Test your deployed application"
    echo "5. Record your demo video"
}

# Run main function
main "$@" 