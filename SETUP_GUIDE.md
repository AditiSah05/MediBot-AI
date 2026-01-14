# Medical Chatbot Setup Guide

# Medical Chatbot Setup Guide

## ✅ **Enhanced Medical Chatbot Now Running!**

**🌐 Access your medical chatbot:**
- **Landing Page**: http://localhost:8080
- **Direct Chat**: http://localhost:8080/chat

## 🎨 **New Modern Interface Features**

### **Landing Page (http://localhost:8080)**
- Professional medical-themed design
- Feature overview with statistics
- Quick access to chat interface
- Comprehensive medical disclaimer

### **Chat Interface (http://localhost:8080/chat)**
- **Modern Design**: Clean, medical-themed UI with gradient backgrounds
- **Emergency Banner**: Prominent emergency information at the top
- **Welcome Message**: Comprehensive introduction with quick suggestions
- **Smart Suggestions**: One-click buttons for common health topics
- **Typing Indicators**: Visual feedback during bot responses
- **Message Formatting**: Proper formatting for medical information
- **Responsive Design**: Works perfectly on mobile and desktop
- **Accessibility**: High contrast support, keyboard navigation
- **Medical Disclaimers**: Clear warnings about professional medical advice

## 🏥 **Comprehensive Health Database (80+ Conditions)**

### **Medical Categories Covered:**
- **Respiratory**: Fever, cough, cold, flu, asthma, pneumonia, bronchitis, sinusitis, allergies, COPD
- **Cardiovascular**: Hypertension, heart attack, stroke, cholesterol, heart failure, arrhythmia, PAD
- **Endocrine**: Diabetes, thyroid disorders, obesity, metabolic syndrome, osteoporosis
- **Gastrointestinal**: Heartburn, constipation, diarrhea, ulcers, IBS, GERD, gallstones, hepatitis
- **Mental Health**: Depression, anxiety, stress, PTSD, bipolar disorder, ADHD, eating disorders
- **Musculoskeletal**: Arthritis, back pain, fibromyalgia, tendinitis, carpal tunnel syndrome
- **Skin Conditions**: Acne, eczema, psoriasis, skin cancer, rosacea
- **Infectious Diseases**: COVID-19, strep throat, UTI, mono, shingles
- **Neurological**: Migraine, epilepsy, Alzheimer's, Parkinson's
- **Eye & Ear**: Glaucoma, cataracts, hearing loss
- **Kidney & Urological**: Kidney stones, kidney disease
- **Women's Health**: Pregnancy, menopause, PCOS, endometriosis
- **Men's Health**: Prostate health, erectile dysfunction, low testosterone
- **Pediatric Health**: Childhood vaccines, growth development
- **Nutrition**: Vitamin deficiencies, food allergies
- **Sleep Disorders**: Sleep apnea, insomnia
- **Emergency Conditions**: Chest pain, allergic reactions, concussion, burns
- **🩹 Vaccination & Immunization**: Comprehensive vaccine information, schedules, safety

### **🩹 Comprehensive Vaccination Information:**
- **Routine Adult Vaccines**: Flu (annual), COVID-19, Tdap, Shingles, Pneumonia, MMR
- **Childhood Vaccine Schedule**: DTaP, MMR, Varicella, Hepatitis B, Hib, PCV13, Rotavirus
- **Travel Vaccines**: Yellow fever, Typhoid, Hepatitis A, Japanese Encephalitis
- **Special Populations**: Pregnant women, immunocompromised, healthcare workers
- **Vaccine Safety**: Testing, monitoring, side effects, effectiveness
- **Myth Debunking**: Scientific evidence against vaccine misinformation
- **Vaccine Ingredients**: Components, safety, preservatives, adjuvants

## 🚀 **Enhanced Query Capabilities**

