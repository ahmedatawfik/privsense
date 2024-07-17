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
            company_name = line.strip()
            if company_name:
                # Add both the original and lowercased versions of each company name
                custom_companies.append({"label": "ORG", "pattern": company_name})
                custom_companies.append({"label": "ORG", "pattern": company_name.lower()})
    return custom_companies

# Load custom companies from companies.txt
custom_companies = load_custom_companies('companies.txt')

# Register the EntityRuler component
@Language.factory("custom_entity_ruler")
def create_entity_ruler(nlp, name):
    return EntityRuler(nlp)

# Add custom EntityRuler to the pipeline
ruler = nlp.add_pipe("custom_entity_ruler", before="ner")

# Add custom patterns for URLs, emails, and phone numbers
patterns = [
    {"label": "URL", "pattern": [{"LIKE_URL": True}]},
    {"label": "EMAIL", "pattern": [{"LIKE_EMAIL": True}]},
    {"label": "PHONE", "pattern": [{"ORTH": {"REGEX": r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"}}]},  # Matches various phone number formats
]

ruler.add_patterns(custom_companies + patterns)

# Function to pseudonymize text
def pseudonymize_text(text):
    doc = nlp(text)
    pseudonymized_text = text

    # Create dictionaries to map original entities to fake ones
    person_map = {}
    org_map = {}
    url_map = {}
    email_map = {}
    phone_map = {}

    # Replace recognized entities
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            if ent.text not in person_map:
                person_map[ent.text] = fake.name()
            pseudonymized_text = pseudonymized_text.replace(ent.text, person_map[ent.text])
        elif ent.label_ == "ORG":
            if ent.text not in org_map:
                org_map[ent.text] = fake.company()
            pseudonymized_text = pseudonymized_text.replace(ent.text, org_map[ent.text])
        elif ent.label_ == "URL":
            if ent.text not in url_map:
                url_map[ent.text] = fake.uri()
            pseudonymized_text = pseudonymized_text.replace(ent.text, url_map[ent.text])
        elif ent.label_ == "EMAIL":
            if ent.text not in email_map:
                email_map[ent.text] = fake.email()
            pseudonymized_text = pseudonymized_text.replace(ent.text, email_map[ent.text])
        elif ent.label_ == "PHONE":
            if ent.text not in phone_map:
                phone_map[ent.text] = fake.phone_number()
            pseudonymized_text = pseudonymized_text.replace(ent.text, phone_map[ent.text])

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
