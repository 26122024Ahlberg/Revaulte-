// Favoritos dos Clientes (Change favoritos): uma linha por par conta + veículo.
// O par único impede duplicar o favorito mesmo em envios simultâneos.
// user_id vem sempre do token; nunca de dados enviados pelo navegador.
table favorite {
  auth = false

  schema {
    int id
    timestamp created_at?=now

    // Conta que favoritou.
    int user_id {
      table = "user"
    }

    // Veículo público favoritado.
    int vehicle_id {
      table = "vehicle"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {
      type : "btree|unique"
      field: [{name: "user_id"}, {name: "vehicle_id"}]
    }
    {type: "btree", field: [{name: "vehicle_id"}]}
  ]
  guid = "bCUjNCabmumomNmKdcMP93krSjw"
}
