from tortoise import fields

from . import AbstractBaseModel


class FoodCategory(AbstractBaseModel):
        name = fields.TextField()

        @staticmethod
        async def get_food_cathegory(id):
            return await FoodCategory.get(id=id)
