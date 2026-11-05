import type { E2EConfig } from 'e2e';
import { chatgpt } from 'e2e/oauth/chatgpt';
import responsive from './e2e.config.js';

// Отдельный конфиг: обычный `npx e2e run` не собирает manual/ и не загружает модель.
export default {
  ...responsive,
  tests: 'manual/**/*.ai.e2e.ts',
  output: '.e2e/manual',
  timeout: 180_000,
  trace: 'on',
  agents: {
    default: {
      model: chatgpt('gpt-6-luna'),
      maxSteps: 8,
      maxModelCalls: 8,
      judgmentTimeout: 60_000,
      system: 'Ты тестировщик русскоязычного сайта. Выполняй только текущую цель через элементы интерфейса и проверяй результат на экране.',
      context: 'AskVK — Django-приложение вопросов и ответов с тестовыми данными. Ссылка «Задать вопрос» открывает форму «Новый вопрос». Формы отправляют POST и проверяют данные без сохранения. Ошибки показываются только для невалидных данных. Пагинация работает на сервере; поиск и фильтрация пока не реализованы.',
    },
  },
} satisfies E2EConfig;
