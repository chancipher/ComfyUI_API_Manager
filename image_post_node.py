import json
import requests
from io import BytesIO
import numpy as np
from PIL import Image


class PostImageToAPI:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", ),
                "api_method": ("STRING", {"default": "PUT"}),
                "api_content_type": ("STRING", {"default": "image/jpg"}),
                "api_url": ("STRING", {"default": ""}),
                "api_callback": ("STRING", {"default": ""}),
                "api_object_id": ("STRING", {"default": ""}),
                "api_key": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "post_images"
    CATEGORY = "API Manager"
    OUTPUT_NODE = True

    def post_images(self, images, api_method, api_content_type, api_url, api_object_id, api_key="", api_callback=""):
        if not api_url:
            print("PostImageToAPI: No API URL provided. Exiting.")
            return {"api_responses": []}

        api_url = api_url.replace("$id", api_object_id)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Content-Type': api_content_type
        }

        if api_key:
            headers.update({'Authorization': api_key})
        results = []

        for (batch_number, image_tensor) in enumerate(images):
            image_np = 255. * image_tensor.cpu().numpy()
            image = Image.fromarray(np.clip(image_np, 0, 255).astype(np.uint8))
            buffer = BytesIO()
            image.save(buffer, format="JPEG")
            buffer.seek(0)

            # Specify file name and MIME type
            files = {'file': ('image.jpg', buffer, api_content_type)}

            if api_method == 'PUT':
                response = requests.put(api_url, headers=headers, data=buffer)
            else:
                del headers['Content-Type']
                response = requests.post(api_url, headers=headers, files=files)

            if response.status_code == 200:
                results.append(response.content)
            else:
                print(f"Error posting image {batch_number}: {response.text}")

            print(f"PostImageToAPI: {api_method} image to {api_url}\nResponse: {results}")

            if api_callback:
                headers.update({'Content-Type': 'application/json'})

                json_data = {
                        'object_id': api_object_id,
                        'size': buffer.getbuffer().nbytes,
                        'width': image.width,
                        'height': image.height,
                        'format': 'JPEG' 
                        }
                response = requests.post(api_callback, headers=headers, json=json_data)
                if response.status_code == 201:
                    pass
                else:
                    print(f"Error callback {batch_number}: {response.text}")

            return {"api_responses": results}

NODE_CLASS_MAPPINGS = {
    "PostImageToAPI": PostImageToAPI,
}

# Define human-readable names for your nodes (optional)
NODE_DISPLAY_NAME_MAPPINGS = {
    "PostImageToAPI": "Image Post Node",
}
