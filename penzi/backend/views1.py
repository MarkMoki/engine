from twilio.rest import Client

# Send the cleaned message using Twilio
account_sid = 'ACf8b960bcd99bb3036ff6e48b0c3ba6b8'
auth_token = '574f801b9bdc06a4fde300381e359081'
client = Client(account_sid, auth_token)

# # Create a MessagingResponse and add the message
# twilio_response = MessagingResponse()
# twilio_response.message(message)

# # Get the string representation of the response
# twilio_response_str = str(twilio_response)

# Send the message using Twilio
message = client.messages.create(
from_='whatsapp:+14155238886',
body='tests',
to=f'whatsapp:+254759215000'
)


