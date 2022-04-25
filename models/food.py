from datetime import datetime

from loguru import logger
from tortoise import fields

from . import AbstractBaseModel


class Food(AbstractBaseModel):
        user = fields.ForeignKeyField('models.User', related_name='food')
        name = fields.TextField()
        date = fields.DateField()
        time = fields.TimeField()
        calories = fields.FloatField()
        category = fields.ForeignKeyField('models.FoodCategory')
        weight = fields.IntField()

        proteins = fields.FloatField(null=True, default=0)
        fats = fields.FloatField(null=True, default=0)
        carbohydrates = fields.FloatField(null=True, default=0)

        @staticmethod
        async def add_food_for_user(user, category, name, calories, weight, proteins, fats, carbohydrates,
                                    date=datetime.now().date()):
            try:
                await Food.create(
                    user=user,
                    category_id=int(category),
                    name=name,
                    calories=float(calories),
                    weight=int(weight),
                    proteins=float(proteins),
                    fats=float(fats),
                    carbohydrates=float(carbohydrates),
                    date=date,
                    time=datetime.now().time()
                )
            except Exception as e:
                logger.error(f'{e}')
