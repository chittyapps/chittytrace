/**
 * Standalone Cloudflare Worker - Modern React App with AI
 *
 * Copy this entire file to Cloudflare Workers dashboard:
 * 1. Go to dash.cloudflare.com > Workers & Pages
 * 2. Create new Worker
 * 3. Paste this code
 * 4. Add AI binding named "AI" in settings
 * 5. Deploy!
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Handle API routes for AI features
    if (url.pathname.startsWith('/api/')) {
      return handleAPIRequest(request, env);
    }

    // Serve the React app for all other routes
    return serveReactApp(env);
  },
};

async function handleAPIRequest(request, env) {
  const url = new URL(request.url);

  // CORS headers
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };

  if (request.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  // AI Text Generation endpoint
  if (url.pathname === '/api/ai/generate') {
    try {
      const { prompt } = await request.json();

      const response = await env.AI.run('@cf/meta/llama-2-7b-chat-int8', {
        messages: [
          {
            role: 'system',
            content: 'You are a creative AI assistant. Generate short, catchy taglines and creative content.'
          },
          {
            role: 'user',
            content: prompt || 'Generate a creative tagline for a modern web application'
          }
        ]
      });

      return new Response(JSON.stringify({
        success: true,
        result: response.response
      }), {
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    } catch (error) {
      return new Response(JSON.stringify({
        success: false,
        error: error.message
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }
  }

  // Health check endpoint
  if (url.pathname === '/api/health') {
    return new Response(JSON.stringify({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      ai_available: !!env.AI,
      version: '1.0.0'
    }), {
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });
  }

  return new Response('API endpoint not found', {
    status: 404,
    headers: corsHeaders
  });
}

async function serveReactApp(env) {
  const htmlContent = \`<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🚀</text></svg>" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Modern React App - Cloudflare Workers AI</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
      tailwind.config = {
        theme: {
          extend: {
            animation: {
              'float': 'float 6s ease-in-out infinite',
              'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
              'gradient': 'gradient 15s ease infinite',
            },
            keyframes: {
              float: {
                '0%, 100%': { transform: 'translateY(0px)' },
                '50%': { transform: 'translateY(-20px)' },
              },
              gradient: {
                '0%, 100%': { 'background-position': '0% 50%' },
                '50%': { 'background-position': '100% 50%' },
              }
            }
          },
        },
      }
    </script>
    <style>
      .bg-gradient-animated {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
      }
    </style>
  </head>
  <body>
    <div id="root"></div>

    <script type="module">
      import { createElement as h, useState, useEffect } from 'https://esm.sh/react@18';
      import { createRoot } from 'https://esm.sh/react-dom@18/client';

      function ModernReactApp() {
        const [mounted, setMounted] = useState(false);
        const [aiResponse, setAiResponse] = useState('');
        const [loading, setLoading] = useState(false);
        const [count, setCount] = useState(0);

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
                prompt: 'Generate a creative and inspiring tagline for a cutting-edge web application powered by AI'
              })
            });
            const data = await response.json();
            if (data.success) {
              setAiResponse(data.result);
            } else {
              setAiResponse('AI service temporarily unavailable. Try again later!');
            }
          } catch (error) {
            console.error('AI call failed:', error);
            setAiResponse('Error connecting to AI service.');
          }
          setLoading(false);
        };

        const checkHealth = async () => {
          try {
            const response = await fetch('/api/health');
            const data = await response.json();
            console.log('Health check:', data);
          } catch (error) {
            console.error('Health check failed:', error);
          }
        };

        useEffect(() => {
          checkHealth();
        }, []);

        return h('div', {
          className: \`min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 relative overflow-hidden transition-all duration-1000 \${mounted ? 'opacity-100' : 'opacity-0'}\`
        }, [
          // Animated background elements
          h('div', { className: 'absolute inset-0 overflow-hidden' }, [
            h('div', { className: 'absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full opacity-20 animate-float' }),
            h('div', { className: 'absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-r from-pink-400 to-orange-400 rounded-full opacity-20 animate-float', style: { animationDelay: '2s' } }),
            h('div', { className: 'absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-r from-green-400 to-blue-400 rounded-full opacity-10 animate-pulse-slow' })
          ]),

          // Main content
          h('div', { className: 'relative z-10 text-center max-w-4xl mx-auto px-6 py-20' }, [
            // Header badge
            h('div', {
              className: 'inline-flex items-center px-6 py-3 bg-gradient-to-r from-orange-50 to-blue-50 rounded-full mb-8 border border-orange-100 shadow-lg backdrop-blur-sm'
            }, [
              h('span', { className: '🚀 mr-2' }),
              h('span', {
                className: 'text-sm font-medium bg-gradient-to-r from-orange-700 to-blue-700 bg-clip-text text-transparent'
              }, 'Powered by Cloudflare Workers AI ⚡')
            ]),

            // Main title
            h('h1', {
              className: 'text-5xl md:text-7xl font-bold mb-8 bg-gradient-to-r from-gray-900 via-blue-800 to-purple-800 bg-clip-text text-transparent leading-tight'
            }, [
              'Modern React App',
              h('br'),
              h('span', { className: 'bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent animate-pulse-slow' }, 'on the Edge')
            ]),

            // Subtitle
            h('p', {
              className: 'text-xl md:text-2xl text-gray-600 mb-12 max-w-3xl mx-auto leading-relaxed'
            }, 'Experience the future of web development with React, Tailwind CSS, and AI - all running on Cloudflare\\'s global edge network.'),

            // Interactive buttons
            h('div', { className: 'flex flex-col sm:flex-row gap-6 justify-center mb-12' }, [
              h('button', {
                onClick: () => setCount(count + 1),
                className: 'px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full font-semibold text-lg hover:shadow-2xl transition-all transform hover:scale-105'
              }, \`👆 Clicked \${count} times\`),

              h('button', {
                onClick: callAI,
                disabled: loading,
                className: 'px-8 py-4 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-full font-semibold text-lg hover:shadow-2xl transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed'
              }, loading ? '🤖 AI is thinking...' : '🤖 Ask AI for Magic'),
            ]),

            // Features grid
            h('div', { className: 'grid grid-cols-1 md:grid-cols-3 gap-6 mb-12' }, [
              h('div', { className: 'p-6 bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg hover:shadow-xl transition-all' }, [
                h('div', { className: 'text-4xl mb-4' }, '⚡'),
                h('h3', { className: 'font-bold text-lg mb-2' }, 'Lightning Fast'),
                h('p', { className: 'text-gray-600 text-sm' }, 'Sub-100ms response times globally')
              ]),
              h('div', { className: 'p-6 bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg hover:shadow-xl transition-all' }, [
                h('div', { className: 'text-4xl mb-4' }, '🤖'),
                h('h3', { className: 'font-bold text-lg mb-2' }, 'AI-Powered'),
                h('p', { className: 'text-gray-600 text-sm' }, 'Integrated with Llama-2 and ResNet-50')
              ]),
              h('div', { className: 'p-6 bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg hover:shadow-xl transition-all' }, [
                h('div', { className: 'text-4xl mb-4' }, '🌍'),
                h('h3', { className: 'font-bold text-lg mb-2' }, 'Global Edge'),
                h('p', { className: 'text-gray-600 text-sm' }, 'Deployed on 200+ locations worldwide')
              ])
            ]),

            // AI Response
            aiResponse && h('div', {
              className: 'mt-8 p-8 bg-gradient-animated text-white rounded-3xl shadow-2xl max-w-2xl mx-auto transform hover:scale-105 transition-all'
            }, [
              h('h3', { className: 'font-bold text-xl mb-4 flex items-center' }, [
                h('span', { className: 'mr-2' }, '🤖'),
                'AI Generated Magic:'
              ]),
              h('p', { className: 'text-lg leading-relaxed italic' }, \`"\${aiResponse}"\`)
            ])
          ])
        ]);
      }

      // Mount the React app
      const root = createRoot(document.getElementById('root'));
      root.render(h(ModernReactApp));
    </script>
  </body>
</html>\`;

  return new Response(htmlContent, {
    headers: {
      'Content-Type': 'text/html',
      'Cache-Control': 'public, max-age=3600',
    },
  });
}