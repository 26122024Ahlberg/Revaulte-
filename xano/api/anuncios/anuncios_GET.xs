// Lista somente os anúncios da conta autenticada, mais recentes primeiro (Change anuncios-cliente, decisão 5).
// Também informa o nome de exibição do anunciante da conta, ou null quando ainda não há anunciante.
query anuncios verb=GET {
  api_group = "Anuncios"
  auth = "user"

  input {
  }

  stack {
    // 401 sem token, token inválido ou conta excluída; 403 para conta sem cargo.
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "member"}
    } as $role_check

    // Anunciante da conta pelo registro seller_account (decisão 1).
    db.query seller {
      join = {
        seller_account: {
          table: "seller_account"
          type : "inner"
          where: $db.seller.id == $db.seller_account.seller_id
        }
      }

      where = $db.seller_account.user_id == $auth.id
      return = {type: "single"}
      output = ["display_name"]
    } as $anunciante

    // Dono pelo vínculo vehicle.seller_id -> seller_account: veículos da equipe (anunciante sem
    // registro, ou seller_id 0) e de outras contas nunca entram na lista.
    db.query vehicle {
      join = {
        seller_account: {
          table: "seller_account"
          type : "inner"
          where: $db.vehicle.seller_id == $db.seller_account.seller_id
        }
      }

      where = $db.seller_account.user_id == $auth.id
      sort = {vehicle.created_at: "desc"}
      return = {type: "list"}
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
      ]
    } as $anuncios
  }

  response = {anunciante: $anunciante, anuncios: $anuncios}
  guid = "y6LyH50acwzVq1w9tHWs8HF1Z4U"
}
