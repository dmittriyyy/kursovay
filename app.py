import os
from flask import Flask, flash, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import func
from datetime import datetime, timedelta
import threading
import logging
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///WebsiteForCarSales.db?check_same_thread=False'
app.config['SECRET_KEY'] = 'your_secret_key' 
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 299,
}
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)
migrate = Migrate(app, db) 

class Autosalon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=False)

class Manager(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_salon = db.Column(db.Integer, db.ForeignKey('autosalon.id'), nullable=False)
    FIO = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(200),nullable=False )

class Cars(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_salon = db.Column(db.Integer, db.ForeignKey('autosalon.id'), nullable=False)
    model = db.Column(db.String(150), nullable=False)
    brend = db.Column(db.String(150), nullable=False)
    body_type = db.Column(db.String(30),nullable=False)
    drive_type = db.Column(db.String(30),nullable=False)
    VIN = db.Column(db.String(17), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    mileage = db.Column(db.Integer, nullable=False)
    horsepower = db.Column(db.Integer,nullable=False)
    type_fuel = db.Column(db.String(50), nullable=False)
    fuel_consumption = db.Column(db.String(30), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    motor_volume = db.Column(db.String(10), nullable=False)
    transmission = db.Column(db.String(20), nullable=False)
    reliable = db.Column(db.Boolean, nullable=False, default=False)
    economical = db.Column(db.Boolean, nullable=False, default=False)
    for_evening_walk = db.Column(db.Boolean, nullable=False, default=False)
    aesthetic = db.Column(db.Boolean, nullable=False, default=False)
    info = db.Column(db.String(50), nullable = True)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    FIO = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(200),nullable=False )

class Reservations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    id_manager = db.Column(db.Integer, db.ForeignKey('manager.id'), nullable = False)
    id_cars = db.Column(db.Integer ,db.ForeignKey('cars.id'), nullable = False )
    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(30), nullable = False)
    info = db.Column(db.Text, nullable = False)
    
@app.route("/")
@app.route("/CarFinder")
def glavnya():
    brand = request.args.get('brand')
    price_range = request.args.get('priceRange')
    horsepower_range = request.args.get('horsepower')
    drive_type = request.args.get('driveType')
    body_type = request.args.get('bodyType')
    mileage_range = request.args.get('mileage')
    reliable = request.args.get('reliable')
    economical = request.args.get('economical')
    for_evening_walk = request.args.get('for_evening_walk')
    aesthetic = request.args.get('aesthetic')

    # Запрос к таблице
    query = Cars.query.filter(Cars.info == None)  # Исключаем автомобили с информацией в поле info

    if brand and brand != 'Выберите марку':
        query = query.filter(func.lower(Cars.brend) == func.lower(brand))

    if price_range:
        try:
            price_min, price_max = map(int, price_range.split('-'))
            query = query.filter(Cars.price >= price_min, Cars.price <= price_max)
        except ValueError:
            pass 

    if horsepower_range:
        try:
            horsepower_min, horsepower_max = map(int, horsepower_range.split('-'))
            query = query.filter(Cars.horsepower >= horsepower_min, Cars.horsepower <= horsepower_max)
        except ValueError:
            pass  

    if drive_type:
        query = query.filter(func.lower(Cars.drive_type) == func.lower(drive_type))

    if body_type and body_type != 'Выберите тип кузова':
        query = query.filter(func.lower(Cars.body_type) == func.lower(body_type))

    if mileage_range:
        try:
            mileage_min, mileage_max = map(int, mileage_range.split('-'))
            query = query.filter(Cars.mileage >= mileage_min, Cars.mileage <= mileage_max)
        except ValueError:
            pass  

    if reliable:
        query = query.filter(Cars.reliable == True)

    if economical:
        query = query.filter(Cars.economical == True)

    if for_evening_walk:
        query = query.filter(Cars.for_evening_walk == True)

    if aesthetic:
        query = query.filter(Cars.aesthetic == True)

    cars = query.all()

    # Добавляем пути к фотографиям для каждого автомобиля
    for car in cars:
        car_folder = os.path.join(app.static_folder, 'img', str(car.id))
        os.makedirs(car_folder, exist_ok=True)  # Убедитесь, что папка существует
        car.images = [f'img/{car.id}/{img}' for img in os.listdir(car_folder) if os.path.isfile(os.path.join(car_folder, img))]

    return render_template("glavnya.html", cars=cars, 
                           brand=brand, 
                           priceRange=price_range, 
                           horsepower=horsepower_range, 
                           driveType=drive_type, 
                           bodyType=body_type, 
                           mileage=mileage_range, 
                           reliable=reliable, 
                           economical=economical, 
                           for_evening_walk=for_evening_walk, 
                           aesthetic=aesthetic)
    #Пара "ключ-значение", где var1 — это имя переменной, которое будет доступно в шаблоне, 
    # а value1 — это значение, которое будет присвоено этой переменной другими словами
    #переменная, содержащая значение бренда, которое вы получили из URL-запроса.

@app.route("/Cars")
def about():
    return render_template("about.html")

@app.route('/cars_by_autosalon/<int:autosalon_id>')
def cars_by_autosalon(autosalon_id):
    # Фильтруем автомобили по id автосалона
    cars = Cars.query.filter_by(id_salon=autosalon_id, info=None).all()
    # Получаем информацию об автосалоне
    autosalon = Autosalon.query.get_or_404(autosalon_id)

    manager = Manager.query.filter_by(id_salon = autosalon_id).all()
    
    # Отображаем результаты на странице
    return render_template('cars_by_autosalon.html', cars=cars, autosalon=autosalon, managers = manager)

@app.route("/Autosalon")
def autosalon():
    autosalons = Autosalon.query.all() # достаем все посты из БД
    return render_template("autosalon.html", autosalons=autosalons)

@app.route('/car_details/<int:car_id>')
def car_details(car_id):
    car = Cars.query.get_or_404(car_id)
    car_folder = os.path.join(app.static_folder, 'img', str(car.id))
    os.makedirs(car_folder, exist_ok=True)  #  папка существует
    images = [f'img/{car.id}/{img}' for img in os.listdir(car_folder) if os.path.isfile(os.path.join(car_folder, img))]
    return render_template('car_details.html', car=car, images=images)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session and 'manager_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/test_drive_form/<int:car_id>')
