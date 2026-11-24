// Ids dos veículos favoritados pela conta autenticada, mais recentes primeiro (Change favoritos, decisão 2).
// Não devolve dados do veículo: o site cruza os ids com o catálogo público.
query favoritos verb=GET {
  api_group = "Favoritos"
  auth = "user"

  input {
  }

  stack {
    // 401 sem token, token inválido ou conta excluída; 403 para conta sem cargo.
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "member"}
    } as $role_check

    db.query favorite {
      where = $db.favorite.user_id == $auth.id
      sort = {favorite.created_at: "desc"}
      return = {type: "list"}
      output = ["vehicle_id", "created_at"]
    } as $favoritos
  }

  response = $favoritos
}
