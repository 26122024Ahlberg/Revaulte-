// Stores the vehicles advertised by the store, with the data needed by the public catalog.
table vehicle {
  auth = false

  schema {
    int id
    timestamp created_at?=now
    text brand filters=trim
    text model filters=trim
    text version? filters=trim
    int year

    // Whether the vehicle is new or used.
    enum condition {
      values = ["new", "used"]
    }

    // Mileage in kilometers.
    int mileage filters=min:0

    // Price in Brazilian reais.
    decimal price filters=min:0

    // True when the vehicle has been modified/prepared after its original configuration.
    bool is_modified?=false

    // Publication state. Draft vehicles are never exposed publicly.
    enum status?="draft" {
      values = ["draft", "available", "sold"]
    }

    // URL of the vehicle's cover image.
    text cover_image_url? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]
  guid = "LukcvdKFTG57QVJaPJZLPHFxbkQ"
}
