// Cria um anúncio do Cliente autenticado, sempre em Rascunho (Change anuncios-cliente, decisões 1 a 6 e 9).
// Não há campos de dono, anunciante, estado, imagem ou data na entrada: o endpoint os define.
query anuncios verb=POST {
  api_group = "Anuncios"
  auth = "user"

  input {
    // Usado somente no primeiro anúncio da conta (criação do anunciante); ignorado depois.
    text? display_name? filters=trim

    text? brand? filters=trim
    text? model? filters=trim
    text? version? filters=trim
    int? year?

    // "new" ou "used".
    text? condition? filters=trim

    // Quilômetros.
    int? mileage?

    // Reais, até duas casas decimais.
    decimal? price?

    bool? is_modified?
    text? color? filters=trim
    text? engine? filters=trim
    text? transmission? filters=trim
    text? description? filters=trim
  }

  stack {
    // Autorização antes de qualquer consulta: 401 sem token, token inválido ou conta excluída;
    // 403 para conta sem cargo. Cliente (member) e Administrador (admin) passam.
    function.run "Quick Start/enforce_role" {
      input = {user_id: $auth.id, required_role: "member"}
    } as $role_check

    // Validação completa antes de qualquer gravação (decisão 6). Texto vazio conta como ausente.
    precondition ($input.brand != null && ($input.brand|strlen) >= 1 && ($input.brand|strlen) <= 40) {
      error_type = "inputerror"
      error = "invalid_brand"
    }

    precondition ($input.model != null && ($input.model|strlen) >= 1 && ($input.model|strlen) <= 60) {
      error_type = "inputerror"
      error = "invalid_model"
    }

    precondition ($input.version == null || ($input.version|strlen) <= 80) {
      error_type = "inputerror"
      error = "invalid_version"
    }

    // Ano atual calculado no fuso UTC.
    var $ano_maximo {
      value = (now|format_timestamp:"Y":"UTC"|to_int) + 1
    }

    precondition ($input.year != null && $input.year >= 1886 && $input.year <= $ano_maximo) {
      error_type = "inputerror"
      error = "invalid_year"
    }

    precondition ($input.condition == "new" || $input.condition == "used") {
      error_type = "inputerror"
      error = "invalid_condition"
    }

    // Comparação estrita (!==): em XanoScript, != é frouxa e trata 0 e false como iguais a null,
    // o que recusava quilometragem 0 e is_modified false (falha da tarefa 3.4, 23/11/2026).
    precondition ($input.mileage !== null && $input.mileage >= 0 && $input.mileage <= 2000000) {
      error_type = "inputerror"
      error = "invalid_mileage"
    }

    // Até duas casas decimais: arredondar para 2 casas não pode mudar o valor.
    precondition ($input.price != null && $input.price > 0 && $input.price <= 100000000 && ($input.price|round:2) == $input.price) {
      error_type = "inputerror"
      error = "invalid_price"
    }

    // Estrita pelo mesmo motivo da quilometragem: false precisa ser aceito.
    precondition ($input.is_modified !== null) {
      error_type = "inputerror"
      error = "invalid_is_modified"
    }

    precondition ($input.color == null || ($input.color|strlen) <= 60) {
      error_type = "inputerror"
      error = "invalid_color"
    }

    precondition ($input.engine == null || ($input.engine|strlen) <= 60) {
      error_type = "inputerror"
      error = "invalid_engine"
    }

    precondition ($input.transmission == null || ($input.transmission|strlen) <= 60) {
      error_type = "inputerror"
      error = "invalid_transmission"
    }

    precondition ($input.description == null || ($input.description|strlen) <= 2000) {
      error_type = "inputerror"
      error = "invalid_description"
    }

    // Campos opcionais vazios são gravados como nulos.
    var $version {
      value = null
    }

    conditional {
      if ($input.version != null && $input.version != "") {
        var.update $version {
          value = $input.version
        }
      }
    }

    var $color {
      value = null
    }

    conditional {
      if ($input.color != null && $input.color != "") {
        var.update $color {
          value = $input.color
        }
      }
    }

    var $engine {
      value = null
    }

    conditional {
      if ($input.engine != null && $input.engine != "") {
        var.update $engine {
          value = $input.engine
        }
      }
    }

    var $transmission {
      value = null
    }

    conditional {
      if ($input.transmission != null && $input.transmission != "") {
        var.update $transmission {
          value = $input.transmission
        }
      }
    }

    var $description {
      value = null
    }

    conditional {
      if ($input.description != null && $input.description != "") {
        var.update $description {
          value = $input.description
        }
      }
    }

    // Anunciante da conta pelo registro seller_account (decisão 1): consulta prévia, fora da
    // transação, só para decidir se o nome de exibição é exigido. Registros nunca são apagados
    // por este endpoint, então se esta consulta encontra um, a de dentro da transação também
    // encontra. Anunciantes da equipe, como o do Opala, não têm registro e nunca coincidem.
    db.query seller_account {
      where = $db.seller_account.user_id == $auth.id
      return = {type: "single"}
      output = ["seller_id"]
    } as $registro_previo

    conditional {
      if ($registro_previo == null) {
        // Primeiro anúncio: o nome de exibição é obrigatório (decisão 3).
        precondition ($input.display_name != null && ($input.display_name|strlen) >= 2 && ($input.display_name|strlen) <= 60) {
          error_type = "inputerror"
          error = "invalid_display_name"
        }
      }
    }

    var $veiculo {
      value = null
    }

    // Limite de rascunhos, busca ou criação do anunciante e gravação do veículo numa única
    // transação (decisões 1 e 9): ou tudo é gravado, ou nada. Concorrência: se outra requisição
    // da mesma conta criar o registro primeiro, o db.add seller_account desta falha no índice
    // único de user_id e a transação desfaz o anunciante criado aqui; nada é apagado depois.
    db.transaction {
      stack {
        // Recusa a criação quando a conta já tem 20 anúncios em Rascunho (decisão 9).
        // Publicados e vendidos não contam.
        db.query vehicle {
          join = {
            seller_account: {
              table: "seller_account"
              type : "inner"
              where: $db.vehicle.seller_id == $db.seller_account.seller_id
            }
          }

          where = $db.seller_account.user_id == $auth.id && $db.vehicle.status == "draft"
          return = {type: "count"}
        } as $rascunhos

        precondition ($rascunhos < 20) {
          error_type = "inputerror"
          error = "draft_limit_reached"
        }

        db.query seller_account {
          where = $db.seller_account.user_id == $auth.id
          return = {type: "single"}
          output = ["seller_id"]
        } as $registro

        var $seller_id {
          value = null
        }

        conditional {
          if ($registro == null) {
            // Contato sempre desligado: o Xano publicado não tem o padrão false (decisão 4).
            // O nome já foi validado acima, porque a consulta prévia também não achou registro.
            db.add seller {
              data = {
                created_at        : "now"
                display_name      : $input.display_name
                whatsapp          : null
                contact_authorized: false
              }
            } as $novo_anunciante

            // Índice único em user_id: numa corrida, só uma destas gravações é aceita.
            db.add seller_account {
              data = {
                created_at: "now"
                user_id   : $auth.id
                seller_id : $novo_anunciante.id
              }
            } as $novo_registro

            var.update $seller_id {
              value = $novo_anunciante.id
            }
          }

          else {
            var.update $seller_id {
              value = $registro.seller_id
            }
          }
        }

        // Estado sempre Rascunho; is_modified gravado explicitamente (sem padrão no Xano publicado).
        db.add vehicle {
          data = {
            created_at  : "now"
            brand       : $input.brand
            model       : $input.model
            version     : $version
            year        : $input.year
            condition   : $input.condition
            mileage     : $input.mileage
            price       : $input.price
            is_modified : $input.is_modified
            status      : "draft"
            color       : $color
            engine      : $engine
            transmission: $transmission
            description : $description
            seller_id   : $seller_id
          }
        } as $novo_veiculo

        var.update $veiculo {
          value = $novo_veiculo
        }
      }
    }
  }

  response = {id: $veiculo.id, status: $veiculo.status}
  guid = "uJlNPqTkPc__A2_dPXOLy8Hh96Y"
}
