from flask import Flask, render_template, jsonify, request, session
import os
import re
import html
import secrets
import time
from collections import defaultdict

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.permanent_session_lifetime = 7200  # 2 hours

# Simple in-memory rate limiter: max 20 requests per minute per IP
_rate_store = defaultdict(list)
RATE_LIMIT = 20
RATE_WINDOW = 60

def is_rate_limited(ip):
    now = time.time()
    timestamps = _rate_store[ip]
    _rate_store[ip] = [t for t in timestamps if now - t < RATE_WINDOW]
    if len(_rate_store[ip]) >= RATE_LIMIT:
        return True
    _rate_store[ip].append(now)
    return False

# Comprehensive medical knowledge base with extensive health information
medical_responses = {
    # Respiratory Conditions
    "fever": "Fever is a temporary increase in body temperature (above 100.4°F/38°C), often due to infection. Symptoms include chills, sweating, headache, and muscle aches. Treatment: Rest, stay hydrated, use fever reducers like acetaminophen or ibuprofen. Seek medical care if fever exceeds 103°F, lasts more than 3 days, or is accompanied by severe symptoms.",
    "cough": "Coughs can be dry (non-productive) or wet (productive with mucus). Causes include infections, allergies, asthma, or GERD. Treatment: Stay hydrated, use honey for soothing, avoid irritants. See a doctor for persistent cough lasting over 3 weeks, blood in sputum, or breathing difficulties.",
    "cold": "Common cold is a viral upper respiratory infection. Symptoms: runny nose, sneezing, sore throat, mild fever, congestion. Treatment: Rest, fluids, saline nasal rinses, throat lozenges. Prevention: Hand washing, avoid close contact with sick individuals. Most colds resolve in 7-10 days.",
    "flu": "Influenza is a viral infection affecting the respiratory system. Symptoms: high fever, body aches, fatigue, headache, dry cough. Treatment: Rest, fluids, antiviral medications if started within 48 hours. Prevention: Annual flu vaccination. Complications can include pneumonia.",
    "asthma": "Chronic respiratory condition causing airway inflammation and narrowing. Symptoms: wheezing, shortness of breath, chest tightness, coughing. Treatment: Rescue inhalers (albuterol), controller medications, avoid triggers. Emergency signs: severe breathing difficulty, blue lips/fingernails.",
    "pneumonia": "Infection causing inflammation in lung air sacs. Symptoms: fever, chills, cough with phlegm, chest pain, shortness of breath. Treatment: Antibiotics for bacterial pneumonia, rest, fluids. Vaccination available for prevention. Seek immediate care for severe symptoms.",
    "bronchitis": "Inflammation of bronchial tubes. Acute bronchitis: viral infection with cough, mucus production. Chronic bronchitis: long-term condition often from smoking. Treatment: Rest, fluids, cough suppressants, bronchodilators if needed.",
    "sinusitis": "Inflammation of sinus cavities causing facial pain, nasal congestion, thick discharge. Acute: lasts <4 weeks, often viral. Chronic: lasts >12 weeks. Treatment: Decongestants, saline rinses, antibiotics for bacterial infections, corticosteroids for severe cases.",
    "allergies": "Immune system overreaction to harmless substances. Symptoms: sneezing, runny nose, itchy eyes, skin rashes. Common allergens: pollen, dust mites, pet dander, foods. Treatment: Avoid triggers, antihistamines, nasal corticosteroids, immunotherapy for severe cases.",
    "copd": "Chronic Obstructive Pulmonary Disease includes emphysema and chronic bronchitis. Symptoms: shortness of breath, chronic cough, wheezing, chest tightness. Main cause: smoking. Treatment: Bronchodilators, corticosteroids, oxygen therapy, pulmonary rehabilitation, smoking cessation.",

    # Cardiovascular Conditions
    "hypertension": "High blood pressure (≥130/80 mmHg) increases risk of heart disease and stroke. Often asymptomatic. Management: DASH diet, regular exercise, weight management, limit sodium and alcohol, stress reduction, medications as prescribed. Regular monitoring essential.",
    "heart attack": "Myocardial infarction occurs when blood flow to heart muscle is blocked. Symptoms: chest pain/pressure, shortness of breath, nausea, sweating, pain radiating to arm/jaw. EMERGENCY: Call 102 immediately. Treatment: Aspirin, medications to restore blood flow, lifestyle changes.",
    "stroke": "Brain attack when blood supply to brain is interrupted. Symptoms (FAST): Face drooping, Arm weakness, Speech difficulty, Time to call 102. Risk factors: high blood pressure, diabetes, smoking, atrial fibrillation. Prevention: control risk factors, healthy lifestyle.",
    "cholesterol": "Waxy substance in blood. High levels increase heart disease risk. LDL (bad) should be <100 mg/dL, HDL (good) should be >40 mg/dL men, >50 mg/dL women. Management: heart-healthy diet, exercise, weight control, medications if needed.",
    "heart failure": "Condition where heart can't pump blood effectively. Symptoms: shortness of breath, fatigue, swelling in legs/ankles, rapid heartbeat. Treatment: ACE inhibitors, beta-blockers, diuretics, lifestyle changes, device therapy in severe cases.",
    "arrhythmia": "Irregular heartbeat patterns. Types: atrial fibrillation, tachycardia, bradycardia. Symptoms: palpitations, dizziness, chest pain, shortness of breath. Treatment: Medications, cardioversion, ablation, pacemaker/defibrillator for severe cases.",
    "peripheral artery disease": "Narrowed arteries reduce blood flow to limbs. Symptoms: leg pain when walking (claudication), cold feet, slow-healing wounds. Risk factors: smoking, diabetes, high cholesterol. Treatment: Exercise, medications, angioplasty, bypass surgery.",

    # Endocrine Conditions
    "diabetes": "Condition where blood glucose levels are too high. Type 1: autoimmune, requires insulin. Type 2: insulin resistance, managed with diet, exercise, medications. Symptoms: increased thirst/urination, fatigue, blurred vision. Complications: heart disease, kidney damage, nerve damage.",
    "thyroid": "Butterfly-shaped gland regulating metabolism. Hyperthyroidism: overactive, causes weight loss, rapid heartbeat, anxiety. Hypothyroidism: underactive, causes weight gain, fatigue, depression. Treatment: medications to normalize hormone levels, regular monitoring.",
    "obesity": "BMI ≥30 kg/m². Health risks: diabetes, heart disease, sleep apnea, certain cancers. Management: caloric deficit through diet and exercise, behavioral changes, medical supervision. Severe cases may require bariatric surgery.",
    "metabolic syndrome": "Cluster of conditions: high blood pressure, high blood sugar, excess abdominal fat, abnormal cholesterol. Increases risk of heart disease, stroke, diabetes. Treatment: Weight loss, exercise, healthy diet, medications for individual components.",
    "osteoporosis": "Bone density loss increasing fracture risk. Risk factors: age, menopause, low calcium/vitamin D, sedentary lifestyle. Prevention: calcium and vitamin D supplements, weight-bearing exercise, avoid smoking and excessive alcohol.",

    # Gastrointestinal Conditions
    "heartburn": "Burning sensation in chest from stomach acid reflux. Triggers: spicy foods, caffeine, alcohol, large meals. Treatment: antacids, avoid triggers, eat smaller meals, elevate head while sleeping. Persistent symptoms may indicate GERD.",
    "constipation": "Fewer than 3 bowel movements per week or difficulty passing stools. Causes: low fiber, dehydration, lack of exercise, medications. Treatment: increase fiber and fluids, exercise, stool softeners if needed. See doctor if persistent or severe.",
    "diarrhea": "Loose, watery stools occurring frequently. Causes: infections, food poisoning, medications, stress. Treatment: stay hydrated with electrolyte solutions, BRAT diet, probiotics. Seek care for severe dehydration, blood in stool, or high fever.",
    "ulcer": "Sores in stomach or small intestine lining. Causes: H. pylori bacteria, NSAIDs, stress. Symptoms: burning stomach pain, bloating, nausea. Treatment: antibiotics for H. pylori, acid reducers, avoid NSAIDs and alcohol.",
    "ibs": "Irritable Bowel Syndrome causes abdominal pain, bloating, diarrhea, constipation. Triggers: stress, certain foods, hormonal changes. Treatment: dietary modifications (low FODMAP), stress management, medications for symptoms, probiotics.",
    "gerd": "Gastroesophageal Reflux Disease: chronic acid reflux. Symptoms: heartburn, regurgitation, chest pain, chronic cough. Treatment: lifestyle changes, proton pump inhibitors, H2 blockers, surgery for severe cases.",
    "gallstones": "Hardened deposits in gallbladder. Symptoms: severe abdominal pain, nausea, vomiting, especially after fatty meals. Risk factors: obesity, rapid weight loss, high-fat diet. Treatment: dietary changes, medications to dissolve stones, surgery if severe.",
    "hepatitis": "Liver inflammation from viruses, alcohol, or toxins. Types: A, B, C (viral). Symptoms: fatigue, nausea, abdominal pain, jaundice. Prevention: vaccination (A, B), safe practices. Treatment: supportive care, antiviral medications for chronic cases.",

    # Mental Health
    "depression": "Persistent sadness and loss of interest affecting daily life. Symptoms: hopelessness, fatigue, sleep changes, appetite changes, difficulty concentrating. Treatment: therapy, medications (antidepressants), lifestyle changes, support groups. Seek help if having suicidal thoughts.",
    "anxiety": "Excessive worry or fear interfering with daily activities. Symptoms: restlessness, rapid heartbeat, sweating, difficulty concentrating. Treatment: therapy (CBT), medications, relaxation techniques, regular exercise, stress management.",
    "stress": "Body's response to challenges or demands. Chronic stress affects physical and mental health. Management: regular exercise, adequate sleep, relaxation techniques, time management, social support, professional help if needed.",
    "ptsd": "Post-Traumatic Stress Disorder develops after traumatic events. Symptoms: flashbacks, nightmares, avoidance, hypervigilance, mood changes. Treatment: trauma-focused therapy (EMDR, CPT), medications, support groups.",
    "bipolar disorder": "Mental health condition with extreme mood swings between mania and depression. Symptoms: elevated mood, increased energy (mania), followed by depression. Treatment: mood stabilizers, therapy, lifestyle management.",
    "adhd": "Attention-Deficit/Hyperactivity Disorder affects focus and behavior. Symptoms: inattention, hyperactivity, impulsivity. Treatment: behavioral therapy, medications (stimulants, non-stimulants), educational support, lifestyle modifications.",
    "eating disorders": "Serious conditions involving eating behaviors. Types: anorexia, bulimia, binge eating disorder. Symptoms: extreme food restriction, binge eating, purging behaviors. Treatment: therapy, nutritional counseling, medical monitoring.",

    # Musculoskeletal Conditions
    "arthritis": "Joint inflammation causing pain and stiffness. Osteoarthritis: wear-and-tear. Rheumatoid arthritis: autoimmune. Treatment: pain relievers, anti-inflammatory medications, physical therapy, exercise, weight management, joint protection techniques.",
    "back pain": "Common condition affecting lower back. Causes: muscle strain, herniated disc, poor posture, arthritis. Treatment: rest, ice/heat, gentle exercise, physical therapy, pain relievers. Prevention: proper lifting, good posture, regular exercise.",
    "fibromyalgia": "Chronic condition causing widespread muscle pain and tenderness. Symptoms: fatigue, sleep problems, cognitive difficulties. Treatment: medications (pregabalin, duloxetine), exercise, stress management, sleep hygiene.",
    "tendinitis": "Inflammation of tendons connecting muscles to bones. Common sites: shoulder, elbow, wrist, knee, ankle. Symptoms: pain, swelling, stiffness. Treatment: rest, ice, anti-inflammatory medications, physical therapy, gradual return to activity.",
    "carpal tunnel syndrome": "Nerve compression in wrist causing hand numbness and tingling. Risk factors: repetitive motions, pregnancy, arthritis. Treatment: wrist splints, ergonomic modifications, corticosteroid injections, surgery for severe cases.",

    # Skin Conditions
    "acne": "Common skin condition with pimples, blackheads, whiteheads. Causes: hormones, bacteria, clogged pores. Treatment: gentle cleansing, topical treatments (benzoyl peroxide, salicylic acid), prescription medications for severe cases.",
    "eczema": "Chronic skin condition causing itchy, inflamed patches. Triggers: allergens, stress, weather changes. Treatment: moisturizers, topical corticosteroids, avoid triggers, gentle skincare routine.",
    "psoriasis": "Autoimmune condition causing scaly, red skin patches. Triggers: stress, infections, medications. Treatment: topical treatments, phototherapy, systemic medications for severe cases, lifestyle modifications.",
    "skin cancer": "Abnormal growth of skin cells. Types: basal cell, squamous cell, melanoma. Risk factors: UV exposure, fair skin, family history. Prevention: sunscreen, protective clothing, avoid tanning beds. Early detection crucial.",
    "rosacea": "Chronic facial redness and inflammation. Triggers: sun exposure, spicy foods, alcohol, stress. Symptoms: persistent redness, visible blood vessels, bumps. Treatment: topical medications, oral antibiotics, laser therapy, trigger avoidance.",

    # Infectious Diseases
    "covid": "COVID-19 is caused by SARS-CoV-2 virus. Symptoms: fever, cough, shortness of breath, loss of taste/smell, fatigue. Prevention: vaccination, masks, hand hygiene, social distancing. Seek care for severe symptoms or high-risk individuals.",
    "strep throat": "Bacterial infection causing severe sore throat. Symptoms: throat pain, fever, swollen lymph nodes, white patches on throat. Treatment: antibiotics, pain relievers, rest, warm salt water gargles.",
    "uti": "Urinary Tract Infection affects bladder, urethra, or kidneys. Symptoms: burning urination, frequent urination, cloudy urine, pelvic pain. Treatment: antibiotics, increased fluid intake. Prevention: proper hygiene, urinate after intercourse.",
    "mono": "Mononucleosis (Epstein-Barr virus) causes extreme fatigue, sore throat, swollen lymph nodes. Treatment: rest, fluids, pain relievers. Avoid contact sports due to spleen enlargement risk. Recovery takes weeks to months.",
    "shingles": "Reactivation of chickenpox virus causing painful rash. Symptoms: burning pain, tingling, followed by blistering rash. Treatment: antiviral medications, pain management. Prevention: shingles vaccine for adults 50+.",

    # Vaccination Information
    "vaccination": "Vaccines prevent serious diseases by building immunity through exposure to weakened or killed pathogens. They're one of the most effective public health interventions. Recommended vaccines vary by age, health status, and risk factors. Follow CDC immunization schedules for optimal protection.",
    "childhood vaccines": "Essential immunizations for children from birth to 18 years. Core vaccines: DTaP (diphtheria, tetanus, pertussis), MMR (measles, mumps, rubella), polio, varicella (chickenpox), hepatitis B, Hib, pneumococcal (PCV13), rotavirus, meningococcal. Schedule: multiple doses at specific ages for optimal immunity.",
    "flu vaccine": "Annual influenza vaccination recommended for everyone 6+ months (with rare exceptions). Best timing: September-October before flu season peaks. Types: inactivated influenza vaccine (shot) or live attenuated (nasal spray). Protects against 3-4 flu strains. Side effects: mild soreness, low-grade fever. Reduces flu risk by 40-60% when well-matched.",
    "covid vaccine": "COVID-19 vaccines provide strong protection against severe illness, hospitalization, and death. Primary series: 2 doses (mRNA vaccines) or 1 dose (viral vector). Boosters recommended based on age, immunocompromised status, and time since last dose. Updated bivalent vaccines target current variants. Side effects: arm pain, fatigue, headache, mild fever.",
    "mmr vaccine": "Measles, Mumps, Rubella combination vaccine. Schedule: First dose 12-15 months, second dose 4-6 years. Adults born after 1957 need 1-2 doses if no evidence of immunity. Highly effective (97% for measles). Contraindicated in pregnancy, severe immunodeficiency. Side effects: fever (5-12 days post-vaccination), mild rash.",
    "dtap vaccine": "Diphtheria, Tetanus, Pertussis (whooping cough) vaccine for children. Schedule: 2, 4, 6 months, 15-18 months, 4-6 years (5 doses total). Adults need Tdap booster every 10 years. Pregnant women should receive Tdap 27-36 weeks each pregnancy to protect newborns. Side effects: soreness, redness, mild fever.",
    "hepatitis b vaccine": "Protects against hepatitis B virus causing chronic liver infection, cirrhosis, liver cancer. Schedule: Birth, 1-2 months, 6-18 months (3 doses). Adults at risk should be vaccinated. Over 95% effective. Lifelong protection in most people. Side effects: soreness at injection site, mild fever. Safe during pregnancy.",
    "hpv vaccine": "Human Papillomavirus vaccine prevents cervical, anal, throat, and other cancers caused by HPV. Recommended ages 11-12 (can start at 9), catch-up through age 26. Two or three-dose series depending on age at start. Most effective before sexual activity begins. Side effects: pain, swelling at injection site, dizziness.",
    "shingles vaccine": "Zoster vaccine (Shingrix) prevents shingles and postherpetic neuralgia. Recommended for adults 50+ regardless of previous shingles or chickenpox vaccination. Two-dose series 2-6 months apart. Reduces shingles risk by >90%. Side effects: arm pain, redness, swelling, muscle pain, fatigue, headache.",
    "pneumonia vaccine": "Pneumococcal vaccines prevent pneumonia, meningitis, bloodstream infections. PCV13 and PPSV23 for adults 65+. Also recommended for younger adults with chronic conditions (diabetes, heart/lung disease, immunocompromised). Different schedules based on age and risk factors. Side effects: soreness, mild fever.",
    "meningitis vaccine": "Meningococcal vaccines prevent bacterial meningitis and bloodstream infections. MenACWY recommended for adolescents (11-12 years, booster at 16). MenB for high-risk individuals or outbreaks. College students living in dorms should be vaccinated. Side effects: soreness, redness, mild fever.",
    "travel vaccines": "Required or recommended based on destination and activities. Common travel vaccines: Yellow fever (required for some countries), typhoid, Japanese encephalitis, hepatitis A, meningococcal. Consult travel medicine clinic 4-6 weeks before departure. Some vaccines require multiple doses or time to develop immunity.",
    "vaccine safety": "Vaccines undergo extensive testing in clinical trials before approval. Continuous safety monitoring through VAERS, VSD, and other systems. Serious adverse events are extremely rare. Common side effects: soreness, mild fever, fatigue. Benefits far outweigh risks. Severe allergic reactions occur in <1 per million doses.",
    "vaccine schedule": "CDC recommended immunization schedules optimize timing for best protection. Birth to 18 years: multiple vaccines at specific ages. Adult schedule: annual flu, Tdap every 10 years, age-specific vaccines (shingles 50+, pneumonia 65+). Catch-up schedules available for missed vaccines. Spacing between vaccines important for effectiveness.",
    "vaccine exemptions": "Medical exemptions for severe allergies (anaphylaxis) to vaccine components or severe immunodeficiency. Some states allow religious or philosophical exemptions for school entry. Medical exemptions require healthcare provider documentation. High vaccination rates (herd immunity) protect entire community, especially vulnerable individuals.",
    "vaccine myths": "Scientific evidence debunks common myths: Vaccines do NOT cause autism (multiple large studies confirm no link). Natural infection is not always safer than vaccination. Vaccines don't overwhelm immune system. Ingredients are safe in vaccine amounts. Vaccines prevent serious diseases, disabilities, and deaths. Benefits far outweigh minimal risks.",
    "vaccine ingredients": "Vaccines contain antigens (weakened/killed pathogens or parts), preservatives (prevent contamination), stabilizers (maintain effectiveness), and adjuvants (enhance immune response). All ingredients tested for safety. Thimerosal removed from childhood vaccines (except some flu vaccines). Aluminum adjuvants used safely for decades.",
    "vaccine effectiveness": "Vaccine effectiveness varies by vaccine and individual factors. Most childhood vaccines >90% effective. Flu vaccine effectiveness varies yearly (40-60% when well-matched). COVID-19 vaccines highly effective against severe disease. Effectiveness may wane over time, requiring boosters. Population-level protection through herd immunity.",

    # Neurological Conditions
    "migraine": "Severe headache with throbbing pain, often one-sided. Symptoms: nausea, vomiting, light/sound sensitivity. Triggers: stress, hormones, foods, weather changes. Treatment: pain medications, preventive medications, lifestyle modifications.",
    "epilepsy": "Neurological disorder causing recurrent seizures. Types: focal, generalized seizures. Treatment: anti-seizure medications, lifestyle modifications, surgery for drug-resistant cases. Seizure first aid: protect from injury, time seizure, call 102 if prolonged.",
    "alzheimer": "Progressive brain disorder causing memory loss and cognitive decline. Symptoms: memory problems, confusion, difficulty with daily tasks. Treatment: medications to slow progression, supportive care, safety modifications.",
    "parkinson": "Progressive nervous system disorder affecting movement. Symptoms: tremor, stiffness, slow movement, balance problems. Treatment: medications (levodopa), physical therapy, deep brain stimulation for advanced cases.",

    # Eye and Ear Conditions
    "glaucoma": "Eye condition with increased pressure damaging optic nerve. Often asymptomatic until advanced. Risk factors: age, family history, high eye pressure. Treatment: eye drops, laser therapy, surgery. Regular eye exams crucial for early detection.",
    "cataracts": "Clouding of eye lens causing vision problems. Symptoms: blurry vision, glare sensitivity, difficulty seeing at night. Treatment: surgery to replace clouded lens. Very common with aging, highly treatable.",
    "hearing loss": "Reduced ability to hear sounds. Types: conductive, sensorineural, mixed. Causes: aging, noise exposure, infections, medications. Treatment: hearing aids, cochlear implants, medical/surgical interventions depending on cause.",

    # Kidney and Urological Conditions
    "kidney stones": "Hard deposits formed in kidneys. Symptoms: severe flank pain, nausea, blood in urine, frequent urination. Treatment: pain management, increased fluids, medications to help pass stones, surgery for large stones.",
    "kidney disease": "Chronic condition with gradual loss of kidney function. Risk factors: diabetes, hypertension, family history. Symptoms: fatigue, swelling, changes in urination. Treatment: blood pressure control, diabetes management, dialysis, transplant for end-stage disease.",

    # Women's Health
    "pregnancy": "Prenatal care essential for healthy pregnancy. Take folic acid, avoid alcohol/smoking, regular checkups, healthy diet, appropriate exercise. Warning signs: severe nausea, bleeding, severe headaches, vision changes.",
    "menopause": "Natural transition when menstruation stops (average age 51). Symptoms: hot flashes, mood changes, sleep disturbances. Treatment: hormone therapy, lifestyle modifications, calcium/vitamin D for bone health.",
    "pcos": "Polycystic Ovary Syndrome affects hormone levels and ovulation. Symptoms: irregular periods, excess hair growth, acne, weight gain. Treatment: lifestyle changes, hormonal birth control, medications for insulin resistance.",
    "endometriosis": "Tissue similar to uterine lining grows outside uterus. Symptoms: pelvic pain, heavy periods, pain during intercourse. Treatment: pain medications, hormonal therapy, surgery for severe cases.",

    # Men's Health
    "prostate": "Walnut-sized gland in men. Benign prostatic hyperplasia (BPH) common with aging, causing urinary symptoms. Prostate cancer screening recommended starting age 50. Symptoms: difficulty urinating, frequent urination, blood in urine.",
    "erectile dysfunction": "Inability to achieve or maintain erection. Causes: cardiovascular disease, diabetes, psychological factors, medications. Treatment: lifestyle changes, medications (PDE5 inhibitors), counseling, medical devices.",
    "low testosterone": "Decreased male hormone levels with aging. Symptoms: fatigue, decreased libido, muscle loss, mood changes. Treatment: testosterone replacement therapy, lifestyle modifications, treatment of underlying conditions.",

    # Pediatric Health
    "childhood vaccines": "Essential for preventing serious diseases. Schedule includes: DTaP, polio, MMR, varicella, hepatitis B, Hib, pneumococcal, rotavirus, meningococcal. Follow CDC recommendations for timing and catch-up schedules.",
    "growth development": "Children grow at different rates. Monitor height, weight, developmental milestones. Concerns: significant deviations from growth curves, delayed milestones, behavioral issues. Regular pediatric checkups essential.",

    # Nutrition and Metabolism
    "vitamin deficiency": "Common deficiencies: Vitamin D (bone health), B12 (anemia, nerve function), iron (anemia), folate (pregnancy, anemia). Symptoms vary by vitamin. Treatment: dietary changes, supplements, addressing underlying causes.",
    "food allergies": "Immune reactions to specific foods. Common allergens: nuts, shellfish, eggs, milk, soy, wheat. Symptoms: hives, swelling, digestive issues, anaphylaxis. Treatment: avoidance, epinephrine for severe reactions, allergy testing.",

    # Sleep Disorders
    "sleep apnea": "Breathing repeatedly stops during sleep. Symptoms: loud snoring, gasping, daytime fatigue, morning headaches. Risk factors: obesity, neck circumference, age. Treatment: CPAP therapy, weight loss, oral appliances, surgery.",
    "insomnia": "Difficulty falling or staying asleep. Causes: stress, anxiety, medications, medical conditions, poor sleep habits. Treatment: sleep hygiene, cognitive behavioral therapy, medications if needed, addressing underlying causes.",

    # Emergency Conditions
    "chest pain": "Can indicate heart attack, especially with shortness of breath, nausea, sweating. Other causes: muscle strain, acid reflux, anxiety. SEEK IMMEDIATE CARE for severe, crushing chest pain or if you suspect heart attack.",
    "allergic reaction": "Immune system response to allergens. Mild: rash, itching. Severe (anaphylaxis): difficulty breathing, swelling, rapid pulse. EMERGENCY for anaphylaxis - use epinephrine, call 102. Avoid known allergens.",
    "concussion": "Mild traumatic brain injury from head impact. Symptoms: headache, confusion, dizziness, nausea, memory problems. Treatment: rest, gradual return to activities, avoid further head trauma. Seek care for worsening symptoms.",
    "burns": "Tissue damage from heat, chemicals, electricity. First-degree: red, painful. Second-degree: blisters. Third-degree: deep tissue damage. Treatment: cool water, pain relief, medical care for severe burns, tetanus shot if needed.",

    # Additional Respiratory Conditions
    "tuberculosis": "Bacterial infection primarily affecting lungs. Symptoms: persistent cough, blood in sputum, weight loss, night sweats, fever. Treatment: long-term antibiotics (6+ months). Prevention: vaccination (BCG), avoid close contact with active cases. Highly contagious when active.",
    "whooping cough": "Pertussis bacterial infection causing severe coughing fits. Symptoms: 'whooping' sound when breathing in, vomiting after coughing, exhaustion. Most dangerous in infants. Treatment: antibiotics, supportive care. Prevention: DTaP/Tdap vaccination.",
    "lung cancer": "Malignant tumor in lungs, often linked to smoking. Symptoms: persistent cough, chest pain, shortness of breath, weight loss, blood in sputum. Treatment: surgery, chemotherapy, radiation, targeted therapy. Prevention: avoid smoking, radon exposure.",
    "sleep apnea": "Breathing repeatedly stops during sleep. Symptoms: loud snoring, gasping, daytime fatigue, morning headaches. Risk factors: obesity, neck circumference, age. Treatment: CPAP therapy, weight loss, oral appliances, surgery.",
    "pulmonary embolism": "Blood clot in lung arteries. Symptoms: sudden shortness of breath, chest pain, rapid heartbeat, coughing up blood. EMERGENCY condition. Risk factors: prolonged immobility, surgery, pregnancy. Treatment: anticoagulants, thrombolytics.",

    # Additional Cardiovascular Conditions
    "atrial fibrillation": "Irregular, rapid heartbeat increasing stroke risk. Symptoms: palpitations, shortness of breath, fatigue, chest pain. Treatment: rate/rhythm control medications, anticoagulants, cardioversion, ablation. Regular monitoring essential.",
    "deep vein thrombosis": "Blood clot in deep veins, usually legs. Symptoms: leg pain, swelling, warmth, redness. Risk factors: immobility, surgery, pregnancy, cancer. Treatment: anticoagulants, compression stockings. Can lead to pulmonary embolism.",
    "varicose veins": "Enlarged, twisted veins, usually in legs. Symptoms: visible bulging veins, aching, heaviness, swelling. Treatment: compression stockings, lifestyle changes, sclerotherapy, surgery. Prevention: exercise, elevation, avoid prolonged standing.",
    "cardiomyopathy": "Disease of heart muscle affecting pumping ability. Types: dilated, hypertrophic, restrictive. Symptoms: shortness of breath, fatigue, swelling, irregular heartbeat. Treatment: medications, devices, lifestyle changes, sometimes transplant.",
    "pericarditis": "Inflammation of heart's outer lining. Symptoms: sharp chest pain (worse when lying down), fever, fatigue. Causes: viral infections, autoimmune conditions. Treatment: anti-inflammatory medications, rest, sometimes steroids.",

    # Additional Endocrine Conditions
    "hyperthyroidism": "Overactive thyroid gland producing excess hormones. Symptoms: weight loss, rapid heartbeat, anxiety, tremors, heat intolerance, bulging eyes. Causes: Graves' disease, toxic nodules. Treatment: antithyroid medications, radioiodine, surgery.",
    "hypothyroidism": "Underactive thyroid gland producing insufficient hormones. Symptoms: weight gain, fatigue, cold intolerance, depression, dry skin, hair loss. Causes: Hashimoto's disease, iodine deficiency. Treatment: thyroid hormone replacement (levothyroxine).",
    "addison disease": "Adrenal gland insufficiency. Symptoms: fatigue, weight loss, low blood pressure, skin darkening, salt cravings. Causes: autoimmune destruction, infections. Treatment: hormone replacement (cortisol, aldosterone). Life-threatening if untreated.",
    "cushing syndrome": "Excess cortisol hormone. Symptoms: weight gain (especially face/trunk), purple stretch marks, high blood sugar, mood changes. Causes: pituitary tumors, steroid medications. Treatment: surgery, medications, radiation.",
    "polycystic ovary syndrome": "PCOS affects hormone levels and ovulation. Symptoms: irregular periods, excess hair growth, acne, weight gain, insulin resistance. Treatment: lifestyle changes, hormonal birth control, metformin, fertility treatments.",

    # Additional Gastrointestinal Conditions
    "crohn disease": "Inflammatory bowel disease affecting any part of digestive tract. Symptoms: abdominal pain, diarrhea, weight loss, fatigue, blood in stool. Treatment: anti-inflammatory medications, immunosuppressants, biologics, surgery.",
    "ulcerative colitis": "Inflammatory bowel disease affecting colon and rectum. Symptoms: bloody diarrhea, abdominal pain, urgency, weight loss. Treatment: anti-inflammatory medications, immunosuppressants, biologics, surgery in severe cases.",
    "celiac disease": "Autoimmune reaction to gluten. Symptoms: diarrhea, abdominal pain, bloating, weight loss, fatigue, skin rash. Treatment: strict gluten-free diet for life. Complications: malnutrition, osteoporosis, increased cancer risk.",
    "pancreatitis": "Inflammation of pancreas. Acute: severe abdominal pain, nausea, vomiting, fever. Chronic: ongoing pain, diabetes, malabsorption. Causes: gallstones, alcohol, medications. Treatment: pain management, enzyme supplements, dietary changes.",
    "diverticulitis": "Inflammation of small pouches in colon wall. Symptoms: left lower abdominal pain, fever, nausea, changes in bowel habits. Treatment: antibiotics, liquid diet, sometimes surgery. Prevention: high-fiber diet, regular exercise.",
    "piles": "Hemorrhoids are swollen veins in the rectum and anus. Internal hemorrhoids: inside rectum, may bleed. External hemorrhoids: under skin around anus, can be painful and itchy. Symptoms: bleeding during bowel movements, itching, pain, swelling, lumps around anus. Causes: straining during bowel movements, chronic constipation/diarrhea, pregnancy, obesity, prolonged sitting. Treatment: high-fiber diet, stool softeners, topical creams, sitz baths, rubber band ligation, surgery for severe cases. Prevention: avoid straining, maintain regular bowel habits, exercise, adequate fiber and water intake.",
    "hemorrhoids": "Swollen and inflamed veins in rectum and anus. Types: Internal (inside rectum, grades I-IV), External (under anal skin). Symptoms: painless bleeding (internal), pain and swelling (external), itching, mucus discharge, feeling of incomplete evacuation. Risk factors: chronic constipation, pregnancy, aging, obesity, prolonged sitting/standing, heavy lifting. Treatment: Conservative: fiber supplements, stool softeners, topical treatments (hydrocortisone, witch hazel), sitz baths. Medical procedures: rubber band ligation, sclerotherapy, infrared coagulation, hemorrhoidectomy. Prevention: high-fiber diet (25-35g daily), adequate hydration, regular exercise, avoid prolonged sitting, proper toilet habits (don't strain or delay).",

    # Additional Mental Health Conditions
    "schizophrenia": "Chronic mental disorder affecting thinking, perception, behavior. Symptoms: hallucinations, delusions, disorganized thinking, social withdrawal. Treatment: antipsychotic medications, therapy, psychosocial support, rehabilitation.",
    "obsessive compulsive disorder": "OCD involves unwanted thoughts (obsessions) and repetitive behaviors (compulsions). Symptoms: excessive cleaning, checking, counting, arranging. Treatment: cognitive behavioral therapy (CBT), exposure therapy, SSRIs.",
    "panic disorder": "Recurrent panic attacks with intense fear and physical symptoms. Symptoms: rapid heartbeat, sweating, trembling, shortness of breath, feeling of doom. Treatment: therapy (CBT), medications (SSRIs, benzodiazepines), relaxation techniques.",
    "seasonal affective disorder": "SAD is depression related to seasonal changes, usually winter. Symptoms: depression, fatigue, oversleeping, weight gain, social withdrawal. Treatment: light therapy, antidepressants, therapy, vitamin D.",
    "borderline personality disorder": "BPD affects relationships, self-image, and emotions. Symptoms: fear of abandonment, unstable relationships, impulsivity, mood swings, self-harm. Treatment: dialectical behavior therapy (DBT), medications for symptoms.",

    # Additional Musculoskeletal Conditions
    "lupus": "Systemic autoimmune disease affecting multiple organs. Symptoms: joint pain, skin rash (butterfly rash), fatigue, fever, kidney problems. Treatment: NSAIDs, antimalarials, corticosteroids, immunosuppressants, biologics.",
    "rheumatoid arthritis": "Autoimmune arthritis causing joint inflammation. Symptoms: joint pain, swelling, stiffness (especially morning), fatigue, fever. Treatment: DMARDs, biologics, corticosteroids, physical therapy, joint protection.",
    "gout": "Arthritis caused by uric acid crystal deposits in joints. Symptoms: sudden, severe joint pain (often big toe), swelling, redness, warmth. Treatment: NSAIDs, colchicine, corticosteroids, uric acid-lowering medications.",
    "scoliosis": "Abnormal sideways curvature of spine. Symptoms: uneven shoulders/hips, back pain, breathing problems (severe cases). Treatment: observation, bracing, physical therapy, surgery for severe curves. Early detection important.",
    "herniated disc": "Spinal disc material presses on nerves. Symptoms: back/neck pain, numbness, tingling, weakness in arms/legs. Treatment: rest, physical therapy, medications, epidural injections, surgery if conservative treatment fails.",

    # Additional Skin Conditions
    "melanoma": "Most serious type of skin cancer. Symptoms: new moles or changes in existing moles (ABCDE: Asymmetry, Border, Color, Diameter, Evolving). Treatment: surgical removal, immunotherapy, targeted therapy. Prevention: sun protection, regular skin checks.",
    "vitiligo": "Autoimmune condition causing loss of skin pigment. Symptoms: white patches on skin, often symmetrical. Treatment: topical corticosteroids, calcineurin inhibitors, phototherapy, cosmetic camouflage. No cure, but treatments can help.",
    "shingles": "Reactivation of chickenpox virus causing painful rash. Symptoms: burning pain, tingling, followed by blistering rash in band pattern. Treatment: antiviral medications, pain management. Prevention: shingles vaccine for adults 50+.",
    "cellulitis": "Bacterial skin and soft tissue infection. Symptoms: red, swollen, warm, tender skin, fever, red streaking. Treatment: antibiotics (oral or IV), elevation, wound care. Seek immediate care for spreading infection or fever.",
    "hidradenitis suppurativa": "Chronic inflammatory skin condition affecting hair follicles. Symptoms: painful lumps, abscesses, scarring in armpits, groin, buttocks. Treatment: antibiotics, anti-inflammatory medications, surgery, lifestyle modifications.",

    # Additional Infectious Diseases
    "lyme disease": "Tick-borne bacterial infection. Early symptoms: bull's-eye rash, fever, headache, fatigue. Late symptoms: joint pain, neurological problems, heart issues. Treatment: antibiotics (doxycycline, amoxicillin). Prevention: tick avoidance, prompt removal.",
    "malaria": "Mosquito-borne parasitic infection. Symptoms: fever, chills, headache, nausea, vomiting, muscle pain. Can be life-threatening. Treatment: antimalarial medications. Prevention: mosquito control, prophylactic medications in endemic areas.",
    "dengue fever": "Mosquito-borne viral infection. Symptoms: high fever, severe headache, eye pain, muscle/joint pain, rash. Severe dengue can cause bleeding, organ failure. Treatment: supportive care, fluid management. Prevention: mosquito control.",
    "meningitis": "Inflammation of brain and spinal cord membranes. Symptoms: severe headache, neck stiffness, fever, sensitivity to light, confusion. MEDICAL EMERGENCY. Treatment: antibiotics (bacterial), supportive care (viral). Vaccination available.",
    "sepsis": "Life-threatening response to infection. Symptoms: fever, rapid heart rate, rapid breathing, confusion, low blood pressure. MEDICAL EMERGENCY. Treatment: antibiotics, IV fluids, vasopressors, organ support. Early recognition crucial.",

    # Additional Neurological Conditions
    "multiple sclerosis": "Autoimmune disease affecting central nervous system. Symptoms: fatigue, numbness, weakness, vision problems, balance issues, cognitive changes. Treatment: disease-modifying therapies, symptom management, rehabilitation.",
    "huntington disease": "Inherited disorder causing progressive breakdown of nerve cells. Symptoms: involuntary movements, emotional problems, cognitive decline. No cure. Treatment: symptom management, supportive care, genetic counseling.",
    "amyotrophic lateral sclerosis": "ALS (Lou Gehrig's disease) affects motor neurons. Symptoms: muscle weakness, twitching, difficulty speaking/swallowing, breathing problems. Progressive and fatal. Treatment: supportive care, riluzole, edaravone.",
    "bell palsy": "Sudden weakness or paralysis of facial muscles on one side. Symptoms: drooping face, difficulty closing eye, drooling, loss of taste. Often improves spontaneously. Treatment: corticosteroids, eye protection, physical therapy.",
    "trigeminal neuralgia": "Severe facial pain along trigeminal nerve. Symptoms: sudden, electric shock-like pain triggered by light touch. Treatment: anticonvulsants (carbamazepine), baclofen, surgery for refractory cases.",

    # Additional Eye and Ear Conditions
    "macular degeneration": "Age-related deterioration of central retina. Symptoms: blurred central vision, difficulty reading, dark spots. Types: dry (more common) and wet. Treatment: vitamins, anti-VEGF injections, laser therapy.",
    "diabetic retinopathy": "Diabetes-related damage to retinal blood vessels. Symptoms: blurred vision, floaters, dark areas, vision loss. Treatment: blood sugar control, laser therapy, anti-VEGF injections, vitrectomy.",
    "meniere disease": "Inner ear disorder affecting hearing and balance. Symptoms: vertigo episodes, hearing loss, tinnitus, ear fullness. Treatment: dietary changes (low sodium), diuretics, vestibular rehabilitation, surgery in severe cases.",
    "tinnitus": "Perception of ringing or buzzing in ears. Causes: hearing loss, medications, ear infections, TMJ. Treatment: hearing aids, sound therapy, tinnitus retraining therapy, addressing underlying causes.",
    "stye": "Bacterial infection of eyelid gland. Symptoms: red, painful bump on eyelid, swelling, tenderness. Treatment: warm compresses, antibiotic ointments, sometimes drainage. Usually resolves within a week.",

    # Additional Kidney and Urological Conditions
    "polycystic kidney disease": "PKD causes fluid-filled cysts in kidneys. Symptoms: high blood pressure, back/side pain, kidney stones, urinary tract infections. Complications: kidney failure, liver cysts. Treatment: blood pressure control, pain management.",
    "bladder cancer": "Malignant tumor in bladder lining. Symptoms: blood in urine, frequent urination, painful urination, pelvic pain. Risk factors: smoking, chemical exposure. Treatment: surgery, chemotherapy, immunotherapy, radiation.",
    "prostatitis": "Inflammation of prostate gland. Symptoms: pelvic pain, difficult/painful urination, flu-like symptoms. Types: acute bacterial, chronic bacterial, chronic pelvic pain syndrome. Treatment: antibiotics, alpha-blockers, pain management.",
    "interstitial cystitis": "Chronic bladder condition causing pain and pressure. Symptoms: pelvic pain, frequent urination, urgency, pain during intercourse. Treatment: dietary modifications, bladder instillations, medications, physical therapy.",
    "nephrotic syndrome": "Kidney disorder causing protein loss in urine. Symptoms: swelling (especially face/legs), foamy urine, weight gain, fatigue. Causes: diabetes, lupus, infections. Treatment: corticosteroids, immunosuppressants, diuretics.",

    # Additional Women's Health Conditions
    "fibroids": "Noncancerous uterine tumors. Symptoms: heavy menstrual bleeding, pelvic pain, frequent urination, constipation. Treatment: observation, medications (hormonal), uterine artery embolization, myomectomy, hysterectomy.",
    "ovarian cysts": "Fluid-filled sacs on ovaries. Most are harmless and resolve spontaneously. Symptoms: pelvic pain, bloating, irregular periods. Complications: rupture, torsion. Treatment: observation, hormonal contraceptives, surgery if large/persistent.",
    "cervical cancer": "Cancer of cervix, often caused by HPV. Symptoms: abnormal vaginal bleeding, pelvic pain, pain during intercourse. Prevention: HPV vaccination, regular Pap smears. Treatment: surgery, radiation, chemotherapy.",
    "gestational diabetes": "Diabetes developing during pregnancy. Symptoms: usually none, detected by screening. Risks: large baby, preterm birth, preeclampsia. Treatment: diet, exercise, blood sugar monitoring, sometimes insulin.",
    "preeclampsia": "Pregnancy complication with high blood pressure and protein in urine. Symptoms: headaches, vision changes, upper abdominal pain, swelling. Serious condition requiring immediate medical care. Treatment: delivery, blood pressure management.",

    # Menstrual Health and Periods
    "menstruation": "Normal monthly shedding of uterine lining in women of reproductive age. Typical cycle: 21-35 days, bleeding lasts 3-7 days. Average blood loss: 30-40ml. Controlled by hormones (estrogen, progesterone). First period (menarche) typically ages 10-15. Menopause ends menstruation around age 51. Normal variations in flow, timing, and symptoms are common.",
    "periods": "Monthly menstrual bleeding is normal part of reproductive cycle. Normal cycle length: 21-35 days. Normal period duration: 3-7 days. Flow varies: light to heavy is normal. Color changes: bright red to dark brown normal. Symptoms may include cramping, bloating, mood changes, breast tenderness. Track cycles to understand your normal pattern.",
    "menstrual cycle": "Monthly hormonal cycle preparing body for pregnancy. Phases: Menstrual (days 1-5), Follicular (days 1-13), Ovulation (around day 14), Luteal (days 15-28). Hormones involved: FSH, LH, estrogen, progesterone. Cycle length varies 21-35 days. Ovulation typically occurs mid-cycle. Understanding your cycle helps with family planning and health monitoring.",
    "irregular periods": "Menstrual cycles outside normal 21-35 day range or unpredictable timing. Causes: stress, weight changes, exercise, PCOS, thyroid disorders, perimenopause, medications. When to see doctor: cycles shorter than 21 days or longer than 35 days, missing periods (not pregnant), bleeding between periods, severe pain. Treatment depends on underlying cause.",
    "heavy periods": "Menorrhagia - excessive menstrual bleeding. Signs: soaking pad/tampon every hour, periods lasting >7 days, clots larger than quarter, bleeding between periods, anemia symptoms. Causes: fibroids, polyps, PCOS, thyroid disorders, bleeding disorders, medications. Treatment: hormonal therapy, NSAIDs, surgical options (endometrial ablation, hysterectomy).",
    "painful periods": "Dysmenorrhea - painful menstrual cramps. Primary: normal cramping without underlying condition. Secondary: pain from medical condition (endometriosis, fibroids). Symptoms: lower abdominal/back pain, nausea, headache, diarrhea. Treatment: NSAIDs, heat therapy, exercise, hormonal birth control, treating underlying conditions.",
    "missed periods": "Amenorrhea - absence of menstruation. Primary: no periods by age 15. Secondary: missing periods for 3+ months in previously menstruating woman. Causes: pregnancy (most common), stress, weight loss/gain, excessive exercise, PCOS, thyroid disorders, medications. See doctor if missing periods and not pregnant.",
    "pms": "Premenstrual Syndrome - physical and emotional symptoms before periods. Symptoms: mood swings, irritability, bloating, breast tenderness, food cravings, fatigue, headaches. Occurs 1-2 weeks before period. Treatment: lifestyle changes (diet, exercise, stress management), calcium/magnesium supplements, hormonal birth control, antidepressants for severe cases.",
    "pmdd": "Premenstrual Dysphoric Disorder - severe form of PMS significantly impacting daily life. Symptoms: severe mood changes, anxiety, depression, anger, difficulty concentrating, physical symptoms. Occurs luteal phase of cycle. Diagnosis requires specific criteria. Treatment: antidepressants (SSRIs), hormonal therapy, lifestyle modifications, counseling.",
    "menstrual products": "Various options for managing menstrual flow. Disposable: pads (external), tampons (internal). Reusable: menstrual cups (internal), cloth pads, period underwear. Choose based on comfort, lifestyle, flow. Change regularly to prevent infection. Toxic Shock Syndrome risk with tampons - follow usage guidelines. Consider environmental impact and cost when choosing.",
    "menstrual hygiene": "Important practices during menstruation. Change products regularly: pads every 4-6 hours, tampons every 4-8 hours, cups every 12 hours. Wash hands before/after changing products. Clean genital area with water, avoid douching. Wear breathable underwear. Track cycle and symptoms. Seek medical care for unusual symptoms or concerns.",
    "first period": "Menarche - first menstrual period typically occurs ages 10-15. Signs approaching: breast development, growth spurt, body hair, vaginal discharge. First periods often irregular for 1-2 years. Prepare with supplies, education about normal changes. Discuss with parent/guardian or healthcare provider. Normal part of growing up and becoming capable of reproduction.",
    "menopause transition": "Perimenopause - transition period before menopause when periods become irregular. Typically begins 40s-early 50s. Symptoms: irregular periods, hot flashes, mood changes, sleep problems, vaginal dryness. Periods may be heavier, lighter, or skip months. Pregnancy still possible. Menopause confirmed after 12 months without periods.",
    "ovulation": "Release of egg from ovary, typically mid-cycle (day 14 of 28-day cycle). Signs: cervical mucus changes (clear, stretchy), slight temperature rise, mild pelvic pain (mittelschmerz), increased libido. Fertile window: 5 days before through day of ovulation. Important for conception timing. Ovulation predictor kits available for tracking.",
    "endometriosis": "Condition where uterine lining grows outside uterus. Symptoms: severe menstrual cramps, heavy periods, pain during intercourse, infertility, chronic pelvic pain. May worsen over time. Diagnosis: pelvic exam, ultrasound, laparoscopy. Treatment: pain management, hormonal therapy, surgery. Can significantly impact quality of life and fertility.",
    "adenomyosis": "Uterine lining grows into muscle wall of uterus. Symptoms: heavy, painful periods, enlarged uterus, chronic pelvic pain. Often occurs in women 40s-50s who have had children. Diagnosis: MRI, ultrasound, biopsy. Treatment: pain management, hormonal therapy, uterine artery embolization, hysterectomy for severe cases.",
    "uterine fibroids": "Noncancerous growths in uterus. Symptoms: heavy menstrual bleeding, prolonged periods, pelvic pressure, frequent urination, constipation, back pain. Size and location affect symptoms. Diagnosis: pelvic exam, ultrasound, MRI. Treatment: observation, medications, minimally invasive procedures, surgery depending on symptoms and fertility desires.",
    "ovarian cysts": "Fluid-filled sacs on ovaries. Most are functional and resolve spontaneously. Symptoms: pelvic pain, bloating, irregular periods, pain during intercourse. Complications: rupture, torsion (twisting). Diagnosis: pelvic exam, ultrasound. Treatment: observation, hormonal birth control, surgery for large/persistent cysts or complications.",
    "pcos": "Polycystic Ovary Syndrome affects hormone levels and ovulation. Symptoms: irregular/absent periods, excess hair growth (hirsutism), acne, weight gain, insulin resistance, difficulty getting pregnant. Diagnosis: clinical symptoms, blood tests, ultrasound. Treatment: lifestyle changes, hormonal birth control, metformin, fertility treatments, hair removal methods.",

    # Additional Men's Health Conditions
    "testicular cancer": "Cancer in testicles, most common in young men. Symptoms: testicular lump, swelling, pain, heaviness. Treatment: surgery (orchiectomy), chemotherapy, radiation. High cure rate when detected early. Monthly self-exams recommended.",
    "benign prostatic hyperplasia": "BPH is enlarged prostate common with aging. Symptoms: frequent urination, weak stream, difficulty starting urination, incomplete emptying. Treatment: alpha-blockers, 5-alpha reductase inhibitors, surgery.",
    "varicocele": "Enlarged veins in scrotum. Symptoms: scrotal swelling, dull ache, fertility problems. Treatment: observation, surgical repair if causing pain or fertility issues. Most common cause of male infertility.",
    "gynecomastia": "Enlarged breast tissue in males. Causes: hormonal changes, medications, medical conditions. Usually benign. Treatment: address underlying cause, surgery for persistent cases causing distress.",
    "male pattern baldness": "Androgenetic alopecia caused by genetics and hormones. Symptoms: receding hairline, crown thinning. Treatment: minoxidil, finasteride, hair transplantation, lifestyle modifications.",

    # Medication and Pill Information
    "medication safety": "Essential guidelines for safe medication use. Always take as prescribed by healthcare provider. Read labels carefully for dosage, timing, and interactions. Store medications properly (temperature, light, moisture). Keep original containers with labels. Don't share medications with others. Complete full course of antibiotics. Report side effects to healthcare provider. Keep updated medication list including supplements. Dispose safely through pharmacy take-back programs. Check expiration dates regularly.",
    "pill identification": "If you find unknown pills, use pill identifier tools or consult pharmacist. Never take unidentified medications. Look for imprints, colors, shapes, and sizes. Contact poison control if accidental ingestion occurs. Keep medications in original labeled containers to avoid confusion.",
    "drug interactions": "Medications can interact with other drugs, foods, or supplements. Types: drug-drug interactions (medications affecting each other), drug-food interactions (food affecting absorption), drug-supplement interactions. Always inform healthcare providers of ALL medications and supplements you take. Use one pharmacy when possible for interaction screening. Common interactions: blood thinners with aspirin, antibiotics with birth control, grapefruit with certain medications.",
    "side effects": "Medication side effects are unwanted effects that may occur. Common side effects: nausea, dizziness, drowsiness, headache, upset stomach. Serious side effects require immediate medical attention: difficulty breathing, severe rash, swelling, chest pain, severe dizziness. Report all side effects to healthcare provider. Don't stop medications without consulting provider. Some side effects improve with time as body adjusts.",
    "prescription drugs": "Medications requiring doctor's prescription for safety and effectiveness. Follow prescribed dosage and schedule exactly. Don't adjust dose without consulting provider. Don't stop abruptly unless instructed. Refill before running out. Store securely, especially controlled substances. Don't share with others. Bring medication list to all medical appointments.",
    "over the counter": "OTC medications available without prescription. Still can have side effects and interactions. Read labels carefully for ingredients, dosage, warnings. Follow age-appropriate dosing. Don't exceed recommended dose or duration. Consult pharmacist or healthcare provider if unsure. Common OTC categories: pain relievers, cold/flu medications, antacids, allergy medications, topical treatments.",
    "antibiotics": "Medications that fight bacterial infections. Don't work against viruses (colds, flu). Take exactly as prescribed, complete full course even if feeling better. Don't save leftover antibiotics or share with others. Take with or without food as directed. Common side effects: upset stomach, diarrhea, yeast infections. Resistance develops when not used properly. Probiotics may help maintain gut health during treatment.",
    "pain medication": "Medications for pain relief. Types: acetaminophen (Tylenol), NSAIDs (ibuprofen, naproxen), opioids (for severe pain). Follow dosing instructions carefully. Don't exceed maximum daily doses. NSAIDs can cause stomach upset, take with food. Acetaminophen can cause liver damage if overdosed. Opioids are addictive, use only as prescribed. Alternative pain management: ice, heat, physical therapy, relaxation techniques.",
    "blood pressure medication": "Medications to control hypertension. Types: ACE inhibitors, ARBs, beta-blockers, calcium channel blockers, diuretics. Take consistently at same time daily. Don't skip doses or stop suddenly. Monitor blood pressure regularly. Side effects vary by type: dizziness, fatigue, cough, swelling. Lifestyle changes enhance effectiveness: diet, exercise, weight management, stress reduction.",
    "diabetes medication": "Medications to control blood sugar. Types: insulin, metformin, sulfonylureas, SGLT2 inhibitors, GLP-1 agonists. Take with meals as directed. Monitor blood sugar levels regularly. Recognize signs of low blood sugar (hypoglycemia): shakiness, sweating, confusion, rapid heartbeat. Always carry glucose tablets or snacks. Rotate insulin injection sites. Store insulin properly (refrigerate, don't freeze).",
    "heart medication": "Medications for heart conditions. Types: beta-blockers, ACE inhibitors, statins, blood thinners, diuretics. Take consistently as prescribed. Monitor for side effects: dizziness, fatigue, bleeding (blood thinners), muscle pain (statins). Regular lab tests may be needed. Don't stop suddenly without medical supervision. Lifestyle changes complement medication: diet, exercise, smoking cessation.",
    "mental health medication": "Medications for psychiatric conditions. Types: antidepressants, antianxiety, mood stabilizers, antipsychotics. May take weeks to show full effect. Don't stop suddenly - may cause withdrawal symptoms. Side effects vary: drowsiness, weight changes, sexual side effects. Regular follow-up with prescriber important. Therapy often combined with medication for best results.",
    "birth control pills": "Oral contraceptives containing hormones to prevent pregnancy. Take daily at same time for effectiveness. Missed pills reduce effectiveness - follow package instructions. Side effects: nausea, breast tenderness, mood changes, breakthrough bleeding. Serious risks: blood clots (rare), especially in smokers over 35. Doesn't protect against STDs. Many types available - discuss options with healthcare provider.",
    "vitamin supplements": "Nutritional supplements to support health. Not regulated like medications - quality varies. Most people get adequate vitamins from balanced diet. Certain groups may need supplements: pregnant women (folic acid), vegans (B12), limited sun exposure (vitamin D). Can interact with medications. Fat-soluble vitamins (A, D, E, K) can accumulate and cause toxicity. Water-soluble vitamins (B, C) excess usually excreted.",
    "herbal supplements": "Plant-based products used for health purposes. Not regulated like medications - purity and potency vary. Can interact with prescription medications. Common herbs: echinacea (immune support), ginkgo (memory), St. John's wort (mood - interacts with many drugs), turmeric (inflammation). Consult healthcare provider before use, especially with medical conditions or other medications.",
    "medication storage": "Proper storage ensures medication effectiveness and safety. Store in cool, dry place unless refrigeration required. Avoid bathroom medicine cabinets (humidity) and cars (temperature extremes). Keep in original containers with labels. Child-resistant caps for safety. Check expiration dates regularly. Dispose expired medications safely through pharmacy take-back programs or FDA guidelines.",
    "pill splitting": "Dividing tablets to adjust dose or save money. Only split pills specifically designed for splitting (scored tablets). Use proper pill splitter, not knives. Split only when recommended by healthcare provider or pharmacist. Some medications should never be split: extended-release, enteric-coated, capsules, very small pills. Uneven splitting can cause dose variations.",
    "medication adherence": "Taking medications exactly as prescribed. Poor adherence leads to treatment failure and complications. Strategies: pill organizers, alarms, routine timing, understanding importance, addressing side effects. Barriers: cost, side effects, complex regimens, forgetfulness. Communicate with healthcare provider about difficulties. Pharmacy services: blister packing, medication synchronization, adherence programs.",

    # Additional Medical Conditions and Specialties
    "anemia": "Condition with insufficient healthy red blood cells or hemoglobin. Types: iron-deficiency (most common), vitamin B12 deficiency, chronic disease anemia, sickle cell anemia. Symptoms: fatigue, weakness, pale skin, shortness of breath, cold hands/feet, brittle nails. Treatment: iron supplements, dietary changes, treating underlying causes, blood transfusions in severe cases.",
    "leukemia": "Cancer of blood-forming tissues including bone marrow. Types: acute lymphoblastic (ALL), acute myeloid (AML), chronic lymphocytic (CLL), chronic myeloid (CML). Symptoms: frequent infections, easy bruising/bleeding, fatigue, swollen lymph nodes, weight loss. Treatment: chemotherapy, radiation, stem cell transplant, targeted therapy.",
    "lymphoma": "Cancer of lymphatic system. Types: Hodgkin's and non-Hodgkin's lymphoma. Symptoms: swollen lymph nodes, fever, night sweats, weight loss, fatigue, chest pain. Treatment: chemotherapy, radiation therapy, immunotherapy, stem cell transplant. Prognosis varies by type and stage.",
    "hemophilia": "Inherited bleeding disorder with impaired blood clotting. Types: Hemophilia A (factor VIII deficiency), Hemophilia B (factor IX deficiency). Symptoms: excessive bleeding, easy bruising, joint bleeding, prolonged bleeding after injury. Treatment: clotting factor replacement therapy, medications to promote clotting.",
    "thalassemia": "Inherited blood disorder affecting hemoglobin production. Types: alpha and beta thalassemia, ranging from minor to major. Symptoms: fatigue, weakness, pale skin, slow growth, bone deformities. Treatment: blood transfusions, iron chelation therapy, bone marrow transplant for severe cases.",
    "sickle cell disease": "Inherited red blood cell disorder causing cells to become sickle-shaped. Symptoms: pain crises, anemia, infections, organ damage, stroke risk. Complications: acute chest syndrome, priapism, leg ulcers. Treatment: pain management, hydroxyurea, blood transfusions, bone marrow transplant.",
    "hemochromatosis": "Iron overload disorder causing excess iron absorption. Symptoms: fatigue, joint pain, abdominal pain, skin darkening, diabetes, heart problems. Complications: liver cirrhosis, heart failure, diabetes. Treatment: phlebotomy (blood removal), iron chelation therapy, dietary modifications.",
    "thrombocytopenia": "Low platelet count affecting blood clotting. Causes: autoimmune destruction, medications, infections, cancer treatments. Symptoms: easy bruising, petechiae (small red spots), excessive bleeding, heavy menstrual periods. Treatment: corticosteroids, immunoglobulins, platelet transfusions, splenectomy.",
    
    "appendicitis": "Inflammation of appendix requiring emergency surgery. Symptoms: abdominal pain starting near navel, moving to lower right, nausea, vomiting, fever, loss of appetite. Pain worsens with movement, coughing, sneezing. MEDICAL EMERGENCY - can rupture causing peritonitis. Treatment: appendectomy (surgical removal).",
    "gallbladder disease": "Conditions affecting gallbladder including stones, inflammation. Symptoms: severe upper right abdominal pain, nausea, vomiting, especially after fatty meals. Complications: cholecystitis, pancreatitis, bile duct obstruction. Treatment: dietary changes, medications, laparoscopic cholecystectomy.",
    "kidney failure": "Acute or chronic loss of kidney function. Acute: sudden onset from dehydration, medications, infections. Chronic: gradual loss from diabetes, hypertension, polycystic kidney disease. Symptoms: decreased urination, swelling, fatigue, nausea. Treatment: dialysis, kidney transplant, treating underlying causes.",
    "liver disease": "Various conditions affecting liver function. Causes: hepatitis, alcohol, fatty liver, autoimmune conditions, genetic disorders. Symptoms: jaundice, abdominal swelling, fatigue, nausea, dark urine. Complications: cirrhosis, liver failure, portal hypertension. Treatment: depends on cause, may require transplant.",
    
    "osteoarthritis": "Degenerative joint disease from cartilage breakdown. Most common in knees, hips, hands, spine. Symptoms: joint pain, stiffness, swelling, decreased range of motion. Risk factors: age, obesity, joint injury, genetics. Treatment: pain management, physical therapy, weight loss, joint replacement surgery.",
    "bursitis": "Inflammation of fluid-filled sacs (bursae) cushioning joints. Common sites: shoulder, elbow, hip, knee. Symptoms: joint pain, swelling, tenderness, limited movement. Causes: repetitive motion, injury, infection. Treatment: rest, ice, anti-inflammatory medications, corticosteroid injections, physical therapy.",
    "tendonitis": "Inflammation of tendons connecting muscles to bones. Common sites: shoulder (rotator cuff), elbow (tennis/golfer's elbow), wrist, knee, ankle. Symptoms: pain, swelling, stiffness. Treatment: rest, ice, anti-inflammatory medications, physical therapy, gradual return to activity.",
    "plantar fasciitis": "Inflammation of tissue connecting heel bone to toes. Symptoms: sharp heel pain, especially first steps in morning or after sitting. Risk factors: age, obesity, high arches, tight calf muscles. Treatment: stretching, orthotics, physical therapy, corticosteroid injections, surgery for severe cases.",
    
    "cataracts": "Clouding of eye lens causing vision problems. Symptoms: blurry vision, glare sensitivity, difficulty seeing at night, colors appearing faded. Risk factors: aging, diabetes, smoking, UV exposure. Treatment: surgery to replace clouded lens with artificial lens. Very common with aging, highly treatable.",
    "macular degeneration": "Age-related deterioration of central retina affecting central vision. Types: dry (more common, gradual) and wet (rapid, severe). Symptoms: blurred central vision, difficulty reading, dark spots in vision. Treatment: vitamins (AREDS formula), anti-VEGF injections for wet type, low vision aids.",
    "diabetic retinopathy": "Diabetes-related damage to retinal blood vessels. Stages: mild, moderate, severe nonproliferative, and proliferative. Symptoms: blurred vision, floaters, dark areas, vision loss. Treatment: blood sugar control, laser therapy, anti-VEGF injections, vitrectomy surgery.",
    "dry eye syndrome": "Insufficient tear production or poor tear quality. Symptoms: burning, stinging, scratchy feeling, light sensitivity, blurred vision. Causes: aging, medications, medical conditions, environmental factors. Treatment: artificial tears, prescription eye drops, punctal plugs, lifestyle modifications.",
    
    "vertigo": "Sensation of spinning or dizziness. Types: peripheral (inner ear) and central (brain). Common causes: benign paroxysmal positional vertigo (BPPV), Meniere's disease, vestibular neuritis. Symptoms: spinning sensation, nausea, balance problems. Treatment: canalith repositioning, medications, vestibular rehabilitation.",
    "tinnitus": "Perception of ringing, buzzing, or other sounds in ears. Causes: hearing loss, ear infections, medications, TMJ, blood vessel disorders. Types: subjective (only you hear) and objective (others can hear). Treatment: hearing aids, sound therapy, tinnitus retraining therapy, treating underlying causes.",
    "hearing loss": "Reduced ability to hear sounds. Types: conductive (outer/middle ear), sensorineural (inner ear/nerve), mixed. Causes: aging, noise exposure, infections, medications, genetics. Treatment: hearing aids, cochlear implants, medical/surgical interventions, assistive listening devices.",
    
    "chronic fatigue syndrome": "Complex disorder characterized by extreme fatigue not improved by rest. Symptoms: severe fatigue, post-exertional malaise, sleep problems, cognitive difficulties, muscle/joint pain. Diagnosis: exclusion of other conditions. Treatment: symptom management, graded exercise, cognitive behavioral therapy, medications for symptoms.",
    "fibromyalgia": "Chronic condition causing widespread muscle pain and tenderness. Symptoms: muscle pain, fatigue, sleep problems, cognitive difficulties ('fibro fog'), headaches. Tender points at specific body locations. Treatment: medications (pregabalin, duloxetine), exercise, stress management, sleep hygiene.",
    "chronic pain": "Persistent pain lasting longer than 3-6 months. Types: nociceptive (tissue damage), neuropathic (nerve damage), mixed. Causes: injury, surgery, arthritis, nerve damage, unknown. Treatment: multimodal approach including medications, physical therapy, psychological support, interventional procedures.",
    
    "autoimmune diseases": "Conditions where immune system attacks body's own tissues. Examples: rheumatoid arthritis, lupus, multiple sclerosis, type 1 diabetes, inflammatory bowel disease. Symptoms vary by condition but may include fatigue, joint pain, skin rashes, organ dysfunction. Treatment: immunosuppressive medications, symptom management.",
    "inflammatory bowel disease": "Chronic inflammation of digestive tract. Types: Crohn's disease (any part of GI tract) and ulcerative colitis (colon/rectum only). Symptoms: abdominal pain, diarrhea, weight loss, fatigue, blood in stool. Treatment: anti-inflammatory medications, immunosuppressants, biologics, surgery.",
    
    "sleep disorders": "Conditions affecting sleep quality or quantity. Types: insomnia, sleep apnea, restless leg syndrome, narcolepsy, circadian rhythm disorders. Symptoms: difficulty falling/staying asleep, excessive daytime sleepiness, abnormal behaviors during sleep. Treatment: sleep hygiene, CPAP therapy, medications, behavioral therapy.",
    "restless leg syndrome": "Neurological disorder causing uncomfortable leg sensations and urge to move. Symptoms: creeping, crawling, tingling sensations in legs, worse at rest/evening, relieved by movement. Treatment: lifestyle changes, iron supplements if deficient, dopamine agonists, anticonvulsants.",
    "narcolepsy": "Neurological disorder affecting sleep-wake cycles. Symptoms: excessive daytime sleepiness, sudden sleep attacks, cataplexy (muscle weakness), sleep paralysis, hallucinations. Treatment: stimulant medications, sodium oxybate, lifestyle modifications, scheduled naps.",
    
    "eating disorders": "Serious mental health conditions involving eating behaviors. Types: anorexia nervosa (restriction), bulimia nervosa (binge-purge), binge eating disorder. Symptoms: extreme food restriction, binge eating, purging behaviors, body image distortion. Treatment: therapy, nutritional counseling, medical monitoring, medications.",
    "substance abuse": "Harmful use of drugs or alcohol affecting health and functioning. Signs: tolerance, withdrawal, inability to control use, neglecting responsibilities, continued use despite problems. Treatment: detoxification, rehabilitation programs, counseling, support groups, medications for addiction.",
    
    "sexually transmitted infections": "Infections spread through sexual contact. Common STIs: chlamydia, gonorrhea, syphilis, herpes, HPV, HIV. Symptoms: may be asymptomatic, discharge, burning urination, sores, rashes. Prevention: safe sex practices, regular testing, vaccination (HPV, hepatitis B). Treatment: antibiotics, antivirals.",
    "hiv aids": "HIV attacks immune system, AIDS is advanced stage. Transmission: unprotected sex, blood contact, mother to child. Symptoms: flu-like illness initially, then asymptomatic period, eventually opportunistic infections. Treatment: antiretroviral therapy (ART), prevention: PrEP, safe sex practices.",
    
    "cancer screening": "Tests to detect cancer before symptoms appear. Mammograms (breast), Pap smears (cervical), colonoscopy (colorectal), PSA (prostate), skin checks (melanoma). Follow age and risk-appropriate guidelines. Early detection improves treatment outcomes and survival rates.",
    "breast cancer": "Most common cancer in women, can occur in men. Symptoms: breast lump, skin changes, nipple discharge, breast pain. Risk factors: age, family history, genetics (BRCA), hormones. Treatment: surgery, chemotherapy, radiation, hormone therapy, targeted therapy. Regular screening important.",
    "prostate cancer": "Common cancer in men, usually slow-growing. Symptoms: urinary problems, blood in urine/semen, pelvic pain. Risk factors: age, race, family history. Screening: PSA test, digital rectal exam. Treatment: active surveillance, surgery, radiation, hormone therapy.",
    "colorectal cancer": "Cancer of colon or rectum. Symptoms: changes in bowel habits, blood in stool, abdominal pain, weight loss. Risk factors: age, family history, inflammatory bowel disease, diet. Screening: colonoscopy starting age 45-50. Treatment: surgery, chemotherapy, radiation.",
    
    "first aid": "Immediate care for injuries or sudden illness. Basic skills: CPR, choking relief (Heimlich maneuver), bleeding control, burn treatment, fracture immobilization. Emergency supplies: bandages, antiseptic, pain relievers, emergency numbers. Training recommended for everyone. Call 102 for serious emergencies.",
    "cpr": "Cardiopulmonary resuscitation for cardiac arrest. Steps: check responsiveness, call 102, chest compressions (30), rescue breaths (2), repeat. Compression rate: 100-120 per minute, depth: 2 inches. AED use if available. Hands-only CPR acceptable if untrained in rescue breathing.",
    "choking": "Airway obstruction preventing breathing. Signs: inability to speak/cough, clutching throat, blue skin. Treatment: Heimlich maneuver (abdominal thrusts), back blows for infants. If unconscious, begin CPR. Prevention: cut food into small pieces, supervise children, avoid talking while eating."
}

