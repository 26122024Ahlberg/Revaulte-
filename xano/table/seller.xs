// Anunciante: quem anuncia o veículo (Change contato-vendedor).
// Cadastrado pelo painel do Xano por um membro do grupo; nunca por dados fictícios.
table seller {
  auth = false

  schema {
    int id
    timestamp created_at?=now

    // Nome exibido publicamente na página do veículo.
    text display_name filters=trim

    // WhatsApp somente com dígitos, com DDI e DDD (por exemplo, 55 + DDD + número).
    text whatsapp? filters=trim {
      sensitive = true
    }

    // O número só é exposto quando o anunciante autorizou.
    bool contact_authorized?=false

    // Data da autorização (registro de consentimento); nunca exposta publicamente.
    timestamp contact_authorized_at? {
      sensitive = true
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
  ]
  guid = "vH9g7EhEUfWlulJGaJLvPKr0p7o"
}
