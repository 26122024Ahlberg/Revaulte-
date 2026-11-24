// Pull all event logs for the authenticated user
query "logs/user/my_events" verb=GET {
  api_group = "Event Logs"
  auth = "user"

  input {
  }

  stack {
    // Retrieve event logs for the authenticated user
    // Saída mínima (Change contas-acesso, tarefa 2.3): só os eventos da própria conta e só
    // id, data e ação. user_id e metadata não saem; a lista continua sendo um array.
    db.query event_log {
      where = $db.event_log.user_id == $auth.id
      sort = {event_log.created_at: "desc"}
      return = {type: "list"}
      output = ["id", "created_at", "action"]
    } as $user_events
  }

  response = $user_events
  tags = ["xano:quick-start"]
  guid = "-iyXujeFKm9_O0k4fzsZ2DxVTe4"
}