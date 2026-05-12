/**
 * ChittyTrace scope projector — thin adapter over @chittyos/schema/scope-projector.
 *
 * Projects forensic investigation lifecycle events into the canonical
 * scopes table. Analysis, timeline, and fund trace = 'trace_investigation'.
 *
 * @canon: chittycanon://gov/governance#core-types
 */

import { createScopeProjector } from '@chittyos/schema/scope-projector';

const traceProjector = createScopeProjector('trace.chitty.cc', {
  characterization: 'Incident',
  statusMapper: {
    requested: 'new',
    analyzing: 'active',
    tracing: 'active',
    generating: 'active',
    completed: 'resolved',
    failed: 'closed',
    archived: 'archived',
  },
});

/**
 * Fire-and-forget scope projection via Hono's executionCtx.waitUntil.
 */
export function traceScopeLog(c, projection, env) {
  traceProjector(c, env, projection);
}
