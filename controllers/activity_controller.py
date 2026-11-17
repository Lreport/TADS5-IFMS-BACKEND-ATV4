"""Recebe as requisicoes HTTP e chama as operacoes do model."""

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Path,
    Query,
    Response,
    status,
)
from sqlalchemy.orm import Session

from controllers.auth_controller import require_authenticated_user
from database import get_session
from models import activity as activity_model
from models.activity import Activity, ActivityInput, ActivityOutput, Subject


router = APIRouter(
    prefix="/activities",
    tags=["Atividades"],
    dependencies=[Depends(require_authenticated_user)],
    responses={
        401: {
            "description": "Token Bearer ausente, inválido ou expirado.",
            "content": {
                "application/json": {
                    "examples": {
                        "sem_token": {
                            "summary": "Requisição sem token",
                            "value": {"detail": "Not authenticated"},
                        },
                        "token_invalido": {
                            "summary": "Token inválido ou expirado",
                            "value": {"detail": "Token inválido ou expirado."},
                        },
                    }
                }
            },
        },
        503: {"description": "Autenticação indisponível por configuração do servidor."},
    },
)


_NOT_FOUND_RESPONSE = {
    "description": "Nenhuma atividade foi encontrada com o ID informado.",
    "content": {
        "application/json": {"example": {"detail": "Atividade nao encontrada."}}
    },
}


@router.post(
    "",
    response_model=ActivityOutput,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar uma atividade",
    description=(
        "Cadastra uma atividade a partir dos campos de formulário.\n\n"
        "- `title`: obrigatório, com 1 a 100 caracteres após remover espaços nas pontas.\n"
        "- `subject`: obrigatório, com uma das disciplinas permitidas.\n"
        "- `description`: opcional, com até 500 caracteres.\n"
        "- `done`: opcional; assume `false` quando omitido.\n\n"
        "O identificador é gerado pela API. Requer autenticação Bearer."
    ),
    response_description="Atividade cadastrada, incluindo o identificador gerado.",
)
def create_activity(
    data: Annotated[ActivityInput, Form()],
    session: Annotated[Session, Depends(get_session)],
) -> Activity:
    """Recebe o formulario e cadastra uma atividade.

    Args:
        data (ActivityInput): Dados validados recebidos nos campos do formulario.
        session (Session): Sessao do banco recebida por injecao de dependencia.

    Returns:
        Activity: Atividade cadastrada, usada no corpo da resposta HTTP 201.
    """
    return activity_model.create(data, session)


@router.get(
    "",
    response_model=list[ActivityOutput],
    summary="Listar atividades",
    description=(
        "Lista as atividades em ordem crescente de identificador.\n\n"
        "Use `subject` para filtrar pela disciplina e `done` para selecionar "
        "concluídas (`true`) ou pendentes (`false`). Os filtros podem ser combinados. "
        "Sem filtros, retorna todas as atividades. Quando não há resultados, "
        "retorna uma lista vazia (`[]`). Requer autenticação Bearer."
    ),
    response_description="Lista de atividades que correspondem aos filtros informados.",
)
def list_activities(
    session: Annotated[Session, Depends(get_session)],
    subject: Annotated[
        Subject | None, Query(description="Filtrar pelo nome completo da disciplina.")
    ] = None,
    done: Annotated[
        bool | None, Query(description="Filtrar atividades concluídas ou pendentes.")
    ] = None,
) -> list[Activity]:
    """Consulta as atividades com filtros opcionais.

    Args:
        session (Session): Sessao do banco recebida por injecao de dependencia.
        subject (Subject | None, optional): Disciplina usada no filtro. None inclui
            todas as disciplinas. Padrao: None.
        done (bool | None, optional): True inclui concluidas e False inclui pendentes.
            None inclui ambas. Padrao: None.

    Returns:
        list[Activity]: Lista de atividades que correspondem aos filtros.
    """
    return activity_model.get_all(session, subject, done)


