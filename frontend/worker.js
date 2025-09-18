/**
 * Modern React App with Cloudflare Workers AI
 * Serves static assets and provides AI-powered features
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Handle API routes for AI features
    if (url.pathname.startsWith('/api/')) {
      return handleAPIRequest(request, env);
    }

    // Handle static assets
    if (url.pathname.startsWith('/assets/') ||
        url.pathname.endsWith('.js') ||
        url.pathname.endsWith('.css') ||
        url.pathname.endsWith('.ico') ||
        url.pathname.endsWith('.svg')) {
      return env.ASSETS.fetch(request);
    }

    // Serve the main React app for all other routes (SPA routing)
    return serveReactApp(env);
  },
};

/**
 * Handle API requests with Cloudflare Workers AI
 */
async function handleAPIRequest(request, env) {
  const url = new URL(request.url);

  // AI Text Generation endpoint
  if (url.pathname === '/api/ai/generate') {
    try {
      const { prompt } = await request.json();

      const response = await env.AI.run('@cf/meta/llama-2-7b-chat-int8', {
        messages: [
          {
            role: 'system',
            content: 'You are a helpful AI assistant for a modern web application.'
          },
          {
            role: 'user',
            content: prompt
          }
        ]
      });

      return new Response(JSON.stringify({
        success: true,
        result: response.response
      }), {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type'
        }
      });
    } catch (error) {
      return new Response(JSON.stringify({
        success: false,
        error: error.message
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }

  // AI Image Classification endpoint
  if (url.pathname === '/api/ai/classify') {
    try {
      const formData = await request.formData();
      const image = formData.get('image');

      const response = await env.AI.run('@cf/microsoft/resnet-50', {
        image: Array.from(new Uint8Array(await image.arrayBuffer()))
      });

      return new Response(JSON.stringify({
        success: true,
        result: response
      }), {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
    } catch (error) {
      return new Response(JSON.stringify({
        success: false,
        error: error.message
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }

  // Health check endpoint
  if (url.pathname === '/api/health') {
    return new Response(JSON.stringify({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      ai_available: !!env.AI,
      environment: env.ENVIRONMENT || 'development'
    }), {
      headers: { 'Content-Type': 'application/json' }
    });
  }

  return new Response('API endpoint not found', { status: 404 });
}

/**
 * Serve the React application
 */
async function serveReactApp(env) {
  // Serve the main HTML file for the React SPA
  const htmlContent = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Modern React App - Powered by Cloudflare Workers AI</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
      tailwind.config = {
        theme: {
          extend: {
            animation: {
              'float': 'float 6s ease-in-out infinite',
              'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            },
            keyframes: {
              float: {
                '0%, 100%': { transform: 'translateY(0px)' },
                '50%': { transform: 'translateY(-20px)' },
              }
            }
          },
        },
      }
    </script>
  </head>
  <body>
    <div id="root">
      <!-- React App will mount here -->
      <div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <div class="text-center max-w-4xl mx-auto px-6">
          <!-- Loading state with Cloudflare branding -->
          <div class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-orange-50 to-blue-50 rounded-full mb-8 border border-orange-100 shadow-lg">
            <svg class="w-5 h-5 text-orange-600 mr-2 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span class="text-sm font-medium bg-gradient-to-r from-orange-700 to-blue-700 bg-clip-text text-transparent">Powered by Cloudflare Workers AI ⚡</span>
          </div>

          <h1 class="text-6xl md:text-8xl font-bold mb-8 bg-gradient-to-r from-gray-900 via-blue-800 to-purple-800 bg-clip-text text-transparent animate-pulse-slow">
            Loading...
          </h1>

          <p class="text-xl md:text-2xl text-gray-600 mb-10 max-w-3xl mx-auto leading-relaxed">
            Modern React App with AI capabilities, deployed on the edge
          </p>

          <div class="flex flex-wrap justify-center gap-4 mb-12">
            <div class="flex items-center bg-white/50 backdrop-blur-sm rounded-full px-6 py-3 shadow-lg">
              <span class="text-sm font-semibold text-gray-700">🚀 Edge Computing</span>
            </div>
            <div class="flex items-center bg-white/50 backdrop-blur-sm rounded-full px-6 py-3 shadow-lg">
              <span class="text-sm font-semibold text-gray-700">🤖 AI-Powered</span>
            </div>
            <div class="flex items-center bg-white/50 backdrop-blur-sm rounded-full px-6 py-3 shadow-lg">
              <span class="text-sm font-semibold text-gray-700">⚡ Instant Global</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <script type="module">
      // Enhanced React app with AI features
      import { createElement as h, useState, useEffect } from 'https://esm.sh/react@18';
      import { createRoot } from 'https://esm.sh/react-dom@18/client';

      function ModernReactApp() {
        const [mounted, setMounted] = useState(false);
        const [aiResponse, setAiResponse] = useState('');
        const [loading, setLoading] = useState(false);

        useEffect(() => {
          setMounted(true);
        }, []);

        const callAI = async () => {
          setLoading(true);
          try {
            const response = await fetch('/api/ai/generate', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                prompt: 'Generate a creative tagline for a modern web application powered by AI'
              })
            });
            const data = await response.json();
            if (data.success) {
              setAiResponse(data.result);
            }
          } catch (error) {
            console.error('AI call failed:', error);
          }
          setLoading(false);
        };

        return h('div', {
          className: \`min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center transition-all duration-1000 \${mounted ? 'opacity-100' : 'opacity-0'}\`
        }, [
          h('div', { className: 'text-center max-w-4xl mx-auto px-6' }, [
            h('div', {
              className: 'inline-flex items-center px-6 py-3 bg-gradient-to-r from-orange-50 to-blue-50 rounded-full mb-8 border border-orange-100 shadow-lg'
            }, [
              h('span', {
                className: 'text-sm font-medium bg-gradient-to-r from-orange-700 to-blue-700 bg-clip-text text-transparent'
              }, '🚀 Deployed on Cloudflare Workers AI')
            ]),

            h('h1', {
              className: 'text-6xl md:text-8xl font-bold mb-8 bg-gradient-to-r from-gray-900 via-blue-800 to-purple-800 bg-clip-text text-transparent'
            }, 'Modern React App'),

            h('p', {
              className: 'text-xl md:text-2xl text-gray-600 mb-10 max-w-3xl mx-auto leading-relaxed'
            }, 'Built with React + Vite + Tailwind CSS, powered by Cloudflare Workers AI'),

            h('button', {
              onClick: callAI,
              disabled: loading,
              className: 'px-10 py-5 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-white rounded-full font-semibold text-lg hover:shadow-2xl transition-all transform hover:scale-105 disabled:opacity-50'
            }, loading ? '🤖 AI Thinking...' : '🤖 Ask AI for a Tagline'),

            aiResponse && h('div', {
              className: 'mt-8 p-6 bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl max-w-2xl mx-auto'
            }, [
              h('h3', { className: 'font-semibold text-lg mb-2' }, '🤖 AI Generated:'),
              h('p', { className: 'text-gray-700' }, aiResponse)
            ])
          ])
        ]);
      }

      // Mount the React app
      const root = createRoot(document.getElementById('root'));
      root.render(h(ModernReactApp));
    </script>
  </body>
</html>`;

  return new Response(htmlContent, {
    headers: {
      'Content-Type': 'text/html',
      'Cache-Control': 'public, max-age=3600',
    },
  });
}