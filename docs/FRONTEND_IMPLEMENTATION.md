# Frontend Branch Work - Implementation Guide

This document outlines the implementation plan for the `feature/frontend-simulator-ui` branch.

## 🎯 Branch Goal

Create a production-grade frontend for the Systems Design Lab simulator with:

- Vite + React + TypeScript setup
- Typed API client from OpenAPI contracts
- SimulatorControlPanel component
- Resilient error handling
- Playwright E2E tests

---

## 📋 Implementation Checklist

### Phase 1: Project Initialization

- [ ] Create `frontend/` directory
- [ ] Initialize Vite project with React + TypeScript
- [ ] Setup package.json with key dependencies
- [ ] Configure TypeScript (strict mode)
- [ ] Setup Prettier and ESLint
- [ ] Configure Playwright for E2E tests
- [ ] Add frontend service to docker-compose.yml

### Phase 2: API Integration

- [ ] Generate TypeScript types from openapi.json
- [ ] Create axios instance with interceptors
- [ ] Implement API client functions:
  - [ ] `listScenarios()` → GET /api/sim/scenarios
  - [ ] `getStatus()` → GET /api/sim/status
  - [ ] `enableScenario()` → POST /api/sim/enable
  - [ ] `disableScenario()` → POST /api/sim/disable
  - [ ] `resetAll()` → POST /api/sim/reset
- [ ] Setup React Query hooks
- [ ] Add error retry logic with exponential backoff

### Phase 3: Core Components

#### ScenarioCard Component

- [ ] Display scenario name, description, targets
- [ ] Show parameter schema as JSON Schema form
- [ ] Enable/disable button with loading state
- [ ] Validation for required parameters
- [ ] Error display for failed operations

#### ScenarioList Component

- [ ] Fetch and display all available scenarios (5 total)
- [ ] Loading skeleton for async state
- [ ] Error boundary for fetch failures
- [ ] Filter/search functionality (optional)
- [ ] Group by category (http, db, etc.)

#### ActiveIndicator Component

- [ ] Banner showing active scenarios
- [ ] Display: scenario name, parameters, expiry time
- [ ] Quick disable button per scenario
- [ ] Reset all button
- [ ] Auto-refresh every 5 seconds
- [ ] Dismiss/minimize functionality

#### SimulatorControlPanel Page

- [ ] Layout: Header + ActiveIndicator + ScenarioList
- [ ] Responsive design (mobile-friendly)
- [ ] Dark mode support (optional)
- [ ] Keyboard navigation

### Phase 4: Error Handling & Resilience

- [ ] Error boundary component
- [ ] Toast/notification system for errors
- [ ] Graceful degradation when backend slow/failing
- [ ] Retry logic for failed requests
- [ ] Loading states for all async operations
- [ ] Optimistic UI updates where appropriate

### Phase 5: Testing

#### E2E Tests (Playwright)

- [ ] Test: Load control panel, see 15 scenarios listed
- [ ] Test: Enable fixed-latency (100ms), verify delay on subsequent requests
- [ ] Test: Enable error-burst (50% error rate), verify UI handles failures
- [ ] Test: Enable scenario, see it in active indicator
- [ ] Test: Disable individual scenario
- [ ] Test: Reset all scenarios
- [ ] Test: UI remains functional when backend is slow
- [ ] Test: UI remains functional when backend returns errors

#### Unit Tests (Vitest - optional for this phase)

- [ ] Test API client functions
- [ ] Test React Query hooks
- [ ] Test component render logic

### Phase 6: Documentation & Polish

- [ ] Update README.md with frontend instructions
- [ ] Add frontend Makefile targets
- [ ] User guide for control panel
- [ ] Screenshots/GIFs of UI in action
- [ ] Accessibility audit (WCAG compliance)

---

## 🏗️ File Structure

```
frontend/
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   ├── api/
│   │   ├── client.ts          # Axios instance with interceptors
│   │   ├── simulator.ts       # Typed simulator API functions
│   │   └── types.ts           # Generated from OpenAPI
│   ├── components/
│   │   ├── ErrorBoundary.tsx
│   │   ├── ScenarioCard.tsx
│   │   ├── ScenarioList.tsx
│   │   ├── ActiveIndicator.tsx
│   │   └── LoadingSpinner.tsx
│   ├── pages/
│   │   └── SimulatorControlPanel.tsx
│   ├── hooks/
│   │   └── useSimulator.ts   # React Query hooks
│   └── styles/
│       └── globals.css
├── e2e/
│   ├── simulator.spec.ts
│   └── fixtures/
│       └── scenarios.json     # Mock scenario data
├── public/
├── Dockerfile
├── package.json
├── tsconfig.json
├── vite.config.ts
├── playwright.config.ts
├── .prettierrc.json
└── .eslintrc.json
```

---

## 🎨 UI Design Principles

### Control Panel Layout

