# UI Verification Guide - Stage 1

## 🚀 Option 1: Run Locally (Recommended)

### Quick Start
```bash
cd contract-intelligence
streamlit run app/main.py
```

This will:
- Start the app at http://localhost:8501
- Open automatically in your browser
- Allow you to interact with all features

### What to Check:
1. **Home Page**
   - Professional legal theme with blue gradient header
   - 6 feature cards with icons
   - Navigation sidebar with stats
   - Getting started section

2. **Navigation**
   - Click each feature card button
   - Verify all 5 pages load:
     - 📄 Upload Contract
     - 📊 Analysis Dashboard
     - ⚖️ Compliance Check
     - 🔄 Compare Contracts
     - 📝 Reports

3. **Each Page**
   - Professional layout
   - Placeholder content
   - Consistent theme
   - No errors

---

## 📸 Option 2: Screenshot Review

### Automatic Screenshot Capture
```bash
# Install dependencies
pip install selenium

# Run screenshot capture
python3 capture_screenshots.py
```

This creates:
- `screenshots/stage1_[timestamp]/` folder
- PNG files for each page
- `index.html` summary report

### Manual Screenshots
If Selenium doesn't work, take manual screenshots:
1. Start the app: `streamlit run app/main.py`
2. Take screenshots of:
   - Home page
   - Each of the 5 feature pages
   - Sidebar navigation
   - Any interactions

---

## 🎥 Option 3: Screen Recording

### Record a Demo Video
```bash
# Start the app
streamlit run app/main.py

# Use screen recording tool:
# - Mac: Cmd+Shift+5
# - Windows: Win+Alt+R
# - Linux: OBS Studio or SimpleScreenRecorder
```

Record:
1. App startup
2. Navigate through all pages
3. Show sidebar features
4. Demonstrate responsive design

---

## 🌐 Option 4: Deploy to Streamlit Cloud (Free)

### Quick Deploy for Remote Review
1. Push code to GitHub
2. Visit https://share.streamlit.io
3. Deploy the app (free tier)
4. Share URL for review

---

## 📱 Option 5: Responsive Testing

### Test Different Screen Sizes
```bash
streamlit run app/main.py
```

Then in browser:
- Press F12 (Developer Tools)
- Click device toolbar icon
- Test on:
  - Desktop (1920x1080)
  - Tablet (768x1024)
  - Mobile (375x667)

---

## ✅ Stage 1 UI Checklist

### Home Page
- [ ] Professional header with gradient
- [ ] App title and description visible
- [ ] 6 feature cards displayed
- [ ] Each card has icon, title, description
- [ ] All "action" buttons work
- [ ] Sidebar shows navigation
- [ ] Quick stats display (0 documents, 0 analyses)
- [ ] Feature toggles show status
- [ ] Help links present

### Upload Contract Page
- [ ] File upload widget visible
- [ ] Accepts PDF, DOCX, DOC, TXT
- [ ] Shows file size limits
- [ ] Getting started guide
- [ ] Sample contract buttons

### Analysis Dashboard
- [ ] 4 tabs: Overview, Risk, Parties, Obligations
- [ ] Metrics cards display
- [ ] Placeholder for contract list
- [ ] Warning if no files uploaded
- [ ] Quick action buttons

### Compliance Check
- [ ] Contract selector dropdown
- [ ] Compliance settings checkboxes
- [ ] 3 tabs: Run Check, Results, Policy Library
- [ ] Run compliance button
- [ ] Policy list with status

### Compare Contracts
- [ ] Two contract selectors
- [ ] Comparison options
- [ ] 4 tabs: Summary, Side-by-Side, Analysis, Report
- [ ] Placeholder for results
- [ ] Export options

### Reports Page
- [ ] Contract selection checkboxes
- [ ] Report type selector
- [ ] Export format options
- [ ] 3 template tabs
- [ ] Report history section

### Overall
- [ ] No error messages
- [ ] Consistent theme across pages
- [ ] Professional appearance
- [ ] All buttons/links functional
- [ ] Responsive layout

---

## 🖼️ Visual Sign-off Template

```
Stage 1 - UI Sign-off
====================
Date: _____________
Reviewer: _____________

Home Page:          ✅ / ❌ / 🔧
Upload Page:        ✅ / ❌ / 🔧
Dashboard:          ✅ / ❌ / 🔧
Compliance:         ✅ / ❌ / 🔧
Compare:            ✅ / ❌ / 🔧
Reports:            ✅ / ❌ / 🔧

Overall Quality:    ⭐⭐⭐⭐⭐
Professional Look:  ⭐⭐⭐⭐⭐
Navigation:         ⭐⭐⭐⭐⭐
Responsiveness:     ⭐⭐⭐⭐⭐

Comments:
_______________________
_______________________

Status: APPROVED / NEEDS REVISION

Signature: _____________
```

---

## 🛠️ Troubleshooting

### App Won't Start
```bash
# Check Python version
python3 --version  # Should be 3.10+

# Install dependencies
pip install -r requirements.txt

# Check for errors
streamlit run app/main.py --logger.level=debug
```

### Page Not Loading
- Check browser console (F12) for errors
- Verify all files exist
- Check Python imports

### Screenshot Script Fails
- Install Chrome browser
- Install ChromeDriver
- Or take manual screenshots

---

## 📤 Sharing for Review

### Option 1: Screenshots
- Save all screenshots to a folder
- Zip and share via email/Slack
- Or use the HTML report from capture_screenshots.py

### Option 2: Live Demo
- Screen share via Zoom/Teams
- Walk through each page
- Get real-time feedback

### Option 3: Deploy
- Use Streamlit Cloud (free)
- Deploy to Heroku/AWS
- Share public URL

### Option 4: Video
- Record full walkthrough
- Upload to YouTube (unlisted)
- Share link for async review