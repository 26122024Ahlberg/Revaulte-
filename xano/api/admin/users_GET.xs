// Lista de usuários para o Administrador: sem CPF, telefone, data de nascimento, endereço ou senha
query users verb=GET {
  api_group = "Admin"
  auth = "user"

  input {
  }

  stack {
    // Autorização no backend, antes de qualquer consulta:
    // 401 sem token ou token inválido (auth = "user") e para conta excluída (enforce_role);
    // 403 para conta sem cargo ou que não é admin (enforce_role).
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "admin"}
    } as $role_check

    // Lista fechada de campos: nunca password, password_reset, cpf, phone, birth_date ou address.
    db.query user {
      sort = {user.created_at: "desc"}
      return = {type: "list"}
      output = ["id", "created_at", "name", "email", "role"]
    } as $users
  }

  response = $users
  guid = "wBRJ36OBsqVAkX5bsn27to9O2TM"
}
