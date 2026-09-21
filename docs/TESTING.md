# NEMESIS — Testing Guide

**Last Updated:** 2026-09-20
**Version:** CP2.5.1

## Test Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| Vitest | 4.1.11 | Test runner |
| Zod | 4.5.4 | Schema validation |
| jsdom | 29.1.1 | Browser simulation |
| @testing-library/react | 16.3.3 | Component testing |

## Test Types

### 1. Contract Tests (Node Env)

Location: src/services/api/__tests__/

Purpose: Verify live backend response against frozen DTO contracts.

Environment: Node (via @vitest-environment node directive)

Why Node env:
- jsdom blocks network (XHR adapter fails)
- Contract tests need real HTTP calls
- Node env has native fetch

Run:
  export VITE_API_URL=http://127.0.0.1:8000/api
  export NEMESIS_TEST_API_URL=http://127.0.0.1:8000/api
  export NEMESIS_TEST_USERNAME=admin
  export NEMESIS_TEST_PASSWORD=<your-rotated-password>
  npm run test:contract

Expected:
  Test Files  3 passed (3)
       Tests  28 passed (28)

### 2. Component Tests (jsdom Env)

Location: src/components/**/*.test.tsx

Purpose: Test UI component behavior.

Environment: jsdom (default from vitest.config.ts)

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| VITE_API_URL | API base URL | /api |
| NEMESIS_TEST_API_URL | Contract test API URL | http://127.0.0.1:8000/api |
| NEMESIS_TEST_USERNAME | Test login username | (required) |
| NEMESIS_TEST_PASSWORD | Test login password | (required) |

Security: Credentials are env-only, never committed to source.

## Contract Test Structure

src/services/api/__tests__/
  schemas/
    graph.schema.ts       (Zod mirror of F3 DTOs)
    risk.schema.ts        (Zod mirror of Risk Engine v3)
  helpers/
    auth.ts               (Login helper with env vars)
  baseline.test.ts          (4 tests - frozen baseline)
  graph.contract.test.ts    (16 tests - F3 contract)
  risk.contract.test.ts     (8 tests - Risk Engine v3)

## Frozen Baseline

| Metric | Value | Provenance |
|--------|-------|------------|
| Risk score | 47.58 | Established frozen |
| Risk level | MEDIUM | Established frozen |
| Graph entities | 4177 | Established frozen |
| Graph relationships | 2424 | Established frozen |
| Collusion relationships | 4 | Current runtime contract |
| GraphNodeDTO shape | 5 fields + id | Established frozen |

Note on Collusion = 4: Current runtime value from
graph_relationships.COLLUSION. Historical frozen provenance not
established. Analytical collusion_detections table remains 0.

## Zod 4 Compatibility

Zod 3 (old):     z.record(z.unknown())
Zod 4 (required): z.record(z.string(), z.unknown())

All schemas must use two arguments for z.record().

## Setup Configuration

Persistent localStorage mock:
- Contract tests set tokens in beforeAll()
- Each test relies on tokens being readable
- DO NOT clear storage per-test (breaks auth)

No fetch mock:
- Removed for contract tests
- Component tests can mock locally if needed

## Troubleshooting

Network Error:
- Check @vitest-environment node is set at top of test file

No refresh token available:
- Check beforeAll(loginForTests()) in test file
- Check setup does not clear storage per-test

ReferenceError: window is not defined:
- client.ts uses window.location.href in error handler
- Guard: if (typeof window !== 'undefined')

MISSING DEPENDENCY Cannot find jsdom:
- Run: npm install --save-dev jsdom

## CI Integration

docker compose up -d api
until curl -sf http://127.0.0.1:8000/health; do sleep 1; done

export VITE_API_URL=http://127.0.0.1:8000/api
export NEMESIS_TEST_USERNAME=$CI_TEST_USERNAME
export NEMESIS_TEST_PASSWORD=$CI_TEST_PASSWORD
npm run test:contract

## References

- Vitest config: vitest.config.ts
- Test setup: src/test/setup.ts
- Frozen DTOs: src/services/api/graph.ts, src/types/risk.ts
- Tag: f3-graph-intelligence-v1 (579e020)
