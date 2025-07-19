# 🚀 Oasiz Chatbot - Deployment Guide

## 📋 **Deployment Strategy**

This guide covers deploying your **Oasiz Chatbot** using a modern, scalable architecture:

- **Frontend**: Vercel (SvelteKit)
- **Backend**: Railway/Render (FastAPI)
- **Database**: Supabase (PostgreSQL)
- **Real-time**: WebSocket support

## 🎯 **Option 1: Full Vercel Deployment (Recommended)**

### **Step 1: Deploy Frontend to Vercel**

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Navigate to Frontend Directory**:
   ```bash
   cd frontend
   ```

3. **Deploy to Vercel**:
   ```bash
   vercel --prod
   ```

4. **Set Environment Variables in Vercel Dashboard**:
   - `VITE_API_URL`: Your backend API URL
   - `VITE_OPENAI_API_KEY`: Your OpenAI API key
   - `VITE_WEATHER_API_KEY`: Your weather API key

### **Step 2: Deploy Backend to Railway**

1. **Create Railway Account**: [railway.app](https://railway.app)

2. **Connect GitHub Repository**:
   - Push your code to GitHub
   - Connect Railway to your repo
   - Select the `backend` directory

3. **Set Environment Variables**:
   ```env
   OPENAI_API_KEY=your_openai_key
   WEATHER_API_KEY=your_weather_key
   DATABASE_URL=your_supabase_url
   ```

4. **Deploy**:
   - Railway will automatically detect FastAPI
   - Deploy and get your API URL

### **Step 3: Set Up Database (Supabase)**

1. **Create Supabase Project**: [supabase.com](https://supabase.com)

2. **Get Connection String**:
   ```
   postgresql://postgres:[password]@[host]:5432/postgres
   ```

3. **Run Migrations**:
   ```bash
   cd backend
   alembic upgrade head
   ```

## 🎯 **Option 2: Hybrid Deployment**

### **Frontend: Vercel**
- Same as above
- Perfect for SvelteKit

### **Backend: Render**
1. **Create Render Account**: [render.com](https://render.com)
2. **Deploy as Web Service**
3. **Set environment variables**
4. **Get API URL**

## 🔧 **Environment Variables Setup**

### **Frontend (.env.local)**:
```env
VITE_API_URL=https://your-backend-url.com
VITE_OPENAI_API_KEY=your_openai_key
VITE_WEATHER_API_KEY=your_weather_key
```

### **Backend (.env)**:
```env
OPENAI_API_KEY=your_openai_key
WEATHER_API_KEY=your_weather_key
DATABASE_URL=your_database_url
CORS_ORIGINS=https://your-frontend-url.vercel.app
```

## 🚀 **Quick Deploy Commands**

### **1. Deploy Frontend**:
```bash
cd frontend
vercel --prod
```

### **2. Deploy Backend (Railway)**:
```bash
cd backend
railway login
railway init
railway up
```

### **3. Update Frontend API URL**:
```bash
vercel env add VITE_API_URL
# Enter your backend URL
```

## 📊 **Performance Optimization**

### **Frontend (Vercel)**:
- ✅ Automatic CDN
- ✅ Edge Functions
- ✅ Image Optimization
- ✅ Analytics

### **Backend (Railway/Render)**:
- ✅ Auto-scaling
- ✅ Health checks
- ✅ Logs monitoring
- ✅ SSL certificates

## 🔒 **Security Checklist**

- [ ] Environment variables set
- [ ] CORS configured
- [ ] API keys secured
- [ ] HTTPS enabled
- [ ] Rate limiting active
- [ ] Input validation
- [ ] SQL injection protection

## 📈 **Monitoring & Analytics**

### **Vercel Analytics**:
- Page views
- Performance metrics
- Error tracking

### **Backend Monitoring**:
- Response times
- Error rates
- Resource usage

## 🎥 **Demo Video Setup**

1. **Record Deployment Process**:
   - Show Vercel deployment
   - Demonstrate live features
   - Show real-time chat
   - Display tool integrations

2. **Highlight Key Features**:
   - Beautiful UI/UX
   - Tool calling
   - MCP integration
   - Streaming responses
   - Voice commands

## 🏆 **Final Checklist**

- [ ] Frontend deployed on Vercel
- [ ] Backend deployed on Railway/Render
- [ ] Database connected
- [ ] Environment variables set
- [ ] CORS configured
- [ ] SSL certificates active
- [ ] Performance optimized
- [ ] Security measures in place
- [ ] Demo video recorded
- [ ] README updated with live URLs

## 🆘 **Troubleshooting**

### **Common Issues**:
1. **CORS Errors**: Check CORS_ORIGINS in backend
2. **API Key Issues**: Verify environment variables
3. **Database Connection**: Check DATABASE_URL format
4. **Build Failures**: Check Node.js version compatibility

### **Support**:
- Vercel Docs: [vercel.com/docs](https://vercel.com/docs)
- Railway Docs: [docs.railway.app](https://docs.railway.app)
- Render Docs: [render.com/docs](https://render.com/docs)

---

**🎉 Your Oasiz Chatbot is ready for deployment! Follow this guide for a professional, scalable deployment.** 