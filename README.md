# MediBot AI


[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()


## About

MediBot AI is a comprehensive medical information chatbot designed to democratize access to reliable health information. Built with modern web technologies, it serves as an intelligent health assistant for users seeking evidence-based medical information, vaccination schedules, emergency guidance, and wellness advice.

The platform combines advanced pattern recognition with an extensive medical knowledge base covering 150+ medical conditions across 20+ medical specialties. Whether you're researching symptoms, understanding treatment options, or learning about preventive care, MediBot AI provides accurate, up-to-date information while maintaining strict medical ethics and safety protocols.

### Mission
To democratize access to reliable health information and empower individuals to make informed decisions about their health while emphasizing the importance of professional medical care.

### Key Differentiators
- **Comprehensive Coverage**: 150+ medical conditions across 20+ specialties
- **Evidence-Based Information**: Sourced from CDC, WHO, and NIH
- **Emergency & First Aid**: Complete protocols for urgent situations
- **Safety-First Approach**: Prominent disclaimers and professional guidance
- **Modern Interface**: Responsive design accessible on all devices

### Technology Stack
- **Backend**: Python 3.8+ with Flask web framework
- **Frontend**: HTML5, CSS3, JavaScript with Bootstrap 5 and Font Awesome
- **AI/ML**: Pattern matching algorithms with sentence-transformers, PyTorch, and Transformers for potential AI integration
- **Database**: In-memory knowledge base (expandable to vector databases)
- **Deployment**: Docker support for containerized deployment
- **Dependencies**: PyPDF for document processing, tqdm for progress tracking

### Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │    │   MediBot AI    │    │  Knowledge Base │
│                 │    │                 │    │                 │
│ • Web Interface │───►│ • Query Parser  │◄──►│ • Medical Data  │
│ • Chat Messages │    │ • Pattern Match │    │ • CDC/WHO Info │
│ • Voice (Future)│    │ • Response Gen  │    │ • Emergency     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Processing    │    │   Safety Check  │    │   Data Sources  │
│                 │    │                 │    │                 │
│ • AI Analysis   │    │ • Disclaimer    │    │ • NIH Guidelines│
│ • Context Aware │    │ • Professional  │    │ • Research      │
│ • Fast Response │    │ • Guidance      │    │ • Updates       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: 500MB free space
- **Browser**: Modern web browser (Chrome, Firefox, Safari, Edge)

## Features

- 150+ medical conditions across 20+ specialties
- Vaccination information and schedules
- Emergency & first aid protocols
- Mental health support
- Modern responsive web interface


Try these example queries:

**Medical Conditions:**
- "What are the symptoms of diabetes?"
- "How is hypertension treated?"
- "Tell me about asthma management"

**Vaccinations:**
- "What vaccines do I need for travel?"
- "Childhood vaccination schedule"
- "COVID vaccine information"

**Emergency Situations:**
- "What to do for chest pain?"
- "Signs of a heart attack"
- "Allergic reaction treatment"

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/Medical-Chatbot.git
   cd Medical-Chatbot-master
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python enhanced_webapp.py
   ```

4. Open http://localhost:8080 in your browser

**Note**: The application runs on port 8080 by default. Make sure this port is not in use by other applications.

## Usage

Ask questions about:
- Medical conditions and symptoms
- Vaccinations and schedules
- Emergency situations
- Health prevention and wellness

## FAQ

**Q: Is MediBot AI a replacement for professional medical advice?**

A: No, MediBot AI provides general health information for educational purposes only. Always consult qualified healthcare providers.

**Q: How accurate is the information?**

A: Information is sourced from authoritative organizations like CDC, WHO, and NIH. Always verify with current medical guidelines.

**Q: Is my health information private?**

A: Yes, no personal health information is stored. All queries are processed locally and anonymously.

## Troubleshooting

**Application won't start**
- Ensure Python 3.8+ is installed
- Install dependencies: `pip install -r requirements.txt`
- Check port 8080 availability

**Chat interface not loading**
- Clear browser cache
- Try different browser
- Check JavaScript console for errors


## Disclaimer

This chatbot provides general health information for educational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult qualified healthcare providers for medical concerns.

## Acknowledgments

- **Original Project**: Based on the Medical Chatbot project by Abhra Ray Chaudhuri
- **Medical References**: CDC, WHO, NIH, and other authoritative health organizations
- **Open Source Libraries**: Flask, Bootstrap, and the Python community

## Changelog

### v2.0.0 (Current)
- Added comprehensive medical database with 150+ conditions
- Implemented vaccination information module
- Enhanced UI with modern responsive design
- Added accessibility features and WCAG 2.1 compliance
- Integrated emergency guidance and safety protocols
- Added FAQ and troubleshooting sections

### v1.5.0
- Complete UI overhaul with Bootstrap 5.3
- Improved mobile responsiveness
- Added typing indicators and chat enhancements
- Enhanced security measures

### v1.0.0
- Initial release with basic medical chatbot functionality
- Pattern matching for medical queries
- Flask backend implementation
- Basic web interface

## Roadmap

### Short-term Goals
- [ ] Mobile application (iOS/Android)
- [ ] Voice interface integration
- [ ] Multi-language support
- [ ] API endpoints for integrations

### Long-term Vision
- [ ] Advanced AI diagnostics assistance
- [ ] Telemedicine platform integration
- [ ] Wearable device connectivity
- [ ] Global health data analytics

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Author: Aditi Sah**
