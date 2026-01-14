# Backboard Dashboard (Demo)

This is a small demo dashboard for Backboard.io to visualize LLM Memory, connected sources, and provide a query interface.

## Local setup

1. Install dependencies:

   npm install

2. Copy env example and set your Backboard key:

   cp .env.local.example .env.local

   # edit .env.local and set BACKBOARD_API_KEY

3. Run in dev mode:

   npm run dev

4. Open http://localhost:3000

## Vercel / Production

Set an environment variable in Vercel (or your host): `BACKBOARD_API_KEY` with the Backboard API key. The app reads from `process.env.BACKBOARD_API_KEY`.

## API Routes

- `POST /api/query` — Accepts `{ prompt: string, source?: string }` and returns a demo reply. Requires the Backboard API key either via `x-backboard-api-key` header or set in server env.
- `POST /api/vscode` — Handshake and query support for the VSCode Buddy extension. Send `{ action: 'handshake' }` or `{ action: 'query', payload: { prompt } }`.

## Demo Repo Toggle

The `Connected Apps` page contains a **Demo Repo Configuration** toggle that hard-links demo statuses for Drive, Codebase and the Summarizer. This is intended for demonstration only.

## Notes

This is a minimal demo scaffolded for the frontend. In production you'd wire connectors (OAuth, webhooks) and use real Backboard APIs to fetch and push memory data.
