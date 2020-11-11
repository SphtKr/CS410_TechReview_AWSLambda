import os
import json
import metapy

def lambda_handler_post(event, context):    
    return lambda_handler(event, context)

def lambda_handler_get(event, context):
    qsParams = event.get("queryStringParameters", {} ) or {}
    body = {
        "query": event.get("pathParameters", {}).get("query", ""),
        "top": qsParams.get("top", 10), 
        "skip": qsParams.get("skip", 0) 
    }
    event["body"] = json.dumps(body)
    return lambda_handler(event, context)

def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e

    cfg = "./data/idx/inv/config.toml"

    # Depending on the request/call mechanism, some of these event properties may not exist...
    bodyJson = event.get("body", "{}")
    body = json.loads(bodyJson if bodyJson != None and bodyJson != "" else "{}")
    #qsParams = event.get("queryStringParameters", {} ) or {}
    
    #query = body.get("query", event.get("pathParameters", {} ).get("query", ""))
    #top = int(body.get("top",  qsParams.get("top", 10)))
    #skip = int(body.get("skip",  qsParams.get("skip", 0)))
    query = body.get("query", "")
    top = body.get("top", 10)
    skip = body.get("skip", 0)
    print("query: {}   top: {}   skip {}".format(query, top, skip))
    print("cwd: {}   files: {}".format(os.getcwd(), os.listdir('.')))
    
    idx = metapy.index.make_inverted_index(cfg)
    ranker = metapy.index.OkapiBM25(k1=1.91,b=0.74,k3=500)

    qdoc = metapy.index.Document()
    qdoc.content(query)
    ranking = ranker.score(idx, qdoc, skip + top)[skip:]
    
    results = []
    for r in ranking:
        mdata = idx.metadata(r[0])
        results.append({
            "doc_id": r[0],
            "url": mdata.get("url"),
            "score": r[1]
        })

    
    return {
        "statusCode": 200,
        "body": json.dumps( {
            "query": query,
            "results": results
        })
    }