def get_medical_response(user_input):
    """Enhanced pattern matching for comprehensive medical queries"""
    user_input = user_input.lower()
    
    # Check for exact condition matches first
    for condition, response in medical_responses.items():
        if condition in user_input:
            return f"**{condition.title()} Information:**\n\n{response}"
    
    # Check for symptom-related queries
    symptom_keywords = {
        "headache": ["head pain", "migraine", "head ache", "headaches"],
        "nausea": ["sick to stomach", "queasy", "vomiting", "throw up"],
        "fatigue": ["tired", "exhausted", "weakness", "energy"],
        "pain": ["hurt", "ache", "sore", "painful"],
        "shortness of breath": ["can't breathe", "breathing problem", "breathless"],
        "dizziness": ["dizzy", "lightheaded", "vertigo"],
        "rash": ["skin irritation", "red spots", "itchy skin"],
        "swelling": ["swollen", "puffy", "inflammation"]
    }
    
    for symptom, keywords in symptom_keywords.items():
        if any(keyword in user_input for keyword in keywords + [symptom]):
            return f"**Regarding {symptom}:** This symptom can have various causes. Common reasons include infections, allergies, stress, or underlying conditions. If persistent, severe, or accompanied by other concerning symptoms, please consult a healthcare provider for proper evaluation and treatment."
    
    # Health tips and general wellness
    if any(word in user_input for word in ["healthy", "wellness", "tips", "advice"]):
        return """**General Health Tips:**
        
• **Exercise regularly:** 150 minutes of moderate activity weekly
• **Eat balanced diet:** Include fruits, vegetables, whole grains, lean proteins
• **Stay hydrated:** 8 glasses of water daily
• **Get adequate sleep:** 7-9 hours nightly for adults
• **Manage stress:** Practice relaxation techniques, meditation
• **Avoid smoking and limit alcohol**
• **Regular checkups:** Preventive care and screenings
• **Maintain healthy weight**
• **Practice good hygiene:** Hand washing, dental care
• **Stay up to date with vaccinations**"""

    # First aid and emergency queries
    emergency_keywords = ["first aid", "cpr", "choking", "emergency", "urgent", "102", "ambulance"]
    if any(keyword in user_input for keyword in emergency_keywords):
        return """**EMERGENCY & FIRST AID INFORMATION:**

**🚨 CALL 102 IMMEDIATELY FOR:**
• **Cardiac Arrest**: No pulse, not breathing, unconscious
• **Severe Bleeding**: Uncontrolled, spurting, or large amounts
• **Choking**: Cannot speak, cough, or breathe
• **Stroke Signs**: FAST test - Face drooping, Arm weakness, Speech difficulty
• **Heart Attack**: Chest pain with shortness of breath, nausea, sweating
• **Severe Allergic Reaction**: Difficulty breathing, swelling, hives
• **Poisoning**: Suspected ingestion of toxic substances
• **Severe Burns**: Large area, electrical, chemical, or airway burns
• **Head/Spine Injuries**: Loss of consciousness, neck/back pain
• **Seizures**: Lasting more than 5 minutes or repeated seizures

**🫁 CPR (Cardiopulmonary Resuscitation):**
1. **Check Responsiveness**: Tap shoulders, shout "Are you okay?"
2. **Call 102**: Get help and AED if available
3. **Position**: Place on firm surface, tilt head back, lift chin
4. **Hand Placement**: Center of chest between nipples
5. **Compressions**: 30 compressions, 100-120 per minute, 2 inches deep
6. **Rescue Breaths**: 2 breaths, watch chest rise
7. **Continue**: 30:2 ratio until help arrives or person responds

**🤲 CHOKING RELIEF (Heimlich Maneuver):**
**For Adults/Children over 1 year:**
1. Stand behind person, wrap arms around waist
2. Make fist, place thumb side above navel
3. Grasp fist with other hand
4. Give quick upward thrusts
5. Continue until object expelled or person unconscious

**For Infants (under 1 year):**
1. Hold face down on forearm
2. Give 5 back blows between shoulder blades
3. Turn over, give 5 chest thrusts
4. Check mouth, remove visible objects
5. Repeat until object expelled

**🩹 BLEEDING CONTROL:**
1. **Apply Direct Pressure**: Clean cloth or bandage on wound
2. **Elevate**: Raise injured area above heart if possible
3. **Pressure Points**: Apply pressure to artery if bleeding continues
4. **Tourniquet**: Only for severe limb bleeding when other methods fail
5. **Don't Remove**: Large embedded objects - stabilize instead

**🔥 BURN TREATMENT:**
**First-Degree (Red, Painful):**
• Cool with running water for 10-20 minutes
• Apply aloe vera or moisturizer
• Take pain relievers as needed
• Avoid ice, butter, or home remedies

**Second-Degree (Blisters):**
• Cool with water, don't break blisters
• Cover with sterile gauze
• Seek medical care for large areas

**Third-Degree (White/Charred):**
• Don't use water on large burns
• Cover with clean cloth
• SEEK IMMEDIATE MEDICAL CARE

**🦴 FRACTURE CARE:**
• Don't move person unless in immediate danger
• Immobilize injured area above and below fracture
• Apply ice wrapped in cloth
• Check circulation below injury
• Seek immediate medical care

**⚡ BASIC FIRST AID KIT:**
• Sterile gauze pads and tape
• Elastic bandages
• Antiseptic wipes
• Pain relievers (acetaminophen, ibuprofen)
• Thermometer
• Disposable gloves
• Emergency contact numbers
• First aid manual

**📞 EMERGENCY NUMBERS:**
• **102**: Emergency services (US)
• **Poison Control**: 1-800-222-1222
• **Crisis Text Line**: Text HOME to 741741
• **Suicide Prevention**: 988

**⚠️ IMPORTANT REMINDERS:**
• Stay calm and assess the situation
• Ensure scene safety before helping
• Don't move seriously injured persons unless necessary
• Provide only care you're trained to give
• Get professional medical help as soon as possible
• Take first aid/CPR classes for proper training

Remember: This information doesn't replace proper first aid training. Take certified courses for hands-on practice and complete knowledge."""

    # Menstrual health and period queries
    menstrual_keywords = ["period", "periods", "menstruation", "menstrual", "cycle", "pms", "cramps", "ovulation"]
    if any(keyword in user_input for keyword in menstrual_keywords):
        return """**Comprehensive Menstrual Health Information:**

**🌸 NORMAL MENSTRUAL CYCLE:**
• **Cycle Length**: 21-35 days (counted from first day of one period to first day of next)
• **Period Duration**: 3-7 days of bleeding
• **Blood Loss**: 30-40ml total (about 2-3 tablespoons)
• **Age Range**: First period (menarche) typically ages 10-15, menopause around age 51
• **Cycle Phases**: Menstrual → Follicular → Ovulation → Luteal

**📅 MENSTRUAL CYCLE PHASES:**

**🩸 Menstrual Phase (Days 1-5):**
• Shedding of uterine lining
• Hormone levels (estrogen, progesterone) are low
• Bleeding typically heaviest first 2-3 days

**🌱 Follicular Phase (Days 1-13):**
• Egg development in ovaries
• Rising estrogen levels
• Uterine lining begins to thicken

**🥚 Ovulation (Around Day 14):**
• Egg release from ovary
• Peak fertility window
• Signs: clear cervical mucus, slight temperature rise, mild pelvic pain

**🌙 Luteal Phase (Days 15-28):**
• High progesterone levels
• PMS symptoms may occur
• If no pregnancy, hormone levels drop triggering next period

**🔴 NORMAL PERIOD CHARACTERISTICS:**
• **Color**: Bright red to dark brown (normal variation)
• **Flow**: Light to heavy (varies person to person and cycle to cycle)
• **Clots**: Small clots normal, large clots (>quarter size) may need evaluation
• **Symptoms**: Mild cramping, bloating, mood changes, breast tenderness

**⚠️ WHEN TO SEE A HEALTHCARE PROVIDER:**

**🚨 Seek Immediate Care:**
• Severe pain that doesn't respond to pain relievers
• Soaking through pad/tampon every hour for several hours
• Fever with tampon use (possible toxic shock syndrome)
• Severe dizziness or fainting

**📞 Schedule Appointment:**
• Cycles shorter than 21 days or longer than 35 days
• Periods lasting longer than 7 days
• Missing periods (when not pregnant)
• Bleeding between periods
• Severe cramping interfering with daily activities
• Sudden changes in cycle pattern

**🩹 COMMON MENSTRUAL PROBLEMS:**

**💔 Painful Periods (Dysmenorrhea):**
• **Primary**: Normal cramping without underlying condition
• **Secondary**: Pain from conditions like endometriosis or fibroids
• **Treatment**: NSAIDs, heat therapy, exercise, hormonal birth control

**🌊 Heavy Periods (Menorrhagia):**
• Soaking pad/tampon every hour
• Periods lasting >7 days
• **Causes**: Fibroids, polyps, PCOS, thyroid disorders
• **Treatment**: Hormonal therapy, NSAIDs, surgical options

**📅 Irregular Periods:**
• Cycles outside 21-35 day range
• **Causes**: Stress, weight changes, PCOS, thyroid issues
• **Treatment**: Address underlying cause, hormonal regulation

**😔 PMS (Premenstrual Syndrome):**
• Physical and emotional symptoms 1-2 weeks before period
• **Symptoms**: Mood swings, bloating, breast tenderness, cravings
• **Treatment**: Lifestyle changes, supplements, medications

**😰 PMDD (Premenstrual Dysphoric Disorder):**
• Severe form of PMS significantly impacting daily life
• **Symptoms**: Severe mood changes, anxiety, depression
• **Treatment**: Antidepressants, hormonal therapy, counseling

**🧴 MENSTRUAL PRODUCTS:**

**🔸 Disposable Options:**
• **Pads**: External protection, various absorbencies
• **Tampons**: Internal protection, change every 4-8 hours

**♻️ Reusable Options:**
• **Menstrual Cups**: Internal, can wear up to 12 hours
• **Cloth Pads**: External, washable and eco-friendly
• **Period Underwear**: Built-in absorbent layers

**🧼 MENSTRUAL HYGIENE:**
• Change products regularly (pads: 4-6 hours, tampons: 4-8 hours)
• Wash hands before and after changing products
• Clean genital area with water only (avoid douching)
• Wear breathable cotton underwear
• Track your cycle and symptoms

**👧 FIRST PERIOD INFORMATION:**
• **Typical Age**: 10-15 years old
• **Early Signs**: Breast development, growth spurt, body hair, vaginal discharge
• **First Year**: Periods often irregular while body adjusts
• **Preparation**: Have supplies ready, understand normal changes

**🔄 CYCLE TRACKING:**
• Track period start/end dates
• Note flow heaviness and symptoms
• Identify your normal pattern
• Apps and calendars can help
• Share information with healthcare provider

**🤰 FERTILITY AWARENESS:**
• **Fertile Window**: 5 days before through day of ovulation
• **Ovulation Signs**: Clear cervical mucus, temperature rise, mild pain
• **Conception**: Most likely during fertile window
• **Contraception**: Understanding cycle helps with family planning

**🌿 NATURAL REMEDIES:**
• **Heat Therapy**: Heating pad or warm bath for cramps
• **Exercise**: Regular activity can reduce symptoms
• **Diet**: Reduce caffeine, salt, sugar; increase calcium, magnesium
• **Stress Management**: Yoga, meditation, adequate sleep
• **Hydration**: Drink plenty of water

**💊 MEDICAL TREATMENTS:**
• **NSAIDs**: Ibuprofen, naproxen for pain and heavy bleeding
• **Hormonal Birth Control**: Regulate cycles, reduce symptoms
• **Antidepressants**: For severe PMS/PMDD
• **Surgical Options**: For severe cases (endometrial ablation, hysterectomy)

**🏥 RELATED CONDITIONS:**
• **Endometriosis**: Uterine lining grows outside uterus
• **PCOS**: Hormonal disorder affecting ovulation
• **Fibroids**: Noncancerous uterine growths
• **Adenomyosis**: Uterine lining grows into muscle wall

**📚 EDUCATION AND SUPPORT:**
• Talk openly with healthcare providers
• Educate yourself about normal menstrual health
• Support friends and family members
• Advocate for menstrual equity and access to products

Remember: Every person's cycle is different. What's normal for you may be different from others. Track your patterns and consult healthcare providers with concerns."""

    # Vaccination and immunization queries
    vaccination_keywords = ["vaccine", "vaccination", "immunization", "shot", "immunize", "vaccinate"]
    if any(keyword in user_input for keyword in vaccination_keywords):
        return """**Comprehensive Vaccination Information:**

**🏥 ROUTINE VACCINES FOR ADULTS:**
• **Annual Flu Vaccine** - Everyone 6+ months (September-October)
• **COVID-19** - Primary series + boosters as recommended
• **Tdap/Td** - Every 10 years (tetanus, diphtheria, pertussis)
• **Shingles (Zoster)** - Adults 50+ (2 doses, 2-6 months apart)
• **Pneumococcal** - Adults 65+ or high-risk conditions
• **MMR** - Adults born after 1957 without immunity evidence

**👶 CHILDHOOD VACCINE SCHEDULE:**
• **Birth:** Hepatitis B (1st dose)
• **2 months:** DTaP, Hib, IPV, PCV13, Rotavirus
• **4 months:** DTaP, Hib, IPV, PCV13, Rotavirus
• **6 months:** DTaP, Hib, IPV, PCV13, Rotavirus, Hepatitis B
• **12-15 months:** MMR, Varicella, PCV13, Hib
• **4-6 years:** DTaP, IPV, MMR, Varicella
• **11-12 years:** Tdap, HPV, Meningococcal

**🌍 TRAVEL VACCINES:**
• **Yellow Fever** - Required for some countries
• **Typhoid** - High-risk areas with poor sanitation
• **Hepatitis A** - International travel
• **Japanese Encephalitis** - Rural Asia travel
• **Meningococcal** - Sub-Saharan Africa, Hajj pilgrimage

**⚡ VACCINE SAFETY & EFFECTIVENESS:**
• Vaccines undergo rigorous testing before approval
• Continuous safety monitoring (VAERS, VSD systems)
• Serious adverse events extremely rare (<1 per million)
• Common side effects: soreness, mild fever, fatigue
• Benefits far outweigh minimal risks

**🔬 HOW VACCINES WORK:**
• Expose immune system to weakened/killed pathogens
• Body develops antibodies and memory cells
• Provides protection against future infections
• Herd immunity protects entire community

**📋 SPECIAL POPULATIONS:**
• **Pregnant Women:** Tdap (27-36 weeks), flu vaccine
• **Immunocompromised:** Modified schedules, avoid live vaccines
• **Healthcare Workers:** Additional vaccines (hepatitis B, annual flu)
• **College Students:** Meningococcal vaccine recommended

**❌ VACCINE MYTHS DEBUNKED:**
• Vaccines do NOT cause autism (extensively studied)
• Natural immunity not always better than vaccine immunity
• Vaccines don't overwhelm immune system
• Ingredients are safe in vaccine amounts

**📞 RESOURCES:**
• CDC Vaccine Information Statements (VIS)
• Your healthcare provider
• State health department
• Travel medicine clinics for travel vaccines

**⚠️ MEDICAL EXEMPTIONS:**
• Severe allergic reactions to vaccine components
• Severe immunodeficiency conditions
• Requires healthcare provider documentation

Consult your healthcare provider for personalized vaccination recommendations based on your age, health status, and risk factors."""

    # Prevention queries
    if any(word in user_input for word in ["prevent", "prevention", "avoid"]):
        return """**Disease Prevention Strategies:**

• **Vaccinations:** Stay current with recommended vaccines
• **Healthy lifestyle:** Regular exercise, balanced diet, adequate sleep
• **Hygiene:** Frequent hand washing, safe food handling
• **Regular screenings:** Cancer screenings, blood pressure checks, cholesterol tests
• **Avoid risk factors:** Don't smoke, limit alcohol, maintain healthy weight
• **Stress management:** Practice relaxation techniques
• **Safe practices:** Use sunscreen, wear seatbelts, practice safe sex
• **Environmental safety:** Clean air, safe water, avoid toxins"""

    # Medication queries
    medication_keywords = ["medication", "medicine", "drug", "pill", "tablet", "capsule", "prescription", "pharmacy"]
    if any(keyword in user_input for keyword in medication_keywords):
        return """**Comprehensive Medication Information:**

**💊 MEDICATION SAFETY ESSENTIALS:**
• **Take as Prescribed**: Follow exact dosage, timing, and duration
• **Read Labels**: Check ingredients, warnings, and expiration dates
• **Store Properly**: Cool, dry place; original containers with labels
• **Don't Share**: Medications are prescribed for specific individuals
• **Complete Courses**: Finish antibiotics even if feeling better
• **Report Side Effects**: Contact healthcare provider for concerns

**🔍 TYPES OF MEDICATIONS:**

**📋 Prescription Medications:**
• Require doctor's prescription for safety and effectiveness
• Follow prescribed schedule exactly
• Don't adjust doses without consulting provider
• Refill before running out
• Store securely (especially controlled substances)

**🏪 Over-the-Counter (OTC) Medications:**
• Available without prescription but still have risks
• Read labels for ingredients, dosage, warnings
• Follow age-appropriate dosing guidelines
• Don't exceed recommended dose or duration
• Common types: pain relievers, cold/flu, antacids, allergy medications

**⚠️ DRUG INTERACTIONS:**
• **Drug-Drug**: Medications affecting each other's effectiveness
• **Drug-Food**: Food affecting medication absorption
• **Drug-Supplement**: Vitamins/herbs interacting with medications
• Always inform providers of ALL medications and supplements

**🩺 SPECIFIC MEDICATION CATEGORIES:**

**🦠 Antibiotics:**
• Fight bacterial infections only (not viruses)
• Complete full course even if feeling better
• Don't save leftovers or share with others
• May cause stomach upset, diarrhea, yeast infections

**🩹 Pain Medications:**
• Acetaminophen: liver damage risk if overdosed
• NSAIDs (ibuprofen): stomach upset, take with food
• Opioids: addictive, use only as prescribed
• Alternative methods: ice, heat, physical therapy

**❤️ Heart Medications:**
• Beta-blockers, ACE inhibitors, blood thinners
• Take consistently at same time daily
• Monitor for dizziness, fatigue, bleeding
• Don't stop suddenly without medical supervision

**🩸 Blood Pressure Medications:**
• Multiple types: ACE inhibitors, diuretics, beta-blockers
• Take daily at consistent times
• Monitor blood pressure regularly
• Lifestyle changes enhance effectiveness

**🍯 Diabetes Medications:**
• Insulin, metformin, other blood sugar controllers
• Take with meals as directed
• Monitor blood sugar levels regularly
• Recognize low blood sugar symptoms

**🧠 Mental Health Medications:**
• Antidepressants, anti-anxiety, mood stabilizers
• May take weeks to show full effect
• Don't stop suddenly (withdrawal risk)
• Regular follow-up with prescriber essential

**💊 PILL IDENTIFICATION & SAFETY:**
• Never take unidentified pills
• Use pill identifier tools or consult pharmacist
• Look for imprints, colors, shapes, sizes
• Contact poison control for accidental ingestion

**📦 PROPER STORAGE:**
• Cool, dry place (not bathroom medicine cabinet)
• Original containers with labels
• Check expiration dates regularly
• Child-resistant caps for safety
• Dispose expired medications through pharmacy take-back

**🎯 ADHERENCE STRATEGIES:**
• Pill organizers and reminder alarms
• Take at same time daily with routine activities
• Understand why medication is important
• Address side effects with healthcare provider
• Use pharmacy services: blister packing, synchronization

**⚠️ WHEN TO SEEK HELP:**
• Severe side effects or allergic reactions
• Questions about dosing or interactions
• Difficulty affording medications
• Problems with adherence or side effects
• Before stopping any prescribed medication

**📞 EMERGENCY SITUATIONS:**
• Difficulty breathing after taking medication
• Severe rash, swelling, or hives
• Chest pain or rapid heartbeat
• Severe dizziness or fainting
• Signs of overdose or poisoning

Remember: Always consult healthcare providers or pharmacists for medication questions. This information is educational and doesn't replace professional medical advice."""

    # Mental health queries
    if any(word in user_input for word in ["mental health", "depression", "anxiety", "stress", "mood"]):
        return """**Mental Health Resources:**

**Common signs to watch for:**
• Persistent sadness or anxiety
• Changes in sleep or appetite
• Loss of interest in activities
• Difficulty concentrating
• Thoughts of self-harm

**Getting help:**
• Talk to healthcare provider
• Contact mental health professional
• Call crisis hotlines if needed
• Consider therapy or counseling
• Medication may be helpful
• Build support network
• Practice self-care

**Crisis Resources:**
• National Suicide Prevention Lifeline: 988
• Crisis Text Line: Text HOME to 741741"""

    # Check for common question patterns
    if any(phrase in user_input for phrase in ["what is", "what are", "tell me about", "explain"]):
        return """**I can provide information about:**

**Common Conditions:** Fever, cold, flu, diabetes, hypertension, asthma, arthritis, depression, anxiety

**Body Systems:** Heart disease, respiratory conditions, digestive issues, skin problems

**Preventive Care:** Vaccinations, exercise, nutrition, sleep hygiene

**Emergency Care:** When to seek immediate medical attention

**Mental Health:** Depression, anxiety, stress management

**Women's Health:** Pregnancy, menopause

**Men's Health:** Prostate health

Please ask about a specific condition or health topic for detailed information."""

    if any(word in user_input for word in ["symptoms", "symptom", "signs"]):
        return """**When to Seek Medical Care:**

**Seek immediate care (102) for:**
• Chest pain with breathing difficulty
• Severe allergic reactions
• Signs of stroke or heart attack
• Severe injuries or bleeding
• Difficulty breathing

**Contact healthcare provider for:**
• Persistent fever over 101°F
• Symptoms lasting more than expected
• Worsening conditions
• New or concerning symptoms
• Medication side effects

**Symptom tracking tips:**
• Note when symptoms started
• Track severity and patterns
• List associated symptoms
• Record what helps or worsens symptoms"""

    # Default response with more comprehensive information
    return """**Welcome to MediBot AI - Your Comprehensive Health Assistant!**

I can provide detailed information about:

**🏥 MEDICAL CONDITIONS (50+)**
• **Blood Disorders**: Anemia, Leukemia, Lymphoma, Hemophilia, Sickle Cell Disease
• **Respiratory**: Asthma, COPD, Pneumonia, Tuberculosis, Lung Cancer
• **Cardiovascular**: Heart Disease, Stroke, Hypertension, Arrhythmia
• **Digestive**: IBS, Crohn's Disease, Ulcers, Liver Disease, Gallbladder Disease
• **Endocrine**: Diabetes, Thyroid Disorders, Adrenal Conditions
• **Neurological**: Alzheimer's, Parkinson's, Multiple Sclerosis, Epilepsy
• **Mental Health**: Depression, Anxiety, PTSD, Bipolar Disorder, Eating Disorders
• **Musculoskeletal**: Arthritis, Osteoporosis, Fibromyalgia, Back Pain
• **Skin Conditions**: Eczema, Psoriasis, Skin Cancer, Acne
• **Eye/Ear**: Cataracts, Glaucoma, Hearing Loss, Tinnitus
• **Kidney/Urological**: Kidney Disease, UTIs, Prostate Conditions
• **Women's Health**: Pregnancy, Menopause, PCOS, Breast Cancer
• **Men's Health**: Prostate Cancer, Testosterone Issues
• **Infectious Diseases**: COVID-19, STIs, Hepatitis, Meningitis
• **Cancer**: Screening, Types, Treatment Options
• **Autoimmune**: Lupus, Rheumatoid Arthritis, IBD

**💊 MEDICATION INFORMATION**
• Prescription and OTC drug safety
• Drug interactions and side effects
• Specific medication categories (antibiotics, pain meds, heart drugs)
• Proper storage and disposal
• Adherence strategies

**🩹 EMERGENCY & FIRST AID**
• CPR and choking relief procedures
• Bleeding control and wound care
• Burn treatment and fracture care
• When to call 102
• Basic first aid techniques

**🛡️ PREVENTIVE CARE**
• Vaccination schedules (childhood, adult, travel)
• Cancer screening guidelines
• Health maintenance recommendations
• Disease prevention strategies

**🧠 MENTAL HEALTH SUPPORT**
• Crisis resources and hotlines
• Mental health conditions and treatments
• Stress management techniques
• When to seek professional help

**💡 EXAMPLE QUERIES:**
• "What are the symptoms of diabetes?"
• "How do I treat a burn?"
• "Vaccination schedule for adults"
• "When should I call 102?"
• "Drug interactions with blood thinners"
• "Depression treatment options"
• "First aid for choking"

**🚨 EMERGENCY DISCLAIMER:**
For life-threatening emergencies, call 102 immediately. This chatbot provides educational information only and cannot replace professional medical care.

**📞 CRISIS RESOURCES:**
• Emergency: 102
• Poison Control: 1-800-222-1222
• Suicide Prevention: 988
• Crisis Text: Text HOME to 741741

Ask me anything about health conditions, treatments, medications, or emergency care!"""

