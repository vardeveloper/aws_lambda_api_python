### [docs API]()

#####Subscription

Endpoint :

    https://z4rww46vh0.execute-api.us-east-1.amazonaws.com/dev/emblue/public/v1/subscription

Method :

    POST
    
Headers:

    Content-Type: application/json

Input : required fields (brand, email)

    {
	    "brand": "gestion",
	    "email": "victor.alcantara@fractalservicios.pe",
	    "name": "Victor",
	    "last_name": "Alcantara"
    }

Output :

    { 
        "result": "Event Tracked." 
    }
    
