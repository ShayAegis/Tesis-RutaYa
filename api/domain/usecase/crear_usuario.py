from domain.entities.usuario import Usuario
from domain.repositories.repositorio_usuarios import RepositorioUsuarios
from domain.servicios.validador_contrasenia import crear_cadena_validacion_contrasenia


class CrearUsuario:
    def __init__(self, repositorio: RepositorioUsuarios):
        self.repositorio = repositorio

    def ejecutar(self, usuario: Usuario) -> Usuario:
        if self.repositorio.usuario_existe(usuario.email):
            raise UsuarioYaExisteError(usuario.email)
        crear_cadena_validacion_contrasenia().validar(usuario.contrasenia)
        self.repositorio.crear_usuario(usuario)
        return self.repositorio.obtener_usuario_por_correo(usuario.email)


class UsuarioYaExisteError(Exception):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Ya existe un usuario registrado con el email {email}")
