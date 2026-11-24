// Remove o favorito da conta autenticada (Change favoritos, decisão 3).
// Idempotente: remover quem não existe também responde 200. Só apaga linhas da própria conta.
query "favoritos/{vehicle_id}" verb=DELETE {
  api_group = "Favoritos"
  auth = "user"

  input {
    int vehicle_id
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "member"}
    } as $role_check

    db.bulk.delete favorite {
      where = $db.favorite.user_id == $auth.id && $db.favorite.vehicle_id == $input.vehicle_id
    } as $removidos
  }

  response = {vehicle_id: $input.vehicle_id, favorited: false}
}