def test_drive_form(car_id):
    car = Cars.query.get_or_404(car_id)
    
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в систему, чтобы записаться на тест-драйв.', 'warning')
        return redirect(url_for('login'))
    
    user = Users.query.get(session['user_id'])
    return render_template('test_drive_form.html', car=car, user=user)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
db_lock = threading.Lock() # - создание блокировки для потоков

@app.route('/submit_test_drive', methods=['POST'])
def submit_test_drive():
    data = request.form
    fio = data['fio']
    phone = data['phone']
    email = data['email']
    car_id = data['car_id']
    test_drive_time_str = data['test_drive_time']

    # Преобразуем строку времени в объект datetime
    try:
        test_drive_time = datetime.fromisoformat(test_drive_time_str)
    except ValueError:
        return "Неверный формат времени", 400

    logger.debug(f"Received data: fio={fio}, phone={phone}, email={email}, car_id={car_id}, test_drive_time={test_drive_time}")

    with app.app_context():
        try:
            # Найти автомобиль
            car = Cars.query.get(car_id)
            if not car:
                logger.error(f"Car not found for id: {car_id}")
                return "Автомобиль не найден", 404

            # Время окончания тест-драйва (выбранное время + 30 минут)
            test_drive_end_time = test_drive_time + timedelta(minutes=30)

            # Проверка доступности времени
            # Проверяем, есть ли уже активная или подтвержденная бронь, которая пересекается с выбранным временем
            existing_reservation = Reservations.query.filter(
                Reservations.id_cars == car.id,
                Reservations.status.in_(['активно', 'подтверждено']),  # Проверяем активные и подтвержденные брони
                # Условие для проверки пересечения времени
                (Reservations.date == test_drive_time) & (Reservations.date <= test_drive_end_time)
            ).first()

            if existing_reservation:
                return "Выбранное время занято. Пожалуйста, выберите другое время.", 400

            # Проверка диапазона времени (сегодня + месяц)
            current_time = datetime.now()
            one_month_later = current_time + timedelta(days=30)

            if test_drive_time < current_time or test_drive_time > one_month_later:
                return "Время должно быть в пределах текущего дня и месяца от текущей даты.", 400

            # Проверка времени на соответствие диапазону с 10:00 до 20:00
            if test_drive_time.hour < 10 or test_drive_time.hour > 20 or (test_drive_time.hour == 20 and test_drive_time.minute > 0):
                return "Тест-драйв можно записать только в промежуток с 10:00 до 20:00.", 400

            # Найти или создать пользователя
            user = Users.query.filter_by(email=email).first()
            if not user:
                user = Users(FIO=fio, phone=phone, email=email)
                db.session.add(user)
                db.session.flush()  # Сбросить сессию, чтобы получить id пользователя

            # Найти автосалон
            autosalon = Autosalon.query.get(car.id_salon)
            if not autosalon:
                logger.error(f"Autosalon not found for id: {car.id_salon}")
                return "Автосалон не найден", 404

            # Найти менеджера
            manager = Manager.query.filter_by(id_salon=autosalon.id).order_by(func.random()).first()
            if not manager:
                logger.error(f"Manager not found for autosalon id: {autosalon.id}")
                return "Менеджер не найден", 404

            # Создать запись о резервировании
            reservation = Reservations(
                id_user=user.id,
                id_manager=manager.id,
                id_cars=car.id,
                date=test_drive_time,  # Сохраняем выбранное время тест-драйва в поле date
                status='активно'
            )
            db.session.add(reservation)

            db.session.commit()

        except Exception as e:
            db.session.rollback()
            logger.error(f"Database error: {e}")
            return f"Ошибка при сохранении в базу данных: {e}", 500

    return redirect(url_for('car_details', car_id=car_id))


