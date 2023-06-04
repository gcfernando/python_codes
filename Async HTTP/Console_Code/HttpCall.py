# Developer ::> Gehan Fernando
# import libraries
import asyncio
import aiohttp
from pprint import pprint

base_url = 'http://northwind.now.sh/api/'

# Function to make HTTP requests asynchronously
async def make_request(method, url, data=None):
    async with aiohttp.ClientSession() as session:
        # Use aiohttp.ClientSession to manage the HTTP session
        
        # Make GET request
        if method.lower() == 'get':
            async with session.get(url) as response:
                return await response.json()
        # Make POST request
        elif method.lower() == 'post':
            async with session.post(url, json=data) as response:
                return await response.json()
        # Make PUT request
        elif method.lower() == 'put':
            async with session.put(url, json=data) as response:
                return await response.json()
        # Make DELETE request
        elif method.lower() == 'delete':
            async with session.delete(url) as response:
                return await response.json()

# Main asynchronous function
async def main():
    while True:
        data = None
        method = input("Enter Method (GET, POST, PUT, DELETE): ")

        if method == "POST" or method == "PUT":
            # For POST and PUT requests, prompt the user for category details
            id = int(input("Enter Category Id: "))
            name = input("Enter Category Name: ")
            description = input("Enter Category Description: ")
            data = {"id": id, "description": description, "name": name}
        elif method == "DELETE":
            # For DELETE request, prompt the user for the category id to delete
            id = int(input("Enter Category Id: "))

        if method.lower() == 'get':
            # Send a GET request to retrieve categories
            response = await make_request('GET', f'{base_url}/categories')
        elif method.lower() == 'post':
            # Send a POST request to create a new category
            response = await make_request('POST', f'{base_url}/categories', data=data)
        elif method.lower() == 'put':
            # Send a PUT request to update an existing category
            response = await make_request('PUT', f'{base_url}/categories/{id}', data=data)
        elif method.lower() == 'delete':
            # Send a DELETE request to delete a category
            response = await make_request('DELETE', f'{base_url}/categories/{id}')
        else:
            # If an invalid method is entered, exit the loop
            break

        pprint(response)

        status = input("More! (Y|N): ")

        if status.lower() != "y":
            # If the user does not want to continue, exit the loop
            break

# Run the main function asynchronously
loop = asyncio.get_event_loop()
loop.run_until_complete(main())