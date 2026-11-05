import type { E2EConfig } from 'e2e';
import { web } from '@e2e-dev/web';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../../', import.meta.url));
const venvPython = fileURLToPath(new URL(
  process.platform === 'win32' ? '../../.venv/Scripts/python.exe' : '../../.venv/bin/python',
  import.meta.url,
));
const python = process.env.E2E_PYTHON ?? (existsSync(venvPython) ? venvPython : 'python3.14');

function application(name: string) {
  // Можно проверить уже запущенный Django/nginx вместо изолированного сервера.
  if (process.env.E2E_BASE_URL) return { url: process.env.E2E_BASE_URL };
  return {
    url: 'http://127.0.0.1:0',
    command: {
      executable: python,
      args: [fileURLToPath(new URL('./scripts/serve_django.py', import.meta.url)), '{port}'],
      cwd: root,
      startupTimeout: 60_000,
      log: `.e2e/logs/server-${name}.log`,
    },
  };
}

export default {
  tests: 'tests/**/*.e2e.ts',
  targets: [
    { name: 'mobile-375', engine: web({ viewport: { width: 375, height: 812 } }), app: application('mobile-375') },
    { name: 'tablet-768', engine: web({ viewport: { width: 768, height: 1024 } }), app: application('tablet-768') },
    { name: 'desktop-1200', engine: web({ viewport: { width: 1200, height: 900 } }), app: application('desktop-1200') },
  ],
  workers: 1,
  retries: 0,
  timeout: 30_000,
  trace: 'retain-on-failure',
  cache: 'off',
  // В обычном наборе нет agent.* — модель и API-ключи не нужны.
} satisfies E2EConfig;
