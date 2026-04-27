"""
蜀来驰二手车展示网站
基于Flask的轻量级二手车展示与管理系统
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'slc_used_car_secret_key_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shulaichi.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/uploads/cars', exist_ok=True)
os.makedirs('static/uploads/sliders', exist_ok=True)

db = SQLAlchemy(app)

# ============== 数据库模型 ==============

class Admin(db.Model):
    """管理员模型"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

class Car(db.Model):
    """车辆模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 车型名称
    brand = db.Column(db.String(50), nullable=False)  # 品牌
    price = db.Column(db.Float, nullable=False)  # 价格（万）
    year = db.Column(db.Integer, nullable=False)  # 年份
    mileage = db.Column(db.Float, nullable=False)  # 公里数
    images = db.Column(db.Text)  # 图片JSON字符串
    description = db.Column(db.Text)  # 车况描述
    inspection_report = db.Column(db.Text)  # 检测报告
    status = db.Column(db.String(20), default='onsale')  # 状态：onsale, sold, hidden
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    view_count = db.Column(db.Integer, default=0)  # 浏览次数

class Slider(db.Model):
    """轮播图模型"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    image = db.Column(db.String(200), nullable=False)
    link = db.Column(db.String(200))
    order = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.now)

class SiteSettings(db.Model):
    """网站设置模型"""
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class VisitLog(db.Model):
    """访问日志"""
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(50))
    path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.now)

# ============== 辅助函数 ==============

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def save_image(file, folder='cars'):
    """保存图片并返回路径"""
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], folder, filename)
        file.save(filepath)
        return f"/static/uploads/{folder}/{filename}"
    return None

def get_site_setting(key, default=''):
    """获取网站设置"""
    setting = SiteSettings.query.filter_by(key=key).first()
    return setting.value if setting else default

def set_site_setting(key, value):
    """设置网站设置"""
    setting = SiteSettings.query.filter_by(key=key).first()
    if setting:
        setting.value = value
    else:
        setting = SiteSettings(key=key, value=value)
        db.session.add(setting)
    db.session.commit()

def init_default_data():
    """初始化默认数据"""
    # 创建默认管理员
    if not Admin.query.first():
        admin = Admin(
            username='admin',
            password_hash=generate_password_hash('slc123456')
        )
        db.session.add(admin)
    
    # 初始化默认网站设置
    default_settings = {
        'shop_name': '蜀来驰二手车',
        'shop_address': '四川省威远县',
        'shop_phone': '400-888-8888',
        'shop_wechat': 'slc888888',
        'shop_intro': '专业从事10万以内短公里数优质二手车，为您提供透明车况、放心交易的服务体验。',
        'shop_slides': json.dumps([
            {'title': '精选车源', 'image': '/static/images/slide1.jpg'},
            {'title': '展厅实拍', 'image': '/static/images/slide2.jpg'},
            {'title': '优惠活动', 'image': '/static/images/slide3.jpg'}
        ])
    }
    
    for key, value in default_settings.items():
        if not SiteSettings.query.filter_by(key=key).first():
            setting = SiteSettings(key=key, value=value)
            db.session.add(setting)
    
    # 添加示例车辆数据
    if not Car.query.first():
        sample_cars = [
            {
                'name': '大众朗逸 2019款 自动舒适版',
                'brand': '大众',
                'price': 7.5,
                'year': 2019,
                'mileage': 3.2,
                'images': json.dumps([
                    '/static/images/car1_1.jpg',
                    '/static/images/car1_2.jpg',
                    '/static/images/car1_3.jpg'
                ]),
                'description': '个人一手车，全程4S店保养，无事故无水泡，发动机变速箱状况良好，内饰干净整洁。',
                'inspection_report': '该车经过三方专业检测，结构件无损伤，发动机变速箱正常，油耗低，适合家用代步。'
            },
            {
                'name': '丰田卡罗拉 2020款 1.2T CVT精英版',
                'brand': '丰田',
                'price': 9.8,
                'year': 2020,
                'mileage': 2.5,
                'images': json.dumps([
                    '/static/images/car2_1.jpg',
                    '/static/images/car2_2.jpg',
                    '/static/images/car2_3.jpg'
                ]),
                'description': '精品车况，原版原漆，全程4S店保养记录可查，适合追求可靠的您。',
                'inspection_report': '第三方检测报告显示：车身骨架完好，无重大事故，水泡火烧排查正常，主要功能部件运行正常。'
            },
            {
                'name': '本田飞度 2021款 1.5L CVT潮跑版',
                'brand': '本田',
                'price': 8.2,
                'year': 2021,
                'mileage': 1.8,
                'images': json.dumps([
                    '/static/images/car3_1.jpg',
                    '/static/images/car3_2.jpg',
                    '/static/images/car3_3.jpg'
                ]),
                'description': '准新车状态，仅行驶1.8万公里，车身小巧灵活，省油耐用，城市通勤首选。',
                'inspection_report': '检测结果：优秀。车况极佳，全车原漆，无事故记录，各系统运行正常。'
            },
            {
                'name': '日产轩逸 2020款 1.6L CVT悦享版',
                'brand': '日产',
                'price': 8.5,
                'year': 2020,
                'mileage': 2.8,
                'images': json.dumps([
                    '/static/images/car4_1.jpg',
                    '/static/images/car4_2.jpg',
                    '/static/images/car4_3.jpg'
                ]),
                'description': '大空间家轿，座椅舒适，油耗低，维修保养便宜，是家用轿车的经典之选。',
                'inspection_report': '检测结果：良好。发动机运转平稳，变速箱换挡顺畅，底盘无异响。'
            },
            {
                'name': '现代悦动 2019款 1.6L自动悦值版',
                'brand': '现代',
                'price': 5.8,
                'year': 2019,
                'mileage': 4.5,
                'images': json.dumps([
                    '/static/images/car5_1.jpg',
                    '/static/images/car5_2.jpg',
                    '/static/images/car5_3.jpg'
                ]),
                'description': '性价比极高的合资紧凑型车，空间宽敞，配置丰富，适合预算有限的家庭。',
                'inspection_report': '检测结果：合格。无重大事故，发动机变速箱正常，主要部件运行良好。'
            },
            {
                'name': '别克英朗 2020款 1.3T自动轻混动精英型',
                'brand': '别克',
                'price': 7.2,
                'year': 2020,
                'mileage': 3.0,
                'images': json.dumps([
                    '/static/images/car6_1.jpg',
                    '/static/images/car6_2.jpg',
                    '/static/images/car6_3.jpg'
                ]),
                'description': '美系品质，底盘扎实，配备轻混动系统更加省油，内饰用料实在。',
                'inspection_report': '检测结果：良好。48V轻混系统工作正常，发动机变速箱工况良好。'
            }
        ]
        
        for car_data in sample_cars:
            car = Car(**car_data)
            db.session.add(car)
    
    db.session.commit()

