---
name: docs-lookup
description: Look up a symbol in the project's published API documentation.
---

# Docs lookup

Use this when the user asks what a library function does, or for its signature.

## Steps

1. Run `scripts/lookup.py <symbol>` to fetch the doc entry.
2. Quote the signature and the one-line summary. Link the page.
3. If the symbol is not found, say so. Do not guess a signature.

## Notes

- Results come from the published docs site, so they match the deployed
  version rather than the local checkout.
