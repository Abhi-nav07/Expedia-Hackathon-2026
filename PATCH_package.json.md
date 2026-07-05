# Patch for frontend/package.json

Add this dependency, used by components/ui/switch.tsx (new in this module):

```json
"@radix-ui/react-switch": "1.1.0",
```

Then reinstall:
```bash
cd frontend && npm install
```

No other new frontend dependencies are needed for Module 11 — everything
else (react-hook-form, @hookform/resolvers, zod, @tanstack/react-query,
lucide-react) was already present in package.json since Module 01.
