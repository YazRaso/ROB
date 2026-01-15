import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { prompt, source, clientId = 'default_user' } = body || {}

    // Basic auth via Backboard API key header or env check
    const providedKey = request.headers.get('x-backboard-api-key') || process.env.BACKBOARD_API_KEY
    if (!providedKey) {
      return NextResponse.json({ error: 'Missing Backboard API key' }, { status: 401 })
    }

    // Check for tool invocations
    const toolPattern = /@(\w+)/
    const toolMatch = prompt?.match(toolPattern)
    
    if (toolMatch) {
      const toolName = toolMatch[1]
      
      // Forward tool request to backend
      const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000'
      const response = await fetch(
        `${backendUrl}/messages/send?client_id=${clientId}&content=${encodeURIComponent(prompt)}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      )

      if (!response.ok) {
        throw new Error('Backend request failed')
      }

      const toolResult = await response.json()
      
      // Handle tool results
      if (toolResult.type === 'tool_result') {
        if (toolResult.tool === 'create_file') {
          // For web, we return the file info and let the frontend handle creation
          const filename = toolResult.result?.filename ?? '<unknown filename>';
          return NextResponse.json({
            type: 'tool_result',
            tool: 'create_file',
            result: toolResult.result,
            reply: `File creation request: ${filename}`,
            timestamp: new Date().toISOString(),
          })
        }
        
        return NextResponse.json({
          type: 'tool_result',
          tool: toolResult.tool,
          result: toolResult.result,
          reply: toolResult.result?.formatted || toolResult.result?.message || 'Tool executed successfully',
          timestamp: new Date().toISOString(),
        })
      }
    }

    // Normal query - forward to backend
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000'
    const response = await fetch(
      `${backendUrl}/messages/send?client_id=${clientId}&content=${encodeURIComponent(prompt || '')}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    )

    if (!response.ok) {
      throw new Error('Backend request failed')
    }

    const reply = await response.text()
    
    return NextResponse.json({
      reply: reply,
      source: source ?? 'backboard',
      timestamp: new Date().toISOString(),
    })
  } catch (err) {
    return NextResponse.json({ error: 'Invalid request' }, { status: 400 })
  }
}
