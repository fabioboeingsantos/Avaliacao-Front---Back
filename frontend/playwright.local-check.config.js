import base from './playwright.config.js'

export default {
  ...base,
  use: { ...base.use, baseURL: 'http://127.0.0.1:5180' },
  webServer: {
    ...base.webServer,
    command: 'npm run dev -- --host 127.0.0.1 --port 5180 --strictPort',
    url: 'http://127.0.0.1:5180',
  },
}
