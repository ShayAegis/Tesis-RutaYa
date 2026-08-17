from pydantic import BaseModel


class UsuarioDTO(BaseModel):
    nombres: str
    apellidos: str
    email: str
    contrasenia: str


class UsuarioCreadoDTO(BaseModel):
    id: int
    nombres: str
    apellidos: str
    email: str

    @classmethod
    def desde_dominio(cls, usuario) -> "UsuarioCreadoDTO":
        return cls(
            id=usuario.id,
            nombres=usuario.nombres,
            apellidos=usuario.apellidos,
            email=usuario.email,
        )
