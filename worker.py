import pika
import time

# Várunk a RabbitMQ-ra
time.sleep(15)

def process_order():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue='jegy_queue')

        def callback(ch, method, properties, body):
            print(f" [V] HÁTTÉRMUNKÁS: Sikeresen feldolgoztam a rendelést: {body.decode()}")

        channel.basic_consume(queue='jegy_queue', on_message_callback=callback, auto_ack=True)
        print(' [*] Várakozás az üzenetekre...')
        channel.start_consuming()
    except Exception as e:
        print(f"Hiba a munkásban: {e}")
        time.sleep(5)
        process_order()

if __name__ == '__main__':
    process_order()