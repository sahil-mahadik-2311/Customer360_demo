from . import activate_escalation , avg_resolution_time, csat_score , delivery_rate, failed_message


activate_escalation_service = activate_escalation.ActiveEscalation()
average_resolution_service = avg_resolution_time.AverageResolutionTime()
csat_score_service = csat_score.CSAT_Score()
delivery_rate_service = delivery_rate.DeliveryRate()
failed_message_service = failed_message.FailedMessage()



