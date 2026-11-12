// Modifications made to a vehicle after its original configuration, grouped by area.
table vehicle_modification {
  auth = false

  schema {
    int id
    timestamp created_at?=now

    // Vehicle that received the modification.
    int vehicle_id {
      table = "vehicle"
    }

    // Area of the modification, following the areas of the domain model.
    enum area {
      values = ["engine", "forced_induction", "power", "fuel", "transmission", "suspension", "wheels_tires", "brakes", "interior", "exterior", "other"]
    }

    text description filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "vehicle_id"}]}
  ]
  guid = "mX9hwhUAkAex9CvjkJ0ezSv3Hbg"
}
