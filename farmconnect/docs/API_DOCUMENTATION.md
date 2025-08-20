# FarmConnect API Documentation

## Base Information
- **Base URL**: `http://localhost:8000/api`
- **Documentation**: `http://localhost:8000/docs`
- **Authentication**: JWT Bearer tokens

## Quick Start
```python
import requests

# Login to get token
response = requests.post("http://localhost:8000/api/auth/login", json={
    "email": "farmer@example.com", 
    "password": "password123"
})
token = response.json()["access_token"]

# Use token for authenticated requests
headers = {"Authorization": f"Bearer {token}"}
products = requests.get("http://localhost:8000/api/products", headers=headers)
```

## Core Endpoints

### Price Comparison
- `GET /price-comparison` - Real-time price comparisons
- `GET /price-comparison/product/{id}/history` - Price history
- `POST /price-comparison/refresh` - Manual price refresh

### Products  
- `GET /products` - List products with filters
- `POST /products` - Create product (farmers only)
- `PUT /products/{id}` - Update product
- `DELETE /products/{id}` - Delete product

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/profile` - Get user profile

### Orders
- `GET /orders` - List user orders  
- `POST /orders` - Create new order
- `PUT /orders/{id}/status` - Update order status

## Response Examples

### Price Comparison Response
```json
{
  "comparisons": [
    {
      "product_id": 1,
      "product_name": "Tomatoes",
      "farmer_price": 45.00,
      "platform_prices": {
        "bigbasket": 65.00,
        "zepto": 70.00, 
        "swiggy": 68.00
      },
      "savings_amount": 20.00,
      "savings_percentage": 30.8,
      "last_updated": "2025-08-19T16:00:00Z"
    }
  ]
}
```

### Product Listing Response  
```json
{
  "products": [
    {
      "id": 1,
      "name": "Organic Tomatoes",
      "price": 45.00,
      "unit": "kg", 
      "farmer": {
        "farm_name": "Green Valley Farm",
        "rating": 4.7
      }
    }
  ]
}
```

## Testing the API

### Using curl
```bash
# Get price comparison
curl "http://localhost:8000/api/price-comparison"

# Login and use token
TOKEN=$(curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' | jq -r '.access_token')

curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/products"
```

For complete API documentation with interactive testing, visit http://localhost:8000/docs after starting the application.
