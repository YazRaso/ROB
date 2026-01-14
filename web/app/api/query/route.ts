import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { prompt, source } = body || {}

    // Basic auth via Backboard API key header or env check
    const providedKey = request.headers.get('x-backboard-api-key') || process.env.BACKBOARD_API_KEY
    if (!providedKey) {
      return NextResponse.json({ error: 'Missing Backboard API key' }, { status: 401 })
    }

    // Demo: return a canned response to emulate querying Backboard LLM Memory
    const demoResponse = {
      reply: `Demo reply for prompt: ${prompt?.slice(0, 200) ?? ''}`,
      source: source ?? 'demo',
      timestamp: new Date().toISOString(),
    }

    return NextResponse.json(demoResponse)
  } catch (err) {
    return NextResponse.json({ error: 'Invalid request' }, { status: 400 })
  }
}
