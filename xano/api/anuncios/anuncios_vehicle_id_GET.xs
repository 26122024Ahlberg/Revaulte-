// Ficha privada de um anúncio da conta autenticada, inclusive em Rascunho (Change anuncios-cliente, decisão 5).
// Anúncio de outra conta, veículo da equipe (como o Opala) e identificador inexistente: o mesmo 404.
query "anuncios/{vehicle_id}" verb=GET {
  api_group = "Anuncios"
  auth = "user"

  input {
    int vehicle_id
  }

  stack {
    // 401 sem token, token inválido ou conta excluída; 403 para conta sem cargo.
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "member"}
    } as $role_check

    // Identificador e dono (registro seller_account) na mesma consulta: nada diferencia
    // "não existe" de "não é seu".
    db.query vehicle {
      join = {
        seller_account: {
          table: "seller_account"
          type : "inner"
          where: $db.vehicle.seller_id == $db.seller_account.seller_id
        }
      }

      where = $db.vehicle.id == $input.vehicle_id && $db.seller_account.user_id == $auth.id
      return = {type: "single"}
      output = [
        "id"
        "brand"
        "model"
        "version"
        "year"
        "condition"
        "mileage"
        "price"
        "is_modified"
        "status"
        "created_at"
        "color"
        "engine"
        "transmission"
        "description"
      ]
    } as $anuncio

    precondition ($anuncio != null) {
      error_type = "notfound"
      error = "not_found"
    }
  }

  response = $anuncio
  guid = "yeePukAlP_uIPZ2BMaEW6zjzTVY"
}