# ============== 前台路由 ==============

@app.before_request
def log_visit():
    """记录访问日志"""
    if not request.path.startswith('/admin') and not request.path.startswith('/static'):
        log = VisitLog(ip=request.remote_addr, path=request.path)
        db.session.add(log)
        db.session.commit()

@app.route('/')
def index():
    """首页"""
    # 获取轮播图
    sliders = Slider.query.filter_by(status='active').order_by(Slider.order).all()
    
    # 获取精选车源（最近上架的6辆）
    featured_cars = Car.query.filter_by(status='onsale').order_by(Car.created_at.desc()).limit(6).all()
    
    # 获取网站设置
    shop_name = get_site_setting('shop_name', '蜀来驰二手车')
    shop_intro = get_site_setting('shop_intro', '')
    
    return render_template('index.html', 
                         sliders=sliders, 
                         featured_cars=featured_cars,
                         shop_name=shop_name,
                         shop_intro=shop_intro)

@app.route('/cars')
def cars():
    """车源列表页"""
    # 获取筛选参数
    price_range = request.args.get('price', '')
    brand = request.args.get('brand', '')
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # 构建查询
    query = Car.query.filter_by(status='onsale')
    
    # 价格筛选
    if price_range == 'under2':
        query = query.filter(Car.price < 2)
    elif price_range == '2to5':
        query = query.filter(Car.price >= 2, Car.price <= 5)
    elif price_range == '5to10':
        query = query.filter(Car.price > 5, Car.price <= 10)
    
    # 品牌筛选
    if brand:
        query = query.filter(Car.brand == brand)
    
    # 分页
    pagination = query.order_by(Car.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    cars = pagination.items
    
    # 获取所有品牌（用于筛选）
    all_brands = db.session.query(Car.brand).filter_by(status='onsale').distinct().all()
    all_brands = [b[0] for b in all_brands]
    
    return render_template('cars.html', 
                         cars=cars,
                         pagination=pagination,
                         all_brands=all_brands,
                         current_price=price_range,
                         current_brand=brand)

@app.route('/car/<int:car_id>')
def car_detail(car_id):
    """车辆详情页"""
    car = Car.query.get_or_404(car_id)
    
    # 增加浏览次数
    car.view_count += 1
    db.session.commit()
    
    # 解析图片JSON
    images = json.loads(car.images) if car.images else []
    
    # 获取网站设置
    shop_phone = get_site_setting('shop_phone', '400-888-8888')
    shop_wechat = get_site_setting('shop_wechat', 'slc888888')
    
    return render_template('car_detail.html', 
                         car=car, 
                         images=images,
                         shop_phone=shop_phone,
                         shop_wechat=shop_wechat)

@app.route('/contact')
def contact():
    """联系方式页"""
    settings = {
        'shop_name': get_site_setting('shop_name', '蜀来驰二手车'),
        'shop_address': get_site_setting('shop_address', '四川省威远县'),
        'shop_phone': get_site_setting('shop_phone', '400-888-8888'),
        'shop_wechat': get_site_setting('shop_wechat', 'slc888888'),
    }
    return render_template('contact.html', **settings)

# ============== 后台管理路由 ==============

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """管理员登录"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and check_password_hash(admin.password_hash, password):
            session['admin_id'] = admin.id
            session['admin_name'] = admin.username
            return jsonify({'success': True, 'message': '登录成功'})
        else:
            return jsonify({'success': False, 'message': '用户名或密码错误'})
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    """退出登录"""
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
def admin_index():
    """后台首页/仪表盘"""
    if not session.get('admin_id'):
        return redirect(url_for('admin_login'))
    
    # 统计数据
    total_cars = Car.query.count()
    on_sale_cars = Car.query.filter_by(status='onsale').count()
    total_views = db.session.query(db.func.sum(Car.view_count)).scalar() or 0
    
    # 最近的访问记录
    recent_visits = VisitLog.query.order_by(VisitLog.created_at.desc()).limit(20).all()
    
    # 今日访问量
    today = datetime.now().date()
    today_visits = VisitLog.query.filter(
        db.func.date(VisitLog.created_at) == today
    ).count()
    
    return render_template('admin/dashboard.html',
                         total_cars=total_cars,
                         on_sale_cars=on_sale_cars,
                         total_views=total_views,
                         today_visits=today_visits,
                         recent_visits=recent_visits)

@app.route('/admin/cars')
def admin_cars():
    """车辆管理列表"""
    if not session.get('admin_id'):
        return redirect(url_for('admin_login'))
    
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = Car.query
    if status:
        query = query.filter_by(status=status)
    
    pagination = query.order_by(Car.created_at.desc()).paginate(
        page=page, per_page=15, error_out=False
    )
    
    return render_template('admin/cars.html',
                         cars=pagination.items,
                         pagination=pagination,
                         current_status=status)

@app.route('/admin/car/add', methods=['GET', 'POST'])
def admin_car_add():
    """添加车辆"""
    if not session.get('admin_id'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        # 处理图片上传
        images = []
        for i in range(1, 6):  # 最多5张图片
            file_key = f'image{i}'
            if file_key in request.files:
                file = request.files[file_key]
                if file.filename:
                    path = save_image(file)
                    if path:
                        images.append(path)
        
        car = Car(
            name=request.form.get('name'),
            brand=request.form.get('brand'),
            price=float(request.form.get('price')),
            year=int(request.form.get('year')),
            mileage=float(request.form.get('mileage')),
            images=json.dumps(images),
            description=request.form.get('description'),
            inspection_report=request.form.get('inspection_report'),
            status=request.form.get('status', 'onsale')
        )
        
        db.session.add(car)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '添加成功', 'car_id': car.id})
    
    return render_template('admin/car_form.html', car=None)

@app.route('/admin/car/edit/<int:car_id>', methods=['GET', 'POST'])
def admin_car_edit(car_id):
    """编辑车辆"""
    if not session.get('admin_id'):
        return redirect(url_for('admin_login'))
    
    car = Car.query.get_or_404(car_id)
    
    if request.method == 'POST':
        car.name = request.form.get('name')
        car.brand = request.form.get('brand')
        car.price = float(request.form.get('price'))
        car.year = int(request.form.get('year'))
        car.mileage = float(request.form.get('mileage'))
        car.description = request.form.get('description')
        car.inspection_report = request.form.get('inspection_report')
        car.status = request.form.get('status', 'onsale')
        
        # 处理新上传的图片
        new_images = json.loads(car.images) if car.images else []
        for i in range(1, 6):
            file_key = f'image{i}'
            if file_key in request.files:
                file = request.files[file_key]
                if file.filename:
                    path = save_image(file)
                    if path:
                        new_images.append(path)
        
        if new_images:
            car.images = json.dumps(new_images)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': '更新成功'})
    
    # 解析现有图片
    car.images_list = json.loads(car.images) if car.images else []
    
    return render_template('admin/car_form.html', car=car)

@app.route('/admin/car/delete/<int:car_id>', methods=['POST'])
def admin_car_delete(car_id):
    """删除车辆"""
    if not session.get('admin_id'):
        return jsonify({'success': False, 'message': '请先登录'})
    
    car = Car.query.get_or_404(car_id)
    db.session.delete(car)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '删除成功'})

@app.route('/admin/car/toggle_status/<int:car_id>', methods=['POST'])
def admin_car_toggle_status(car_id):
    """切换车辆状态"""
    if not session.get('admin_id'):
        return jsonify({'success': False, 'message': '请先登录'})
    
    car = Car.query.get_or_404(car_id)
    car.status = 'sold' if car.status == 'onsale' else 'onsale'
    db.session.commit()
    
    return jsonify({'success': True, 'message': '状态已更新', 'status': car.status})

@app.route('/admin/settings', methods=['GET', 'POST'])
def admin_settings():
    """网站设置"""
    if not session.get('admin_id'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        settings_keys = ['shop_name', 'shop_address', 'shop_phone', 'shop_wechat', 'shop_intro']
        for key in settings_keys:
            value = request.form.get(key, '')
            set_site_setting(key, value)
        
        return jsonify({'success': True, 'message': '设置已保存'})
    
    settings = {
        'shop_name': get_site_setting('shop_name', ''),
        'shop_address': get_site_setting('shop_address', ''),
        'shop_phone': get_site_setting('shop_phone', ''),
        'shop_wechat': get_site_setting('shop_wechat', ''),
        'shop_intro': get_site_setting('shop_intro', ''),
    }
    
    return render_template('admin/settings.html', **settings)

@app.route('/admin/sliders')
def admin_sliders():
    """轮播图管理"""
    if not session.get('admin_id'):
        return redirect(url_for('admin_login'))
    
    sliders = Slider.query.order_by(Slider.order).all()
    return render_template('admin/sliders.html', sliders=sliders)

@app.route('/admin/slider/add', methods=['POST'])
def admin_slider_add():
    """添加轮播图"""
    if not session.get('admin_id'):
        return jsonify({'success': False, 'message': '请先登录'})
    
    file = request.files.get('image')
    if not file or not file.filename:
        return jsonify({'success': False, 'message': '请上传图片'})
    
    image_path = save_image(file, 'sliders')
    if not image_path:
        return jsonify({'success': False, 'message': '图片上传失败'})
    
    # 获取最大排序值
    max_order = db.session.query(db.func.max(Slider.order)).scalar() or 0
    
    slider = Slider(
        title=request.form.get('title', ''),
        image=image_path,
        link=request.form.get('link', ''),
        order=max_order + 1,
        status='active'
    )
    
    db.session.add(slider)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '添加成功'})

@app.route('/admin/slider/delete/<int:slider_id>', methods=['POST'])
def admin_slider_delete(slider_id):
    """删除轮播图"""
    if not session.get('admin_id'):
        return jsonify({'success': False, 'message': '请先登录'})
    
    slider = Slider.query.get_or_404(slider_id)
    db.session.delete(slider)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '删除成功'})

@app.route('/admin/password', methods=['GET', 'POST'])
def admin_password():
    """修改密码"""
    if not session.get('admin_id'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        old_password = request.form.get('old_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        admin = Admin.query.get(session['admin_id'])
        
        if not check_password_hash(admin.password_hash, old_password):
            return jsonify({'success': False, 'message': '原密码错误'})
        
        if new_password != confirm_password:
            return jsonify({'success': False, 'message': '两次密码输入不一致'})
        
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': '密码长度不能少于6位'})
        
        admin.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '密码修改成功'})
    
    return render_template('admin/password.html')

# ============== API接口 ==============

@app.route('/api/cars')
def api_cars():
    """获取车辆列表API"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = Car.query.filter_by(status='onsale')
    pagination = query.order_by(Car.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'success': True,
        'data': [{
            'id': car.id,
            'name': car.name,
            'brand': car.brand,
            'price': car.price,
            'year': car.year,
            'mileage': car.mileage,
            'images': json.loads(car.images)[0] if car.images else '',
            'view_count': car.view_count
        } for car in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

# ============== 初始化 ==============

with app.app_context():
    db.create_all()
    init_default_data()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
