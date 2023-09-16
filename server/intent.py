import transformers

from transformers import pipeline

CLASSIFIER = pipeline("zero-shot-classification",
                  model="facebook/bart-large-mnli")

def get_intent(sent, candidates):
    results = CLASSIFIER(sent, candidates)
    print(results)
    return results["labels"][0]
