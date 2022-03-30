from datetime import datetime

from peewee import *

from conf import DB

db = SqliteDatabase(DB)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    chat_id = TextField()
    calories = FloatField(default=0)
    proteins = IntegerField(default=0)
    fats = IntegerField(default=0)
    carbohydrates = IntegerField(default=0)
    age = IntegerField(default=0)


class FoodCategory(BaseModel):
    name = TextField()


class Food(BaseModel):
    user = ForeignKeyField(User, related_name='food')
    name = TextField()
    date = DateField()
    time = TimeField()
    calories = FloatField()
    category = ForeignKeyField(FoodCategory)
    weight = IntegerField()

    proteins = IntegerField(null=True, default=0)
    fats = IntegerField(null=True, default=0)
    carbohydrates = IntegerField(null=True, default=0)


def add_user_to_db(text):
    try:
        user = User.select().where(User.chat_id == text).get()
        return user
    except:
        user = User(
            chat_id=text,
        )
        user.save()
        return user


def user_not_empty(user):
    try:
        user = User.select().where(User.chat_id == user).get()
        if user.calories:
            return True
        else:
            return False
    except:
        user = User(
            chat_id=user,
        )
        user.save()
        return False


def user_calories(user):
    try:
        user = User.select().where(User.chat_id == user).get()
        return user.calories
    except:
        return 0


def get_user(text):
    return add_user_to_db(text)


def add_food_cathegory_to_db(text):
    try:
        cat = FoodCategory.select().where(FoodCategory.id == int(text)).get()
        return cat
    except:
        cat = FoodCategory(
            name=text,
        )
        cat.save()
        return cat


def add_calories_to_user(user, cal):
    user = User.select().where(User.chat_id == user).get()
    user.calories = cal
    user.save()


def add_proteins_to_user(user, proteins):
    user = User.select().where(User.chat_id == user).get()
    user.proteins = proteins
    user.save()


def add_fats_to_user(user, fats):
    user = User.select().where(User.chat_id == user).get()
    user.fats = fats
    user.save()


def add_carbohydrates_to_user(user, carbohydrates):
    user = User.select().where(User.chat_id == user).get()
    user.carbohydrates = carbohydrates
    user.save()


def add_food_for_user(user, category, name, calories, weight, proteins, fats, carbohydrates):
    food = Food(
        user=user,
        category=category,
        name=name,
        calories=float(calories),
        weight=int(weight),
        proteins=int(proteins),
        fats=int(fats),
        carbohydrates=int(carbohydrates),
        date=datetime.now().date(),
        time=datetime.now().time()
    )
    food.save()
    return food


def get_food_cathegory(id):
    try:
        return FoodCategory.select().where(FoodCategory.id == int(id)).get()
    except:
        return None


def get_food_by_user(chat, date=None):
    try:
        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
        else:
            date = datetime.now().date()

        user = User.select().where(User.chat_id == chat).get()
        foods = user.food.select().where(Food.date == date)

        return foods
    except:
        return []


def get_cal_by_user(chat, date=None):
    try:
        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
        else:
            date = datetime.now().date()

        user = User.select().where(User.chat_id == chat).get()
        cal = user.food.select(fn.SUM(Food.calories)).where(Food.date == date).scalar()

        return cal
    except:
        return 0


def get_prot_by_user(chat, date=None):
    try:
        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
        else:
            date = datetime.now().date()

        user = User.select().where(User.chat_id == chat).get()
        prot = user.food.select(fn.SUM(Food.proteins)).where(Food.date == date).scalar()

        return prot
    except:
        return 0


def get_fats_by_user(chat, date=None):
    try:
        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
        else:
            date = datetime.now().date()

        user = User.select().where(User.chat_id == chat).get()
        fats = user.food.select(fn.SUM(Food.fats)).where(Food.date == date).scalar()

        return fats
    except:
        return 0


def get_carb_by_user(chat, date=None):
    try:
        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
        else:
            date = datetime.now().date()

        user = User.select().where(User.chat_id == chat).get()
        cal = user.food.select(fn.SUM(Food.carbohydrates)).where(Food.date == date).scalar()

        return cal
    except:
        return 0


def init_db():
    db.create_tables([User, Food, FoodCategory])
    print('DB created')
