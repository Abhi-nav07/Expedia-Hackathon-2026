# Patch for frontend/package.json

Add the Mapbox GL dependency and its types, used by
`components/travel/map-container.tsx`:

```json
"mapbox-gl": "3.7.0",
```

and in devDependencies:
```json
"@types/mapbox-gl": "3.4.1",
```

Then reinstall:
```bash
cd frontend && npm install
```

## Also required: a Mapbox token to actually see a map

`MapContainer` reads `NEXT_PUBLIC_MAPS_API_KEY` from `.env` (already
present as an empty value in Module 01's `.env.example`). Without it,
the component renders a graceful "Map not configured" empty state
rather than crashing — this is intentional, not a bug, since most of
the hackathon will likely run before a Mapbox token is actually needed.

To enable it: sign up at https://mapbox.com, grab a public token, and
set:
```
NEXT_PUBLIC_MAPS_API_KEY=pk.your_token_here
```
