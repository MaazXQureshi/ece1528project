FROM node:22

WORKDIR /app

COPY package*.json ./
RUN npm install

RUN npx prisma generate

COPY . .

EXPOSE 8080

CMD ["npm", "start"]
