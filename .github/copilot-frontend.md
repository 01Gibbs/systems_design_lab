# Frontend Constraints - NON-NEGOTIABLE

## Technology Stack (STRICT)

**Frontend**: Vite + React + TypeScript + TailwindCSS + Playwright  
**Backend**: Python + FastAPI (separate concern)

### Forbidden Technologies

❌ **NEVER use**:

- Next.js (use Vite instead)
- Server-side rendering frameworks
- API contract duplication with Zod
- Scattered fetch calls in components

✅ **MUST use**:

- Vite as build tool and dev server
- React 18+ with TypeScript
- TailwindCSS for all styling
- Zod ONLY for client-side form validation
- Playwright for E2E testing
- openapi-typescript for contract generation

## API Architecture Rules

### Contract-First (STRICT)

1. **Single Source of Truth**: `../openapi.json` (backend OpenAPI snapshot)
2. **Type Generation**: `npm run contracts:gen` generates `src/api/types.ts`
3. **Centralized Client**: All API calls through `src/api/client.ts`
4. **NO fetch in components**: Components import from `@/api/client` only

### Zod Usage Restrictions

**Zod is ONLY for client-side form validation:**

- ✅ Validate user input before submitting to API
- ✅ Build dynamic schemas from backend parameter_schema
- ✅ Use in forms, inputs, UI validation

**Zod MUST NOT be used for:**

- ❌ Validating API responses
- ❌ Duplicating backend request/response shapes
- ❌ Replacing TypeScript types from openapi-typescript
- ❌ API contract enforcement (that's TypeScript's job)

### API Client Pattern

```typescript
// src/api/client.ts
import type { paths, components } from "./types"; // From openapi-typescript

type ApiResult<T> =
  | { ok: true; data: T }
  | { ok: false; status: number; error: unknown };

export const simApi = {
  scenarios: () => request<ScenariosResponse>("/api/sim/scenarios"),
  // ... other endpoints
};
```

```typescript
// Component usage
import { simApi } from "@/api/client";

const result = await simApi.scenarios();
if (result.ok) {
  // result.data is fully typed from OpenAPI
}
```

```typescript
// Form validation (Zod allowed here)
import { buildParameterSchema } from "@/schemas/forms";

const zodSchema = buildParameterSchema(backendParamSchema);
zodSchema.parse(formData); // Validate before API call
await simApi.enable(scenario, formData); // Typed API call
```

## Project Structure (MANDATORY)

```
frontend/
├── src/
│   ├── api/
│   │   ├── client.ts       # Centralized typed API client
│   │   └── types.ts        # Generated from openapi-typescript
│   ├── schemas/
│   │   └── forms.ts        # Zod for form validation only
│   ├── components/
│   ├── pages/
│   ├── App.tsx
│   └── main.tsx
├── e2e/
│   └── simulator.spec.ts   # Playwright tests
├── index.html              # Vite entry point
├── vite.config.ts
├── tailwind.config.js
└── package.json
```

## Development Workflow

```bash
# 1. Backend updates OpenAPI snapshot
cd backend
# ... make API changes ...
# openapi.json updated automatically

# 2. Regenerate frontend types
cd ../frontend
npm run contracts:gen   # Generates src/api/types.ts

# 3. TypeScript catches breaking changes
npm run typecheck       # Fails if API contract broken

# 4. Fix components to match new contracts
# Update imports, types, function signatures

# 5. Validate
npm run lint
npm run format
npm run test:e2e
```

## Guardrails (Enforced)

```bash
npm run format      # Prettier
npm run lint        # ESLint
npm run typecheck   # TypeScript strict
npm run test:e2e    # Playwright E2E
```

Or via Makefile:

```bash
make fe-format
make fe-lint
make fe-typecheck
make fe-test-e2e
```

## Critical Rules

1. **Vite only** - No Next.js, no SSR, no server components
2. **Contract-first** - Types from OpenAPI, not Zod
3. **Centralized API** - No fetch outside `src/api/client.ts`
4. **Zod scope** - Forms only, not API contracts
5. **TailwindCSS** - All styling via Tailwind classes
6. **Playwright** - E2E tests use API setup, no sleeps

## AI Agent Instructions

When implementing frontend features:

❌ **Do NOT**:

- Suggest Next.js
- Use Zod to validate API responses
- Add fetch calls in components
- Duplicate backend types in Zod
- Create custom HTTP clients

✅ **Do**:

- Use Vite + React setup
- Generate types from OpenAPI
- Use central `simApi` client
- Use Zod only for form validation
- Reference `src/api/types.ts` for all API types
- Add TailwindCSS classes for styling

## Contract Regeneration

**When backend API changes:**

```bash
npm run contracts:gen
```

This generates `src/api/types.ts` from `../openapi.json`.  
TypeScript will catch breaking changes at compile time.  
Update components to match new contracts.

## Example: Adding New Scenario Parameter

**Backend** adds a new parameter to scenario schema → `openapi.json` updated

**Frontend**:

1. `npm run contracts:gen` → `src/api/types.ts` updated
2. TypeScript error in `src/components/ScenarioCard.tsx`
3. Update form to include new parameter
4. Update Zod validation in `src/schemas/forms.ts` if needed
5. `npm run typecheck` passes
6. `npm run test:e2e` validates E2E flow

**No Zod schemas duplicating the API contract.**
