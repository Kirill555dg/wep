# WEP E2E Testing

## Commands

```bash
npm run test:e2e    # Run E2E tests (requires backend running)
npm run cypress     # Open Cypress UI

# Manual setup
cd deploy && docker compose up -d
cd ../backend && uv run uvicorn app.main:app --reload --port 8023 &
cd ../frontend && bun run dev &
```

## Test Data

Uses existing `cypress/fixtures/user.json` - teacher user with Russian fields.

## Scenarios

1. Teacher creates public test - solves formula support problem
2. Student takes test - solves automatic grading problem
