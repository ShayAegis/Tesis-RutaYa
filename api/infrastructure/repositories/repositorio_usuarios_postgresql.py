from datetime import datetime, timezone, timedelta
from typing import Union
from sqlalchemy import Select, update, insert
from sqlalchemy.orm import Session

from domain.repositories.repositorio_usuarios import RepositorioUsuarios
from domain.entities.usuario import Usuario as UsuarioDominio
from infrastructure.models.usuario import Usuario, RefreshToken
from passlib.hash import django_pbkdf2_sha256


class RepositorioUsuariosPostgreSql(RepositorioUsuarios):
    def __init__(self,db: Session):
        self.db = db
    def usuario_existe(self, email:str) -> bool:
        stmt = ( Select(Usuario)
                 .where(Usuario.email == email) )
        usuario = self.db.execute(stmt).scalar()
        return usuario is not None
    def obtener_usuario_por_correo(self,email:str) -> UsuarioDominio | None:

        stmt = ( Select(Usuario)
                 .where(Usuario.email == email) )

        usuario_modelo: Union[Usuario,None] = self.db.execute(stmt).scalar()

        if usuario_modelo is not None:

            return UsuarioDominio(
                id=usuario_modelo.id,
                email=usuario_modelo.email,
                nombres=usuario_modelo.first_name,
                apellidos=usuario_modelo.last_name,
                contrasenia=usuario_modelo.password
            )

        return None

    def crear_usuario(self,usuario:UsuarioDominio):

        email = usuario.email
        arroba_indice = email.index("@")
        nombre_usuario = email[:arroba_indice]

        self.db.add(Usuario(
            email=usuario.email,
            first_name=usuario.nombres,
            last_name=usuario.apellidos,
            password=django_pbkdf2_sha256.hash(usuario.contrasenia),
            username=nombre_usuario,
            is_superuser=False,
            is_staff=True,
            is_active=True,
            date_joined=datetime.now(),
            empresa_id=None
        ))
        
        self.db.commit()

    def actualizar_ultimo_login(self,email:str):
        stmt = ( update(Usuario)
                 .where(Usuario.email == email)
                 .values(last_login=datetime.now(timezone.utc)) )
        self.db.execute(stmt)
        self.db.commit()

    def guardar_token_refresco(self,usuario: UsuarioDominio, token_hash: str,expiration: datetime):
        stmt = (  insert(RefreshToken)
                  .values(token_hash=token_hash,
                          usuario_id=usuario.id,
                          issued_at=datetime.now(timezone.utc),
                          expires_at=expiration,
                          used_at=None) )
        self.db.execute(stmt)
        self.db.commit()
    def usar_token_refresco(self, token_hash: str) -> UsuarioDominio | None:
        # UPDATE...RETURNING atómico: valida y marca como usado en una sola
        # sentencia para que dos requests concurrentes con el mismo token no
        # puedan pasar ambas la validación (evita reuso/rotación duplicada).
        now = datetime.now(timezone.utc)
        stmt = ( update(RefreshToken)
                 .where(RefreshToken.token_hash == token_hash,
                        RefreshToken.used_at.is_(None),
                        RefreshToken.expires_at >= now)
                 .values(used_at=now)
                 .returning(RefreshToken.usuario_id) )
        usuario_id = self.db.execute(stmt).scalar()
        self.db.commit()

        if usuario_id is not None:
            return self.obtener_usuario_por_id(usuario_id)

        self._revocar_familia_si_hay_reuso(token_hash)
        return None

    def _revocar_familia_si_hay_reuso(self, token_hash: str):
        stmt = ( Select(RefreshToken)
                 .where(RefreshToken.token_hash == token_hash) )
        token = self.db.execute(stmt).scalar()

        if token is None or token.used_at is None:
            return

        stmt_revocar = ( update(RefreshToken)
                          .where(RefreshToken.usuario_id == token.usuario_id,
                                 RefreshToken.used_at.is_(None))
                          .values(used_at=datetime.now(timezone.utc)) )
        self.db.execute(stmt_revocar)
        self.db.commit()

    def obtener_usuario_por_id(self, usuario_id: int) -> UsuarioDominio | None:
        stmt = ( Select(Usuario)
                 .where(Usuario.id == usuario_id) )

        usuario_modelo: Union[Usuario,None] = self.db.execute(stmt).scalar()

        if usuario_modelo is not None:
            return UsuarioDominio(
                id=usuario_modelo.id,
                email=usuario_modelo.email,
                nombres=usuario_modelo.first_name,
                apellidos=usuario_modelo.last_name,
                contrasenia=usuario_modelo.password
            )

        return None