```
┌────────────────────────────────────────────┐
│  Systems Design Lab - Simulator Control    │
├────────────────────────────────────────────┤
│  🔴 ACTIVE: fixed-latency (100ms) [×]      │  ← Active Indicator
│  🔴 ACTIVE: error-burst (25%) [×]          │
│  [Reset All]                               │
├────────────────────────────────────────────┤
│                                            │
│  Available Scenarios (5)                   │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │  Fixed Latency                       │ │
│  │  Adds fixed delay to HTTP requests   │ │
│  │  Targets: HTTP                       │ │
│  │                                      │ │
│  │  Parameters:                         │ │
│  │    ms: [100] (1-10000)              │ │
│  │    probability: [1.0] (0.0-1.0)     │ │
│  │                                      │ │
│  │  [Enable Scenario]                   │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │  Error Burst                         │ │
│  │  Probabilistic 5xx errors            │ │
│  │  ...                                 │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  (3 more scenarios...)                     │
└────────────────────────────────────────────┘
```

### Design Requirements

- Clean, professional appearance
- Clear visual hierarchy
- Prominent active scenario indicator
- Easy parameter input with validation
- Accessible (keyboard navigation, ARIA labels)
- Responsive (works on mobile)

---

## 🛠️ Key Dependencies

```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "@tanstack/react-query": "^5.0.0",
    "axios": "^1.6.0",
    "zod": "^3.22.0",
    "react-hook-form": "^7.49.0",
    "@hookform/resolvers": "^3.3.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "@playwright/test": "^1.40.0",
    "prettier": "^3.1.0",
    "eslint": "^8.56.0",
    "@typescript-eslint/eslint-plugin": "^6.18.0",
    "@typescript-eslint/parser": "^6.18.0",
    "vitest": "^1.1.0",
    "@testing-library/react": "^14.1.0"
  }
}
```

---

## 🧪 Testing Strategy

### E2E Test Example

```typescript
import { test, expect } from "@playwright/test";

test.describe("Simulator Control Panel", () => {
  test.beforeEach(async ({ page }) => {
    // Reset simulator state
    await page.request.post("http://localhost:8000/api/sim/reset");
    await page.goto("http://localhost:5173");
  });

  test("should list all available scenarios", async ({ page }) => {
    await expect(page.locator('[data-testid="scenario-card"]')).toHaveCount(5);
    await expect(page.getByText("Fixed Latency")).toBeVisible();
    await expect(page.getByText("Error Burst")).toBeVisible();
  });

  test("should enable fixed-latency and observe delay", async ({
    page,
    request,
  }) => {
    // Enable scenario via UI
    await page.getByLabel("ms").fill("500");
    await page.getByRole("button", { name: "Enable Fixed Latency" }).click();

    // Verify active indicator appears
    await expect(page.locator('[data-testid="active-banner"]')).toContainText(
      "fixed-latency",
    );

    // Make API request and measure time
    const startTime = Date.now();
    const response = await request.get("http://localhost:8000/api/health");
    const endTime = Date.now();

    expect(response.ok()).toBeTruthy();
    expect(endTime - startTime).toBeGreaterThanOrEqual(500);
  });

  test("should handle backend errors gracefully", async ({ page }) => {
    // Simulate backend failure (stop backend container)
    // UI should show error state but not crash

    await expect(page.locator('[data-testid="error-message"]')).toContainText(
      "Unable to load scenarios",
    );
    await expect(page.locator('[data-testid="retry-button"]')).toBeVisible();
  });
});
```

---

## 🚀 Development Workflow

### Local Development

```bash
# Terminal 1: Run backend
make up

# Terminal 2: Run frontend dev server
cd frontend
npm run dev

# Terminal 3: Watch tests
npm run test:e2e -- --ui
```

### Docker Development

```bash
# Build and run everything
docker-compose up --build

# Frontend available at http://localhost:5173
# Backend available at http://localhost:8000
```

---

## ✅ Definition of Done

Before merging this branch, ensure:

1. **Functionality**
   - All 15 scenarios can be enabled/disabled via UI
   - Parameters are validated before submission
   - Active scenarios shown in banner
   - Reset all functionality works

2. **Quality**
   - All E2E tests pass
   - No TypeScript errors (`make fe-typecheck`)
   - No ESLint errors (`make fe-lint`)
   - Code formatted with Prettier (`make fe-format`)
   - Error boundaries catch and display errors gracefully

3. **Documentation**
   - README.md updated with frontend instructions
   - QUICK_START.md includes frontend setup
   - Code comments for complex logic
   - README includes screenshots

4. **Integration**
   - docker-compose.yml includes frontend service
   - Makefile has frontend targets
   - Frontend can communicate with backend
   - CORS configured correctly

5. **Observability**
   - Request IDs propagated from backend to UI
   - Errors logged to console with context
   - Loading states visible to user

---

## 📚 References

- [Vite Documentation](https://vitejs.dev/)
- [React Query Documentation](https://tanstack.com/query/latest)
- [Playwright Documentation](https://playwright.dev/)
- [OpenAPI TypeScript Generator](https://github.com/drwpow/openapi-typescript)
- [React Hook Form](https://react-hook-form.com/)
- [Zod Validation](https://zod.dev/)

---

**Ready to start? Begin with Phase 1: Project Initialization** 🚀