@app.route("/")
def index():
    return render_template('index.html', condition_count=len(medical_responses))

@app.route("/chat")
def chat_page():
    session.permanent = True
    return render_template('chat.html')

@app.route("/get", methods=["GET", "POST"])
def chat():
    if is_rate_limited(request.remote_addr):
        return "Too many requests. Please wait a moment.", 429

    msg = request.form.get("msg", "").strip()
    if not msg:
        return "Please enter a message.", 400

    msg = html.escape(msg)[:500]
    response = get_medical_response(msg)

    if 'history' not in session:
        session['history'] = []
    session['history'].append({'role': 'user', 'text': msg})
    session['history'].append({'role': 'bot', 'text': response})
    session.modified = True

    return response

@app.route("/history", methods=["GET"])
def history():
    return jsonify(session.get('history', []))

@app.route("/clear", methods=["POST"])
def clear_history():
    session.pop('history', None)
    return jsonify({'status': 'ok'})

@app.route("/search", methods=["GET"])
def search_topics():
    q = request.args.get("q", "").strip().lower()
    if not q or len(q) < 2:
        return jsonify([])
    results = [k for k in medical_responses if q in k.lower()][:8]
    return jsonify(results)

@app.route("/health")
def health():
    return jsonify({'status': 'ok', 'conditions': len(medical_responses)})

@app.route("/robots.txt")
def robots():
    return app.send_static_file('robots.txt') if os.path.exists('static/robots.txt') else ('', 204)

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
