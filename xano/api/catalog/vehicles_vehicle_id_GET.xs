// Public detail of one vehicle: only available and sold vehicles; draft and missing return the same 404
query "vehicles/{vehicle_id}" verb=GET {
  api_group = "Catalog"

  input {
    int vehicle_id
  }

  stack {
    // Same allow-list of public states as GET /vehicles
    db.query vehicle {
      where = $db.vehicle.id == $input.vehicle_id && ($db.vehicle.status == "available" || $db.vehicle.status == "sold")
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
        "cover_image_url"
        "color"
        "engine"
        "transmission"
        "description"
        "seller_id"
      ]
    } as $vehicle

    precondition ($vehicle != null) {
      error_type = "notfound"
      error = "Vehicle not found"
    }

    db.query vehicle_modification {
      where = $db.vehicle_modification.vehicle_id == $input.vehicle_id
      sort = {vehicle_modification.id: "asc"}
      return = {type: "list"}
      output = ["area", "description"]
    } as $modifications

    // Anunciante: só para veículo Disponível; vendido ou sem anunciante recebe null.
    // O número só sai do backend quando o anunciante autorizou o contato.
    var $seller {
      value = null
    }

    conditional {
      if ($vehicle.status == "available" && $vehicle.seller_id != null) {
        db.query seller {
          where = $db.seller.id == $vehicle.seller_id
          return = {type: "single"}
          output = ["display_name", "whatsapp", "contact_authorized"]
        } as $seller_record

        conditional {
          if ($seller_record != null) {
            var $public_whatsapp {
              value = null
            }

            conditional {
              if ($seller_record.contact_authorized == true && $seller_record.whatsapp != null && $seller_record.whatsapp != "") {
                var.update $public_whatsapp {
                  value = $seller_record.whatsapp
                }
              }
            }

            var.update $seller {
              value = {display_name: $seller_record.display_name, whatsapp: $public_whatsapp}
            }
          }
        }
      }
    }

    // seller_id é interno: sai da resposta; contact_authorized nunca é exposto.
    var $detail {
      value = $vehicle|unset:"seller_id"|set:"modifications":$modifications|set:"seller":$seller
    }
  }

  response = $detail
  guid = "XoRgoOzyhZy3-Xa7aO7-03pXdQk"
}
