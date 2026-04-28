import httpx
import asyncio
import json

async def test():
    async with httpx.AsyncClient() as c:
        # Upload file
        files = {'file': ('test.csv', b'transaction_id,timestamp,amount,currency,from_account,to_account,location,type,note\nTXN001,2024-01-15T09:30:00,45000,INR,ACCT-001,OFFSHORE-001,Cayman Islands,wire_transfer,\nTXN002,2024-01-16T09:30:00,50000,INR,ACCT-001,OFFSHORE-001,Cayman Islands,wire_transfer,\nTXN003,2024-01-17T09:30:00,49000,INR,ACCT-001,OFFSHORE-001,Cayman Islands,wire_transfer,\nTXN004,2024-01-18T09:30:00,1200000,INR,ACCT-001,OFFSHORE-001,Cayman Islands,wire_transfer,', 'text/csv')}
        r = await c.post('http://localhost:8000/api/v1/analyze/csv', files=files, data={'subject_account': 'admin'})
        print(json.dumps(r.json(), indent=2))

asyncio.run(test())
