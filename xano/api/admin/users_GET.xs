// Lista de usuários para o Administrador: sem CPF, telefone, data de nascimento, endereço ou senha
query users verb=GET {
  api_group = "Admin"
  auth = "user"

  input {
  }

  stack {
    // Autorização no backend: 401 sem token (auth = "user") e 403 para quem não é admin.
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "admin"}
    } as $role_check

    db.query user {
      sort = {user.created_at: "desc"}
      return = {type: "list"}
      output = ["id", "created_at", "name", "email", "role"]
    } as $users
  }

  response = $users
}
