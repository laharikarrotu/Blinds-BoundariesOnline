# 🚀 Dual Deployment Strategy Guide

## Overview
This project uses **two deployment methods** for optimal reliability and efficiency:

1. **Manual Deployment** - For heavy releases with AI models
2. **GitHub Actions** - For regular updates and development

---

## 📦 Manual Deployment (Heavy Releases)

### When to Use:
- ✅ Major feature releases
- ✅ AI model updates (SAM, YOLOv8)
- ✅ Critical bug fixes
- ✅ When you need full control

### Steps:
1. **Create deployment package:**
   ```bash
   python deploy-manual.py
   ```

2. **Go to Azure Portal:**
   - Visit: https://portal.azure.com
   - Navigate to: `blinds-boundaries-api` App Service
   - Go to: "Deployment Center"

3. **Upload and deploy:**
   - Choose "Manual deployment"
   - Upload: `manual_deployment.zip`
   - Click "Deploy"

### What's Included:
- ✅ Full AI-Enhanced detection (SAM + YOLOv8 + Hybrid)
- ✅ All features and capabilities
- ✅ Complete deployment package

### Deployment Time: 8-15 minutes

---

## 🔄 GitHub Actions (Regular Updates)

### When to Use:
- ✅ Code improvements
- ✅ Bug fixes
- ✅ Frontend updates
- ✅ Regular development workflow

### How it Works:
1. **Automatic triggers:**
   - Push to `main` branch
   - Excludes heavy AI model files
   - Uses lightweight dependencies

2. **Manual triggers:**
   - Go to GitHub Actions tab
   - Click "Run workflow"
   - Choose deployment type

### What's Included:
- ✅ Hybrid detector (Azure Vision + Gemini + OpenCV)
- ✅ Core functionality
- ✅ Lightweight deployment

### Deployment Time: 3-5 minutes

---

## 🎯 Deployment Decision Matrix

| Change Type | Method | Reason |
|-------------|--------|---------|
| AI model updates | Manual | Heavy models, need control |
| Major features | Manual | Full testing, reliability |
| Bug fixes | GitHub Actions | Fast, automated |
| Code improvements | GitHub Actions | Regular workflow |
| Frontend updates | GitHub Actions | Lightweight changes |
| Critical fixes | Manual | Immediate control |

---

## 📋 File Structure

### Manual Deployment Files:
```
manual_deployment.zip          # Full deployment package
deploy-manual.py              # Manual deployment script
requirements.txt              # Full dependencies (with AI models)
```

### GitHub Actions Files:
```
.github/workflows/azure-deploy-simple.yml  # Regular updates workflow
requirements-simple.txt                    # Lightweight dependencies
```

---

## 🔧 Switching Between Methods

### From Manual to GitHub Actions:
1. Push code changes
2. GitHub Actions automatically deploys
3. No manual intervention needed

### From GitHub Actions to Manual:
1. Run: `python deploy-manual.py`
2. Upload to Azure Portal
3. Deploy manually

---

## 🚨 Troubleshooting

### Manual Deployment Issues:
- Check Azure Portal logs
- Verify file upload
- Ensure all dependencies included

### GitHub Actions Issues:
- Check GitHub Actions logs
- Verify workflow triggers
- Check Azure credentials

### Common Solutions:
- Clear Azure cache
- Restart App Service
- Check environment variables

---

## 📞 Support

### For Manual Deployment:
- Use Azure Portal logs
- Check deployment package contents
- Verify file structure

### For GitHub Actions:
- Check GitHub Actions tab
- Review workflow logs
- Verify Azure integration

---

## 🎉 Best Practices

1. **Test locally first** before any deployment
2. **Use manual deployment** for major changes
3. **Use GitHub Actions** for regular updates
4. **Monitor deployment logs** for issues
5. **Keep both methods ready** for flexibility

---

## 📈 Deployment History

Track your deployments:
- **Manual**: Azure Portal deployment history
- **GitHub Actions**: GitHub Actions tab
- **Both**: Azure App Service logs

---

*This dual strategy ensures reliable deployments for all scenarios!* 