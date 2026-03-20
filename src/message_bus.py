from collections import deque

_message_queue = deque()

def send_message(msg):
    #add message to queue
    if hasattr(msg, 'to_dict'):
        msg = msg.to_dict()
    _message_queue.append(msg)

def get_messages_for(agent_name):
    # fetch + remove messages for agent
    results = [m for m in list(_message_queue)
               if m['recipient'] in (agent_name, "broadcast")]
    for m in results:
        try:
            _message_queue.remove(m)
        except ValueError:
            pass
    return results
