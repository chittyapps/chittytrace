var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// worker.js
var worker_default = {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname.startsWith("/api/")) {
      return handleAPIRequest(request, env);
    }
    if (url.pathname.startsWith("/assets/") || url.pathname.endsWith(".js") || url.pathname.endsWith(".css") || url.pathname.endsWith(".ico") || url.pathname.endsWith(".svg")) {
      return env.ASSETS.fetch(request);
    }
    return serveReactApp(env);
  }
};
async function handleAPIRequest(request, env) {
  const url = new URL(request.url);
  if (url.pathname === "/api/ai/generate") {
    try {
      const { prompt } = await request.json();
      const response = await env.AI.run("@cf/meta/llama-2-7b-chat-int8", {
        messages: [
          {
            role: "system",
            content: "You are a helpful AI assistant for a modern web application."
          },
          {
            role: "user",
            content: prompt
          }
        ]
      });
      return new Response(JSON.stringify({
        success: true,
        result: response.response
      }), {
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type"
        }
      });
    } catch (error) {
      return new Response(JSON.stringify({
        success: false,
        error: error.message
      }), {
        status: 500,
        headers: { "Content-Type": "application/json" }
      });
    }
  }
  if (url.pathname === "/api/ai/classify") {
    try {
      const formData = await request.formData();
      const image = formData.get("image");
      const response = await env.AI.run("@cf/microsoft/resnet-50", {
        image: Array.from(new Uint8Array(await image.arrayBuffer()))
      });
      return new Response(JSON.stringify({
        success: true,
        result: response
      }), {
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*"
        }
      });
    } catch (error) {
      return new Response(JSON.stringify({
        success: false,
        error: error.message
      }), {
        status: 500,
        headers: { "Content-Type": "application/json" }
      });
    }
  }
  if (url.pathname === "/api/health") {
    return new Response(JSON.stringify({
      status: "healthy",
      timestamp: (/* @__PURE__ */ new Date()).toISOString(),
      ai_available: !!env.AI,
      environment: env.ENVIRONMENT || "development"
    }), {
      headers: { "Content-Type": "application/json" }
    });
  }
  return new Response("API endpoint not found", { status: 404 });
}
__name(handleAPIRequest, "handleAPIRequest");
async function serveReactApp(env) {
  const htmlContent = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Modern React App - Powered by Cloudflare Workers AI</title>
    <script src="https://cdn.tailwindcss.com"><\/script>
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
    <\/script>
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
            <span class="text-sm font-medium bg-gradient-to-r from-orange-700 to-blue-700 bg-clip-text text-transparent">Powered by Cloudflare Workers AI \u26A1</span>
          </div>

          <h1 class="text-6xl md:text-8xl font-bold mb-8 bg-gradient-to-r from-gray-900 via-blue-800 to-purple-800 bg-clip-text text-transparent animate-pulse-slow">
            Loading...
          </h1>

          <p class="text-xl md:text-2xl text-gray-600 mb-10 max-w-3xl mx-auto leading-relaxed">
            Modern React App with AI capabilities, deployed on the edge
          </p>

          <div class="flex flex-wrap justify-center gap-4 mb-12">
            <div class="flex items-center bg-white/50 backdrop-blur-sm rounded-full px-6 py-3 shadow-lg">
              <span class="text-sm font-semibold text-gray-700">\u{1F680} Edge Computing</span>
            </div>
            <div class="flex items-center bg-white/50 backdrop-blur-sm rounded-full px-6 py-3 shadow-lg">
              <span class="text-sm font-semibold text-gray-700">\u{1F916} AI-Powered</span>
            </div>
            <div class="flex items-center bg-white/50 backdrop-blur-sm rounded-full px-6 py-3 shadow-lg">
              <span class="text-sm font-semibold text-gray-700">\u26A1 Instant Global</span>
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
              }, '\u{1F680} Deployed on Cloudflare Workers AI')
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
            }, loading ? '\u{1F916} AI Thinking...' : '\u{1F916} Ask AI for a Tagline'),

            aiResponse && h('div', {
              className: 'mt-8 p-6 bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl max-w-2xl mx-auto'
            }, [
              h('h3', { className: 'font-semibold text-lg mb-2' }, '\u{1F916} AI Generated:'),
              h('p', { className: 'text-gray-700' }, aiResponse)
            ])
          ])
        ]);
      }

      // Mount the React app
      const root = createRoot(document.getElementById('root'));
      root.render(h(ModernReactApp));
    <\/script>
  </body>
