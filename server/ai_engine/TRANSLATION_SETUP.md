# Day 6 multilingual analysis

English (`en`) runs locally without credentials. Hindi (`hi`), Marathi (`mr`) and
automatic source detection (`auto`) use Azure Translator v3. No live translation
has been tested without user-provided credentials; unit tests mock provider replies.

Configure AZURE_TRANSLATOR_KEY and, for regional resources,
AZURE_TRANSLATOR_REGION in the backend process environment. Restart Django after
setting them. Do not commit the key or put it in NEXT_PUBLIC variables. This project
does not automatically read .env files. No provider resource is created by this code.

Endpoint reference: https://learn.microsoft.com/en-us/azure/ai-services/translator/text-translation/how-to/use-rest-api

Mount `path("api/ai/", include("ai_engine.urls"))` in config/urls.py (Naman).
POST /api/ai/classify/ takes {text, language}, authenticated with a CSRF token.
It returns {analysis, analysis_token}. Tokens expire after 15 minutes and are bound
to the original text, source language and user. Use verify_analysis when persisting
results, rather than trusting client-submitted category/priority/translated text.
Manual category corrections can remain separate from the AI suggestion.

If translation is unavailable, the API returns 503, never a fabricated translation.
Citizens can still submit their original complaint without AI. Raw complaint text
is sent to Azure only when translating/detecting; uploaded photos are not sent.
Selected language is treated as a user declaration, not verified detection. Auto
detection is provider-backed; uncertain/unsupported detection requires manual choice.
