import spacy
from spacy.pipeline import EntityRuler
from spacy.language import Language
from faker import Faker
import re

# Load spaCy transformer model
nlp = spacy.load("en_core_web_trf")
fake = Faker()

# Function to load custom companies from a file
def load_custom_companies(file_path):
    custom_companies = []
    with open(file_path, 'r') as file:
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
ruler.add_patterns(custom_companies)

# Function to pseudonymize text
def pseudonymize_text(text):
    doc = nlp(text)
    pseudonymized_text = text

    # Create dictionaries to map original entities to fake ones
    person_map = {}
    org_map = {}

    # Replace recognized entities
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            if ent.text not in person_map:
                person_map[ent.text] = fake.name()
            pseudonymized_text = re.sub(r'\b{}\b'.format(re.escape(ent.text)), person_map[ent.text], pseudonymized_text)
        elif ent.label_ == "ORG":
            if ent.text not in org_map:
                org_map[ent.text] = fake.company()
            pseudonymized_text = re.sub(r'\b{}\b'.format(re.escape(ent.text)), org_map[ent.text], pseudonymized_text)

    return pseudonymized_text

# Example usage with file input and output
def main():
    # Read input text from a file
    input_file = 'input.txt'
    with open(input_file, 'r') as file:
        data = file.read()

    # Print the original text
    print("Before:")
    print(data)

    # Apply pseudonymization
    pseudonymized_data = pseudonymize_text(data)

    # Write pseudonymized text to an output file
    output_file = 'output.txt'
    with open(output_file, 'w') as file:
        file.write(pseudonymized_data)

    # Print the pseudonymized text
    print("\nAfter:")
    print(pseudonymized_data)

if __name__ == "__main__":
    main()