</html>`;
  return new Response(htmlContent, {
    headers: {
      "Content-Type": "text/html",
      "Cache-Control": "public, max-age=3600"
    }
  });
}
__name(serveReactApp, "serveReactApp");

// ../.config/npm/node_global/lib/node_modules/wrangler/templates/middleware/middleware-ensure-req-body-drained.ts
var drainBody = /* @__PURE__ */ __name(async (request, env, _ctx, middlewareCtx) => {
  try {
    return await middlewareCtx.next(request, env);
  } finally {
    try {
      if (request.body !== null && !request.bodyUsed) {
        const reader = request.body.getReader();
        while (!(await reader.read()).done) {
        }
      }
    } catch (e) {
      console.error("Failed to drain the unused request body.", e);
    }
  }
}, "drainBody");
var middleware_ensure_req_body_drained_default = drainBody;

// ../.config/npm/node_global/lib/node_modules/wrangler/templates/middleware/middleware-miniflare3-json-error.ts
function reduceError(e) {
  return {
    name: e?.name,
    message: e?.message ?? String(e),
    stack: e?.stack,
    cause: e?.cause === void 0 ? void 0 : reduceError(e.cause)
  };
}
__name(reduceError, "reduceError");
var jsonError = /* @__PURE__ */ __name(async (request, env, _ctx, middlewareCtx) => {
  try {
    return await middlewareCtx.next(request, env);
  } catch (e) {
    const error = reduceError(e);
    return Response.json(error, {
      status: 500,
      headers: { "MF-Experimental-Error-Stack": "true" }
    });
  }
}, "jsonError");
var middleware_miniflare3_json_error_default = jsonError;

// .wrangler/tmp/bundle-JxcM8o/middleware-insertion-facade.js
var __INTERNAL_WRANGLER_MIDDLEWARE__ = [
  middleware_ensure_req_body_drained_default,
  middleware_miniflare3_json_error_default
];
var middleware_insertion_facade_default = worker_default;

// ../.config/npm/node_global/lib/node_modules/wrangler/templates/middleware/common.ts
var __facade_middleware__ = [];
function __facade_register__(...args) {
  __facade_middleware__.push(...args.flat());
}
__name(__facade_register__, "__facade_register__");
function __facade_invokeChain__(request, env, ctx, dispatch, middlewareChain) {
  const [head, ...tail] = middlewareChain;
  const middlewareCtx = {
    dispatch,
    next(newRequest, newEnv) {
      return __facade_invokeChain__(newRequest, newEnv, ctx, dispatch, tail);
    }
  };
  return head(request, env, ctx, middlewareCtx);
}
__name(__facade_invokeChain__, "__facade_invokeChain__");
function __facade_invoke__(request, env, ctx, dispatch, finalMiddleware) {
  return __facade_invokeChain__(request, env, ctx, dispatch, [
    ...__facade_middleware__,
    finalMiddleware
  ]);
}
__name(__facade_invoke__, "__facade_invoke__");

// .wrangler/tmp/bundle-JxcM8o/middleware-loader.entry.ts
var __Facade_ScheduledController__ = class ___Facade_ScheduledController__ {
  constructor(scheduledTime, cron, noRetry) {
    this.scheduledTime = scheduledTime;
    this.cron = cron;
    this.#noRetry = noRetry;
  }
  static {
    __name(this, "__Facade_ScheduledController__");
  }
  #noRetry;
  noRetry() {
    if (!(this instanceof ___Facade_ScheduledController__)) {
      throw new TypeError("Illegal invocation");
    }
    this.#noRetry();
  }
};
function wrapExportedHandler(worker) {
  if (__INTERNAL_WRANGLER_MIDDLEWARE__ === void 0 || __INTERNAL_WRANGLER_MIDDLEWARE__.length === 0) {
    return worker;
  }
  for (const middleware of __INTERNAL_WRANGLER_MIDDLEWARE__) {
    __facade_register__(middleware);
  }
  const fetchDispatcher = /* @__PURE__ */ __name(function(request, env, ctx) {
    if (worker.fetch === void 0) {
      throw new Error("Handler does not export a fetch() function.");
    }
    return worker.fetch(request, env, ctx);
  }, "fetchDispatcher");
  return {
    ...worker,
    fetch(request, env, ctx) {
      const dispatcher = /* @__PURE__ */ __name(function(type, init) {
        if (type === "scheduled" && worker.scheduled !== void 0) {
          const controller = new __Facade_ScheduledController__(
            Date.now(),
            init.cron ?? "",
            () => {
            }
          );
          return worker.scheduled(controller, env, ctx);
        }
      }, "dispatcher");
      return __facade_invoke__(request, env, ctx, dispatcher, fetchDispatcher);
    }
  };
}
__name(wrapExportedHandler, "wrapExportedHandler");
function wrapWorkerEntrypoint(klass) {
  if (__INTERNAL_WRANGLER_MIDDLEWARE__ === void 0 || __INTERNAL_WRANGLER_MIDDLEWARE__.length === 0) {
    return klass;
  }
  for (const middleware of __INTERNAL_WRANGLER_MIDDLEWARE__) {
    __facade_register__(middleware);
  }
  return class extends klass {
    #fetchDispatcher = /* @__PURE__ */ __name((request, env, ctx) => {
      this.env = env;
      this.ctx = ctx;
      if (super.fetch === void 0) {
        throw new Error("Entrypoint class does not define a fetch() function.");
      }
      return super.fetch(request);
    }, "#fetchDispatcher");
    #dispatcher = /* @__PURE__ */ __name((type, init) => {
      if (type === "scheduled" && super.scheduled !== void 0) {
        const controller = new __Facade_ScheduledController__(
          Date.now(),
          init.cron ?? "",
          () => {
          }
        );
        return super.scheduled(controller);
      }
    }, "#dispatcher");
    fetch(request) {
      return __facade_invoke__(
        request,
        this.env,
        this.ctx,
        this.#dispatcher,
        this.#fetchDispatcher
      );
    }
  };
}
__name(wrapWorkerEntrypoint, "wrapWorkerEntrypoint");
var WRAPPED_ENTRY;
if (typeof middleware_insertion_facade_default === "object") {
  WRAPPED_ENTRY = wrapExportedHandler(middleware_insertion_facade_default);
} else if (typeof middleware_insertion_facade_default === "function") {
  WRAPPED_ENTRY = wrapWorkerEntrypoint(middleware_insertion_facade_default);
}
var middleware_loader_entry_default = WRAPPED_ENTRY;
export {
  __INTERNAL_WRANGLER_MIDDLEWARE__,
  middleware_loader_entry_default as default
};
//# sourceMappingURL=worker.js.map
