# Patch for frontend/package.json

Add these dependencies, used by components/ui/*.tsx in this module:

```json
"@radix-ui/react-slot": "1.1.0",
"@radix-ui/react-label": "2.1.0",
"@radix-ui/react-avatar": "1.1.0",
"class-variance-authority": "0.7.0",
```

Note: `class-variance-authority` may already be listed if you applied
Module 01 exactly as given — check for duplicates before adding. The
three `@radix-ui/*` packages are new in this module (Component Library)
and are the accessible, unstyled primitives that `label.tsx` and
`avatar.tsx` wrap; `button.tsx`'s `asChild` polymorphism depends on
`@radix-ui/react-slot`.

Then reinstall:
```bash
cd frontend && npm install
```
