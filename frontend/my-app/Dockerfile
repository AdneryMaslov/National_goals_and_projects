# frontend/my-app/Dockerfile

# --- ЭТАП 1: Сборка приложения ---
# --- ИЗМЕНЕНИЕ ЗДЕСЬ: Обновляем версию Node.js до 20 ---
FROM node:20 AS build

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем переменную окружения для всей стадии сборки.
# Оставляем это на всякий случай, это не должно навредить.
ENV NODE_OPTIONS=--openssl-legacy-provider

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем остальной код приложения
COPY . .

# Запускаем сборку
RUN npm run build

# --- ЭТАП 2: Сервировка статических файлов ---
FROM nginx:stable-alpine

# Копируем собранные файлы из этапа "build" в директорию Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Копируем кастомную конфигурацию Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Открываем порт 80
EXPOSE 80

# Команда для запуска Nginx
CMD ["nginx", "-g", "daemon off;"]
