# Backend Translations

## Overview

The backend API now uses a translation system to support multiple languages for all user-facing strings like error messages and endpoint descriptions.

## Usage

All translations are managed through the `translations.py` module:

```python
from src.backend.translations import t

# Basic usage
message = t("error_file_must_be_pdf", lang="fr")  # Returns French message
message = t("error_file_must_be_pdf", lang="en")  # Returns English message

# With variable substitution
message = t("error_invalid_improvement_mode", lang="fr", values="none, basic, targeted")
message = t("error_internal", lang="en", error="Connection timeout")
```

## Adding New Translations

To add a new translatable string:

1. Open `src/backend/translations.py`
2. Add your key to both `"en"` and `"fr"` dictionaries:

```python
TRANSLATIONS = {
    "en": {
        ...
        "your_new_key": "Your English message",
        "your_key_with_var": "Error: {error_details}",
    },
    "fr": {
        ...
        "your_new_key": "Votre message en français",
        "your_key_with_var": "Erreur : {error_details}",
    }
}
```

3. Use it in your code:

```python
detail = t("your_new_key", lang="fr")
detail = t("your_key_with_var", lang="en", error_details="Something went wrong")
```

## Available Translation Keys

### API Descriptions
- `api_description`: Main API description
- `api_root_description`: Root endpoint description
- `api_health_description`: Health check endpoint description

### Endpoint Parameter Descriptions
- `file_description`: CV file upload description
- `improvement_mode_description`: Improvement mode parameter
- `job_offer_description`: Job offer file parameter
- `candidate_name_description`: Candidate name parameter
- `max_pages_description`: Max pages parameter
- `target_language_description`: Target language parameter
- `file_pdf_description`: PDF file description
- `job_offer_targeted_description`: Job offer for targeted improvement

### Error Messages
- `error_file_must_be_pdf`: File type validation error
- `error_invalid_improvement_mode`: Invalid improvement mode (use with `values` parameter)
- `error_job_offer_required`: Missing job offer for targeted mode
- `error_job_offer_format`: Invalid job offer file format
- `error_conversion_failed`: CV conversion failure
- `error_internal`: Internal server error (use with `error` parameter)
- `error_conversion_expired`: Conversion cache expired
- `error_file_not_found`: Generated file not found

### Class Docstrings
- `improvement_mode_doc`: ImprovementMode class documentation

## Current Languages

- **French (fr)**: Default language
- **English (en)**: Secondary language

## Language Selection

The API currently defaults to French (`lang="fr"`). To change the language:

```python
# Option 1: Manual selection in code
detail = t("error_message", lang="en")

# Option 2: Get from request headers (future implementation)
# Accept-Language: en
```

## Future Improvements

1. **Auto-detect language from request headers**: Read `Accept-Language` header
2. **Add more languages**: Spanish (es), Italian (it), German (de)
3. **Database-backed translations**: For dynamic content
4. **Translation validation**: Ensure all keys exist in all languages
