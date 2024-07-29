import spacy
from spacy.pipeline import EntityRuler
from spacy.language import Language
from faker import Faker

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

# Function to print added patterns for debugging
def print_patterns(patterns):
    print("Patterns added to the EntityRuler:")
    for pattern in patterns:
        print(pattern)

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

    pseudonymized_text = replace_entities(text, entities, person_map, org_map, url_map, email_map)
    return pseudonymized_text

# Function to read text from a file
def read_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Function to write text to a file
def write_text(file_path, text):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)

# Main function for example usage
def main():
    input_file = 'input.txt'
    output_file = 'output.txt'
    
    data = read_text(input_file)
    print("Before:")
    print(data)
    
    pseudonymized_data = pseudonymize_text(data)
    write_text(output_file, pseudonymized_data)
    
    print("\nAfter:")
    print(pseudonymized_data)

if __name__ == "__main__":
    custom_companies = load_custom_companies('companies.txt')
    patterns = [
        {"label": "URL", "pattern": [{"LIKE_URL": True}]},
        {"label": "EMAIL", "pattern": [{"LIKE_EMAIL": True}]},
    ]
    all_patterns = custom_companies + patterns
    add_entity_ruler(nlp, all_patterns)
    print_patterns(all_patterns)
    main()