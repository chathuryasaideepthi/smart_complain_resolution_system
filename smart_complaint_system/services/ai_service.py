import os
import numpy as np
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from transformers import pipeline
import nltk
import pytesseract
import cv2
from config import Config

for resource in ('punkt', 'punkt_tab'):
    try:
        nltk.download(resource, quiet=True)
    except Exception:
        pass

MODEL = SentenceTransformer('all-MiniLM-L6-v2')
CLASSIFIER = None

CLASS_LABELS = ['Water', 'Electricity', 'Roads', 'Sanitation', 'Security', 'Health']


def load_classifier():
    global CLASSIFIER
    if CLASSIFIER is None:
        vectorizer = TfidfVectorizer(max_features=2000, stop_words='english')
        example_texts = [
            'water supply complaint',
            'electricity outage issue',
            'broken road pothole',
            'garbage collection delay',
            'street safety patrol',
            'medical service request',
        ]
        labels = ['Water', 'Electricity', 'Roads', 'Sanitation', 'Security', 'Health']
        X = vectorizer.fit_transform(example_texts)
        model = LogisticRegression()
        model.fit(X, labels)
        CLASSIFIER = (vectorizer, model)
    return CLASSIFIER


def classify_department(text):
    vectorizer, model = load_classifier()
    X = vectorizer.transform([text])
    result = model.predict(X)[0]
    return str(result)


def predict_priority(text):
    lower = text.lower()
    if 'emergency' in lower or 'urgent' in lower or 'critical' in lower:
        return 'Critical'
    if 'high' in lower or 'danger' in lower or 'immediately' in lower:
        return 'High'
    if 'medium' in lower or 'soon' in lower:
        return 'Medium'
    return 'Low'


def analyze_sentiment(text):
    if not text:
        return 'Neutral'
    if any(word in text.lower() for word in ['angry', 'terrible', 'hate', 'worst', 'fraud']):
        return 'Angry'
    if any(word in text.lower() for word in ['good', 'thank', 'great', 'satisfied', 'happy']):
        return 'Positive'
    if any(word in text.lower() for word in ['issue', 'delay', 'problem', 'concern']):
        return 'Neutral'
    return 'Neutral'


def summarize_text(text):
    if not text:
        return ''
    try:
        sentences = nltk.sent_tokenize(text)
        return ' '.join(sentences[:2])
    except LookupError:
        return text[:200]


def estimate_resolution_time(priority):
    mapping = {
        'Critical': '1-2 days',
        'High': '3-5 days',
        'Medium': '1-2 weeks',
        'Low': '2-4 weeks'
    }
    return mapping.get(priority, '1-2 weeks')


def find_duplicate(text, complaints):
    if not text or not complaints:
        return None, 0.0
    query_embedding = MODEL.encode(text, convert_to_tensor=True)
    best_score = 0.0
    best_complaint = None
    for complaint in complaints:
        if not complaint.description:
            continue
        target_embedding = MODEL.encode(complaint.description, convert_to_tensor=True)
        score = util.pytorch_cos_sim(query_embedding, target_embedding).item()
        if score > best_score:
            best_score = score
            best_complaint = complaint
    return best_complaint, best_score


def perform_ocr(image_path):
    try:
        pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD
        img = cv2.imread(image_path)
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception:
        return ''


def verify_image_relevance(text, image_path):
    extracted = perform_ocr(image_path)
    return bool(extracted) or any(keyword in text.lower() for keyword in ['road', 'water', 'electricity', 'garbage', 'health', 'security'])


def detect_spam(text):
    if not text:
        return False
    spam_indicators = ['free', 'money', 'hack', 'fake', 'urgent', 'scam']
    return any(token in text.lower() for token in spam_indicators)
