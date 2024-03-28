FROM node:18-slim

ARG PROJ_DIR=/vue_proj

RUN mkdir -p ${PROJ_DIR}
COPY ./frontend ${PROJ_DIR}

WORKDIR ${PROJ_DIR}

RUN npm install -g npm

COPY ./frontend/package.json ${PROJ_DIR}
COPY ./frontend/package-lock.json ${PROJ_DIR}

RUN npm i -g @quasar/cli
RUN npm install

CMD [ "quasar", "dev" ]