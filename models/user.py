from datetime import datetime

from tortoise import fields

from . import AbstractBaseModel


class User(AbstractBaseModel):
        chat_id = fields.TextField()
        calories = fields.FloatField(default=0)
        proteins = fields.FloatField(default=0)
        fats = fields.FloatField(default=0)
        carbohydrates = fields.FloatField(default=0)
        age = fields.IntField(default=0)

        @staticmethod
        async def add_user(chat_id):
            await User.get_or_create(chat_id=chat_id)

        @staticmethod
        async def is_user_not_empty(chat_id):
            return await User.exists(chat_id=chat_id)

        @staticmethod
        async def add_info(user, data):
            await User.filter(chat_id=user).update(
                    calories=data.get('calories'),
                    proteins=data.get('proteins'),
                    fats=data.get('fats'),
                    carbohydrates=data.get('carbohydrates')
            )

        @staticmethod
        async def get_food_by_user(chat, date=None):
            if date:
                date = datetime.strptime(date, "%Y-%m-%d").date()
            else:
                date = datetime.now().date()

            user = await User.filter(chat_id=chat).get()
            return await user.food.filter(date=date)

        @staticmethod
        async def get_cal_by_user(user, date=None):
            if date:
                date = datetime.strptime(date, "%Y-%m-%d").date()
            else:
                date = datetime.now().date()

            cal = await user.food.filter(date=date).values_list('calories', flat=True)

            return sum(cal)

        @staticmethod
        async def get_calories_by_user(user, date=None):
            if date:
                date = datetime.strptime(date, "%Y-%m-%d").date()
            else:
                date = datetime.now().date()

            calories = await user.food.filter(date=date).values_list('calories', flat=True)

            return sum(calories)

        @staticmethod
        async def get_proteins_by_user(user, date=None):
            if date:
                date = datetime.strptime(date, "%Y-%m-%d").date()
            else:
                date = datetime.now().date()

            proteins = await user.food.filter(date=date).values_list('proteins', flat=True)

            return sum(proteins)

        @staticmethod
        async def get_fats_by_user(user, date=None):
            if date:
                date = datetime.strptime(date, "%Y-%m-%d").date()
            else:
                date = datetime.now().date()

            fats = await user.food.filter(date=date).values_list('fats', flat=True)

            return sum(fats)

        @staticmethod
        async def get_carbohydrates_by_user(user, date=None):
            if date:
                date = datetime.strptime(date, "%Y-%m-%d").date()
            else:
                date = datetime.now().date()

            proteins = await user.food.filter(date=date).values_list('proteins', flat=True)

            return sum(proteins)

        @staticmethod
        async def delete_today(user, date=None):
            if date:
                date = datetime.strptime(date, "%Y-%m-%d").date()
            else:
                date = datetime.now().date()

            await user.food.filter(date=date).delete()
