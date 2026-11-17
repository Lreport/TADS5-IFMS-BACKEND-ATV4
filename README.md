# TADS5-IFMS-BACKEND-ATV4

Prof. Rogério, essa é a última parte do gerenciador de atividades. A base continua sendo a da atividade anterior, e aqui o foco ficou na documentação das rotas no Swagger e nos testes com Pytest e TestClient.

Vou deixar abaixo como rodar o projeto e testar essa parte, seguindo a mesma ideia das atividades anteriores.

## Como rodar

Abra a pasta do projeto no VS Code e abra um terminal PowerShell.

1. Se for a primeira vez rodando o projeto, crie o ambiente virtual, instale as dependências e faça as migrações:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   .\.venv\Scripts\python.exe -m alembic upgrade head
   ```

2. Crie a conta do aluno:

   ```powershell
   .\.venv\Scripts\python.exe -m create_user
   ```

   Coloque o e-mail e uma senha. O terminal pede a confirmação e a senha não aparece enquanto você digita. No banco fica salvo o hash dela.

3. Gere uma chave de assinatura e inicie a API no mesmo terminal:

   ```powershell
   $env:JWT_SECRET_KEY = .\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(32))"
   .\.venv\Scripts\python.exe -m uvicorn main:app --reload
   ```

   A chave fica nesse terminal, então deixe ele aberto enquanto usa a API. Se gerar outra chave, faça login de novo para pegar um novo token. Para parar o servidor, dê `Ctrl+C`.

4. Com a API rodando, abra o [Swagger](http://127.0.0.1:8000/docs).

## Como testar pelo Swagger

No Swagger, as rotas ficam separadas em **Autenticação** e **Atividades**. Cada uma tem uma descrição do que faz, dos campos que recebe e das respostas que pode retornar.

1. Antes de fazer login, tente executar **GET /activities**, clicando em **Try it out** e depois em **Execute**. Deve voltar **401**, porque essa rota precisa de um token.
2. Clique em **Authorize**. Coloque o e-mail do aluno em `username` e a senha em `password`. Deixe os campos de cliente vazios. Depois clique em **Authorize** e em **Close**. O Swagger faz o login pela rota `POST /token` e passa a enviar o token nas próximas requisições.
3. Execute **GET /activities** de novo. Agora deve voltar **200**, com as atividades cadastradas ou `[]` se o banco estiver vazio.
4. Para cadastrar uma atividade, use **POST /activities** e preencha `title` e `subject`. Os campos `description` e `done` são opcionais. Se estiver tudo certo, volta **201**, com os dados da atividade e o `id` gerado pela API.

O token dura 30 minutos. Quando expirar, é só fazer login de novo pelo **Authorize**. Todas as rotas de atividades precisam dele.

Também dá para consultar uma atividade pelo ID em **GET /activities/{activity_id}**, editar pelo **PUT** e excluir pelo **DELETE**. A exclusão retorna **204**, sem nada no corpo da resposta.

Na listagem, o campo `subject` filtra pela disciplina e o `done` separa as concluídas (`true`) das pendentes (`false`). Dá para usar os dois juntos.

Um detalhe do **PUT**: ele troca todos os dados da atividade. Precisa mandar `title` e `subject`; se não mandar `description`, ela fica `null`, e se não mandar `done`, ele fica `false`.

Se o ID não existir, volta **404**. Se algum campo estiver inválido, volta **422**. O **503** indica que a autenticação está indisponível por causa da configuração do servidor, como a falta da chave de assinatura.

## Como rodar os testes

Com o ambiente virtual criado, instale as dependências dos testes e rode o Pytest:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

Não precisa deixar a API rodando para isso, o TestClient faz as requisições durante os testes. Eles também criam bancos temporários, uma conta e uma chave de teste, então o arquivo `activities.db` do projeto fica como estava.

Os casos de teste são:

- Cadastrar uma atividade e consultar os dados depois, esperando **201** e **200**.
- Listar as atividades usando os filtros de disciplina e conclusão.
- Atualizar uma atividade mantendo o mesmo ID.
- Excluir uma atividade e conferir se ela saiu do banco, esperando **204** na exclusão e **404** na consulta seguinte.
- Tentar consultar, atualizar ou excluir um ID que não existe, esperando **404**.
- Tentar acessar as rotas sem token, esperando **401**.
- Fazer login e conferir a assinatura e a validade do token.
- Mandar dados inválidos no cadastro, esperando **422** e nenhum registro criado.

Os testes das atividades ficam em [test_activity.py](tests/test_activity.py), e os de login e token em [test_auth.py](tests/test_auth.py). Também tem os testes da criação da conta em [test_create_user.py](tests/test_create_user.py) e das migrações em [test_migrations.py](tests/test_migrations.py).
