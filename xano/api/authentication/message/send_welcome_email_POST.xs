// DESATIVADO (Change contas-acesso, decisão 10): endpoint herdado do Quick Start, sem autenticação
// e não usado pela Revaulte. Responde sempre 404, sem consultar o banco, enviar e-mail,
// criar token ou registrar evento. Nome, verbo, grupo, tags e guid preservados.
query "message/send_welcome_email" verb=POST {
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
  guid = "rw5loJr5zd0y9ViGgL4ZpcBhKQA"
}
