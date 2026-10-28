# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some Oxlint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the Oxlint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and Oxlint's TypeScript related rules in your project.

## Unit tests

The unit tests use [Vitest](https://vitest.dev/), [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/) and [jsdom](https://github.com/jsdom/jsdom). They live outside this folder, in `tests/unit/frontend/` at the repository root, mirroring `src/`. The test settings are in `vitest.config.js`.

Run them from this folder:

```bash
npm ci                   # installs the exact versions recorded in package-lock.json
npm run test             # runs every unit test once
npm run test:coverage    # also prints a coverage summary and writes coverage/lcov.info
```

The tests never call the real backend: each test stubs `fetch` and returns a fixed `/api/billing` response. The `coverage/` folder is generated output and is not committed.
