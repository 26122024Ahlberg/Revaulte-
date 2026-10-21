// Public listing of the catalog: only available and sold vehicles, newest first
query vehicles verb=GET {
  api_group = "Catalog"

  input {
  }

  stack {
    // Allow-list of public states: draft (or any future state) is never returned
    db.query vehicle {
      where = $db.vehicle.status == "available" || $db.vehicle.status == "sold"
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
        "cover_image_url"
      ]
    } as $vehicles
  }

  response = $vehicles
  guid = "2NrSHko3uiujiRf5bUJCd3VJ2pk"
}
