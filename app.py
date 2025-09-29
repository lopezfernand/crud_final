import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Crear instancia de Flask
app = Flask(__name__)

# Configuración de la base de datos (Render)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo
class Estudiante(db.Model):
    __tablename__ = 'estudiantes'
    no_control = db.Column(db.String, primary_key=True)
    nombre = db.Column(db.String)
    ap_paterno = db.Column(db.String)
    ap_materno = db.Column(db.String)
    semestre = db.Column(db.Integer)

    def to_dict(self):
        return {
            'no_control': self.no_control,
            'nombre': self.nombre,
            'ap_paterno': self.ap_paterno,
            'ap_materno': self.ap_materno,
            'semestre': self.semestre,
        }

# ===== Web =====
@app.route('/')
def home():
    return render_template('index.html')

# Formulario web: crear estudiante (GET/POST)
@app.route('/estudiantes/new', methods=['GET', 'POST'])
def create_estudiante():
    if request.method == 'POST':
        no_control = request.form['no_control']
        nombre = request.form.get('nombre')
        ap_paterno = request.form.get('ap_paterno')
        ap_materno = request.form.get('ap_materno')
        semestre = request.form.get('semestre')

        e = Estudiante(
            no_control=no_control,
            nombre=nombre,
            ap_paterno=ap_paterno,
            ap_materno=ap_materno,
            semestre=int(semestre) if semestre else None
        )
        db.session.add(e)
        db.session.commit()
        return redirect(url_for('home'))

    # GET: muestra el formulario
    return render_template('create_estudiante.html')

# ===== API REST =====
# Listar todos
@app.route('/estudiantes', methods=['GET'])
def api_list():
    estudiantes = Estudiante.query.all()
    return jsonify([e.to_dict() for e in estudiantes])

# Obtener uno
@app.route('/estudiantes/<no_control>', methods=['GET'])
def api_get(no_control):
    e = Estudiante.query.get(no_control)
    if e is None:
        return jsonify({'msg': 'Estudiante no encontrado'}), 404
    return jsonify(e.to_dict())

# Crear (API)
@app.route('/estudiantes', methods=['POST'])
def api_create():
    data = request.get_json()
    e = Estudiante(
        no_control=data['no_control'],
        nombre=data.get('nombre'),
        ap_paterno=data.get('ap_paterno'),
        ap_materno=data.get('ap_materno'),
        semestre=data.get('semestre'),
    )
    db.session.add(e)
    db.session.commit()
    return jsonify({'msg': 'Estudiante agregado correctamente'})

# Actualizar parcial (API)
@app.route('/estudiantes/<no_control>', methods=['PATCH'])
def api_update(no_control):
    e = Estudiante.query.get(no_control)
    if e is None:
        return jsonify({'msg': 'Estudiante no encontrado'}), 404
    data = request.get_json() or {}
    if 'nombre' in data: e.nombre = data['nombre']
    if 'ap_paterno' in data: e.ap_paterno = data['ap_paterno']
    if 'ap_materno' in data: e.ap_materno = data['ap_materno']
    if 'semestre' in data: e.semestre = data['semestre']
    db.session.commit()
    return jsonify({'msg': 'Estudiante actualizado correctamente'})

# Eliminar (API)
@app.route('/estudiantes/<no_control>', methods=['DELETE'])
def api_delete(no_control):
    e = Estudiante.query.get(no_control)
    if e is None:
        return jsonify({'msg': 'Estudiante no encontrado'}), 404
    db.session.delete(e)
    db.session.commit()
    return jsonify({'msg': 'Estudiante eliminado correctamente'})
# ---- Vista: eliminar estudiante ----
@app.route('/estudiantes/delete/<string:no_control>')
def delete_estudiante(no_control):
    e = Estudiante.query.get(no_control)
    if e:
        db.session.delete(e)
        db.session.commit()
    return redirect(url_for('home'))

# ---- Vista: actualizar estudiante (GET/POST) ----
@app.route('/estudiantes/update/<string:no_control>', methods=['GET', 'POST'])
def update_estudiante(no_control):
    e = Estudiante.query.get(no_control)
    if not e:
        return redirect(url_for('home'))

    if request.method == 'POST':
        e.nombre = request.form.get('nombre') or None
        e.ap_paterno = request.form.get('ap_paterno') or None
        e.ap_materno = request.form.get('ap_materno') or None
        sem = request.form.get('semestre')
        e.semestre = int(sem) if sem else None
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('update_estudiante.html', e=e)

if __name__ == '__main__':
    app.run(debug=True)