@app.route('/reservations', methods=['GET', 'POST'])
def reservations():
    if 'manager_id' not in session:
        return redirect(url_for('login'))
    
    manager_id = session['manager_id']
    
    # Получаем информацию о текущем менеджере
    manager = Manager.query.get(manager_id)
    
    if not manager:
        return "Менеджер не найден", 404
    
    # Фильтруем бронирования по id_salon текущего менеджера
    reservations = Reservations.query.join(Cars).filter(
        Cars.id_salon == manager.id_salon,
        Reservations.status != 'удалено'  # Исключаем резервации со статусом "удалено"
    ).all()
    
    # Получаем данные о пользователях и автомобилях для каждой резервации
    for reservation in reservations:
        reservation.user = Users.query.get(reservation.id_user)
        reservation.car = Cars.query.get(reservation.id_cars)
    
    if request.method == 'POST':
        reservation_id = request.form['reservation_id']
        action = request.form['action']
        reservation = Reservations.query.get(reservation_id)
        if action == 'confirm':
            reservation.status = 'подтверждено'
            reservation.info = f'подтверждено {manager.FIO}'
        elif action == 'delete':
            reservation.status = 'удалено'  
            reservation.info = f'удалено {manager.FIO}'
        db.session.commit()
        return redirect(url_for('reservations'))
    
    return render_template('reservations.html', reservations=reservations)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Проверка в таблице Manager
        manager = Manager.query.filter_by(email=email).first()
        if manager and manager.password == password:
            session['manager_id'] = manager.id
            return redirect(url_for('glavnya'))

        # Проверка в таблице Users
        user = Users.query.filter_by(email=email).first()
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('glavnya'))

        return "Неверный логин или пароль", 401

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('manager_id', None)
    session.pop('user_id', None)
    return redirect(url_for('glavnya'))

@app.route('/registration', methods=['GET'])
def registration():
    return render_template('registration.html')
@app.route('/register', methods=['POST'])
def register():
    fio = request.form['fio']
    email = request.form['email']
    phone = request.form['phone']
    password = request.form['password']

    # Проверка, что пользователь с таким email еще не зарегистрирован
    existing_user = Users.query.filter_by(email=email).first()
    if existing_user:
        return "Пользователь с таким email уже существует", 400

    # Создание нового пользователя
    new_user = Users(FIO=fio, email=email, phone=phone, password=password)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('login'))

