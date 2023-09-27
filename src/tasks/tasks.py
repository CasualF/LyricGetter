from src.tasks.celery_app import celery
from PIL import Image
from io import BytesIO


@celery.task(bind=True)
def process_pic(self, image_data, name: str):
    image = Image.open(BytesIO(*image_data))
    image_path = f'media/images/{name}.jpg'
    image.save(image_path)


@celery.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
