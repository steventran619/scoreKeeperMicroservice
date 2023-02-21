# Purpose of this microservice is to monitor
#!/usr/bin/env python
import pika, sys, os, csv

def getWinner(username, dir):
    if username == None:
        return
    os.chdir(dir)
    foundUser = False
    returnScore = 1

    # Read in rows from scores.txt
    with open(dir + "/scores.txt", 'r') as scoreDatabase:
        lines = csv.reader(scoreDatabase)
        data = list(lines)
        # print(data)
    scoreDatabase.close()
    
    # Cycle through until username is found in the db
    for i in range(0, len(data)):
        if data[i][0] == username:
            oldScore = data[i][1]
            returnScore = int(oldScore) + 1
            data[i][1] = str(returnScore)
            foundUser = True
            break

    # Update the username's win count
    if foundUser:
        with open(dir + "/scores.txt", 'w') as scoreDatabase:
            writer = csv.writer(scoreDatabase)
            for row in data:
                writer.writerow(row)
    
    # Otherwise create a new entry for the username
    else:
        with open(dir + "/scores.txt", 'a') as scoreDatabase:
            writer = csv.writer(scoreDatabase)
            writer.writerow([username, returnScore])
    
    scoreDatabase.close()
    return returnScore
        
def main():
    # Create a connection on the local machine
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    dbDirectory = os.path.dirname(os.path.abspath(__file__))
    channel = connection.channel()

    # good practice to declare the queue in both programs in case of which program is run
    channel.queue_declare(queue='winnerPipe') 
    channel.queue_declare(queue='winRatePipe')

    # Need to subscribe a callback function to a queue
    def callback(ch, method, properties, body):
        score = None
        if (body == None):
            print("Invalid username sent")
            return
        else:
            name = body.decode('utf-8')
            score = getWinner(name, dbDirectory)
            print(f"Win count updated for {name} with {score} wins.")
            # Second call back to the winRatePipe
            if score:
                channel.basic_publish(exchange='',
                        routing_key='winRatePipe',
                        body=str(score))
    
    # Main callback receiving the winning username
    channel.basic_consume(queue='winnerPipe',
                        auto_ack=True,
                        on_message_callback=callback)

    print("\n===========================")
    print("ScoreKeeper Service Started")
    print("===========================")
    print('\n>> Waiting for winners to come through.\nTo exit press CTRL + C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)