import type { E2EConfig } from 'e2e';
import { web } from '@e2e-dev/web';
import { fileURLToPath } from 'node:url';

const app = {
  // Свободный порт: не мешает серверу, уже запущенному на 8000.
  url: 'http://127.0.0.1:0',
  command: {
    executable: 'python3',
    args: ['-m', 'http.server', '{port}', '--bind', '127.0.0.1', '--directory',
      fileURLToPath(new URL('../../public/', import.meta.url))],
    log: '.e2e/logs/server.log',
  },
};

export default {
  tests: 'tests/**/*.e2e.ts',
  targets: [
    { name: 'mobile-375', engine: web({ viewport: { width: 375, height: 812 } }), app },
    { name: 'tablet-768', engine: web({ viewport: { width: 768, height: 1024 } }), app },
    { name: 'desktop-1200', engine: web({ viewport: { width: 1200, height: 900 } }), app },
  ],
  workers: 1,
  retries: 0,
  timeout: 30_000,
  trace: 'retain-on-failure',
  cache: 'off',
  // Все проверки точные, без agent.*: модель и API-ключи не нужны.
} satisfies E2EConfig;
