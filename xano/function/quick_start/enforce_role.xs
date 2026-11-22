// Checks that a user has the appropriate role level. This example sets a hierarchy of roles, and a user must pass the minimum level to execute.
// Change contas-acesso: conta excluída -> 401; conta sem cargo ou com cargo insuficiente -> 403.
// As mensagens de erro não revelam o cargo atual do usuário.
function "Quick Start/enforce_role" {
  input {
    // The ID of the user to check the role for.
    int user_id

    // The role required to perform the action.
    text required_role
  }

  stack {
    // Defines a hierarchy of roles with numerical levels.
    var $role_hierarchy {
      value = {admin: 2, member: 1}
    }

    // Retrieve the user's role from the database.
    db.get user {
      field_name = "id"
      field_value = $input.user_id
      output = ["id", "role"]
    } as $user

    // Conta excluída depois da emissão do token: a sessão deixa de valer (401).
    precondition ($user != null) {
      error_type = "unauthorized"
      error = "unauthorized"
    }

    // Conta sem cargo não tem nenhuma permissão (403).
    precondition ($user.role != null) {
      error_type = "accessdenied"
      error = "forbidden"
    }

    // Get the numerical level of the user's role.
    var $user_role_level {
      value = $role_hierarchy|get:$user.role
    }

    // Get the numerical level of the required role.
    var $required_role_level {
      value = $role_hierarchy|get:$input.required_role
    }

    // Ensure the required role is a valid, defined role in the hierarchy (erro de programação).
    precondition ($required_role_level > 0) {
      error_type = "inputerror"
      error = "Invalid required role specified."
    }

    // Cargo insuficiente (por exemplo, Cliente pedindo recurso de Administrador): 403.
    precondition ($user_role_level >= $required_role_level) {
      error_type = "accessdenied"
      error = "forbidden"
    }
  }

  response = null
  tags = ["xano:quick-start"]
  guid = "iA9kfiAa3LxpetzMrAH4SVH-RII"
}
