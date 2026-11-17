from fastapi import FastAPI

from controllers.activity_controller import router as activity_router
from controllers.auth_controller import router as auth_router


app = FastAPI(
    title="Gerenciador de Atividades",
    version="1.0.0",
    description=(
        "API para gerenciar as atividades das disciplinas atuais do curso. "
        "Permite cadastrar, consultar, filtrar, atualizar e excluir atividades.\n\n"
        "### Como autenticar\n"
        "Clique em **Authorize** e informe o e-mail cadastrado no campo "
        "`username` e a senha no campo `password`. O login emite um token "
        "Bearer válido por **30 minutos**. Todas as operações de atividades "
        "exigem esse token."
    ),
    openapi_tags=[
        {
            "name": "Autenticação",
            "description": "Login do aluno e emissão do token de acesso Bearer.",
        },
        {
            "name": "Atividades",
            "description": (
                "Cadastro, consulta, filtros, atualização e exclusão de atividades. "
                "Todas as operações deste grupo exigem autenticação."
            ),
        },
    ],
)

app.include_router(activity_router)
app.include_router(auth_router)
