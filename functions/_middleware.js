// Cloudflare Pages Functions middleware for ChittyTrace
export async function onRequest(context) {
  const { request, next, env } = context;
  
  // Add security headers
  const response = await next();
  
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set('X-Powered-By', 'ChittyCorp');
  
  return response;
}