### **Try These Advanced Queries:**
- **Specific Conditions**: "What is diabetes?", "Tell me about heart disease", "Migraine symptoms"
- **Emergency Situations**: "When to call 911?", "Emergency signs", "Chest pain help"
- **Mental Health**: "Depression symptoms", "Anxiety management", "Stress relief"
- **Prevention**: "How to prevent heart disease?", "Vaccination information", "Vaccine schedule", "Flu vaccine", "COVID vaccine", "Cancer screening"
- **Lifestyle**: "Healthy diet tips", "Exercise recommendations", "Sleep hygiene"
- **Medication**: "Medication safety", "Drug interactions", "Proper dosage"
- **Women's Health**: "Pregnancy care", "Menopause symptoms", "PCOS information"
- **Men's Health**: "Prostate health", "Testosterone levels", "Heart health for men"

## 🎯 **Smart Features**

### **Interactive Elements:**
- **Quick Suggestion Buttons**: Instant access to common health topics
- **Emergency Recognition**: Automatic detection of emergency-related queries
- **Symptom Analysis**: Intelligent responses to symptom descriptions
- **Health Tips**: Comprehensive wellness and prevention advice
- **Crisis Resources**: Mental health support and emergency contacts

### **User Experience:**
- **Auto-resizing Input**: Text area expands as you type
- **Keyboard Shortcuts**: Enter to send, Shift+Enter for new line
- **Message Timestamps**: Track conversation history
- **Smooth Animations**: Professional loading and typing indicators
- **Mobile Optimized**: Perfect experience on all devices

## 📱 **Navigation**
- **Home Page**: http://localhost:8080 - Overview and features
- **Chat Interface**: http://localhost:8080/chat - Direct access to chatbot
- **Responsive**: Works on desktop, tablet, and mobile devices

## 🔒 **Safety & Disclaimers**
- **Emergency Banner**: Prominent 911 reminder for emergencies
- **Medical Disclaimers**: Clear warnings throughout the interface
- **Crisis Resources**: Mental health hotlines and emergency contacts
- **Professional Advice**: Consistent reminders to consult healthcare providers

## 📊 **Technical Improvements**
- **Modern HTML5**: Semantic markup and accessibility features
- **Bootstrap 5**: Latest responsive framework
- **Font Awesome 6**: Updated medical icons
- **Google Fonts**: Professional Inter font family
- **CSS Grid & Flexbox**: Modern layout techniques
- **JavaScript ES6+**: Enhanced interactivity and performance

Your medical chatbot now provides a comprehensive, professional-grade health information experience with modern design and extensive medical knowledge!

## For Full RAG-based Chatbot (Advanced Setup)

### Prerequisites
1. **Pinecone Account**: Sign up at https://www.pinecone.io/
2. **Llama2 Model**: Download from HuggingFace
3. **Python Dependencies**: Install full requirements

### Steps for Full Setup

#### 1. Install Full Dependencies
```bash
pip install langchain langchain-community langchain-pinecone pinecone-client ctransformers
```

#### 2. Download Llama2 Model
- Download `llama-2-7b-chat.ggmlv3.q4_0.bin` from HuggingFace
- Place it in the project root directory

#### 3. Set up Pinecone
- Create a Pinecone index named "medical-chatbot"
- Get your API key from Pinecone dashboard

#### 4. Process Medical Documents
```bash
python src/store_index.py
```
This will:
- Load the medical PDF from `data/medical_book.pdf`
- Split it into chunks
- Create embeddings
- Store in Pinecone vector database

#### 5. Run Full Chatbot
```bash
python webapp.py
```
Enter your Pinecone API key when prompted.

## Files Overview
- `enhanced_webapp.py` - Current working basic chatbot
- `webapp.py` - Full RAG-based chatbot (requires setup)
- `simple_webapp.py` - Minimal test version
- `src/helper.py` - Utility functions for document processing
- `src/store_index.py` - Script to create vector embeddings
- `templates/chat.html` - Web interface
- `static/style.css` - Styling

## Troubleshooting
- If you get import errors, install missing packages with pip
- For Pinecone issues, check your API key and index name
- For model issues, ensure the Llama2 model file is downloaded

## Current Limitations
- Basic version uses simple pattern matching (not AI-powered)
- Full version requires external services (Pinecone, model download)
- Responses are for informational purposes only

**Note**: Always consult healthcare professionals for medical advice. This chatbot is for educational purposes only.