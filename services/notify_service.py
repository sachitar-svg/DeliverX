
def send_sms(phone: str, message: str) -> bool:
    """
    SMS stub — replace with Twilio / MSG91 / WhatsApp API later.
    For now prints to terminal so you can see the message during testing.
    """
    print(f"\n[SMS] To: {phone}")
    print(f"[SMS] Message: {message}\n")
    return True


def notify_customer_enroute(phone: str, order_id: str, agent_name: str) -> dict:
    """
    Sends SMS to customer when delivery agent is en route.
    """
    message = (
        f"Your DeliverX order ({order_id}) is on the way! "
        f"Delivery agent {agent_name} is heading to your location. "
        f"Please be ready to receive your parcel."
    )
    sent = send_sms(phone, message)
    return {
        "sms_sent": sent,
        "to": phone,
        "agent": agent_name
    }


def notify_parcel_arrived(phone: str, order_id: str,
                          hub_name: str, hub_location: str,
                          open_time: str, close_time: str,
                          customer_otp: str) -> dict:
    """
    Sends SMS to customer when parcel has arrived at micro-hub.
    Includes hub name, location, operating hours, and OTP-2.
    """
    message = (
        f"Your DeliverX parcel ({order_id}) has arrived at "
        f"{hub_name}, {hub_location}. "
        f"Hub hours: {open_time} to {close_time}. "
        f"Your pickup OTP is: {customer_otp}. "
        f"Show this OTP at the hub to collect your parcel."
    )
    sent = send_sms(phone, message)
    return {
        "sms_sent": sent,
        "to": phone,
        "hub": hub_name,
        "otp_sent": customer_otp
    }
