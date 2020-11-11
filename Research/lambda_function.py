import json

def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps([{'ticker': 'FB', 'reason': 'Good adverticement company'},
                            {'ticker': 'SEDG', 'reason': 'tbd'},
                            {'ticker': 'LTHM', 'reason': 'tbd'},
                            {'ticker': 'SQ', 'reason': 'tbd'},
                            {'ticker': 'TTWO', 'reason': 'tbd'},
                            {'ticker': 'OTRK', 'reason': 'tbd'},
                            {'ticker': 'HUM', 'reason': 'tbd'},
                            {'ticker': 'AAPL', 'reason': 'tbd'},
                            {'ticker': 'ZG', 'reason': 'tbd'},
                            {'ticker': 'MSFT', 'reason': 'tbd'},
                            {'ticker': 'NVDA', 'reason': 'tbd'},
                            {'ticker': 'BEP', 'reason': 'tbd'},
                            {'ticker': 'GOOGL', 'reason': 'tbd'},
                            {'ticker': 'ETSY', 'reason': 'tbd'},
                            {'ticker': 'IVAC', 'reason': 'tbd'},
                            {'ticker': 'PTON', 'reason': 'tbd'},
                            {'ticker': 'ADI', 'reason': 'tbd'},
                            {'ticker': 'CRM', 'reason': 'tbd'},
                            {'ticker': 'CHWY', 'reason': 'tbd'},
                            {'ticker': 'AZN', 'reason': 'tbd'}])
    }
