# Systems Design Lab - Frontend

**Vite + React + TypeScript + TailwindCSS + Zod + Playwright**

## Frontend Architecture & Guardrails

### Technology Stack (NON-NEGOTIABLE)

- **Vite** - Build tool and dev server (NOT Next.js)
- **React 18** - UI framework
- **TypeScript** - Type safety
- **TailwindCSS** - Utility-first styling
- **Zod** - Client-side form validation ONLY (not API contracts)
- **Playwright** - E2E testing
- **openapi-typescript** - Contract-first type generation

### Critical Architecture Rules

#### 1. Contract-First Development

**Single source of truth**: `../openapi.json` (backend OpenAPI snapshot)

```bash
# When backend API changes, regenerate frontend types
npm run contracts:gen
# Generates: src/api/types.ts from ../openapi.json
```

**Flow**:

1. Backend updates OpenAPI spec → `../openapi.json`
2. Frontend runs `npm run contracts:gen`
3. TypeScript types generated in `src/api/types.ts`
4. TypeScript catches breaking changes at compile time
5. Fix components to adapt to new contracts

❌ **NEVER duplicate API contracts with Zod**  
✅ **Always use TypeScript types from generated `src/api/types.ts`**

#### 2. Zod Usage Restrictions

**Zod is ONLY for client-side form validation:**

```typescript
// ✅ CORRECT: Validate form input before API call
import { buildParameterSchema } from '@/schemas/forms';

const zodSchema = buildParameterSchema(backendParamSchema);
zodSchema.parse(formData); // Validate user input
await simApi.enable(scenario, formData); // Then call typed API
```

```typescript
// ❌ WRONG: Do NOT validate API responses with Zod
const response = await fetch('/api/sim/scenarios');
const data = await response.json();
ScenariosSchema.parse(data); // NO! Use TypeScript types instead
```

**Allowed**:

- ✅ Form validation
- ✅ User input validation
- ✅ Dynamic schema building from backend `parameter_schema`

**Forbidden**:

- ❌ API response validation
- ❌ Duplicating backend request/response shapes
- ❌ Replacing TypeScript types from openapi-typescript

#### 3. Centralized API Access

**All API calls MUST go through** `src/api/client.ts`:

```typescript
// ✅ CORRECT: Import from central client
import { simApi } from '@/api/client';

const result = await simApi.scenarios();
if (result.ok) {
  // result.data is fully typed from OpenAPI
  console.log(result.data.scenarios);
}
```

```typescript
// ❌ WRONG: Direct fetch in components
const response = await fetch('/api/sim/scenarios'); // NO!
```

**No scattered** `fetch()` **calls allowed in components**.

## Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   ├── client.ts       # Centralized typed API client
│   │   └── types.ts        # Generated from openapi-typescript
│   ├── schemas/
│   │   └── forms.ts        # Zod schemas for form validation only
│   ├── components/
│   │   ├── GlobalBanner.tsx
│   │   ├── ActiveScenarios.tsx
│   │   └── ScenarioCard.tsx
│   ├── pages/
│   │   └── SimulatorControlPanel.tsx
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css           # Tailwind directives
├── e2e/
│   └── simulator.spec.ts   # Playwright tests
├── index.html              # Vite entry point
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.ts
├── postcss.config.js
└── package.json
```

## Commands

```bash
# Install dependencies
npm install

# Generate types from backend OpenAPI snapshot
npm run contracts:gen

# Development server (port 5173)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run typecheck

# Linting
npm run lint

# Format code
npm run format

# E2E tests (requires backend running)
npm run test:e2e
```

## Development Workflow

```bash
# 1. Backend makes API changes
cd backend
# ... backend development ...
# openapi.json automatically updated

# 2. Regenerate frontend types
cd ../frontend
npm run contracts:gen

# 3. TypeScript will show errors if contracts changed
npm run typecheck

# 4. Fix components to match new contracts
# Update types, function signatures, etc.

# 5. Run guardrails
npm run lint
npm run format
npm run test:e2e
```

## Guardrails (Enforced)

```bash
npm run format      # Prettier
npm run lint        # ESLint (strict)
npm run typecheck   # TypeScript (strict mode)
npm run test:e2e    # Playwright E2E tests
```

Or via Makefile:

```bash
make fe-format
make fe-lint
make fe-typecheck
make fe-test-e2e
```

## Testing Strategy

**Playwright E2E Tests**:

- Enable/disable scenarios via backend API (not UI clicks)
- Use `request` fixture for setup
- No arbitrary sleeps - use proper waits: `expect().toBeVisible({ timeout })`
- Validate UI updates after API changes

## Key Features

- ✅ **Contract-first**: Types from OpenAPI, enforced by TypeScript
- ✅ **Centralized API**: Single typed client module
- ✅ **Zod scope**: Form validation only, not API contracts
- ✅ **TailwindCSS**: All styling via utility classes
- ✅ **Global banner**: Shows active scenario count
- ✅ **Control panel**: Enable/disable scenarios, view status
- ✅ **2-second polling**: Auto-refresh active scenarios
- ✅ **Error handling**: Loading states, error panels, retry buttons

## Environment Variables

Create `.env.local`:

```env
VITE_API_URL=http://localhost:8000
```

## Docker Integration

```bash
# From project root
docker compose up frontend
# → http://localhost:5173
```

## FAQ

**Q: Can I use Next.js instead of Vite?**  
A: NO. Vite is non-negotiable per project requirements.

**Q: Can I use Zod to validate API responses?**  
A: NO. Zod is only for client-side form validation. API contracts are enforced by TypeScript types from openapi-typescript.

**Q: Can I add fetch calls directly in components?**  
A: NO. All API calls must go through `src/api/client.ts`.

**Q: When should I regenerate contracts?**  
A: Whenever `../openapi.json` changes (backend API updates). Run `npm run contracts:gen`.

## Critical Rules

1. **Vite only** - No Next.js, SSR, or server components
2. **Contract-first** - Types from OpenAPI, NOT Zod
3. **Centralized API** - No fetch outside `src/api/client.ts`
4. **Zod scope** - Forms only, NOT API validation
5. **TailwindCSS** - All styling via Tailwind
6. **Playwright** - E2E tests with API setup, no sleeps

## References

- [Vite Documentation](https://vitejs.dev)
- [React Documentation](https://react.dev)
- [TailwindCSS Documentation](https://tailwindcss.com)
- [Zod Documentation](https://zod.dev) (for form validation only)
- [openapi-typescript](https://github.com/drwpow/openapi-typescript)
- [Playwright Documentation](https://playwright.dev)
