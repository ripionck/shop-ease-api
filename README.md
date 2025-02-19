
# ShopEase API Documentation

Welcome to the ShopEase API documentation. This API allows you to manage users, categories, products, wishlists, carts, reviews, orders, and payments for an e-commerce platform.

---

## Base URL
The base URL for all API endpoints is:
```
http://127.0.0.1:8000/api/v1/
```

---

## Authentication
Most endpoints require authentication using a Bearer Token. Include the token in the `Authorization` header as follows:
```
Authorization: Bearer <token>
```

---

## Endpoints

### Users

#### 1. User Login
- **URL**: `/login/`
- **Method**: `POST`
- **Body** (JSON):
  ```json
  {
    "email": "admin@example.com",
    "password": "admin123!"
  }
  ```

#### 2. User Register
- **URL**: `/register/`
- **Method**: `POST`
- **Body** (JSON):
  ```json
  {
    "username": "test",
    "email": "test@example.com",
    "phone_number": "12134567890",
    "password": "test123!"
  }
  ```

#### 3. View Profile
- **URL**: `/profile/`
- **Method**: `GET`
- **Authorization**: Bearer Token

#### 4. Edit Profile
- **URL**: `/profile/`
- **Method**: `PUT`
- **Authorization**: Bearer Token
- **Body** (JSON):
  ```json
  {
    "country": "Bangladesh"
  }
  ```

---

### Categories

#### 1. Add Category
- **URL**: `/categories/`
- **Method**: `POST`
- **Authorization**: Bearer Token
- **Body** (JSON):
  ```json
  {
    "name": "Smart Home",
    "description": "Devices for home automation",
    "parent_category": "",
    "subcategories": [
      {
        "name": "Smart Speakers",
        "description": "Voice-controlled speakers"
      },
      {
        "name": "Smart Lighting",
        "description": "Automated lighting systems"
      }
    ]
  }
  ```

#### 2. Update Category
- **URL**: `/categories/{category_id}/`
- **Method**: `PUT`
- **Authorization**: Bearer Token
- **Body** (JSON):
  ```json
  {
    "name": "Updated Electronics",
    "description": "Updated description for electronic devices and accessories",
    "parent_category": null,
    "subcategories": [
      {
        "name": "Updated Smartphones",
        "description": "Updated mobile phones and accessories"
      },
      {
        "name": "Updated Laptops",
        "description": "Updated laptops and notebooks"
      }
    ]
  }
  ```

#### 3. Retrieve Categories
- **URL**: `/categories/`
- **Method**: `GET`

#### 4. Delete Category
- **URL**: `/categories/{category_id}/`
- **Method**: `DELETE`
- **Authorization**: Bearer Token

---

### Products

#### 1. Add Product
- **URL**: `/products/`
- **Method**: `POST`
- **Authorization**: Bearer Token
- **Body** (JSON):
  ```json
  {
    "name": "Wireless Gaming Headset",
    "description": "Immerse yourself in the game with this comfortable and high-quality wireless headset.",
    "price": "99.99",
    "discounted_price": "79.99",
    "category_id": "0be23434-7fd4-468d-9e1d-d41ff7b2b77d",
    "brand": "GameOn",
    "stock": 20,
    "features": [
      "Low-latency wireless connection",
      "Noise-canceling microphone",
      "50mm drivers"
    ],
    "specifications": [
      {"key": "Frequency response", "value": "20Hz - 20kHz"},
      {"key": "Wireless range", "value": "15m"}
    ],
    "tags": [
      "gaming",
      "headset",
      "wireless"
    ]
  }
  ```

#### 2. Image Upload
- **URL**: `/products/{product_id}/images/`
- **Method**: `POST`
- **Authorization**: Bearer Token
- **Body** (form-data):
  ```
  image: <file>
  is_main: True
  ```

#### 3. All Products
- **URL**: `/products/`
- **Method**: `GET`

#### 4. Single Product
- **URL**: `/products/{product_id}/`
- **Method**: `GET`

#### 5. Update Product
- **URL**: `/products/{product_id}/`
- **Method**: `PATCH`
- **Authorization**: Bearer Token
- **Body** (JSON):
  ```json
  {
    "name": "Gaming Console X Updated"
  }
  ```

#### 6. Delete Product
- **URL**: `/products/{product_id}/`
- **Method**: `DELETE`
- **Authorization**: Bearer Token

---

### Wishlist

#### 1. All Wishlist
- **URL**: `/wishlist/`
- **Method**: `GET`
- **Authorization**: Bearer Token

