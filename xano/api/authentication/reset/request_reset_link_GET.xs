// DESATIVADO (Change contas-acesso, decisão 10): recuperação de senha está fora do escopo.
// Responde sempre 404, sem consultar o banco, gerar link ou token, enviar e-mail ou registrar
// evento. Nome, verbo, grupo, tags e guid preservados.
query "reset/request-reset-link" verb=GET {
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
  guid = "TODx3DGJ3o0L9UAANFUmU6QDDyU"
}
