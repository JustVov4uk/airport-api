from django.core.mail import send_mail


def send_order_confirmation(order):
    subject = "Hello"
    message = f"Order #{order.id} confirmed. Ticket: {order.tickets.count()}."
    send_mail(subject, message, None, [order.user.email])
