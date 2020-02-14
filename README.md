# Gestor Arhivos

## Descripción

## Artefactos producidos

## Requisitos

## Pruebas

## Librerias Backend (Python 3)

- pip3
- Flask == 1.1.1
- flask_mysqldb
- mysqlclient==1.4.4
- pep8==1.7.1
- autopep8==1.4.4
- flake8==3.7.9
- Flask-MySQLdb==0.2.0
- Google Drive API V3
  - google-api-python-client == 1.7.11
  - google-auth == 1.6.3
  - google-auth-httplib2 == 0.0.3
  - google-auth-oauthlib == 0.4.1
  - google-pasta == 0.1.7

---

## Comandos de Ejecución

- Html, Css, Javascript

  - formateo Prettier

  ```json
      "editor.rulers": [100],
      "editor.defaultFormatter": "esbenp.prettier-vscode",
      "editor.formatOnSave": true,
      "prettier.arrowParens": "always",
      "prettier.bracketSpacing": true,
      "prettier.htmlWhitespaceSensitivity": "css",
      "prettier.insertPragma": false,
      "prettier.jsxBracketSameLine": false,
      "prettier.jsxSingleQuote": true,
      "prettier.printWidth": 80,
      "prettier.proseWrap": "always",
      "prettier.quoteProps": "as-needed",
      "prettier.requirePragma": false,
      "prettier.semi": false,
      "prettier.singleQuote": true,
      "prettier.tabWidth": 2,
      "prettier.trailingComma": "all",
      "prettier.useTabs": true,
      "prettier.vueIndentScriptAndStyle": true
  ```

- Python

  - ejecutar

  ```console
  ~/Backend >> python3 app.py
  ```

  - formateo

  ```console
  ~/Backend >> autopep8 --in-place --aggressive --aggressive app.py
  ```

  - revision de errores

  ```console
  ~/Backend >> flake8 .
  ```

- Docker

  - Docker Compose
    - Docker-Compose build / service build

  ```console
  ~/Backend >> docker-compose build
  ```

  - Docker-Compose up / service start

  ```console
  ~/Backend >> docker-compose up
  ```

  - Docker-Compose down / service down

  ```console
  ~/Backend >> docker-compose up
  ```

  - Docker
    - compilar / guardar cambios

  ```console
  ~Backend >> docker build -t gestor .
  ```

  - ejecutar

  ```console
  ~Backend >> docker run -it -p 3000:4000 gestor
  ```

---

## **Tasks**

- [x] Backend
  - [x] Coding Methods
    - [x] GET
    - [x] POST
    - [x] GET/ID
    - [x] PUT/ID
    - [x] DELETE/ID
- [x] Frontend
  - [x] Design
  - [x] Link Pages
- [x] Testing
- [ ] Deploy
