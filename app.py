from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

def get_db():
    db_path = os.path.join(os.path.dirname(__file__), 'reserva_escolar.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

with get_db() as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS reservas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    solicitante TEXT NOT NULL,
                    recurso TEXT NOT NULL,
                    fecha_hora TEXT NOT NULL,
                    horas INTEGER NOT NULL,
                    estado TEXT NOT NULL)''')
    conn.commit()

HTML_RESERVAS = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ReservaEscolar - CECyTEC 302</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@1/css/pico.min.css">
</head>
<body class="container" style="padding-top: 20px;">
    <h2>ReservaEscolar - Control de Recursos y Salas</h2>
    <p><small>CECyTEC Plantel 5 Coyote | Grupo 302 | Sesión 19 de Noviembre de 2026</small></p>
    <hr>

    <section>
        <form action="/reservar" method="POST">
            <div class="grid">
                <input type="text" name="solicitante" required placeholder="Nombre del Solicitante">
                <select name="recurso" required>
                    <option value="" disabled selected>Seleccione Recurso</option>
                    <option value="Proyector Aula 9">Proyector Aula 9</option>
                    <option value="Carrito Laptop CC2">Carrito Laptop CC2</option>
                    <option value="Cancha Fut 7 / Audio">Cancha Fut 7 / Audio</option>
                </select>
            </div>
            <div class="grid">
                <input type="text" name="fecha_hora" required placeholder="Fecha y Hora (Ej. 19/11 09:00)">
                <input type="number" name="horas" min="1" max="8" value="1" required placeholder="Horas">
                <select name="estado" required>
                    <option value="Confirmada">Confirmada</option>
                    <option value="Pendiente">Pendiente</option>
                </select>
            </div>
            <button type="submit" style="background-color: #006341; border: none;">Registrar Reserva</button>
        </form>
    </section>

    <section style="margin-top: 30px;">
        <h3>Reservas Registradas</h3>
        <table>
            <thead>
                <tr>
                    <th>Folio</th>
                    <th>Solicitante</th>
                    <th>Recurso</th>
                    <th>Horario</th>
                    <th>Horas</th>
                    <th>Estado</th>
                </tr>
            </thead>
            <tbody>
                {% for r in reservas %}
                <tr>
                    <td>#{{ r.id }}</td>
                    <td><strong>{{ r.solicitante }}</strong></td>
                    <td>{{ r.recurso }}</td>
                    <td>{{ r.fecha_hora }}</td>
                    <td>{{ r.horas }}h</td>
                    <td><strong>{{ r.estado }}</strong></td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="6" style="text-align: center;">No hay reservas registradas todavía.</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </section>
</body>
</html>
"""

@app.route('/')
def inicio():
    try:
        conn = get_db()
        reservas = conn.execute('SELECT * FROM reservas ORDER BY id DESC').fetchall()
        conn.close()
    except Exception:
        reservas = []
    return render_template_string(HTML_RESERVAS, reservas=reservas)

@app.route('/reservar', methods=['POST'])
def reservar():
    try:
        solicitante = request.form.get('solicitante', 'Sin Nombre').strip()
        recurso = request.form.get('recurso', 'General').strip()
        fecha_hora = request.form.get('fecha_hora', 'Por definir').strip()
        horas = int(request.form.get('horas', 1))
        if horas < 1:
            horas = 1
        estado = request.form.get('estado', 'Confirmada').strip()

        conn = get_db()
        conn.execute(
            'INSERT INTO reservas (solicitante, recurso, fecha_hora, horas, estado) VALUES (?, ?, ?, ?, ?)',
            (solicitante, recurso, fecha_hora, horas, estado)
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

    return redirect(url_for('inicio'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
