import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  try {
    const body = await request.json()
    // Simple handshake from VSCode Buddy extension
    const { action, payload } = body || {}

    if (action === 'handshake') {
      return NextResponse.json({ ok: true, message: 'vscode-buddy handshake received' })
    }

    // Example: extension can forward queries using the same logic as /api/query
    if (action === 'query') {
      const prompt = payload?.prompt
      const demoResponse = { reply: `VSCode-buddy demo reply to: ${prompt?.slice(0,200)}`, timestamp: new Date().toISOString() }
      return NextResponse.json(demoResponse)
    }

    return NextResponse.json({ error: 'Unknown action' }, { status: 400 })
  } catch (err) {
    return NextResponse.json({ error: 'Invalid request' }, { status: 400 })
  }
}
