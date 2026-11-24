// Registro do anunciante de cada conta (Change anuncios-cliente, decisões 1 e 9).
// Única fonte do vínculo conta -> anunciante: um anúncio pertence à conta X quando
// vehicle.seller_id = seller_account.seller_id e seller_account.user_id = X.
// Só recebe linhas criadas pelo POST /anuncios, sempre com uma conta real: nunca há user_id
// nulo ou zero, então o índice único não depende de como o Xano trata valores vazios.
// O índice único em user_id garante no máximo um anunciante por conta mesmo em envios
// simultâneos: a segunda gravação falha e a transação do endpoint desfaz tudo o que ela gravou.
// Anunciantes cadastrados pela equipe (como o do Opala) não têm linha aqui.
table seller_account {
  auth = false

  schema {
    int id
    timestamp created_at?=now

    // Conta dona do anunciante, sempre definida pelo backend a partir do token.
    int user_id {
      table = "user"
    }

    // Anunciante criado para essa conta.
    int seller_id {
      table = "seller"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "user_id"}]}
    {type: "btree|unique", field: [{name: "seller_id"}]}
  ]
  guid = "bAy4KG-8TNfZXpsRlhp4vpnwmsA"
}
