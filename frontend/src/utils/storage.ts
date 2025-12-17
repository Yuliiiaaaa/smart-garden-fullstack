// src/utils/storage.ts
export const storage = {
  // Сохранение данных
  set: <T>(key: string, value: T): void => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('Ошибка сохранения в localStorage:', error);
    }
  },

  // Получение данных
  get: <T>(key: string, defaultValue?: T): T | null => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue || null;
    } catch (error) {
      console.error('Ошибка чтения из localStorage:', error);
      return defaultValue || null;
    }
  },

  // Удаление данных
  remove: (key: string): void => {
    localStorage.removeItem(key);
  },

  // Очистка всех данных
  clear: (): void => {
    localStorage.clear();
  },
};