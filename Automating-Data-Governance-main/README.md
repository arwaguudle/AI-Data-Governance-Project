# Supplementary Material for "Automating Data Governance with Generative AI"

Accepted at [AAAI/ACM Conference on AI, Ethics, and Society 2025](https://doi.org/10.1609/aies.v8i1.36587). [PDF Download](https://linusdietz.com/assets/papers/AIES25AutomatingDataGovernanceWithGenerative.pdf)

```
@Article{Dietz2025Automating,
 author = {Linus W. Dietz and Arif Wider and Simon Harrer},
 journal = {AAAI/ACM Conference on AI, Ethics, and Society},
 title = {Automating Data Governance with Generative {AI}},
 year = {2025},
 issn = {3065-8365},
 month = oct,
 number = {1},
 pages = {760--771},
 volume = {8},
 doi = {10.1609/aies.v8i1.36587},
 publisher = {{AAAI/ACM}},
 series = {AIES'25},
}
```

## Base Data Maps

The directory `datamaps` contains a folder with the `.yml` files for the base data maps of both domains.

## Access Requests

The directory `access_requests` contains two `.csv` files with the originally generated access requests alongside with the script `request_gen.py` to generate them. The prompts for the Large-Language Models are extracted into `prompting.py`.

## Governance AI Prompts

The directory `governance_ai` contains the prompts of the Governance AI.

## Expert Ratings

The `expert_opinions` directory contains the annotations of the domain experts regarding the access requests, warnings, and suggestions.