@router.get(
    "/{activity_id}",
    response_model=ActivityOutput,
    summary="Consultar uma atividade",
    description=(
        "Consulta uma atividade pelo seu identificador inteiro e positivo. "
        "Retorna 404 quando a atividade não existe. Requer autenticação Bearer."
    ),
    response_description="Dados da atividade correspondente ao identificador.",
    responses={404: _NOT_FOUND_RESPONSE},
)
def get_activity(
    activity_id: Annotated[
        int, Path(gt=0, description="Identificador inteiro e positivo da atividade.")
    ],
    session: Annotated[Session, Depends(get_session)],
) -> Activity:
    """Consulta uma atividade pelo identificador.

    Args:
        activity_id (int): Identificador positivo recebido no caminho da requisicao.
        session (Session): Sessao do banco recebida por injecao de dependencia.

    Raises:
        HTTPException: Erro HTTP 404 quando a atividade nao existe.

    Returns:
        Activity: Dados da atividade encontrada.
    """
    activity = activity_model.get_by_id(activity_id, session)
    if activity is None:
        raise HTTPException(status_code=404, detail="Atividade nao encontrada.")
    return activity


@router.put(
    "/{activity_id}",
    response_model=ActivityOutput,
    summary="Substituir os dados de uma atividade",
    description=(
        "Substitui os dados de uma atividade existente, mantendo seu identificador. "
        "Envie os campos de formulário `title` e `subject`, que são obrigatórios.\n\n"
        "**Atenção:** o PUT substitui todos os dados. Ao omitir `description`, "
        "ela passa a ser `null`; ao omitir `done`, ele passa a ser `false`. "
        "Retorna 404 quando a atividade não existe. Requer autenticação Bearer."
    ),
    response_description="Atividade atualizada, com o mesmo identificador.",
    responses={404: _NOT_FOUND_RESPONSE},
)
def update_activity(
    activity_id: Annotated[
        int, Path(gt=0, description="Identificador inteiro e positivo da atividade.")
    ],
    data: Annotated[ActivityInput, Form()],
    session: Annotated[Session, Depends(get_session)],
) -> Activity:
    """Substitui os dados de uma atividade existente.

    Args:
        activity_id (int): Identificador positivo da atividade que sera atualizada.
        data (ActivityInput): Novos dados. Campos opcionais omitidos usam
            description=None e done=False.
        session (Session): Sessao do banco recebida por injecao de dependencia.

    Raises:
        HTTPException: Erro HTTP 404 quando a atividade nao existe.

    Returns:
        Activity: Atividade atualizada com o mesmo identificador.
    """
    activity = activity_model.update(activity_id, data, session)
    if activity is None:
        raise HTTPException(status_code=404, detail="Atividade nao encontrada.")
    return activity


@router.delete(
    "/{activity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Excluir uma atividade",
    description=(
        "Exclui a atividade correspondente ao identificador informado. "
        "Quando a exclusão é concluída, retorna 204 sem corpo de resposta. "
        "Retorna 404 quando a atividade não existe. Requer autenticação Bearer."
    ),
    response_description="Atividade excluída; a resposta não possui corpo.",
    responses={404: _NOT_FOUND_RESPONSE},
)
def delete_activity(
    activity_id: Annotated[
        int, Path(gt=0, description="Identificador inteiro e positivo da atividade.")
    ],
    session: Annotated[Session, Depends(get_session)],
) -> Response:
    """Exclui uma atividade pelo identificador.

    Args:
        activity_id (int): Identificador positivo da atividade que sera removida.
        session (Session): Sessao do banco recebida por injecao de dependencia.

    Raises:
        HTTPException: Erro HTTP 404 quando a atividade nao existe.

    Returns:
        Response: Resposta HTTP 204 sem corpo.
    """
    if not activity_model.delete(activity_id, session):
        raise HTTPException(status_code=404, detail="Atividade nao encontrada.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
