// Favorita um veículo público para a conta autenticada (Change favoritos, decisões 3 e 4).
// Idempotente: repetir não duplica. Rascunho e identificador inexistente recebem o mesmo 404.
query "favoritos/{vehicle_id}" verb=POST {
  api_group = "Favoritos"
  auth = "user"

  input {
    int vehicle_id
  }

  stack {
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "member"}
    } as $role_check

    // Só veículos do catálogo público: Disponível ou Vendido.
    db.query vehicle {
      where = $db.vehicle.id == $input.vehicle_id && ($db.vehicle.status == "available" || $db.vehicle.status == "sold")
      return = {type: "single"}
      output = ["id"]
    } as $veiculo

    precondition ($veiculo != null) {
      error_type = "notfound"
      error = "not_found"
    }

    db.query favorite {
      where = $db.favorite.user_id == $auth.id && $db.favorite.vehicle_id == $input.vehicle_id
      return = {type: "single"}
      output = ["id"]
    } as $existente

    conditional {
      if ($existente == null) {
        db.add favorite {
          data = {
            created_at: "now"
            user_id   : $auth.id
            vehicle_id: $input.vehicle_id
          }
        } as $novo
      }
    }
  }

  response = {vehicle_id: $input.vehicle_id, favorited: true}
}