@app.route('/car_upr', methods=['GET', 'POST'])
def car_upr():
    if 'manager_id' not in session:
        return redirect(url_for('login'))

    manager_id = session['manager_id']
    manager = Manager.query.get(manager_id)

    if not manager:
        return "Менеджер не найден", 404

    if request.method == 'POST':
        # Проверяем наличие ключа 'action' в данных формы
        if 'action' not in request.form:
            flash('Неверный запрос', 'error')
        else:
            action = request.form['action']
            if action == 'add':
                # Проверяем, что машина с таким VIN еще не существует
                vin = request.form['vin']
                existing_car = Cars.query.filter_by(VIN=vin).first()
                if existing_car:
                    flash('Машина с таким VIN уже существует', 'error')
                else:
                    new_car = Cars(
                        id_salon=manager.id_salon,  # Добавляем id_salon текущего менеджера
                        model=request.form['model'],
                        brend=request.form['brend'],
                        body_type=request.form['body_type'],
                        drive_type=request.form['drive_type'],
                        VIN=vin,
                        year=request.form['year'],
                        price=request.form['price'],
                        mileage=request.form['mileage'],
                        type_fuel=request.form['fuel_type'],
                        fuel_consumption=request.form['fuel_consumption'],
                        color=request.form['color'],
                        motor_volume=request.form['motor_volume'],
                        transmission=request.form['transmission'],
                        reliable=bool(request.form.get('reliable')),
                        economical=bool(request.form.get('economical')),
                        for_evening_walk=bool(request.form.get('for_evening_walk')),
                        aesthetic=bool(request.form.get('aesthetic')),
                        horsepower=request.form['horsepower']  # Добавляем поле horsepower
                    )
                    db.session.add(new_car)
                    db.session.commit()

                    # Сохраняем фотографии
                    if 'images' in request.files:
                        car_folder = os.path.join(app.static_folder, 'img', str(new_car.id))
                        os.makedirs(car_folder, exist_ok=True)
                        for file in request.files.getlist('images'):
                            if file.filename != '':
                                filename = secure_filename(file.filename)
                                file.save(os.path.join(car_folder, filename))

                    flash('Машина успешно добавлена', 'success')
            elif action == 'delete':
                car_id = request.form['car_id']
                car = Cars.query.get(car_id)
                if car.id_salon != manager.id_salon:
                    return "Вы не можете удалить эту машину", 403
                car.info = f"Удалено менеджером {manager.FIO} ({manager.email})"
                db.session.commit()
                flash('Машина успешно удалена', 'success')

    # Фильтруем машины по id_salon текущего менеджера и исключаем удаленные
    cars = Cars.query.filter_by(id_salon=manager.id_salon).filter(Cars.info == None).all()
    return render_template('car_upr.html', cars=cars)


@app.route('/edit_car/<int:car_id>', methods=['GET', 'POST'])
@login_required
def edit_car(car_id):
    car = Cars.query.get_or_404(car_id)
    manager_id = session['manager_id']
    manager = Manager.query.get(manager_id)

    if car.id_salon != manager.id_salon:
        return "Вы не можете редактировать эту машину", 403

    if request.method == 'POST':
        car.model = request.form['model']
        car.brend = request.form['brend']
        car.body_type = request.form['body_type']
        car.drive_type = request.form['drive_type']
        car.VIN = request.form['vin']
        car.year = request.form['year']
        car.price = request.form['price']
        car.mileage = request.form['mileage']
        car.type_fuel = request.form['fuel_type']
        car.fuel_consumption = request.form['fuel_consumption']
        car.color = request.form['color']
        car.motor_volume = request.form['motor_volume']
        car.transmission = request.form['transmission']
        car.horsepower = request.form['horsepower']
        car.reliable = bool(request.form.get('reliable'))
        car.economical = bool(request.form.get('economical'))
        car.for_evening_walk = bool(request.form.get('for_evening_walk'))
        car.aesthetic = bool(request.form.get('aesthetic'))

        db.session.commit()

        # Сохраняем фотографии
        if 'images' in request.files:
            car_folder = os.path.join(app.static_folder, 'img', str(car.id))
            os.makedirs(car_folder, exist_ok=True)
            for file in request.files.getlist('images'):
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(car_folder, filename))

        flash('Машина успешно отредактирована', 'success')
        return redirect(url_for('car_upr'))

    return render_template('edit_car.html', car=car)

if __name__ == '__main__': 
    port = int(os.environ.get('PORT', 5000))  # Используйте порт из Render или 5000 по умолчанию
    app.run(host='0.0.0.0', port=port, debug=True)
    



