psql -h localhost -U temporal -d temporal -p 5436 -W

curl -X POST http://localhost:8000/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Điện thoại Iphone 15",
    "description": "Điện thoại thông minh cao cấp từ Apple",
    "price": 25000,
    "stock_quantity": 50,
    "category": "electronics"
  }'