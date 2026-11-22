// DESATIVADO (Change contas-acesso, decisão 10): login por link mágico está fora do escopo.
// Responde sempre 404, sem consultar o banco, criar token ou sessão, enviar e-mail ou
// registrar evento. Nome, verbo, grupo, tags e guid preservados.
query "reset/magic-link-login" verb=POST {
  api_group = "Authentication"

  input {
  }

  stack {
    precondition (false) {
      error_type = "notfound"
      error = "not_found"
    }
  }

  response = null
  tags = ["xano:quick-start"]
  guid = "-6gXbVbSs_1-jKvlhohLG4VmDw0"
}
