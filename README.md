
# ScoreKeeper Communication Contract
## Prerequisites
* Python 3
* RabbitMQ installed (https://www.rabbitmq.com/)

## Starting/running the Service
```
python3 scoreKeeper.py
```

## How to Request Data

There must be a `scores.txt` file in the same directory as the ScoreKeeper microservice. This will hold rows of data of a username, followed by an integer. For example:
```
# scores.txt
the1User,2
someUser2,19
userName3,11
```

You'll need to create a new RabbitMQ connection and channel. In Python this is done by:
```
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
```
In order to request data from the ScoreKeeper microservice, you must have a queue within the channel named `winnerPipe`. This can be done with the following:
```
channel.queue_declare(queue='winnerPipe')
```
Finally to request data, you must publish a message via that the queue/pipe name `winnerPipe` with the username as the body.
```
winner = 'someUserName4'
channel.basic_publish(exchange='',
                      routing_key='winnerPipe',
                      body=winner)
```


## How to Receive Data
Similar to requesting data, a second queue/pipe name `winRatePipe` is used to transmit/receive the win count for the requested username.
```
channel.queue_declare(queue='winRatePipe')
```
You'll want to listen in on that pipe line after sending the data request in order to receive the win count.
```
channel.basic_consume(queue='winRatePipe',
                      auto_ack=True,
                      on_message_callback=callback)
```
where `callback` is
```
def callback(ch, method, properties, body):
    # message is the win count as a string
    message = body.decode('utf-8')
```
One method of listening in is to use the `start_consuming` method on the channel.
```
channel.start_consuming()
```

## UML Diagram
![image](https://user-images.githubusercontent.com/65416951/218338877-0ae5f45a-d890-488e-92b2-cd6191c90d27.png)
