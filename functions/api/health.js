// Cloudflare Pages API endpoint for health check
export async function onRequestGet(context) {
  return new Response(JSON.stringify({
    status: 'healthy',
    service: 'ChittyTrace',
    timestamp: new Date().toISOString(),
    environment: context.env.ENVIRONMENT || 'production'
  }), {
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*'
    }
  });
}