# Day 6 multilingual analysis

English (`en`) runs locally without credentials. Hindi (`hi`) and Marathi (`mr`) use
Azure Translator v3 when available, with a labelled local keyword fallback when the
provider is unavailable. Automatic source detection (`auto`) requires the provider. No live translation
has been tested without user-provided credentials; unit tests mock provider replies.

Configure AZURE_TRANSLATOR_KEY and, for regional resources,
AZURE_TRANSLATOR_REGION in the backend process environment. Restart Django after
setting them. Do not commit the key or put it in NEXT_PUBLIC variables. This project
does not automatically read .env files. No provider resource is created by this code.

Endpoint reference: https://learn.microsoft.com/en-us/azure/ai-services/translator/text-translation/how-to/use-rest-api

The AI routes are mounted in config/urls.py.
POST /api/ai/classify/ takes {text, language}, authenticated with a CSRF token.
It returns {analysis, analysis_token}. Tokens expire after 15 minutes and are bound
to the original text, source language and user. Use verify_analysis when persisting
results, rather than trusting client-submitted category/priority/translated text.
Manual category corrections can remain separate from the AI suggestion.

If translation is unavailable for a selected Hindi/Marathi language, analysis returns
local keyword-based category/priority suggestions with `method: rules`, a visible
`notice`, and `translated_text: null`. This is not a translation or a trained multilingual
model. Unknown or ambiguous terms return `other`; officers should review all suggestions.
Automatic language detection still returns 503 when the provider is unavailable.
Citizens can always submit their original complaint without analysis. Raw complaint text
is sent to Azure only when translating/detecting; uploaded photos are not sent.
Selected language is treated as a user declaration, not verified detection. Auto
detection is provider-backed; uncertain/unsupported detection requires manual choice.
