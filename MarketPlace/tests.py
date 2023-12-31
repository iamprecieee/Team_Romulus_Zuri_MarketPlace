from django.test import TestCase

# Create your tests here.

from rest_framework.test import APIClient
from .models import Shop, ProductCategory, Product
from django.urls import reverse
from rest_framework import status
from typing import OrderedDict
from .serializers import ProductSerializer


class TestGetAllProductsBasedOnCategory(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.test_shop = Shop.objects.create(
            name="Sample Shop",
            policy_confirmation=True,
            reviewed=True,
            rating=4.5
        )

        self.test_category1 = ProductCategory.objects.create(
            name="Sample Category 1",
            # parent_category = 1,
            status="approved"
        )

        self.test_category2 = ProductCategory.objects.create(
            name="Sample Category 2",
            # parent_category = 2,
            status="approved"
        )

        self.test_product1 = Product.objects.create(
            shop_id=self.test_shop,
            name="Sample Product 1",
            description="Sample Description 1",
            quantity=10,
            category=self.test_category1,
            image_id=1,
            price=100.00,
            discount_price=90.00,
            tax=10.00,
            is_published=True,
            currency="USD"
        )

        self.test_product2 = Product.objects.create(
            shop_id=self.test_shop,
            name="Sample Product 2",
            description="Sample Description 2",
            quantity=5,
            category=self.test_category1,
            image_id=2,
            price=50.00,
            discount_price=45.00,
            tax=5.00,
            is_published=True,
            currency="USD",
        )

    def test_get_all_products_by_category(self):
        url = reverse("get_all_products_by_categories", args=[self.test_category1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(len(response.data), None)
        for x in response.data:
            self.assertIsInstance(x, OrderedDict)
        print(response.data)

    def test_get_empty_products_list_by_category(self):
        url = reverse("get_all_products_by_categories", args=[self.test_category2])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
        print(response.data)

    def test_return_404_for_nonexistent_category(self):
        nonexistent_category = "NonExistentCategory"
        url = reverse("get_all_products_by_categories",
                      args=[nonexistent_category])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(b'{"message":"Category not found."}', list(response))
        self.assertEqual(response.data["message"], "Category not found.")
        print(response.data)

    def tearDown(self):
        self.test_shop.delete()
        self.test_category1.delete()
        self.test_category2.delete()
        self.test_product1.delete()
        self.test_product2.delete()


class ProductListAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient

        # To create sample test data
        self.test_shop = Shop.objects.create(
            name="Sample Shop",
            policy_confirmation=True,
            reviewed=True,
            rating=3.5
        )
        self.subcategory1 = 'ebook'
        self.subcategory2 = 'mobile_app'
        self.category_obj = ProductCategory.objects.create(name='digital services', status='approved')
        self.subcategory_obj_1 = ProductCategory.objects.create(name=self.subcategory1, shop_id=self.test_shop, parent_category_id=self.category_obj.id)
        self.subcategory_obj_2 = ProductCategory.objects.create(name=self.subcategory1, shop_id=self.test_shop, parent_category_id=self.category_obj.id)

        self.product1 = Product.objects.create(shop_id=1, name='Product_1', description='Product_1 description', quantity=10,
                                               category=self.subcategory_obj_1, price=1000.00, discount_price=100.00, tax=50.00, is_published=True, currency='Naira')
        self.product2 = Product.objects.create(shop_id=2, name='Product_2', description='Product_2 description', quantity=15,
                                               category=self.subcategory_obj_1, price=1300.00, discount_price=110.00, tax=70.00, is_published=True, currency='Naira')

    def test_list_products_sorted_by_price(self):
        # url = self.client.get(f'/api/products/category/{self.subcategory}')
        url2 = reverse('get_products_by_subcategories', args={'category': self.category_obj, 'subcategory': self.subcategory})  # args=[self.subcategory.id=1]
        response = self.client.get(url2, format='json', data={'ordering': 'price'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # To confirm that the response is ordered by price
        self.assertTrue(response.data[0], self.product1)
        # serializer = ProductSerializer(self.product1, many=True)
        # self.assertEqual(response.data, serializer.data)

    def test_list_products_sorted_by_name(self):
        url = reverse('get_products_by_subcategories', args={'category': self.category_obj, 'subcategory': self.subcategory1})  # , args=[self.subcategory.id=1]
        response = self.client.get(url, format='json', data={'ordering': 'name'})
        serializer = ProductSerializer(self.product2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        # To confirm that the response is ordered by price
        self.assertTrue(response.data[0], self.product1)

    def test_list_products_empty_subcategory(self):
        url = reverse('get_products_by_subcategories', args={'category': self.category_obj, 'subcategory': self.subcategory2})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        print(response.data)

    def test_list_nonexistent_category(self):
        url = reverse('get_products_by_subcategories', args={'category': self.category_obj, 'subcategory': 'Non existent subcategory'})
        response = self.client.get(url, format('json'))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def tearDown(self):
        self.category_obj.delete()
        self.subcategory_obj_1.delete()
        self.subcategory_obj_2.delete()

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import UserProfile, UserProductInteraction, Product

from django.contrib.auth.models import User  # Import User model

class RecommendationAPITest(TestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')

        # Create user profiles for test users
        UserProfile.objects.create(user=self.user1, age=25, gender='male')
        UserProfile.objects.create(user=self.user2, age=30, gender='female')

        # Create test products
        self.product1 = Product.objects.create(name='Product 1', description='Description of Product 1', category='Electronics', price=499.99)
        self.product2 = Product.objects.create(name='Product 2', description='Description of Product 2', category='Clothing', price=39.99)
        self.product3 = Product.objects.create(name='Product 3', description='Description of Product 3', category='Electronics', price=799.99)

        # Create test user-product interactions
        UserProductInteraction.objects.create(user=self.user1, product=self.product1, interaction_type='viewed')
        UserProductInteraction.objects.create(user=self.user1, product=self.product2, interaction_type='purchased')
        UserProductInteraction.objects.create(user=self.user2, product=self.product1, interaction_type='viewed')
        UserProductInteraction.objects.create(user=self.user2, product=self.product3, interaction_type='viewed')


    def test_recommendations_endpoint(self):
        # Test the recommendations/<int:user_id>/ endpoint

        # Replace with a valid user_id
        user_id = self.user1.id
        url = reverse('recommendations', args=[user_id])
        client = APIClient()
        response = client.get(url)

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Add more specific tests based on your recommendation logic
        # For now, let's check if the response is not empty
        self.assertNotEqual(len(response.data), 0)

    def test_invalid_user_id(self):
        # Test the recommendations/<int:user_id>/ endpoint with an invalid user_id
        url = reverse('recommendations', args=[999])  # Assuming user with ID 999 doesn't exist
        client = APIClient()
        response = client.get(url)

        # Check if the response status code is 404 Not Found
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Add more test cases as needed to cover different scenarios and edge cases
