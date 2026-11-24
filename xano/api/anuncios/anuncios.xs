// Anúncios enviados por Clientes autenticados (Change anuncios-cliente).
// Todos os endpoints exigem token (auth = "user") e chamam enforce_role antes de qualquer consulta.
// O dono do anúncio vem sempre de $auth.id, pelo vínculo
// vehicle.seller_id -> seller_account.seller_id e seller_account.user_id.
api_group Anuncios {
  canonical = "revaulte-anuncios"
  swagger = {active: false}
  guid = "OyIaBjpbRVpyEzrfFu89xx77juc"
}
