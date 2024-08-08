import spacy
from spacy.pipeline import EntityRuler
from spacy.language import Language
from faker import Faker
from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load spaCy transformer model and Faker instance
nlp = spacy.load("en_core_web_trf")
fake = Faker()

# Function to load custom companies from a file
def load_custom_companies(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [{"label": "ORG", "pattern": line.strip().lower()} for line in file if line.strip()]

# Function to create and register the EntityRuler
def add_entity_ruler(nlp, patterns):
    @Language.factory("custom_entity_ruler")
    def create_entity_ruler(nlp, name):
        return EntityRuler(nlp)
    
    ruler = nlp.add_pipe("custom_entity_ruler", before="ner")
    ruler.add_patterns(patterns)
    return ruler

# Function to create entity maps and pseudonymize text
def create_entity_maps(doc):
    person_map, org_map, url_map, email_map = {}, {}, {}, {}
    entities = [(ent.start_char, ent.end_char, ent.label_, ent.text) for ent in doc.ents]
    
    for start, end, label, text in entities:
        if label == "PERSON":
            if text not in person_map:
                person_map[text] = fake.name()
        elif label == "ORG":
            if text not in org_map:
                org_map[text] = fake.company()
        elif label == "URL":
            if text not in url_map:
                url_map[text] = fake.uri()
        elif label == "EMAIL":
            if text not in email_map:
                email_map[text] = fake.email()
    
    return person_map, org_map, url_map, email_map, entities

# Function to replace entities in the text
def replace_entities(text, entities, person_map, org_map, url_map, email_map):
    pseudonymized_text = text
    offset = 0

    for start, end, label, orig_text in entities:
        if label == "PERSON":
            replacement = person_map[orig_text]
        elif label == "ORG":
            replacement = org_map[orig_text]
        elif label == "URL":
            replacement = url_map[orig_text]
        elif label == "EMAIL":
            replacement = email_map[orig_text]
        else:
            continue

        pseudonymized_text = pseudonymized_text[:start + offset] + replacement + pseudonymized_text[end + offset:]
        offset += len(replacement) - (end - start)

    return pseudonymized_text

# Function to pseudonymize text
def pseudonymize_text(text):
    doc = nlp(text.lower())
    person_map, org_map, url_map, email_map, entities = create_entity_maps(doc)

    # Debug: Print all recognized entities
    print("Recognized entities:")
    for start, end, label, orig_text in entities:
        print(f"Text: {orig_text}, Label: {label}")

    # Debug: Print all recognized entities and their pseudonymized counterparts
    print("Recognized entities and their pseudonymized counterparts:")
    for start, end, label, orig_text in entities:
        if label == "PERSON":
            pseudonymized = person_map[orig_text]
        elif label == "ORG":
            pseudonymized = org_map[orig_text]
        elif label == "URL":
            pseudonymized = url_map[orig_text]
        elif label == "EMAIL":
            pseudonymized = email_map[orig_text]
        else:
            continue
        print(f"Text: {orig_text}, Label: {label}, Pseudonymized: {pseudonymized}")

    # Write entities to CSV
    csv_file_path = 'entities.csv'
    write_entities_to_csv(entities, person_map, org_map, url_map, email_map, csv_file_path)    

    pseudonymized_text = replace_entities(text, entities, person_map, org_map, url_map, email_map)
    return pseudonymized_text

# Function to write entities to a CSV file
def write_entities_to_csv(entities, person_map, org_map, url_map, email_map, csv_file_path):
    seen_entities = set()   # To avoid duplicate entries in the CSV
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['Original Text', 'Label', 'Pseudonymized Text']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        writer.writeheader()
        for start, end, label, orig_text in entities:
            if (label, orig_text) not in seen_entities:
                seen_entities.add((label, orig_text))
                if label == "PERSON":
                    pseudonymized = person_map[orig_text]
                elif label == "ORG":
                    pseudonymized = org_map[orig_text]
                elif label == "URL":
                    pseudonymized = url_map[orig_text]
                elif label == "EMAIL":
                    pseudonymized = email_map[orig_text]
                else:
                    continue
                writer.writerow({'Original Text': orig_text, 'Label': label, 'Pseudonymized Text': pseudonymized})


# Endpoint to pseudonymize text from JSON
@app.route('/pseudonymize', methods=['POST'])
def pseudonymize_json():
    data = request.json
    text = data.get('text', '')
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    pseudonymized_text = pseudonymize_text(text)
    return jsonify({"pseudonymized_text": pseudonymized_text})

# Endpoint to pseudonymize text from a file
@app.route('/pseudonymize-file', methods=['POST'])
def pseudonymize_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    text = file.read().decode('utf-8')
    
    pseudonymized_text = pseudonymize_text(text)
    return jsonify({"pseudonymized_text": pseudonymized_text})

if __name__ == "__main__":
    custom_companies = load_custom_companies('companies.txt')
    patterns = [
        {"label": "URL", "pattern": [{"LIKE_URL": True}]},
        {"label": "EMAIL", "pattern": [{"LIKE_EMAIL": True}]},
    ]
    all_patterns = custom_companies + patterns
    add_entity_ruler(nlp, all_patterns)
    app.run(host='0.0.0.0', port=5000)
