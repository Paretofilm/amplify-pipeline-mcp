# Example: Adding Test Integration

## Scenario
You want to add testing to your pipeline to ensure code quality.

## Option 1: Using Claude Code

```
You: "Add testing to my pipeline"
```

Claude will automatically set up test integration.

## Option 2: Using the Script

```bash
cd your-project
./scripts/add-features.sh test
```

## What Gets Added

### 1. Test Runner Workflow

```yaml
# .github/workflows/test.yml
name: Test Runner

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      - run: npm ci
      - run: npm test -- --coverage --passWithNoTests
      - uses: actions/upload-artifact@v3
        with:
          name: coverage
          path: coverage/
```

### 2. Update Main Pipeline

The main pipeline now includes:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      # ... test steps

  deploy:
    needs: [test]  # Only deploy if tests pass
    # ... deployment steps
```

## Setting Up Tests

### 1. Install Jest (if not already installed)

```bash
npm install --save-dev jest @types/jest
```

### 2. Add Test Script to package.json

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  }
}
```

### 3. Configure Jest

Create `jest.config.js`:

```javascript
module.exports = {
  testEnvironment: 'node',
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

### 4. Write Your First Test

```javascript
// src/utils/example.test.js
describe('Example Test', () => {
  it('should pass', () => {
    expect(true).toBe(true);
  });
});
```

## Coverage Reports

### On Pull Requests

The pipeline automatically comments coverage on PRs:

```markdown
## Test Coverage Report 📊

| Type | Coverage |
|------|----------|
| Lines | 85.2% |
| Statements | 84.7% |
| Functions | 78.3% |
| Branches | 82.1% |
```

### Viewing Full Reports

1. Go to GitHub Actions
2. Click on the test workflow run
3. Download the coverage artifact
4. Open `index.html` in the coverage folder

## Best Practices

### 1. Test Organization

```
src/
├── components/
│   ├── Button.tsx
│   └── Button.test.tsx
├── utils/
│   ├── helpers.ts
│   └── helpers.test.ts
```

### 2. Test Naming

```javascript
describe('Button Component', () => {
  it('should render with text', () => {});
  it('should handle click events', () => {});
  it('should be disabled when prop is true', () => {});
});
```

### 3. Coverage Goals

- Start with 60% coverage
- Gradually increase to 80%
- Focus on critical paths
- Don't test implementation details

## Troubleshooting

### Tests Failing in CI but Passing Locally

Check:
1. Node version matches (v18)
2. Environment variables are set
3. File paths are case-sensitive in CI

### Coverage Too Low

1. Add more unit tests
2. Focus on untested functions
3. Check coverage report for gaps

### Tests Running Slowly

1. Use `--runInBand` for CI
2. Mock external dependencies
3. Use test.skip for slow integration tests

## Next Steps

1. Add E2E tests with Cypress
2. Add visual regression tests
3. Set up test database for integration tests