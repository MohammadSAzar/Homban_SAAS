from django.utils.translation import gettext as _


# --------------------------------- FILES ---------------------------------
beings = [
    ('is', _('Is')),
    ('isnt', _('Is not')),
]


booleans = [
    ('has', _('Has')),
    ('hasnt', _('Has Not')),
]


restorations = [
    ('done', _('Done')),
    ('dont', _('not Done')),
]


statuses = [
    ('acc', _('Accepted')),
    ('can', _('Canceled')),
    ('pen', _('Pending')),
]


directions = [
    ('nth', _('North')),
    ('sth', _('South')),
    ('est', _('East')),
    ('wst', _('West')),
]


hot_water = [
    ('HW', 'آبگرم‌کن'),
    ('MH', 'موتورخانه'),
    ('PK', 'پکیج'),
    ('OT', 'سایر'),
]


toilets = [
    ('IR', 'ایرانی'),
    ('FG', 'فرنگی'),
    ('BT', 'هر دو'),
]


sources = [
    ('DV', 'دیوار'),
    ('KS', 'کاشانو'),
    ('SK', 'اسکان'),
    ('OT', 'سایر'),
    ('PV', 'پیوند'),
    ('EH', 'احیایی'),
    ('PN', 'شخص'),
]


apartments_per_level = [
    ('one', 'تک واحدی'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
    ('7', '7'),
    ('8', '8'),
    ('9', '9'),
    ('10', '10'),
    ('more-10', 'بیش از 10'),
]


rooms = [
    ('0', 'بدون اتاق'),
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', 'بیش از 5'),
]


levels = [
    ('-1', 'زیر همکف'),
    ('0', 'همکف'),
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
    ('7', '7'),
    ('8', '8'),
    ('9', '9'),
    ('10', '10'),
    ('11', '11'),
    ('12', '12'),
    ('13', '13'),
    ('14', '14'),
    ('15', '15'),
    ('16', '16'),
    ('17', '17'),
    ('18', '18'),
    ('19', '19'),
    ('20', '20'),
    ('21', '21'),
    ('22', '22'),
    ('23', '23'),
    ('24', '24'),
    ('25', '25'),
    ('26', '26'),
    ('27', '27'),
    ('28', '28'),
    ('29', '29'),
    ('30', '30'),
    ('31', 'بالاتر از 30'),
]


ages = [
    ('-1', 'کلید نخورده'),
    ('0', 'نوساز'),
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
    ('7', '7'),
    ('8', '8'),
    ('9', '9'),
    ('10', '10'),
    ('11', '11'),
    ('12', '12'),
    ('13', '13'),
    ('14', '14'),
    ('15', '15'),
    ('16', '16'),
    ('17', '17'),
    ('18', '18'),
    ('19', '19'),
    ('20', '20'),
    ('21', '21'),
    ('22', '22'),
    ('23', '23'),
    ('24', '24'),
    ('25', '25'),
    ('26', '26'),
    ('27', '27'),
    ('28', '28'),
    ('29', '29'),
    ('30', '30'),
    ('31', 'بیش از 30'),
]


# --------------------------------- SERVS --------------------------------
times = [
    ('mg', _('Morning')),
    ('nn', _('Noon')),
    ('eg', _('Evening')),
    ('nt', _('Night')),
]


serv_statuses = [
    ('sub', 'منتظر تایید'),
    ('acc', 'آماده انجام'),
    ('can', 'رد شده'),
    ('dne', 'انجام شده'),
    ('end', 'تایید نتیجه'),
]


fc_statuses = [
    ('tkn', 'گرفته شده'),
    ('ntk', 'گرفته نشده'),
]


types = [
    ('sale', _('Sale')),
    ('rent', _('Rent')),
    ]


budgets = [
    ('CS', 'نقد'),
    ('UC', 'غیر نقد'),
]

# --------------------------------- MNGs --------------------------------
task_types = [
    ('fp', _('For File Person')),
    ('cp', _('For Customer Person')),
    ('bt', _('For Dual Person')),
]


task_statuses = [
    ('OP', 'باز'),
    ('UR', 'تحویل داده شده'),
    ('CL', 'بسته'),
]


boss_task_types = [
    ('sf', 'فایل فروش جدید'),
    ('rf', 'فایل اجاره جدید'),
    ('by', 'خریدار جدید'),
    ('rt', 'مستاجر جدید'),
    ('ps', 'آگهی‌دهنده جدید'),
    ('vs', 'بازدید جدید'),
    ('ss', 'نشست جدید'),
    ('rv', 'نتیجه بازدید'),
    ('rs', 'نتیجه نشست'),
    ('ts', 'نتیجه وظیفه'),
]


boss_task_statuses = [
    ('op', 'باز'),
    ('cl', 'بسته'),
]


# --------------------------------- DELs --------------------------------
yes_or_no = [
    ('Yes', 'بله'),
    ('No', 'خیر'),
]