#### 2. Add Wishlist
- **URL**: `/wishlist/add/`
- **Method**: `POST`
- **Authorization**: Bearer Token
- **Body** (JSON):
  ```json
  {
    "product_id": "e0db2959-9c20-4589-b2a5-e2150020f35e"
  }
  ```

#### 3. Remove Wishlist
- **URL**: `/wishlist/remove/{wishlist_id}/`
- **Method**: `DELETE`
- **Authorization**: Bearer Token

---

### Cart

#### 1. Cart Items
- **URL**: `/cart/`
- **Method**: `GET`
- **Authorization**: Bearer Token

#### 2. Add to Cart
- **URL**: `/cart/add/`
- **Method**: `POST`
- **Authorization**: Bearer Token
- **Body** (JSON):
  ```json
  {
    "product_id": "e0db2959-9c20-4589-b2a5-e2150020f35e",
    "quantity": 1
  }
  ```

#### 3. Update Cart
- **URL**: `/cart/update/{product_id}/`
- **Method**: `PATCH`
- **Authorization**: Bearer Token
- **Body** (JSON):
  ```json
  {
    "quantity": 5
  }
  ```

#### 4. Remove Item
- **URL**: `/cart/remove/{product_id}/`
- **Method**: `DELETE`
- **Authorization**: Bearer Token

---

### Reviews

#### 1. Add Review
- **URL**: `/products/{product_id}/reviews/`
- **Method**: `POST`
- **Authorization**: Bearer Token
- **Body** (JSON):
  ```json
  {
    "rating": 5,
    "comment": "This product is amazing! Highly recommended."
  }
  ```

#### 2. All Reviews
- **URL**: `/products/{product_id}/reviews/`
- **Method**: `GET`

#### 3. Delete Review
- **URL**: `/reviews/{review_id}/`
- **Method**: `DELETE`
- **Authorization**: Bearer Token

#### 4. Edit Review
- **URL**: `/reviews/{review_id}/`
- **Method**: `PATCH`
- **Authorization**: Bearer Token
- **Body** (JSON):
  ```json
  {
    "rating": 4
  }
  ```

---

### Orders

#### 1. Add Order
- **URL**: `/orders/create/`
- **Method**: `POST`
- **Authorization**: Bearer Token
- **Body** (JSON):
  ```json
  {
    "products": [
      { "product_id": "1734bb47-0177-49db-903e-5f1a4bb520fc", "quantity": 1 },
      { "product_id": "815d4748-53f6-451a-ae38-0c3330aaefd6", "quantity": 4 }
    ],
    "shipping_address": {
      "street": "123 Main St",
      "city": "Anytown",
      "state": "State",
      "country": "Country",
      "zipCode": "12345"
    },
    "payment_method": "credit_card"
  }
  ```

#### 2. Update Status
- **URL**: `/orders/update-status/{order_id}/`
- **Method**: `PATCH`
- **Authorization**: Bearer Token
- **Body** (JSON):
  ```json
  {
    "status": "shipped"
  }
  ```

#### 3. Track Order
- **URL**: `/orders/track/{order_id}/`
- **Method**: `GET`
- **Authorization**: Bearer Token

#### 4. Order Details
- **URL**: `/orders/{order_id}/`
- **Method**: `GET`
- **Authorization**: Bearer Token

#### 5. All Orders
- **URL**: `/orders/`
- **Method**: `GET`
- **Authorization**: Bearer Token

#### 6. Cancel Order
- **URL**: `/orders/cancel/{order_id}/`
- **Method**: `PATCH`
- **Authorization**: Bearer Token
- **Body** (JSON):
  ```json
  {
    "status": "cancelled"
  }
  ```

---

### Payments

#### 1. Create Payment
- **URL**: `/payments/`
- **Method**: `POST`
- **Authorization**: Bearer Token
- **Body** (JSON):
  ```json
  {
    "order": "c1b7c291-ccb3-4900-be86-17b41d9844e0",
    "amount": "100.00",
    "payment_method": "credit_card"
  }
  ```

#### 2. Payment Details
- **URL**: `/payments/{payment_id}/`
- **Method**: `GET`
- **Authorization**: Bearer Token

---

## Testing
To test the API, use the following endpoint:
- **URL**: `/`
- **Method**: `GET`

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

For any questions or issues, please contact the development team.

---

This `README.md` file provides a comprehensive guide to using the ShopEase API. You can customize it further based on your specific requirements.
