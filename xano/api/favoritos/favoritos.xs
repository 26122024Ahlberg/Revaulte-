// Favoritos do Cliente autenticado (Change favoritos).
// Todos os endpoints exigem token (auth = "user") e chamam enforce_role antes de qualquer consulta.
// A conta vem sempre de $auth.id.
api_group Favoritos {
  canonical = "revaulte-favoritos"
  swagger = {active: false}
}
