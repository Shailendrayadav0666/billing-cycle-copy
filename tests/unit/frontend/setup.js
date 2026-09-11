import '@testing-library/jest-dom/vitest'
import { configure } from '@testing-library/react'

// Default waitFor timeout (1000ms) is tight on a cold/shared CI runner for an assertion that waits on
// a fetch().then().catch() chain plus a React state update; raise the margin rather than race it.
configure({ asyncUtilTimeout: 5000 })
