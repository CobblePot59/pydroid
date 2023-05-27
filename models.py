from app import app, db
from sqlalchemy.exc import IntegrityError

class Sdk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=False)
    installed = db.Column(db.Boolean, nullable=False, default=0)

class Emulator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    image = db.Column(db.String(255), nullable=False)

# Insert Sdk
sdks = [
('2.3.3','system-images;android-10;default;x86','Intel x86 Atom System Image'),
('2.3.3','system-images;android-10;google_apis;x86','Google APIs Intel x86 Atom System Image'),
('4.0.3','system-images;android-15;default;x86','Intel x86 Atom System Image'),
('4.0.3','system-images;android-15;google_apis;x86','Google APIs Intel x86 Atom System Image'),
('4.1','system-images;android-16;default;x86','Intel x86 Atom System Image'),
('4.1','system-images;android-16;google_apis;x86','Google APIs Intel x86 Atom System Image'),
('4.2','system-images;android-17;default;x86','Intel x86 Atom System Image'),
('4.2','system-images;android-17;google_apis;x86','Google APIs Intel x86 Atom System Image'),
('4.3','system-images;android-18;default;x86','Intel x86 Atom System Image'),
('4.3','system-images;android-18;google_apis;x86','Google APIs Intel x86 Atom System Image'),
('4.4','system-images;android-19;default;x86','Intel x86 Atom System Image'),
('4.4','system-images;android-19;google_apis;x86','Google APIs Intel x86 Atom System Image'),
('5.0','system-images;android-21;default;x86','Intel x86 Atom System Image'),
('5.0','system-images;android-21;default;x86_64','Intel x86 Atom_64 System Image'),
('5.0','system-images;android-21;google_apis;x86','Google APIs Intel x86 Atom System Image'),
('5.0','system-images;android-21;google_apis;x86_64','Google APIs Intel x86 Atom_64 System Image'),
('5.1','system-images;android-22;default;x86','Intel x86 Atom System Image'),
('5.1','system-images;android-22;default;x86_64','Intel x86 Atom_64 System Image'),
('5.1','system-images;android-22;google_apis;x86','Google APIs Intel x86 Atom System Image'),
('5.1','system-images;android-22;google_apis;x86_64','Google APIs Intel x86 Atom_64 System Image'),
('6.0','system-images;android-23;default;x86','Intel x86 Atom System Image'),
('6.0','system-images;android-23;default;x86_64','Intel x86 Atom_64 System Image'),
('6.0','system-images;android-23;google_apis;x86','Google APIs Intel x86 Atom System Image'),
('6.0','system-images;android-23;google_apis;x86_64','Google APIs Intel x86 Atom_64 System Image'),
('7.0','system-images;android-24;default;x86','Intel x86 Atom System Image'),
('7.0','system-images;android-24;default;x86_64','Intel x86 Atom_64 System Image'),
('7.0','system-images;android-24;google_apis;x86','Google APIs Intel x86 Atom System Image'),
('7.0','system-images;android-24;google_apis;x86_64','Google APIs Intel x86 Atom_64 System Image'),
('7.0','system-images;android-24;google_apis_playstore;x86','Google Play Intel x86 Atom System Image'),
('7.1','system-images;android-25;default;x86','Intel x86 Atom System Image'),
('7.1','system-images;android-25;default;x86_64','Intel x86 Atom_64 System Image'),
('7.1','system-images;android-25;google_apis;x86','Google APIs Intel x86 Atom System Image'),
('7.1','system-images;android-25;google_apis;x86_64','Google APIs Intel x86 Atom_64 System Image'),
('7.1','system-images;android-25;google_apis_playstore;x86','Google Play Intel x86 Atom System Image'),
('8.0','system-images;android-26;default;x86','Intel x86 Atom System Image'),
('8.0','system-images;android-26;default;x86_64','Intel x86 Atom_64 System Image'),
('8.0','system-images;android-26;google_apis;x86','Google APIs Intel x86 Atom System Image'),
('8.0','system-images;android-26;google_apis;x86_64','Google APIs Intel x86 Atom_64 System Image'),
('8.0','system-images;android-26;google_apis_playstore;x86','Google Play Intel x86 Atom System Image'),
('8.1','system-images;android-27;default;x86','Intel x86 Atom System Image'),
('8.1','system-images;android-27;default;x86_64','Intel x86 Atom_64 System Image'),
('8.1','system-images;android-27;google_apis;x86','Google APIs Intel x86 Atom System Image'),
('8.1','system-images;android-27;google_apis_playstore;x86','Google Play Intel x86 Atom System Image'),
('9','system-images;android-28;default;x86','Intel x86 Atom System Image'),
('9','system-images;android-28;default;x86_64','Intel x86 Atom_64 System Image'),
('9','system-images;android-28;google_apis;x86','Google APIs Intel x86 Atom System Image'),
('9','system-images;android-28;google_apis;x86_64','Google APIs Intel x86 Atom_64 System Image'),
('9','system-images;android-28;google_apis_playstore;x86','Google Play Intel x86 Atom System Image'),
('9','system-images;android-28;google_apis_playstore;x86_64','Google Play Intel x86 Atom_64 System Image'),
('10','system-images;android-29;default;x86','Intel x86 Atom System Image'),
('10','system-images;android-29;default;x86_64','Intel x86 Atom_64 System Image'),
('10','system-images;android-29;google_apis;x86','Google APIs Intel x86 Atom System Image'),
('10','system-images;android-29;google_apis;x86_64','Google APIs Intel x86 Atom_64 System Image'),
('10','system-images;android-29;google_apis_playstore;x86','Google Play Intel x86 Atom System Image'),
('10','system-images;android-29;google_apis_playstore;x86_64','Google Play Intel x86 Atom_64 System Image'),
('11','system-images;android-30;default;x86_64','Intel x86 Atom_64 System Image'),
('11','system-images;android-30;google_apis;x86','Google APIs Intel x86 Atom System Image'),
('11','system-images;android-30;google_apis;x86_64','Google APIs Intel x86 Atom_64 System Image'),
('11','system-images;android-30;google_apis_playstore;x86','Google Play Intel x86 Atom System Image'),
('11','system-images;android-30;google_apis_playstore;x86_64','Google Play Intel x86 Atom_64 System Image'),
('12','system-images;android-31;default;x86_64','Intel x86 Atom_64 System Image'),
('12','system-images;android-31;google_apis;x86_64','Google APIs Intel x86 Atom_64 System Image'),
('12','system-images;android-31;google_apis_playstore;x86_64','Google Play Intel x86 Atom_64 System Image'),
('12L','system-images;android-32;google_apis;x86_64','Google APIs Intel x86 Atom_64 System Image'),
('12L','system-images;android-32;google_apis_playstore;x86_64','Google Play Intel x86 Atom_64 System Image'),
('13','system-images;android-33;google_apis;x86_64','Google APIs Intel x86 Atom_64 System Image'),
('13','system-images;android-33;google_apis_playstore;x86_64','Google Play Intel x86 Atom_64 System Image'),
('2.3.3','system-images;android-10;google_apis;armeabi-v7a','Google APIs ARM EABI v7a System Image'),
('4.0','system-images;android-14;default;armeabi-v7a','ARM EABI v7a System Image'),
('4.0.3','system-images;android-15;default;armeabi-v7a','ARM EABI v7a System Image'),
('4.0.3','system-images;android-15;google_apis;armeabi-v7a','Google APIs ARM EABI v7a System Image'),
('4.1','system-images;android-16;default;armeabi-v7a','ARM EABI v7a System Image'),
('4.1','system-images;android-16;google_apis;armeabi-v7a','Google APIs ARM EABI v7a System Image'),
('4.2','system-images;android-17;default;armeabi-v7a','ARM EABI v7a System Image'),
('4.2','system-images;android-17;google_apis;armeabi-v7a','Google APIs ARM EABI v7a System Image'),
('4.3','system-images;android-18;default;armeabi-v7a','ARM EABI v7a System Image'),
('4.3','system-images;android-18;google_apis;armeabi-v7a','Google APIs ARM EABI v7a System Image'),
('4.4','system-images;android-19;default;armeabi-v7a','ARM EABI v7a System Image'),
('4.4','system-images;android-19;google_apis;armeabi-v7a','Google APIs ARM EABI v7a System Image'),
('5.0','system-images;android-21;default;arm64-v8a','ARM 64 v8a System Image'),
('5.0','system-images;android-21;default;armeabi-v7a','ARM EABI v7a System Image'),
('5.0','system-images;android-21;google_apis;arm64-v8a','Google APIs ARM 64 v8a System Image'),
('5.0','system-images;android-21;google_apis;armeabi-v7a','Google APIs ARM EABI v7a System Image'),
('5.1','system-images;android-22;default;arm64-v8a','ARM 64 v8a System Image'),
('5.1','system-images;android-22;default;armeabi-v7a','ARM EABI v7a System Image'),
('5.1','system-images;android-22;google_apis;arm64-v8a','Google APIs ARM 64 v8a System Image'),
('5.1','system-images;android-22;google_apis;armeabi-v7a','Google APIs ARM EABI v7a System Image'),
('6.0','system-images;android-23;default;arm64-v8a','ARM 64 v8a System Image'),
('6.0','system-images;android-23;default;armeabi-v7a','ARM EABI v7a System Image'),
('6.0','system-images;android-23;google_apis;arm64-v8a','Google APIs ARM 64 v8a System Image'),
('6.0','system-images;android-23;google_apis;armeabi-v7a','Google APIs ARM EABI v7a System Image'),
('7.0','system-images;android-24;default;arm64-v8a','ARM 64 v8a System Image'),
('7.0','system-images;android-24;default;armeabi-v7a','ARM EABI v7a System Image'),
('7.0','system-images;android-24;google_apis;arm64-v8a','Google APIs ARM 64 v8a System Image'),
('7.1','system-images;android-25;default;arm64-v8a','ARM 64 v8a System Image'),
('7.1','system-images;android-25;google_apis;arm64-v8a','Google APIs ARM 64 v8a System Image'),
('7.1','system-images;android-25;google_apis;armeabi-v7a','Google APIs ARM EABI v7a System Image'),
('8.0','system-images;android-26;default;arm64-v8a','ARM 64 v8a System Image'),
('8.0','system-images;android-26;google_apis;arm64-v8a','Google APIs ARM 64 v8a System Image'),
('8.1','system-images;android-27;default;arm64-v8a','ARM 64 v8a System Image'),
('8.1','system-images;android-27;google_apis;arm64-v8a','Google APIs ARM 64 v8a System Image'),
('9','system-images;android-28;default;arm64-v8a','ARM 64 v8a System Image'),
('9','system-images;android-28;google_apis;arm64-v8a','Google APIs ARM 64 v8a System Image'),
('9','system-images;android-28;google_apis_playstore;arm64-v8a','Google ARM64-V8a Play ARM 64 v8a System Image'),
('10','system-images;android-29;default;arm64-v8a','ARM 64 v8a System Image'),
('10','system-images;android-29;google_apis;arm64-v8a','Google APIs ARM 64 v8a System Image'),
('11','system-images;android-30;default;arm64-v8a','ARM 64 v8a System Image'),
('11','system-images;android-30;google_apis;arm64-v8a','Google APIs ARM 64 v8a System Image'),
('11','system-images;android-30;google_atd;arm64-v8a','Google APIs ATD ARM 64 v8a System Image'),
('12','system-images;android-31;default;arm64-v8a','ARM 64 v8a System Image'),
('12','system-images;android-31;google_apis;arm64-v8a','Google APIs ARM 64 v8a System Image'),
('12L','system-images;android-32;android-desktop;arm64-v8a','Desktop ARM 64 v8a System Image'),
('12L','system-images;android-32;google_apis;arm64-v8a','Google APIs ARM 64 v8a System Image'),
('13','system-images;android-33;google_apis;arm64-v8a','Google APIs ARM 64 v8a System Image')
]

def insert_data():
    for sdk in sdks:
        db.session.add(Sdk(version=sdk[0], image=sdk[1], description=sdk[2]))
    db.session.commit()

with app.app_context():
    db.create_all()
    try:
        insert_data()
    except IntegrityError:
        pass
