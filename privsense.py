import spacy
from spacy.pipeline import EntityRuler
from spacy.language import Language
from faker import Faker

# Load spaCy transformer model
nlp = spacy.load("en_core_web_trf")
fake = Faker()

# Function to load custom companies from a file
def load_custom_companies(file_path):
    custom_companies = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            company_name = line.strip().lower()  # Convert to lowercase
            if company_name:
                custom_companies.append({"label": "ORG", "pattern": company_name})
    return custom_companies

# Load custom companies from companies.txt
custom_companies = load_custom_companies('companies.txt')

# Register the EntityRuler component
@Language.factory("custom_entity_ruler")
def create_entity_ruler(nlp, name):
    return EntityRuler(nlp)

# Add custom EntityRuler to the pipeline
ruler = nlp.add_pipe("custom_entity_ruler", before="ner")

# Add custom patterns for URLs and emails
patterns = [
    {"label": "URL", "pattern": [{"LIKE_URL": True}]},
    {"label": "EMAIL", "pattern": [{"LIKE_EMAIL": True}]},
]


ruler.add_patterns(custom_companies + patterns)

# Debug: Print the patterns added to the EntityRuler
print("Patterns added to the EntityRuler:")
for pattern in custom_companies + patterns:
    print(pattern)

# Function to pseudonymize text
def pseudonymize_text(text):
    lower_text = text.lower()  # Convert the entire text to lowercase
    doc = nlp(lower_text)
    pseudonymized_text = text

    # Create dictionaries to map original entities to fake ones
    person_map = {}
    org_map = {}
    url_map = {}
    email_map = {}

    # Print all recognized entities
    print("Recognized entities:")
    for ent in doc.ents:
        print(f"Text: {ent.text}, Label: {ent.label_}")

    # Replace recognized entities
    entities = [(ent.start_char, ent.end_char, ent.label_, ent.text) for ent in doc.ents]
    offset = 0

    for start, end, label, text in entities:
        if label == "PERSON":
            if text not in person_map:
                person_map[text] = fake.name()
            replacement = person_map[text]
        elif label == "ORG":
            if text not in org_map:
                org_map[text] = fake.company()
            replacement = org_map[text]
        elif label == "URL":
            if text not in url_map:
                url_map[text] = fake.uri()
            replacement = url_map[text]
        elif label == "EMAIL":
            if text not in email_map:
                email_map[text] = fake.email()
            replacement = email_map[text]
        else:
            continue

        # Adjust for offset due to previous replacements
        pseudonymized_text = pseudonymized_text[:start + offset] + replacement + pseudonymized_text[end + offset:]
        offset += len(replacement) - (end - start)

    return pseudonymized_text

# Example usage with file input and output
def main():
    # Read input text from a file
    input_file = 'input.txt'
    with open(input_file, 'r', encoding='utf-8') as file:
        data = file.read()

    # Print the original text
    print("Before:")
    print(data)

    # Apply pseudonymization
    pseudonymized_data = pseudonymize_text(data)

    # Write pseudonymized text to an output file
    output_file = 'output.txt'
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(pseudonymized_data)

    # Print the pseudonymized text
    print("\nAfter:")
    print(pseudonymized_data)

if __name__ == "__main__":
    main()
