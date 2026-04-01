FROM node:22-alpine

WORKDIR /app
COPY package.json tsconfig.json next-env.d.ts next.config.mjs postcss.config.js tailwind.config.ts /app/
COPY app /app/app
COPY components /app/components
COPY lib /app/lib

RUN npm install
RUN npm run build

CMD ["npm", "run", "start"]
