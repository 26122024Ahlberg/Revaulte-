// Cadastro de Cliente (Change contas-acesso): cria a conta sempre com perfil "member" e devolve o token
query "auth/signup" verb=POST {
  api_group = "Authentication"

  input {
    text name? filters=trim
    email email? filters=trim|lower
    text password?

    // CPF e telefone somente com dígitos; data no formato AAAA-MM-DD.
    text cpf? filters=trim
    text phone? filters=trim
    text birth_date? filters=trim
    text address? filters=trim
  }

  stack {
    // Campos obrigatórios e formatos. O frontend confere também os dígitos verificadores do CPF.
    precondition ($input.name != null && ($input.name|strlen) >= 2 && ($input.name|strlen) <= 100) {
      error_type = "inputerror"
      error = "invalid_name"
    }

    precondition ($input.email != null && $input.email != "") {
      error_type = "inputerror"
      error = "invalid_email"
    }

    precondition ($input.password != null && ($input.password|strlen) >= 8) {
      error_type = "inputerror"
      error = "invalid_password"
    }

    precondition ($input.cpf != null && ("/^[0-9]{11}$/"|regex_matches:$input.cpf) && !("/^(0{11}|1{11}|2{11}|3{11}|4{11}|5{11}|6{11}|7{11}|8{11}|9{11})$/"|regex_matches:$input.cpf)) {
      error_type = "inputerror"
      error = "invalid_cpf"
    }

    precondition ($input.phone != null && ("/^[0-9]{10,11}$/"|regex_matches:$input.phone)) {
      error_type = "inputerror"
      error = "invalid_phone"
    }

    precondition ($input.birth_date != null && ("/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/"|regex_matches:$input.birth_date)) {
      error_type = "inputerror"
      error = "invalid_birth_date"
    }

    // Data de nascimento no passado e posterior a 1900; nenhuma idade mínima é presumida.
    var $nascimento {
      value = $input.birth_date|to_timestamp:"UTC"
    }

    precondition ($nascimento < now && $nascimento >= ("1900-01-01"|to_timestamp:"UTC")) {
      error_type = "inputerror"
      error = "invalid_birth_date"
    }

    precondition ($input.address != null && ($input.address|strlen) >= 5 && ($input.address|strlen) <= 200) {
      error_type = "inputerror"
      error = "invalid_address"
    }

    // E-mail e CPF não podem pertencer a outra conta.
    db.get user {
      field_name = "email"
      field_value = $input.email
      output = ["id"]
    } as $user_email

    precondition ($user_email == null) {
      error_type = "accessdenied"
      error = "email_taken"
    }

    db.get user {
      field_name = "cpf"
      field_value = $input.cpf
      output = ["id"]
    } as $user_cpf

    precondition ($user_cpf == null) {
      error_type = "accessdenied"
      error = "cpf_taken"
    }

    // O perfil é sempre Cliente; o tipo password grava somente o hash.
    db.add user {
      data = {
        created_at: "now"
        name      : $input.name
        email     : $input.email
        password  : $input.password
        role      : "member"
        cpf       : $input.cpf
        phone     : $input.phone
        birth_date: $input.birth_date
        address   : $input.address
      }
    } as $user

    security.create_auth_token {
      table = "user"
      extras = {}
      expiration = 86400
      id = $user.id
    } as $authToken

    // Nenhum dado pessoal no log.
    function.run "Quick Start/log_event" {
      input = {user_id: $user.id, action: "signup", metadata: {}}
    } as $event_log
  }

  response = {authToken: $authToken, user_id: $user.id}
  tags = ["xano:quick-start"]
  guid = "la96rUuCVyDv3BIMVm138VE8Rm0"
}
